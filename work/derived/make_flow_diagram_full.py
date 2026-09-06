# -*- coding: utf-8 -*-
"""W4 流程图·全量版（独立新脚本，不覆盖 make_flow_diagram.py / flow_main.svg）。

相对旧版的增量（对应 J26 分析的 A/B/C 三类问题）：
  A 补遗漏：新增单元 某管道汇合(JUNC)/某黑盒管线(HEIX)/E-3509/E-3510/T-3509/T-3508/V-3504，
    补回 13 条观测实线（R-3501A/B→汇合、汇合→V-3502、T-3501A→T-3512、T-3512→黑盒、
    T-3509→V-3503、V-3503→E-3510、E-3510→T-3502、P-3505A→E-3509、E-3509→T-3502、
    P-3505A→T-3501A、V-3504→T-3508、MEH→T-3509）。
  B 孤岛：P-3505A 因补回观测边不再孤立；P-3502/P-3503 仍孤岛但保留声明 callout。
  C 糊：所有 stream 设 showTitle=False（隐藏 Sxx 编号标签，消除端口旁叠字）。
  ✕ 三台（E-3502/E-3503/FV301）画成带 ✕ 的符号而非仅右侧文字。
  悬空/自环不画线，以 callout 声明：E-302 未知端、P-3505B 入口断口、T-3508 出口断口、
  E-3513 放空端、MEH 萃取水自环回路、person1 四个未标注框（候选不立节点）。
线型语义同旧版：实=观测、虚=prior、点划=公用；箭头仅排版非方向主张。
产出：figures/flow_main_full.svg（仅此一个文件）。
登记：work/PROJECT_LEDGER.md §7（D15 扩展）、DEV_JOURNAL J27。
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

pfd = Flowsheet("MTBE-W4-FULL", "MTBE unit flow (full: all observed + prior-declared)", "W4 full diagram")

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
    Vessel("JUNC", "某管道汇合", position=(900, 400), size=(30, 30)),
    Vessel("HEIX", "某黑盒管线(未明)", position=(1160, 660), size=(30, 30)),
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
    Pump("T3509", "T-3509 采出泵", position=(1240, 60)),
    HeatExchanger("E3510", "E-3510 萃取水冷凝", position=(1240, 160)),
    HeatExchanger("E3509", "E-3509 萃取进料冷却", position=(1240, 260)),
    Pump("T3508", "T-3508 C4出料泵", position=(1300, 420)),
    Vessel("V3504", "V-3504 C4残液", position=(1300, 320), size=(40, 60)),
]
# ---- 缺陷符号（✕） ----
U += [
    Vessel("E3502X", "E-3502 ✕ 身份不明", position=(1300, 520), size=(36, 50)),
    Vessel("E3503X", "E-3503 ✕ 身份不明", position=(1300, 600), size=(36, 50)),
    Valve("FV301X", "FV301 ✕ 无管线", position=(1300, 680)),
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
    # ---- 补回的观测边（旧版遗漏） ----
    ("S20", "R3501A", "Out", "JUNC", "In"),
    ("S21", "R3501B", "Out", "JUNC", "In"),
    ("S22", "JUNC", "Out", "V3502", "In"),
    ("S23", "T3501A", "LOut", "T3512", "In"),
    ("S24", "T3512", "Out", "HEIX", "In"),
    ("S25", "T3509", "Out", "V3503", "In"),
    ("S26", "V3503", "Out", "E3510", "TIn"),
    ("S27", "E3510", "TOut", "T3502", "VIn"),
    ("S28", "P3505A", "Out", "E3509", "TIn"),
    ("S29", "E3509", "TOut", "T3502", "VIn"),
    ("S30", "P3505A", "Out", "T3501A", "VIn"),
    ("S31", "V3504", "Out", "T3508", "In"),
    ("S32", "MEH", "VOut", "T3509", "In"),
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
    ("P12", "REFLUX", "Out", "MEH", "VIn"),
]
UTIL = [("U01", "STEAM", "Out", "E3513", "SIn")]

for sid, a, ap, b, bp in OBS:
    pfd.connect(sid, pfd.unitOperations[a][ap], pfd.unitOperations[b][bp])
    pfd.streams[sid].showTitle = False
    pfd.streams[sid].textColor = (255, 255, 255)  # hack: hide stream-id labels on white bg (showTitle ineffective in 0.2.2); svgcontext 需要三元组
for sid, a, ap, b, bp in PRIOR:
    pfd.connect(sid, pfd.unitOperations[a][ap], pfd.unitOperations[b][bp])
    pfd.streams[sid].dashArray = "7,4"
    pfd.streams[sid].showTitle = False
    pfd.streams[sid].textColor = (255, 255, 255)
for sid, a, ap, b, bp in UTIL:
    pfd.connect(sid, pfd.unitOperations[a][ap], pfd.unitOperations[b][bp])
    pfd.streams[sid].dashArray = "2,3,8,3"
    pfd.streams[sid].showTitle = False
    pfd.streams[sid].textColor = (255, 255, 255)

pfd.callout("LEGEND: solid=observed(field)  dashed=prior-driven(book/decision)  dash-dot=utility", (10, 10))
pfd.callout("        X-symbol=declared unclosed survey defect   arrows=layout only, NOT direction claims", (10, 26))
pfd.callout("?  E-302 unknown dangling end (keep unknown)", (40, 90))
pfd.callout("?  P-3505B inlet broken end - not drawn as line", (980, 760))
pfd.callout("?  T-3508 outlet broken end - not drawn as line", (1360, 460))
pfd.callout("?  E-3513 vent end - not drawn as line", (600, 700))
pfd.callout("self-loop not drawn: TMP-MEOHCOL extraction-water recycle (declared)", (40, 780))
pfd.callout("person1 four unlabeled boxes kept as candidates, not nodes (declared)", (40, 740))
pfd.callout("P-3502/P-3503 bottom-circulation pumps: prior edges not drawn (clutter), see handcopy", (820, 740))
pfd.callout("R-3501A outlet: series-to-B vs parallel-to-junction = union of two surveys, unresolved (4th ambiguity)", (40, 800))
pfd.callout("utility lines (CW in/out, condensate return, vents) omitted per basic-PFD convention; see report appendix table", (40, 816))

out = os.path.join(FIG, "flow_main_full.svg")
ctx = SvgContext(out)
pfd.draw(ctx)
ctx.render(scale=1)
print(f"[ok] svg={out}")
print(f"  units={len(pfd.unitOperations)} streams={len(pfd.streams)}")
print(f"  runtime={time.perf_counter() - T0:.2f}s")
