# -*- coding: utf-8 -*-
"""W4 流程图产出（pyflowsheet 0.2.2 + pathfinding 1.0.1 钉版）：
   1) figures/flow_main.svg   参考主图（真化工图标）
   2) figures/flow_main.mermaid.md  md 内联快览
   3) figures/flow_handcopy.md     手抄规格（分区框+线清单）
线型语义：实线=观测边；虚线=prior-driven（P2语法3+A1–A3裁决3+P4最小补集7）；点划=公用工程；
          callout ✕=声明不闭合缺陷设备；callout ?=未知悬空线。
声明：图中流向箭头仅为排版可读性，**不是方向主张**（方向待枚举，见 ledger §5/D12）。
登记：work/PROJECT_LEDGER.md §7（D15）；工具选型改判见 DEV_JOURNAL J16。
"""
from __future__ import annotations

import os
import time

from pyflowsheet import (
    Flowsheet, Distillation, HeatExchanger, Pump, Valve, Vessel, StreamFlag, SvgContext,
)

T0 = time.perf_counter()
HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)

pfd = Flowsheet("MTBE-W4", "MTBE unit flow (observed + prior-declared)", "W4 reference diagram")

U = []
# ---- 300 系（仅 person1 观测） ----
U += [
    Vessel("V302", "V-302", position=(40, 300), size=(40, 80)),
    Distillation("T301", "T-301 ?", hasCondenser=False, hasReboiler=False, position=(130, 220), size=(40, 150)),
    HeatExchanger("E301", "E-301", position=(230, 240)),
    HeatExchanger("E302", "E-302", position=(230, 110)),
    Distillation("T302", "T-302", hasCondenser=False, hasReboiler=False, position=(330, 220), size=(40, 150)),
    Vessel("V301", "V-301", position=(350, 70), size=(40, 60)),
    HeatExchanger("E303", "E-303", position=(430, 260)),
]
# ---- 3500 原料+醚化 ----
U += [
    Vessel("V3506", "V-3506 C4原料", position=(560, 70), size=(40, 70)),
    Vessel("V3501", "V-3501 甲醇", position=(560, 180), size=(40, 70)),
    Vessel("MIX", "C4混合罐(未标号)", position=(660, 70), size=(40, 70)),
    Pump("P3511", "P-3511", position=(660, 180)),
    Pump("P3501", "P-3501", position=(660, 260)),
    HeatExchanger("E3501", "E-3501 预热", position=(760, 180)),
    Vessel("R3501A", "R-3501A 一段醚化", position=(850, 110), size=(36, 110)),
    Vessel("R3501B", "R-3501B 二段醚化", position=(850, 260), size=(36, 110)),
]
# ---- 催化蒸馏 ----
U += [
    Distillation("T3501B", "T-3501B 下塔", hasCondenser=False, hasReboiler=False, position=(950, 240), size=(40, 180)),
    Distillation("T3501A", "T-3501A 上塔", hasCondenser=False, hasReboiler=False, position=(1040, 150), size=(40, 180)),
    HeatExchanger("E3506", "E-3506 重沸", position=(950, 470)),
    HeatExchanger("E3507", "E-3507 塔冷", position=(1040, 50)),
    Vessel("V3503", "V-3503 回流罐", position=(1140, 50), size=(40, 60)),
    Vessel("V3502", "V-3502 醚后C4", position=(1140, 160), size=(40, 70)),
    Pump("P3505B", "P-3505B", position=(1040, 400)),
    Pump("P3505A", "P-3505A", position=(1140, 300)),
    HeatExchanger("E3505", "E-3505 产品换热", position=(950, 570)),
    Pump("T3512", "T-3512 MTBE出料", position=(1060, 570)),
    HeatExchanger("E3508", "E-3508 产品冷却", position=(1160, 570)),
]
# ---- 萃取+回收 ----
U += [
    Distillation("T3502", "T-3502 萃取塔", hasCondenser=False, hasReboiler=False, position=(820, 460), size=(40, 150)),
    Distillation("MEH", "TMP-MEOHCOL 回收塔", hasCondenser=False, hasReboiler=False, position=(660, 460), size=(40, 150)),
    HeatExchanger("E3512", "E-3512 冷凝", position=(540, 420)),
    Vessel("REFLUX", "回收塔回流罐(未标号)", position=(430, 420), size=(40, 60)),
    Vessel("V402", "V-402", position=(430, 520), size=(40, 60)),
    HeatExchanger("E3513", "E-3513 重沸", position=(540, 640)),
    Pump("P3502", "P-3502 循环", position=(880, 660)),
    Pump("P3503", "P-3503 循环", position=(960, 660)),
]
# ---- 外部旗标 ----
U += [
    StreamFlag("STEAM", "蒸汽(公用)", position=(430, 660)),
    StreamFlag("SFEC4", "醚后C4去萃取(档2-弱)", position=(700, 380)),
]
pfd.addUnits(U)

OBS = [
    ("S01", "V302", "Out", "T301", "Feed"),
    ("S02", "T301", "LOut", "E301", "TIn"),
    ("S03", "E301", "TOut", "V301", "In"),
    ("S04", "E301", "SOut", "T302", "Feed"),
    ("S05", "E302", "TOut", "T302", "VIn"),
    ("S06", "T302", "LOut", "E303", "TIn"),
    ("S07", "E3501", "TOut", "R3501A", "In"),
    ("S08", "R3501A", "Out", "R3501B", "In"),
    ("S09", "R3501B", "Out", "V3502", "In"),
    ("S10", "V3502", "Out", "P3505B", "In"),
    ("S11", "P3505B", "Out", "T3501B", "Feed"),
    ("S12", "T3501B", "VOut", "T3501A", "VIn"),
    ("S13", "T3501A", "VOut", "E3507", "TIn"),
    ("S14", "E3507", "TOut", "V3503", "In"),
    ("S15", "T3502", "LOut", "MEH", "Feed"),
    ("S16", "MEH", "VOut", "E3512", "TIn"),
    ("S17", "E3512", "TOut", "REFLUX", "In"),
    ("S18", "REFLUX", "Out", "V402", "In"),
    ("S19", "MEH", "LOut", "E3513", "TIn"),
]
PRIOR = [
    ("P01", "V3506", "Out", "MIX", "In"),
    ("P02", "MIX", "Out", "P3511", "In"),
    ("P03", "P3511", "Out", "E3501", "TIn"),
    ("P04", "V3501", "Out", "P3501", "In"),
    ("P05", "P3501", "Out", "E3501", "SIn"),
    ("P06", "T3501B", "LOut", "E3506", "TIn"),
    ("P07", "E3506", "TOut", "T3501B", "RIn"),
    ("P08", "V3503", "Out", "T3501A", "VIn"),
    ("P09", "E3505", "TOut", "T3512", "In"),
    ("P10", "T3512", "Out", "E3508", "TIn"),
    ("P11", "SFEC4", "Out", "T3502", "Feed"),
]
UTIL = [("U01", "STEAM", "Out", "E3513", "SIn")]

for sid, a, ap, b, bp in OBS:
    pfd.connect(sid, pfd.unitOperations[a][ap], pfd.unitOperations[b][bp])
for sid, a, ap, b, bp in PRIOR:
    pfd.connect(sid, pfd.unitOperations[a][ap], pfd.unitOperations[b][bp])
    pfd.streams[sid].dashArray = "7,4"
for sid, a, ap, b, bp in UTIL:
    pfd.connect(sid, pfd.unitOperations[a][ap], pfd.unitOperations[b][bp])
    pfd.streams[sid].dashArray = "2,3,8,3"

pfd.callout("LEGEND: solid=observed(field)  dashed=prior-driven(book/decision)  dash-dot=utility", (10, 10))
pfd.callout("        ?=unknown dangling end   X=declared unclosed survey defect   arrows=layout only, NOT direction claims", (10, 26))
pfd.callout("?  E-302 unknown dangling end (A4: keep unknown)", (40, 90))
pfd.callout("X  E-3502 / E-3503 identity unknown (name/tag mismatch) - not connected", (1240, 420))
pfd.callout("X  FV301 valve without line - not connected", (1240, 440))
pfd.callout("prior(optional, not drawn): V-3503 reflux already dashed P08; T-3501B->E-3505 optional", (1240, 460))
pfd.callout("P-3502/P-3503 bottom-circulation pumps: prior edges to T-3501B/E-3506 not drawn (clutter), see handcopy", (820, 700))

out = os.path.join(FIG, "flow_main.svg")
ctx = SvgContext(out)
pfd.draw(ctx)
ctx.render(scale=1)

mer = ["# MTBE 流程快览（Mermaid；实线语义见 SVG 图例）", "", "```mermaid", "flowchart LR"]
mer += [
    "  V3506 --> MIX --> P3511 --> E3501 --> R3501A --> R3501B --> V3502 --> P3505B --> T3501B",
    "  V3501 --> P3501 --> E3501",
    "  T3501B --> T3501A --> E3507 --> V3503 -.回流.-> T3501A",
    "  T3501B -.重沸loop.-> E3506 -.-> T3501B",
    "  T3501B -.-> E3505 --> T3512 --> E3508",
    "  SFEC4 -.档2-弱.-> T3502 --> MEH --> E3512 --> REFLUX --> V402",
    "  MEH --> E3513",
    "  V302 --> T301 --> E301 --> T302 --> E303",
    "  E301 --> V301",
    "  E302 --> T302",
    "  classDef defect fill:#eee,stroke:#999",
    "  E3502X[E-3502 X 缺陷]:::defect",
    "  E3503X[E-3503 X 缺陷]:::defect",
    "  FV301X[FV301 X 缺陷]:::defect",
    "```",
]
with open(os.path.join(FIG, "flow_main.mermaid.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(mer) + "\n")

hand = """# 手抄规格（分区抄；线型：实=观测，虚=prior）

## 区1 300系（7框：V-302,T-301,E-301,E-302,T-302,V-301,E-303；6实线+1未知虚线）
实: V-302—T-301, T-301—E-301, E-301—V-301, E-301—T-302, E-302—T-302, T-302—E-303
虚?: E-302 一条未知端悬空线

## 区2 原料+醚化（8框：V-3506,V-3501,混合罐,P-3511,P-3501,E-3501,R-3501A,R-3501B；2实+5虚）
虚: V-3506—混合罐, 混合罐—P-3511, P-3511—E-3501, V-3501—P-3501, P-3501—E-3501
实: E-3501—R-3501A, R-3501A—R-3501B

## 区3 催化蒸馏（11框：T-3501B,T-3501A,E-3506,E-3507,V-3503,V-3502,P-3505A,P-3505B,E-3505,T-3512,E-3508；6实+5虚）
实: R-3501B—V-3502, V-3502—P-3505B, P-3505B—T-3501B, T-3501B—T-3501A, T-3501A—E-3507, E-3507—V-3503
虚: E-3506—T-3501B(loop两笔), V-3503—T-3501A回流, E-3505—T-3512, T-3512—E-3508

## 区4 萃取+回收（8框：T-3502,TMP-MEOHCOL,E-3512,回流罐,V-402,E-3513,P-3502,P-3503；5实+2虚）
实: T-3502—TMP-MEOHCOL, TMP-MEOHCOL—E-3512, E-3512—回流罐, 回流罐—V-402, TMP-MEOHCOL—E-3513
虚: 醚后C4—T-3502(档2-弱), P-3502/P-3503—T-3501B/E-3506 循环(可画一笔代表)
点划: 蒸汽—E-3513

## 缺陷标注（不连线）：E-3502 ✕ / E-3503 ✕ / FV301 ✕
"""
with open(os.path.join(FIG, "flow_handcopy.md"), "w", encoding="utf-8") as f:
    f.write(hand)

print(f"[ok] svg={out}")
print(f"  units={len(pfd.unitOperations)} streams={len(pfd.streams)}")
print(f"  runtime={time.perf_counter() - T0:.2f}s")
