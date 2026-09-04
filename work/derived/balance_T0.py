# -*- coding: utf-8 -*-
"""W2 Tier 0 稳态组分物料衡算（手写平衡，非模拟器；A5 检验环的一环）。

教学口径（每个输入数的含义与出处）：
  basis   = 100 kmol/h 混合 C4 进料。选 100 是为了让 mol% 直接读成 kmol/h，好核对。
  y_iC4   = 混合 C4 中异丁烯摩尔分数 0.25。assumed：FCC 混合 C4 异丁烯常见 0.2–0.35 区间中值；
            本次检索未拿到该厂实测值 → 标 assumed，报告里写"取典型值"。
  R_M     = 醇烯比（甲醇:异丁烯）1.1。assumed：文献常见 1.0–1.2 控醇烯比（D11 摘要提到控醇烯比但无数字）。
  X       = 异丁烯转化率 0.95（敏感性 0.90）。literature 摘要级：D11 知乎专栏"预反应转化率 90–95%"。
  eta_EX  = 萃取塔甲醇脱除率 0.99。assumed：水萃取甲醇效率高，取 99%；无文献数字。
  x_MeOH_bottom = 催化蒸馏塔底 MTBE 产品带甲醇 0.2 mol%。assumed：产品规格级杂质水平，无文献数字。
  W       = 萃取水 80 kmol/h。assumed：水/C4 约 0.8–1.0 mol 比区间取值；无文献数字。
  MW      = MeOH 32.04 / MTBE 88.15 / iC4= 56.11 / 其余C4 57.12(烷/烯混均值, assumed) / H2O 18.02。
反应计量：iC4= + MeOH -> MTBE，1:1:1。
闭合校验：总进质量 = 总出质量（水回路闭合、无损失假设下），assert 1e-6。
用途：① 给报告 ②.1 提供原料/产品指标/转化率数字；② 检验 D12 流程"每条流都有去处"（A5 检验环）。
登记：work/PROJECT_LEDGER.md §7（D14）。
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/derived/balance_T0.yaml"

MW = {"MeOH": 32.04, "MTBE": 88.15, "iC4=": 56.11, "C4other": 57.12, "H2O": 18.02}


def balance(X: float) -> dict:
    basis = 100.0
    y_iC4 = 0.25
    R_M = 1.1
    eta_EX = 0.99
    x_MeOH_bottom = 0.002
    W = 80.0

    iC4_in = basis * y_iC4            # 25
    other_in = basis - iC4_in         # 75
    reacted = X * iC4_in              # MTBE 生成 = 异丁烯反应量 (1:1)
    MeOH_reactor_in = R_M * iC4_in    # 27.5
    MeOH_unreacted = MeOH_reactor_in - reacted
    # 催化蒸馏塔：底=MTBE+少量MeOH；顶=醚后C4+其余MeOH
    MTBE = reacted
    MeOH_bottom = x_MeOH_bottom / (1 - x_MeOH_bottom) * MTBE   # 由 mol% 反算 mol 量
    MeOH_top = MeOH_unreacted - MeOH_bottom
    # 萃取：99% 甲醇进水相
    MeOH_raff = (1 - eta_EX) * MeOH_top
    MeOH_extract = MeOH_top - MeOH_raff
    # 甲醇回收：塔顶回收甲醇回用；塔底水回萃取
    recycle = MeOH_extract
    fresh_MeOH = reacted + MeOH_bottom + MeOH_raff   # 净耗 = 反应 + 两路损失
    # 流表 (kmol/h)
    streams = {
        "S1_C4feed": {"iC4=": iC4_in, "C4other": other_in},
        "S2_MeOH_fresh": {"MeOH": fresh_MeOH},
        "S3_reactor_out": {"MTBE": MTBE, "iC4=": iC4_in - reacted, "C4other": other_in, "MeOH": MeOH_unreacted},
        "S4_CD_bottom_MTBE": {"MTBE": MTBE, "MeOH": MeOH_bottom},
        "S5_CD_top": {"iC4=": iC4_in - reacted, "C4other": other_in, "MeOH": MeOH_top},
        "S6_EX_raffinate": {"iC4=": iC4_in - reacted, "C4other": other_in, "MeOH": MeOH_raff},
        "S7_EX_extract": {"MeOH": MeOH_extract, "H2O": W},
        "S8_MR_top_recycle": {"MeOH": recycle},
        "S9_MR_bottom_water": {"H2O": W},
    }
    kg = {s: {c: v * MW[c] for c, v in comp.items()} for s, comp in streams.items()}
    mass_in = sum(kg["S1_C4feed"].values()) + sum(kg["S2_MeOH_fresh"].values())
    mass_out = sum(kg["S4_CD_bottom_MTBE"].values()) + sum(kg["S6_EX_raffinate"].values())
    # 产品指标
    mtbe_purity_wt = kg["S4_CD_bottom_MTBE"]["MTBE"] / sum(kg["S4_CD_bottom_MTBE"].values())
    raff_MeOH_ppm_mol = MeOH_raff / (MeOH_raff + iC4_in - reacted + other_in) * 1e6
    meoh_per_mtbe_t = MW["MeOH"] / MW["MTBE"]   # 理论吨耗
    return {
        "X": X,
        "streams_kmol_h": streams,
        "streams_kg_h": {s: {c: round(v, 2) for c, v in comp.items()} for s, comp in kg.items()},
        "mass_in_kg_h": round(mass_in, 2),
        "mass_out_kg_h": round(mass_out, 2),
        "closure_err_kg_h": round(mass_in - mass_out, 6),
        "MTBE_kg_h": round(kg["S4_CD_bottom_MTBE"]["MTBE"], 1),
        "MTBE_purity_wt": round(mtbe_purity_wt, 5),
        "raffinate_MeOH_ppm_mol": round(raff_MeOH_ppm_mol, 1),
        "MeOH_theoretical_t_per_t_MTBE": round(meoh_per_mtbe_t, 4),
        "fresh_MeOH_kmol_h": round(fresh_MeOH, 3),
        "recycle_MeOH_kmol_h": round(recycle, 3),
    }


def main() -> int:
    base = balance(0.95)
    sens = balance(0.90)
    assert abs(base["closure_err_kg_h"]) < 1e-6, base["closure_err_kg_h"]
    doc = {
        "meta": {
            "level": "W2/Tier0", "method": "手写稳态组分衡算（非模拟器）",
            "script": "work/derived/balance_T0.py",
            "stoichiometry": "iC4= + MeOH -> MTBE (1:1:1)",
            "closure": "总进质量=总出质量（水回路闭合、无损失）；assert 1e-6 通过",
        },
        "assumptions": [
            {"name": "basis", "value": "100 kmol/h 混合C4", "kind": "convention"},
            {"name": "y_iC4", "value": 0.25, "kind": "assumed", "note": "FCC混合C4异丁烯典型0.2–0.35中值；无该厂实测"},
            {"name": "R_M 醇烯比", "value": 1.1, "kind": "assumed", "note": "文献常见1.0–1.2；D11摘要提到控醇烯比但无数字"},
            {"name": "X 转化率", "value": 0.95, "kind": "literature摘要级", "note": "D11 知乎专栏 90–95%；敏感性0.90"},
            {"name": "eta_EX 萃取脱除率", "value": 0.99, "kind": "assumed"},
            {"name": "x_MeOH_bottom", "value": 0.002, "kind": "assumed", "note": "产品杂质水平"},
            {"name": "W 萃取水", "value": 80.0, "kind": "assumed", "note": "水/C4 mol比约0.8"},
            {"name": "MW 其余C4", "value": 57.12, "kind": "assumed", "note": "烷/烯混均值"},
        ],
        "base_X0.95": base,
        "sensitivity_X0.90": {k: sens[k] for k in ("MTBE_kg_h", "MTBE_purity_wt", "fresh_MeOH_kmol_h", "closure_err_kg_h")},
    }
    with OUT.open("w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)
    print(f"[ok] wrote {OUT.relative_to(ROOT)}")
    print(f"  MTBE = {base['MTBE_kg_h']} kg/h, purity_wt = {base['MTBE_purity_wt']}")
    print(f"  raffinate MeOH = {base['raffinate_MeOH_ppm_mol']} ppm(mol)")
    print(f"  fresh MeOH = {base['fresh_MeOH_kmol_h']} kmol/h, recycle = {base['recycle_MeOH_kmol_h']} kmol/h")
    print(f"  MeOH t/t MTBE (theoretical) = {base['MeOH_theoretical_t_per_t_MTBE']}")
    print(f"  closure err = {base['closure_err_kg_h']} kg/h; X=0.90 -> MTBE {sens['MTBE_kg_h']} kg/h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
