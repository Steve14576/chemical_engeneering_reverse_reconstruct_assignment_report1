# -*- coding: utf-8 -*-
"""W2 Tier 0.5：能量衡算（重沸/冷凝负荷粗估）+ 敏感性网格。

教学口径（每个输入的含义与出处）：
  R_CD  = 催化蒸馏塔回流比 1.5。assumed：催化蒸馏回流比常见 1–2 区间取值；无该厂数据。
  R_MR  = 甲醇回收塔回流比 1.0。assumed：甲醇-水分离回流比典型值；无该厂数据。
  λ     = 汽化潜热 kJ/kmol（典型值, assumed）：C4mix 22000 / MeOH 35200 / MTBE 30000 / H2O 40700。
  λ_stm = 蒸汽潜热 2257 kJ/kg（约 1 bar 饱和蒸汽, assumed）。
  负荷粗估法：Q_cond ≈ V_top × λ_top；Q_reb ≈ Q_cond（忽略进料显热与热损失，Tier 0.5 精度声明）。
  V_top = D_top × (R+1)。
敏感性网格：X∈{0.90,0.95} × R_M∈{1.0,1.1,1.2} × y_iC4∈{0.20,0.25,0.30} × η_EX∈{0.95,0.99} = 36 组，
  输出 MTBE kg/h、纯度 wt%、醚后C4 残甲醇 ppm 的 min/max/span。
登记：work/PROJECT_LEDGER.md §7（D17）。
"""
from __future__ import annotations

import itertools
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
from balance_T0 import balance  # noqa: E402  (复用 Tier 0 物料衡算)

LAM = {"C4mix": 22000.0, "MeOH": 35200.0, "MTBE": 30000.0, "H2O": 40700.0}
LAM_STEAM = 2257.0  # kJ/kg
R_CD = 1.5
R_MR = 1.0


def energy(b: dict) -> dict:
    # 从 Tier 0 流表取摩尔流量
    s5 = b["streams_kmol_h"]["S5_CD_top"]
    d_top = sum(s5.values())
    v_cd = d_top * (R_CD + 1)
    q_cond_cd = v_cd * LAM["C4mix"]          # kJ/h
    q_reb_cd = q_cond_cd
    d_meoh = b["recycle_MeOH_kmol_h"]
    v_mr = d_meoh * (R_MR + 1)
    q_reb_mr = v_mr * LAM["MeOH"]
    q_cond_mr = q_reb_mr
    steam = q_reb_mr / LAM_STEAM             # kg/h
    return {
        "V_CD_kmol_h": round(v_cd, 1),
        "Q_cond_CD_kW": round(q_cond_cd / 3600, 0),
        "Q_reb_CD_kW": round(q_reb_cd / 3600, 0),
        "V_MR_kmol_h": round(v_mr, 2),
        "Q_reb_MR_kW": round(q_reb_mr / 3600, 1),
        "steam_kg_h": round(steam, 1),
    }


def main() -> int:
    base = balance(0.95)
    en = energy(base)
    grid = []
    for X, RM, y, eta in itertools.product((0.90, 0.95), (1.0, 1.1, 1.2), (0.20, 0.25, 0.30), (0.95, 0.99)):
        # 重算物料（复制 balance 逻辑的参数化版本：直接改全局不便，这里内联简化重算）
        iC4 = 100.0 * y
        reacted = X * iC4
        mtbe_kg = reacted * 88.15
        meoh_in = RM * iC4
        meoh_un = meoh_in - reacted
        meoh_bot = 0.002 / 0.998 * reacted
        meoh_top = meoh_un - meoh_bot
        meoh_raff = (1 - eta) * meoh_top
        raff_ppm = meoh_raff / (meoh_raff + iC4 - reacted + 100.0 - iC4) * 1e6
        purity = reacted * 88.15 / (reacted * 88.15 + meoh_bot * 32.04)
        grid.append({"X": X, "R_M": RM, "y_iC4": y, "eta_EX": eta,
                     "MTBE_kg_h": round(mtbe_kg, 1), "purity_wt": round(purity, 5),
                     "raff_ppm_mol": round(raff_ppm, 1)})
    mt = [g["MTBE_kg_h"] for g in grid]
    pu = [g["purity_wt"] for g in grid]
    rp = [g["raff_ppm_mol"] for g in grid]
    doc = {
        "meta": {
            "level": "W2/Tier0.5",
            "method": "负荷粗估 Q≈V_top×λ_top, Q_reb≈Q_cond（忽略显热与热损失）；λ 与回流比均 assumed",
            "script": "work/derived/balance_T05.py",
        },
        "assumptions": [
            {"name": "R_CD 回流比", "value": R_CD, "kind": "assumed"},
            {"name": "R_MR 回流比", "value": R_MR, "kind": "assumed"},
            {"name": "λ C4mix/MeOH/MTBE/H2O kJ/kmol", "value": [LAM["C4mix"], LAM["MeOH"], LAM["MTBE"], LAM["H2O"]], "kind": "assumed典型值"},
            {"name": "λ_steam kJ/kg", "value": LAM_STEAM, "kind": "assumed"},
        ],
        "energy_base_X0.95": en,
        "sensitivity_grid_n": len(grid),
        "sensitivity_span": {
            "MTBE_kg_h": {"min": min(mt), "max": max(mt)},
            "purity_wt": {"min": min(pu), "max": max(pu)},
            "raff_ppm_mol": {"min": min(rp), "max": max(rp)},
        },
        "grid": grid,
    }
    out = os.path.join(HERE, "balance_T05.yaml")
    with open(out, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)
    print(f"[ok] wrote {os.path.basename(out)}")
    print(f"  Q_cond_CD={en['Q_cond_CD_kW']} kW, Q_reb_CD={en['Q_reb_CD_kW']} kW")
    print(f"  Q_reb_MR={en['Q_reb_MR_kW']} kW, steam={en['steam_kg_h']} kg/h")
    print(f"  MTBE span {min(mt)}..{max(mt)} kg/h; purity {min(pu)}..{max(pu)}; raff {min(rp)}..{max(rp)} ppm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
