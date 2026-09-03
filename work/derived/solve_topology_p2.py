# -*- coding: utf-8 -*-
"""L3 拓扑求解 P2（MILP via scipy/HiGHS；观测边可 drop + 语法候选 hidden 边）。

P2 相对 P0h 的新增（让歧义显形）：
  - 每条**观测边**加 drop 布尔变量（= 该边可能是假管/画错/不存在），重罚 1000；
  - 由**通用精馏/命名语法**生成候选 hidden 边（布尔变量，罚 100）：
      塔↔其冷凝器/冷却器、塔↔其再沸器/重沸器、塔↔其回流罐、冷凝器↔回流罐、
      泵↔共享物料词（甲醇/C4/萃取水/MTBE/醚后）的罐或塔；
    语法仅用 name_zh 的子串/物料词，属通用单元语法（非 MTBE 序列先验，那是 P3）；
  - 悬空端附着 one-hot（罚 = 几何距离/50 取整 +1）；
  - 度数闭合：观测(未drop) + 语法 + 附着 + slack ≥ required；slack 重罚 5000 作最后手段；
  - 未知标记实体（断了？/黑盒/放空/汇合）**不加度数约束**（可为假管），其边靠 drop 表达；
  - 重号合并仍外层穷举（2 组 → 4 combo），每 combo 用整数割枚举 ≤K 个最优解；
  - 频率跨全部枚举解统计：drop_freq>0 的观测边 = "可能画错/假管"候选；
    use_freq 高的语法边 = 推断的 hidden 边；drop_freq=0 的观测边 = P2 稳定。
求解器：scipy.optimize.milp (HiGHS)。ortools 因 wheel 段错误已弃（见 SOURCE_PROVENANCE 第 8 条）。
"""
from __future__ import annotations

import argparse
import itertools
import math
import re
from pathlib import Path

import yaml
import numpy as np
from scipy.optimize import LinearConstraint, milp

ROOT = Path(__file__).resolve().parents[2]
MERGED = ROOT / "work/derived/observations.merged.yaml"

REQUIRED_INCIDENT = {"pump": 2, "column": 1, "vessel": 1, "exchanger": 1, "reactor": 1}
COND_W = ("冷凝器", "冷却器")
REB_W = ("再沸器", "重沸器")
MAT_W = ("甲醇", "C4", "萃取水", "MTBE", "醚后")


def dist(g1: dict | None, g2: dict | None) -> float:
    if not g1 or not g2:
        return 1e9
    c1 = (g1["x"] + g1["width"] / 2, g1["y"] + g1["height"] / 2)
    c2 = (g2["x"] + g2["width"] / 2, g2["y"] + g2["height"] / 2)
    return math.hypot(c1[0] - c2[0], c1[1] - c2[1])


def geom_of(e: dict) -> dict | None:
    for s in ("p2", "p1r"):
        if e["geom"].get(s):
            return e["geom"][s]
    for v in e["geom"].values():
        if v:
            return v
    return None


def grammar_candidates(entities: dict, observed_pairs: set) -> list[tuple[str, str, str]]:
    """通用精馏/命名语法候选 hidden 边。返回 (a, b, rule)。"""
    names = {k: e["name_zh"] for k, e in entities.items() if e.get("name_zh")}
    columns = [k for k in names if entities[k]["shape_class"] == "column"]
    tok_of: dict[str, set[str]] = {}
    for c in columns:
        base = names[c]
        tok_of[c] = {base, re.sub(r"(上塔|下塔)$", "", base)} - {""}
    out: list[tuple[str, str, str]] = []
    seen = set()

    def add(a: str, b: str, rule: str) -> None:
        p = tuple(sorted((a, b)))
        if a == b or p in seen or p in observed_pairs:
            return
        seen.add(p)
        out.append((p[0], p[1], rule))

    for k, n in names.items():
        for c in columns:
            for tok in tok_of[c]:
                if tok and tok != n and tok in n:
                    if any(w in n for w in COND_W):
                        add(c, k, f"column<->condenser[{tok}]")
                    if any(w in n for w in REB_W):
                        add(c, k, f"column<->reboiler[{tok}]")
                    if "回流罐" in n:
                        add(c, k, f"column<->refluxdrum[{tok}]")
    alltok = set().union(*tok_of.values()) if tok_of else set()
    for tok in alltok:
        conds = [k for k, n in names.items() if tok in n and any(w in n for w in COND_W)]
        drums = [k for k, n in names.items() if tok in n and "回流罐" in n]
        for c in conds:
            for d in drums:
                add(c, d, f"condenser<->refluxdrum[{tok}]")
    for k, n in names.items():
        if "泵" not in n:
            continue
        for mat in MAT_W:
            if mat in n:
                for j, m in names.items():
                    if j != k and mat in m and ("罐" in m or "塔" in m):
                        add(k, j, f"pump<->share[{mat}]")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="work/derived/solver_result_P2.yaml")
    ap.add_argument("--k", type=int, default=12, help="每 combo 枚举最优解上限")
    ap.add_argument("--max-seconds", type=float, default=10.0)
    ap.add_argument("--max-gram", type=int, default=80)
    args = ap.parse_args()

    with MERGED.open(encoding="utf-8") as f:
        merged = yaml.safe_load(f)
    entities = {e["id"]: e for e in merged["entities"]}
    edges = merged["edges"]
    dangles = merged["dangles"]
    dup_groups = merged["hypotheses"]["duplicate_identity"]
    observed_pairs = {tuple(sorted((e["a"], e["b"]))) for e in edges if e["a"] != e["b"]}
    grams_all = grammar_candidates(entities, observed_pairs)
    truncated_gram = len(grams_all) > args.max_gram
    grams = grams_all[: args.max_gram]

    dup_tags = [g["tag"] for g in dup_groups]
    combos = list(itertools.product([0, 1], repeat=len(dup_tags)))

    drop_freq: dict[str, int] = {e["id"]: 0 for e in edges}
    gram_freq: dict[tuple[str, str], int] = {g[:2]: 0 for g in grams}
    att_freq: list[dict[str, int]] = [{} for _ in dangles]
    nsol = 0
    log = []

    for combo in combos:
        merge_flags = dict(zip(dup_tags, combo))
        rep = {}
        for g in dup_groups:
            leader = g["members"][0]
            for m in g["members"]:
                rep[m] = leader if merge_flags[g["tag"]] else m

        def R(k: str) -> str:
            return rep.get(k, k)

        functional = [k for k in entities if entities[k]["tag_status"] != "unknown_marker"]
        # 变量布局
        E, G = len(edges), len(grams)
        natt = sum(max(1, len([c for c in entities if c != d["anchored"]])) for d in dangles)
        att_idx: list[list[tuple[str, int]]] = []
        base = E + G
        ptr = base
        for d in dangles:
            cands = [c for c in entities if c != d["anchored"]]
            att_idx.append([(c, ptr + i) for i, c in enumerate(cands)])
            ptr += max(1, len(cands))
        slack_idx = {k: ptr + i for i, k in enumerate(functional)}
        nvar = ptr + len(functional)

        c = [0.0] * nvar
        for i in range(E):
            c[i] = 1000.0
        for i in range(G):
            c[E + i] = 100.0
        for d_i, d in enumerate(dangles):
            ga = geom_of(entities[d["anchored"]]) if d["anchored"] in entities else None
            for (cc, idx) in att_idx[d_i]:
                c[idx] = float(int(dist(ga, geom_of(entities[cc])) / 50) + 1)
        for k in functional:
            c[slack_idx[k]] = 5000.0

        rows_A: list[list[float]] = []
        rows_lb: list[float] = []
        rows_ub: list[float] = []
        for k in functional:
            row = [0.0] * nvar
            deg = 0
            for i, e in enumerate(edges):
                if e["a"] == e["b"]:
                    continue
                if R(e["a"]) == R(k) or R(e["b"]) == R(k):
                    row[i] -= 1.0
                    deg += 1
            for gi, (a, b, _) in enumerate(grams):
                if R(a) == R(k) or R(b) == R(k):
                    row[E + gi] += 1.0
            for d_i, lst in enumerate(att_idx):
                for (cc, idx) in lst:
                    if R(cc) == R(k):
                        row[idx] += 1.0
            row[slack_idx[k]] += 1.0
            req = REQUIRED_INCIDENT.get(entities[k]["shape_class"], 1)
            rows_A.append(row)
            rows_lb.append(float(req - deg))
            rows_ub.append(math.inf)
        for lst in att_idx:
            row = [0.0] * nvar
            for (_, idx) in lst:
                row[idx] = 1.0
            rows_A.append(row)
            rows_lb.append(-math.inf)
            rows_ub.append(1.0)

        integrality = [1.0] * (base) + [0.0] * (nvar - base)
        lbs = [0.0] * nvar
        ubs = [1.0] * base + [math.inf] * (nvar - base)
        constraints = LinearConstraint(rows_A, rows_lb, rows_ub) if rows_A else None

        cuts: list[tuple[list[float], float]] = []
        for _ in range(args.k):
            all_A = rows_A + [ct[0] for ct in cuts]
            all_lb = rows_lb + [-math.inf] * len(cuts)
            all_ub = rows_ub + [ct[1] for ct in cuts]
            res = milp(
                c=c,
                constraints=LinearConstraint(all_A, all_lb, all_ub),
                integrality=integrality,
                bounds=(np.array(lbs), np.array(ubs)),
                options={"time_limit": args.max_seconds},
            )
            if res.status != 0 or res.x is None:
                break
            x = res.x
            nsol += 1
            for i, e in enumerate(edges):
                if x[i] > 0.5:
                    drop_freq[e["id"]] += 1
            for gi, (a, b, _) in enumerate(grams):
                if x[E + gi] > 0.5:
                    gram_freq[(a, b)] += 1
            for d_i, lst in enumerate(att_idx):
                for (cc, idx) in lst:
                    if x[idx] > 0.5:
                        att_freq[d_i][R(cc)] = att_freq[d_i].get(R(cc), 0) + 1
            # 整数割：排除本解（仅二元部分）
            row = [0.0] * nvar
            s1 = 0
            for i in range(base):
                if x[i] > 0.5:
                    row[i] = 1.0
                    s1 += 1
                else:
                    row[i] = -1.0
            cuts.append((row, float(s1 - 1)))
        log.append({"merge": merge_flags, "solutions": nsol})

    observed_summary = [
        {"id": e["id"], "edge": [e["a"], e["b"]], "drop_freq": drop_freq[e["id"]], "of_solutions": nsol}
        for e in edges
    ]
    gram_summary = [
        {"edge": list(k), "rule": next(r for (a, b, r) in grams_all if (a, b) == k),
         "use_freq": v, "of_solutions": nsol}
        for k, v in gram_freq.items() if v > 0
    ]
    doc = {
        "meta": {
            "level": "L3", "tier": "P2", "solver": "scipy.optimize.milp (HiGHS)",
            "input": "work/derived/observations.merged.yaml",
            "script": "work/derived/solve_topology_p2.py",
            "grammar_candidates_total": len(grams_all), "grammar_used": len(grams),
            "grammar_truncated": truncated_gram,
            "penalties": {"drop_obs": 1000, "gram": 100, "slack": 5000, "attach": "geo/50+1"},
        },
        "summary": {
            "solutions": nsol,
            "observed_edges": observed_summary,
            "inferred_grammar_edges": gram_summary,
            "dangle_attachment_freq": att_freq,
        },
        "log": log,
    }
    out = ROOT / args.out
    with out.open("w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)
    ndrop = sum(1 for e in edges if drop_freq[e["id"]] > 0)
    nstable = sum(1 for e in edges if drop_freq[e["id"]] == 0 and nsol)
    print(f"[ok] tier=P2 wrote {out.relative_to(ROOT)}")
    print(f"  solutions={nsol} grammar_candidates={len(grams)}")
    print(f"  observed_stable={nstable} observed_drop_candidate={ndrop}")
    print(f"  inferred_grammar_edges_nonzero={len(gram_summary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
