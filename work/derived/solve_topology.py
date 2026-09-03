# -*- coding: utf-8 -*-
"""L3 拓扑求解 v2（纯 Python 全枚举；CP-SAT 已弃）。

弃用 CP-SAT 的原因（登记于 SOURCE_PROVENANCE）：本环境 ortools wheel 的 CpSolver.Solve
对最小模型即触发 0xC0000005 访问违例，与建模无关，故改用纯 Python 全枚举。
内层搜索空间小（悬空端候选 × {none}），全枚举可行且比 k-best 更强：频率为精确值、无采样。

方法（保守穷举，不裁决）：
  - 外层穷举离散假设世界(world)：重名组是否合并（H_same/H_segment→合并；H_distinct→不合并）
    × 未知标记实体 functional ∈ {0,1}。本实例 = 2^2 × 2^5 = 128 世界。
  - 内层对每个世界全枚举悬空端附着（每端 ∈ 候选 ∪ {none}），hidden-edge 需求为派生整数
    hidden_need = max(0, required - observed_incident - attachments)，不占搜索维。
  - 每个世界取目标最小解集（P0h：min Σhidden_need；P1：再加 min 附着几何距离 + min functional 数）；
    解集内及跨世界的频率即稳定/歧义依据。
  - P0 严格版（不加 --allow-hidden）：观测 incident 不足即判该世界 infeasible（degree_deficit），
    用于实证"盲逆在闭合公理下不可解"。
  - 每世界枚举量有上限保护（--max-inner），超限截断并记录 truncated=true。
"""
from __future__ import annotations

import argparse
import itertools
import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MERGED = ROOT / "work/derived/observations.merged.yaml"

REQUIRED_INCIDENT = {"pump": 2, "column": 1, "vessel": 1, "exchanger": 1, "reactor": 1}


def dist(g1: dict | None, g2: dict | None) -> float:
    if not g1 or not g2:
        return 1e9
    c1 = (g1["x"] + g1["width"] / 2, g1["y"] + g1["height"] / 2)
    c2 = (g2["x"] + g2["width"] / 2, g2["y"] + g2["height"] / 2)
    return math.hypot(c1[0] - c2[0], c1[1] - c2[1])


def geom_of(e: dict, src_pref: tuple[str, ...] = ("p2", "p1r")) -> dict | None:
    for s in src_pref:
        if e["geom"].get(s):
            return e["geom"][s]
    for v in e["geom"].values():
        if v:
            return v
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="P0", choices=["P0", "P1"])
    ap.add_argument("--out", default="work/derived/solver_result.yaml")
    ap.add_argument("--max-inner", type=int, default=200000, help="每世界内层枚举上限保护")
    ap.add_argument("--allow-hidden", action="store_true",
                    help="承认漏画：hidden-edge 派生整数补足度数（P0 严格版不加）")
    args = ap.parse_args()

    with MERGED.open(encoding="utf-8") as f:
        merged = yaml.safe_load(f)
    entities = {e["id"]: e for e in merged["entities"]}
    obs = [(e["id"], e["a"], e["b"]) for e in merged["edges"]]
    id_pair = {eid: [a, b] for (eid, a, b) in obs}
    dangles = merged["dangles"]
    dup_groups = merged["hypotheses"]["duplicate_identity"]
    unknown_ids = [h["entity"] for h in merged["hypotheses"]["functional"]]

    dangle_cands = []
    for d in dangles:
        a = d["anchored"]
        if a not in entities:
            dangle_cands.append([])
            continue
        ga = geom_of(entities[a])
        cands = [k for k in entities if k != a]
        if args.tier == "P1" and ga:
            cands.sort(key=lambda k: dist(ga, geom_of(entities[k])))
            cands = cands[:8]
        dangle_cands.append(cands)

    dup_tags = [g["tag"] for g in dup_groups]
    # 物理标签：重号组成员统一用其 tag（H_same 下二者即同一容器），用于跨世界频率统计
    member_label = {m: g["tag"] for g in dup_groups for m in g["members"]}

    def L(k: str) -> str:
        return member_label.get(k, k)

    combos = list(itertools.product([0, 1], repeat=len(dup_tags) + len(unknown_ids)))

    worlds = 0
    edge_freq: dict[str, int] = {eid: 0 for (eid, _, _) in obs}
    dangle_freq: list[dict[str, int]] = [{} for _ in dangles]
    hidden_stats: list[int] = []
    iter_log: list[dict] = []
    truncated_any = False

    for combo in combos:
        merge_flags = dict(zip(dup_tags, combo[: len(dup_tags)]))
        func_flags = dict(zip(unknown_ids, combo[len(dup_tags):]))

        rep = {}
        for g in dup_groups:
            leader = g["members"][0]
            for m in g["members"]:
                rep[m] = leader if merge_flags[g["tag"]] else m

        def R(k: str) -> str:
            return rep.get(k, k)

        functional = {k for k in entities if k not in unknown_ids}
        incident: dict[str, int] = {k: 0 for k in entities}
        active_ids: set[str] = set()
        loops: set[str] = set()
        for (eid, a, b) in obs:
            if a == b:
                active_ids.add(eid)   # 原始自环（recycle）：保留为 loop 观测
                loops.add(eid)
                continue
            ra, rb = R(a), R(b)
            if ra == rb:
                continue              # 本世界因重号合并而退化为自环：该观测边不存在
            active_ids.add(eid)
            incident[ra] += 1
            incident[rb] += 1

        deficient = [
            {"entity": k, "shape": entities[k]["shape_class"],
             "observed_incident": incident[R(k)],
             "required": REQUIRED_INCIDENT.get(entities[k]["shape_class"], 1)}
            for k in functional
            if incident[R(k)] < REQUIRED_INCIDENT.get(entities[k]["shape_class"], 1)
        ]
        if deficient and not args.allow_hidden:
            iter_log.append({"world": {"merge": merge_flags, "func": func_flags},
                             "feasible": False, "reason": "degree_deficit", "n_deficient": len(deficient)})
            continue

        # 内层全枚举悬空附着
        options = [[None] + c for c in dangle_cands]
        inner = list(itertools.product(*options)) if options else [()]
        truncated = len(inner) > args.max_inner
        if truncated:
            inner = inner[: args.max_inner]
        truncated_any = truncated_any or truncated

        scored: list[tuple[int, float, tuple]] = []
        for assign in inner:
            adds: dict[str, int] = {}
            for di, c in enumerate(assign):
                if c is not None:
                    adds[R(c)] = adds.get(R(c), 0) + 1
            hidden_need = 0
            for k in functional:
                req = REQUIRED_INCIDENT.get(entities[k]["shape_class"], 1)
                need = req - incident[k] - adds.get(R(k), 0)
                if need > 0:
                    hidden_need += need
            geo = 0.0
            if args.tier == "P1":
                for di, c in enumerate(assign):
                    if c is not None:
                        ga = geom_of(entities[dangles[di]["anchored"]]) if dangles[di]["anchored"] in entities else None
                        geo += dist(ga, geom_of(entities[c]))
            obj = hidden_need + (0 if args.tier != "P1" else 0)
            scored.append((obj, geo, assign))
        if not scored:
            iter_log.append({"world": {"merge": merge_flags, "func": func_flags},
                             "feasible": False, "reason": "no_inner"})
            continue
        best_obj = min(s[0] for s in scored)
        best_geo = min(s[1] for s in scored if s[0] == best_obj)
        optimal = [s for s in scored if s[0] == best_obj and s[1] == best_geo]

        worlds += len(optimal)
        for (obj, geo, assign) in optimal:
            for eid in active_ids:
                edge_freq[eid] += 1
            for di, c in enumerate(assign):
                if c is not None:
                    lc = L(R(c))
                    dangle_freq[di][lc] = dangle_freq[di].get(lc, 0) + 1
            hn = obj
            hidden_stats.append(hn)
        iter_log.append({"world": {"merge": merge_flags, "func": func_flags}, "feasible": True,
                         "n_optimal": len(optimal), "best_hidden_need": best_obj,
                         "active_edges": len(active_ids), "loops": sorted(loops), "truncated": truncated})

    stable = [{"edge": id_pair[eid], "id": eid} for eid, c in edge_freq.items() if worlds and c == worlds]
    ambiguous = [{"edge": id_pair[eid], "id": eid, "freq": c, "of_worlds": worlds}
                 for eid, c in edge_freq.items() if 0 < c < worlds]
    absent = [{"edge": id_pair[eid], "id": eid} for eid, c in edge_freq.items() if c == 0]

    out = ROOT / args.out
    doc = {
        "meta": {
            "level": "L3", "tier": args.tier,
            "solver": "pure_python_full_enumeration (CP-SAT abandoned: ortools wheel segfault 0xC0000005)",
            "input": "work/derived/observations.merged.yaml",
            "script": "work/derived/solve_topology.py",
            "allow_hidden": args.allow_hidden,
            "enumeration": f"worlds_outer={len(combos)} inner=full(dangle attach)",
            "truncated_any": truncated_any,
        },
        "summary": {
            "combos_total": len(combos), "worlds_optimal": worlds,
            "stable_edges": stable, "ambiguous_edges": ambiguous, "absent_edges": absent,
            "dangle_attachment_freq": dangle_freq,
            "hidden_need": ({
                "min": min(hidden_stats) if hidden_stats else None,
                "max": max(hidden_stats) if hidden_stats else None,
                "mean": round(sum(hidden_stats) / len(hidden_stats), 2) if hidden_stats else None,
            } if hidden_stats else None),
        },
        "iteration_log": iter_log,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)
    print(f"[ok] tier={args.tier} allow_hidden={args.allow_hidden} wrote {out.relative_to(ROOT)}")
    print(f"  combos={len(combos)} worlds_optimal={worlds}")
    print(f"  stable={len(stable)} ambiguous={len(ambiguous)} absent={len(absent)}")
    if hidden_stats:
        print(f"  hidden_need min/max/mean={min(hidden_stats)}/{max(hidden_stats)}/{sum(hidden_stats)/len(hidden_stats):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
