# -*- coding: utf-8 -*-
"""L3 P4 最小补集枚举（A5 规则落地：补也试出来、只补最小必需、禁最乐观）。

固定边 = 观测 40 条（无向）+ P2 稳定语法推断 3 条 + A1/A2/A3 裁决 3 条。
候选补边 c1–c7 = 标准 MTBE 骨架中"物料必须有去处"逼出的边（背书见 prior_backing.yaml D11）。
不闭合白名单（声明为测绘缺陷、不补）：E-3502、E-3503（名字与位号类型不符，身份不明）、FV301（阀无管线）。
模型：min Σ c_i  s.t. 每台功能设备度数闭合（泵≥2，其余≥1）；整数割枚举 ≤K 个最小解；
      稳定候选 = 所有最小解都用；备选 = 部分解用。求解器 scipy.optimize.milp (HiGHS)。
登记：work/PROJECT_LEDGER.md §7（D12）。
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml
import numpy as np
from scipy.optimize import LinearConstraint, milp

ROOT = Path(__file__).resolve().parents[2]
MERGED = ROOT / "work/derived/observations.merged.yaml"

REQ = {"pump": 2, "column": 1, "vessel": 1, "exchanger": 1, "reactor": 1}

P2_STABLE = [("P-3511", "V-3506"), ("P-3501", "V-3501"), ("E-3505", "T-3512")]
A_EDGES = [("E-3506", "T-3501B"), ("P-3511", "E-3501"), ("P-3501", "E-3501")]

CANDIDATES = [
    ("c1", "E-3508", "T-3512", "MTBE 产品冷却器接产品出料泵（档2-弱）"),
    ("c2", "P-3502", "T-3501B", "反应塔底循环泵#1 抽自下塔（档1+命名）"),
    ("c3", "P-3502", "E-3506", "反应塔底循环泵#1 送再沸器（档1+命名）"),
    ("c4", "P-3503", "T-3501B", "反应塔底循环泵#2 抽自下塔（档1+命名）"),
    ("c5", "P-3503", "E-3506", "反应塔底循环泵#2 送再沸器（档1+命名）"),
    ("c6", "V-3504", "T-3508", "C4 残液罐接 C4 出料罐泵（档1 命名语法）"),
    ("c7", "T-3508", "V-3502", "C4 出料罐泵送回醚后 C4 罐/外输（档2-弱）"),
    ("c8", "p2::5D5qHUWBTGfa0SRdJl68-5", "P-3511", "C4 原料混合罐接 C4 原料泵（档1 命名/档2-弱）"),
    ("c9", "p2::5D5qHUWBTGfa0SRdJl68-5", "V-3506", "C4 原料罐接 C4 原料混合罐（档2-弱）"),
]
OPTIONAL_NOT_ADDED = [
    ("V-3503", "p2::5D5qHUWBTGfa0SRdJl68-35", "催化蒸馏回流罐→上塔回流：度数已闭合，按 A5 最小原则不补，图上可画并标 prior"),
    ("T-3501B", "E-3505", "MTBE 自下塔去产品换热器：度数已闭合，同上"),
]
DEFICIENT_ALLOWED = ["E-3502", "E-3503", "FV301"]
# 档1 惯例特例：feed drum（C4 原料混合罐）有进有出 → 度数要求 2（消除 c8/c9 二选一分歧，非乐观补全）
SPECIAL_REQ = {"p2::5D5qHUWBTGfa0SRdJl68-5": 2}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="work/derived/solver_result_P4.yaml")
    ap.add_argument("--k", type=int, default=8)
    args = ap.parse_args()

    with MERGED.open(encoding="utf-8") as f:
        merged = yaml.safe_load(f)
    entities = {e["id"]: e for e in merged["entities"]}
    obs = [tuple(sorted((e["a"], e["b"]))) for e in merged["edges"] if e["a"] != e["b"]]
    fixed = obs + [tuple(sorted(p)) for p in P2_STABLE] + [tuple(sorted(p)) for p in A_EDGES]

    functional = [k for k in entities
                  if entities[k]["tag_status"] != "unknown_marker" and k not in DEFICIENT_ALLOWED]

    n = len(CANDIDATES)
    c = [1.0] * n
    rows, lbs, ubs = [], [], []
    for k in functional:
        row = [0.0] * n
        deg = sum(1 for (a, b) in fixed if a == k or b == k)
        for i, (_, a, b, _) in enumerate(CANDIDATES):
            if a == k or b == k:
                row[i] += 1.0
        rows.append(row)
        lbs.append(float(SPECIAL_REQ.get(k, REQ.get(entities[k]["shape_class"], 1)) - deg))
        ubs.append(np.inf)
    for k, lb, row in zip(functional, lbs, rows):
        if lb > 0:
            print(f"  [deficit] {k} shape={entities[k]['shape_class']} need+{lb:.0f} candidate_touch={sum(row):.0f}")
    # 候选边本身不强制；仅度数约束
    res_sets = []
    cuts = []
    for _ in range(args.k):
        A = rows + [ct[0] for ct in cuts]
        lo = lbs + [-np.inf] * len(cuts)
        hi = ubs + [ct[1] for ct in cuts]
        r = milp(c=c, constraints=LinearConstraint(A, lo, hi),
                 integrality=[1.0] * n, bounds=(0.0, 1.0),
                 options={"time_limit": 10.0})
        if r.status != 0 or r.x is None:
            break
        used = [CANDIDATES[i][0] for i in range(n) if r.x[i] > 0.5]
        res_sets.append(used)
        row = [1.0 if r.x[i] > 0.5 else -1.0 for i in range(n)]
        cuts.append((row, float(sum(1 for i in range(n) if r.x[i] > 0.5) - 1)))

    stable = [cid for cid in [cc[0] for cc in CANDIDATES]
              if res_sets and all(cid in s for s in res_sets)]
    doc = {
        "meta": {
            "level": "L3/P4", "solver": "scipy.optimize.milp (HiGHS)",
            "policy": "A5 minimal_closure_only：min Σc，枚举最小解；禁最乐观",
            "fixed_edges": {"observed": len(obs), "p2_grammar_stable": P2_STABLE, "A1_A3": A_EDGES},
            "deficient_allowed_no_closure": DEFICIENT_ALLOWED,
            "backing": "work/derived/prior_backing.yaml (D11)",
        },
        "candidates": [{"id": i, "edge": [a, b], "note": note} for (i, a, b, note) in CANDIDATES],
        "minimal_sets": res_sets,
        "stable_candidates": stable,
        "optional_not_added": [{"edge": [a, b], "note": note} for (a, b, note) in OPTIONAL_NOT_ADDED],
    }
    out = ROOT / args.out
    with out.open("w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)
    print(f"[ok] wrote {out.relative_to(ROOT)}")
    print(f"  minimal_sets={len(res_sets)}")
    for s in res_sets:
        print("   ", s)
    print(f"  stable={stable}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
