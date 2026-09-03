# 规模纪律：POC 单图，目标 < 5 秒。用 pyflowsheet 0.2.2 出精馏 PFD (SVG)。
# 目的：证明 Win+uv 环境能用 pyflowsheet 出 B 类流程图。
# 归档：poc-02（开工前 POC，非某一讲；写第 06 讲蒸馏时会被正式脚本取代/复用）。
# 说明：pyflowsheet 0.2.2 的 BitmapContext 残缺（circle/text 空实现、缺 startGroup 等），
#       可靠出口只有 SvgContext -> SVG。SVG 用浏览器直接打开即可看。
import os
import time
from pyflowsheet import (
    Flowsheet,
    Distillation,
    HeatExchanger,
    Pump,
    StreamFlag,
    SvgContext,
)

T0 = time.perf_counter()

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)

# 连续精馏：进料 -> 泵 -> 预热器 -> 精馏塔(自带冷凝器+再沸器) -> 塔顶馏出液 / 塔底釜液
pfd = Flowsheet("POC-DISTIL", "Continuous Distillation PFD", "POC: pyflowsheet 0.2.2")

Feed = StreamFlag("Feed", "Feed", position=(0, 260))
P1 = Pump("P-101", "Feed Pump", position=(140, 260))
HX1 = HeatExchanger("E-101", "Preheater", position=(280, 260))
T1 = Distillation(
    "T-101",
    "Distillation Column",
    hasCondenser=True,
    hasReboiler=True,
    position=(440, 120),
    size=(40, 260),
)
Dist = StreamFlag("D", "Distillate", position=(660, 80))
Bot = StreamFlag("W", "Bottoms", position=(660, 440))

pfd.addUnits([Feed, P1, HX1, T1, Dist, Bot])

# 端口名以 pyflowsheet 0.2.2 源码为准：
#   StreamFlag: In/Out  Pump: In/Out  HeatExchanger: TIn/TOut/SIn/SOut
#   Distillation(带冷凝器+再沸器): Feed/Top/Bottom
pfd.connect("S01", Feed["Out"], P1["In"])
pfd.connect("S02", P1["Out"], HX1["TIn"])
pfd.connect("S03", HX1["TOut"], T1["Feed"])
pfd.connect("S04", T1["Top"], Dist["In"])
pfd.connect("S05", T1["Bottom"], Bot["In"])

out = os.path.join(FIGDIR, "poc_distillation_pfd.svg")
ctx = SvgContext(out)
pfd.draw(ctx)
ctx.render(scale=1)  # saveFile 默认 True，写出到构造函数给的文件名

print("=== POC-02 Distillation PFD (pyflowsheet 0.2.2) ===")
print(f"  units: {list(pfd.unitOperations.keys())}")
print(f"  streams: {list(pfd.streams.keys())}")
print(f"  -> [OK] PFD SVG written: {out}")
print(f"  TOTAL runtime: {time.perf_counter() - T0:.2f}s")
