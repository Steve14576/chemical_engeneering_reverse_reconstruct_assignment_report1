# 规模纪律：POC 单图，目标 < 5 秒。纯 numpy + matplotlib，不依赖重型框架。
# 目的：证明 Win+uv 环境能用 matplotlib 出 A 类曲线图；顺带数值验证 McCabe-Thiele 逐板作图。
# 归档：poc-01（开工前 POC，非某一讲；写第 06 讲蒸馏时会被正式脚本取代/复用）。
import os
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")  # 无显示环境，直接存文件，避免弹窗阻塞
import matplotlib.pyplot as plt

T0 = time.perf_counter()

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)

# ---- 参数（苯-甲苯类二元体系）----
alpha = 2.5   # 相对挥发度
xF = 0.50     # 进料轻组分摩尔分数
xD = 0.95     # 塔顶(馏出液)
xW = 0.05     # 塔底(釜液)
q = 1.0       # 进料热状况(饱和液体 q=1)


def eq_y(x):
    """气液平衡线: y = a*x / (1 + (a-1)*x)"""
    return alpha * x / (1 + (alpha - 1) * x)


def eq_x(y):
    """平衡线反解: 由 y 求 x（阶梯作图水平步用）"""
    return y / (alpha - (alpha - 1) * y)


# ---- 最小回流比 Rmin ----
# q=1 时 q 线是竖线 x=xF，与平衡线交点 (xF, eq_y(xF)) 即夹紧点
y_feed = eq_y(xF)
Rmin = (xD - y_feed) / (y_feed - xF)
R = 1.5 * Rmin  # 工程常取 1.2~2 倍 Rmin，这里取 1.5


# ---- 操作线 ----
def rect_ol(x):
    """精馏段操作线: y = R/(R+1)*x + xD/(R+1)"""
    return R / (R + 1) * x + xD / (R + 1)


# q=1 -> q 线竖直 x=xF；与精馏段操作线交点
x_int = xF
y_int = rect_ol(x_int)


def strip_ol(x):
    """提馏段操作线: 过 (x_int,y_int) 与 (xW,xW) 两点"""
    slope = (y_int - xW) / (x_int - xW)
    return xW + slope * (x - xW)


# ---- 逐板阶梯作图 ----
stair_x = [xD]
stair_y = [xD]
x, y = xD, xD
stages = 0
feed_stage = None
while x > xW and stages < 100:
    x = eq_x(y)              # 水平步：走到平衡线（一块理论板）
    stages += 1
    stair_x.append(x)
    stair_y.append(y)
    if x <= xW:
        break
    if feed_stage is None and x <= x_int:
        feed_stage = stages  # 跨过 q 线交点 -> 此后换提馏段操作线
    y = strip_ol(x) if feed_stage is not None else rect_ol(x)  # 垂直步：走到操作线
    stair_x.append(x)
    stair_y.append(y)

print("=== POC-01 McCabe-Thiele ===")
print(f"  alpha={alpha}, xF={xF}, xD={xD}, xW={xW}, q={q}")
print(f"  y at feed pinch = {y_feed:.4f}")
print(f"  Rmin = {Rmin:.4f}, chosen R = 1.5*Rmin = {R:.4f}")
print(f"  theoretical stages (incl. reboiler) = {stages}")
print(f"  feed stage = {feed_stage}")
print(f"  last x = {x:.4f} (expect <= xW={xW})")
ok = x <= xW + 1e-9
print(f"  -> {'[OK]' if ok else '[FAIL]'} staircase reached xW; stages={stages}")

# ---- 画图 ----
xs = np.linspace(0, 1, 400)
xs2 = np.linspace(xW, x_int, 120)
fig, ax = plt.subplots(figsize=(6.5, 6.5))
ax.plot(xs, xs, "k--", lw=1, label="y = x (diagonal)")
ax.plot(xs, eq_y(xs), "b-", lw=2, label=f"equilibrium (alpha={alpha})")
ax.plot(xs, rect_ol(xs), "r-", lw=1.5, label=f"rectifying OL (R={R:.2f})")
ax.plot(xs2, strip_ol(xs2), "g-", lw=1.5, label="stripping OL")
ax.plot([xF, xF], [0, y_feed], "m:", lw=1.5, label="q-line (q=1)")
ax.plot(stair_x, stair_y, "k-", lw=1.0, label=f"{stages} stages")
ax.plot([xD], [xD], "ko", ms=4)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel("x  (liquid mole fraction, light component)")
ax.set_ylabel("y  (vapor mole fraction, light component)")
ax.set_title(f"McCabe-Thiele: {stages} theoretical stages, feed stage {feed_stage}")
ax.legend(loc="upper left", fontsize=8)
ax.grid(True, alpha=0.3)

out = os.path.join(FIGDIR, "poc_mccabe_thiele.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"  figure saved: {out}")
print(f"  TOTAL runtime: {time.perf_counter() - T0:.2f}s")
