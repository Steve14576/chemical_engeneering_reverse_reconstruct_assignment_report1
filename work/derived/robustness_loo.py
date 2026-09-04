# -*- coding: utf-8 -*-
"""W1 鲁棒性：leave-one-out（LOO）拓扑检验。

问两个问题：
  LOO-prior：逐条拿掉 13 条 prior 边（P2语法3 + A1–A3裁决3 + P4最小补集7），把它降为候选，
              看最小补集规模是否变化 → prior 边里哪些是"不可缺的骨架"、哪些可被替代。
  LOO-obs  ：逐条拿掉 40 条观测边，看闭合是否仍可行/最小补集是否跳变 → 哪些观测边是"关键边"。
方法：度数闭合 MILP（min Σ 候选边），与 solve_closure_P4 同口径（泵≥2、其余≥1、
      E-3502/E-3503/FV301 不闭合白名单、C4混合罐 req=2）。
登记：work/PROJECT_LEDGER.md §7（D17）。
"""
from __future__ import annotations

import os

import numpy as np
import yaml
from scipy.optimize import LinearConstraint, milp

HERE = os.path.dirname(os.path.abspath(__file__))
MERGED = os.path.join(HERE, "observations.merged.yaml")

REQ = {"pump": 2, "column": 1, "vessel": 1, "exchanger": 1, "reactor": 1}
SPECIAL_REQ = {"p2::5D5qHUWBTGfa0SRdJl68-5": 2}
DEFICIENT_ALLOWED = {"E-3502", "E-3503", "FV301"}

P2_GRAMMAR = [("P-3511", "V-3506"), ("P-3501", "V-3501"), ("E-3505", "T-3512")]
A_EDGES = [("E-3506", "T-3501B"), ("P-3511", "E-3501"), ("P-3501", "E-3501")]
P4_MIN = [
    ("E-3508", "T-3512"), ("P-3502", "T-3501B"), ("P-3502", "E-3506"),
    ("P-3503", "T-3501B"), ("P-3503", "E-3506"),
    ("p2::5D5qHUWBTGfa0SRdJl68-5", "P-3511"), ("V-3506", "p2::5D5qHUWBTGfa0SRdJl68-5"),
]
POOL_EXTRA = [("V-3503", "p2::5D5qHUWBTGfa0SRdJl68-35"), ("T-3501B", "E-3505"), ("T-3508", "V-3502"), ("V-3504", "T-3508")]


def norm(p):
    return tuple(sorted(p))


def min_closure(fixed, pool, entities):
    functional = [k for k in entities
                  if entities[k]["tag_status"] != "unknown_marker" and k not in DEFICIENT_ALLOWED]
    pool = [norm(p) for p in pool]
    n = len(pool)
    if n == 0:
        return None
    c = [1.0] * n
    rows, lbs, ubs = [], [], []
    for k in functional:
        row = [0.0] * n
        deg = sum(1 for (a, b) in fixed if a == k or b == k)
        for i, (a, b) in enumerate(pool):
            if a == k or b == k:
                row[i] += 1.0
        req = SPECIAL_REQ.get(k, REQ.get(entities[k]["shape_class"], 1))
        rows.append(row)
        lbs.append(float(req - deg))
        ubs.append(np.inf)
    r = milp(c=c, constraints=LinearConstraint(rows, lbs, ubs),
             integrality=[1.0] * n, bounds=(0.0, 1.0), options={"time_limit": 10.0})
    if r.status != 0 or r.x is None:
        return None
    return int(round(sum(r.x)))


def main() -> int:
    with open(MERGED, encoding="utf-8") as f:
        merged = yaml.safe_load(f)
    entities = {e["id"]: e for e in merged["entities"]}
    obs = [norm((e["a"], e["b"])) for e in merged["edges"] if e["a"] != e["b"]]
    prior = [norm(p) for p in P2_GRAMMAR + A_EDGES + P4_MIN]
    pool0 = [norm(p) for p in P4_MIN] + [norm(p) for p in POOL_EXTRA]

    fixed0 = [norm(p) for p in obs] + [norm(p) for p in prior]
    base = min_closure(fixed0, pool0, entities)

    loo_prior = []
    for e in prior:
        f2 = [x for x in fixed0 if x != e]
        p2 = list(pool0) + [e]
        s = min_closure(f2, p2, entities)
        loo_prior.append({"edge": list(e), "min_size": s, "delta": (None if s is None else s - (base or 0))})

    loo_obs = []
    crit = 0
    for e in obs:
        f2 = [x for x in fixed0 if x != e]
        s = min_closure(f2, pool0, entities)
        if s is None or (base is not None and s > base):
            crit += 1
        loo_obs.append({"edge": list(e), "min_size": s})

    doc = {
        "meta": {
            "level": "W1/robustness", "method": "leave-one-out + 度数闭合 MILP（min Σ 候选）",
            "script": "work/derived/robustness_loo.py",
            "baseline_min_closure": base,
        },
        "loo_prior": loo_prior,
        "loo_obs_critical_count": crit,
        "loo_obs": loo_obs,
    }
    out = os.path.join(HERE, "robustness_loo.yaml")
    with open(out, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)
    print(f"[ok] wrote {os.path.basename(out)}")
    print(f"  baseline min closure = {base}")
    for r in loo_prior:
        print(f"   prior {r['edge']} -> min {r['min_size']} (delta {r['delta']})")
    print(f"  LOO-obs critical (infeasible or size jump) = {crit} / {len(obs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
