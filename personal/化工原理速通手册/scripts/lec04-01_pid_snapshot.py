# 规模纪律：第 04 讲 P&ID 教学图，目标 < 5 秒。用 pyflowsheet 0.2.2 出带阀门与线型语义的简化 P&ID。
# 目的：生成第 04 讲正文引用的 P&ID 截图——演示阀门符号、实线(确认)/虚线(推测/公用工程)、
#       并借图例讲清三中线型(实/虚/叉号)的实际落图方式。
# 说明：该图包含阀门(Valve)、离心泵(Pump)、换热器(HeatExchanger)、精馏塔(Distillation,
#       自带冷凝器+再沸器)和进出料 StreamFlag。冷却水做虚线(公用工程/推测)。
#       图例用 callout 写在图中左上角。
# 归档：lec04-01（第 04 讲第 1 个脚本，生成图而非数值验证）。
import os
import time
from pyflowsheet import (
    Flowsheet,
    Distillation,
    HeatExchanger,
    Pump,
    Valve,
    StreamFlag,
    SvgContext,
)

T0 = time.perf_counter()
HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)

pfd = Flowsheet("LEC04-PID", "Simplified P&ID", "P&ID snapshot with valve + line-type semantics")

Feed = StreamFlag("Feed", "Feed", position=(0, 240))
V1   = Valve("V-101", "FCV-101", position=(110, 240), size=(40, 20))
P1   = Pump("P-101", "Feed Pump", position=(230, 240))
HX1  = HeatExchanger("E-101", "Preheater", position=(370, 240))
T1   = Distillation(
    "T-101",
    "Distillation Col.",
    hasCondenser=True,
    hasReboiler=True,
    position=(530, 100),
    size=(40, 260),
)
Dist = StreamFlag("D", "Distillate", position=(720, 60))
Bot  = StreamFlag("W", "Bottoms", position=(720, 400))
CW   = StreamFlag("CW", "Cooling Water", position=(320, 40))
CWR  = StreamFlag("CWR", "CW Return", position=(440, 40))

pfd.addUnits([Feed, V1, P1, HX1, T1, Dist, Bot, CW, CWR])

# -- 主线 (实线, dashArray=None = 默认) --
pfd.connect("S01", Feed["Out"], V1["In"])
pfd.connect("S02", V1["Out"], P1["In"])
pfd.connect("S03", P1["Out"], HX1["TIn"])
pfd.connect("S04", HX1["TOut"], T1["Feed"])
pfd.connect("S05", T1["Top"], Dist["In"])
pfd.connect("S06", T1["Bottom"], Bot["In"])

# -- 冷却水 (虚线, 表示公用工程 / 不属于主工艺) --
pfd.connect("S07", CW["Out"], HX1["SIn"])
pfd.connect("S08", HX1["SOut"], CWR["In"])
pfd.streams["S07"].dashArray = "8,5"
pfd.streams["S08"].dashArray = "8,5"

# -- 图例 (用 callout 写在图左上角) --
pfd.callout("LINE-TYPE LEGEND (P&ID):", (10, 10))
pfd.callout("────  confirmed / main process (solid)", (10, 28))
pfd.callout("┄┄┄┄  inferred / utility (dashed)", (10, 44))
pfd.callout("  ✗    broken / false pipe (callout mark)", (10, 60))
pfd.callout("  ?    connection unknown (callout mark)", (10, 76))

# -- 假管/断管示例说明 --
pfd.callout("", (10, 94))

out = os.path.join(FIGDIR, "lec04_pid_snapshot.svg")
ctx = SvgContext(out)
pfd.draw(ctx)
ctx.render(scale=1)
print("=== LEC04 P&ID snapshot (pyflowsheet 0.2.2) ===")
print(f"  units: {list(pfd.unitOperations.keys())}")
print(f"  streams: {list(pfd.streams.keys())}")
print(f"  -> [OK] SVG written: {out}")
print(f"  TOTAL runtime: {time.perf_counter() - T0:.2f}s")