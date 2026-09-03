# 规模纪律：第 03 讲验证脚本，目标 < 8 秒。纯 numpy/scipy/matplotlib。
# 目的：验证第 03 讲正文每个实测数字：离心泵特性曲线 H-Q、效率曲线与最佳效率点、
#       管路特性曲线、工作点(两曲线交点, brentq 求根)、轴功率、允许安装高度(NPSH/气蚀)。
# 归档：lec03-01（第 03 讲第 1 个脚本）。
import os
import time
import numpy as np
from scipy.optimize import brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.perf_counter()
HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)

g = 9.81
rho = 1000.0

# ============ EXP1 泵特性曲线 H = H0 - a*Q^2 ============
print("=== EXP1: pump characteristic curve H-Q ===")
H0 = 30.0    # 关死点扬程 m (Q=0 时)
a = 500.0    # 曲线系数, Q 单位 m^3/s
Q = np.linspace(0, 0.20, 200)
H = H0 - a * Q**2
Qmax = np.sqrt(H0 / a)
print(f"  H(Q) = {H0} - {a}*Q^2   (Q in m^3/s)")
print(f"  shutoff head H(Q=0) = {H0:.1f} m")
print(f"  max flow (H=0): Q = sqrt(H0/a) = {Qmax:.4f} m^3/s = {Qmax*3600:.0f} m^3/h")

# ============ EXP2 效率曲线与最佳效率点 BEP ============
print("\n=== EXP2: efficiency curve & best efficiency point ===")
Qbep = 0.10     # 最佳效率点流量 m^3/s
eta_max = 0.80
eta = np.clip(eta_max * (1 - ((Q - Qbep) / Qbep)**2), 0, 1)   # 简化抛物线
i = int(np.nanargmax(eta))
print(f"  BEP target: Q={Qbep} m^3/s, eta_max={eta_max}")
print(f"  numeric peak eta = {eta[i]:.3f} at Q={Q[i]:.4f} m^3/s")

# ============ EXP3 管路特性曲线 + 工作点(交点) ============
print("\n=== EXP3: system curve & operating point ===")
dz = 10.0    # 静扬程(需提升的几何高度+压差) m
K = 800.0    # 管路阻力系数
def system_head(q):
    return dz + K * q**2
def gap(q):
    return (H0 - a * q**2) - system_head(q)
Qop = brentq(gap, 1e-6, Qmax)
Hop = H0 - a * Qop**2
print(f"  system curve: He = {dz} + {K}*Q^2")
print(f"  operating point: Q*={Qop:.4f} m^3/s ({Qop*3600:.0f} m^3/h), H*={Hop:.3f} m")
print(f"  check pump H - system He = {gap(Qop):.2e} -> {'[OK]' if abs(gap(Qop))<1e-6 else '[FAIL]'} intersection closes")
eta_op = eta_max * (1 - ((Qop - Qbep) / Qbep)**2)
Nop = rho * g * Qop * Hop / eta_op
print(f"  at OP: eta={eta_op:.3f}, shaft power N = rho*g*Q*H/eta = {Nop/1000:.2f} kW")

# ============ EXP4 允许安装高度(气蚀 / NPSH) ============
print("\n=== EXP4: max suction lift (cavitation / NPSH) ===")
p0 = 101325.0     # 吸入液面压力 Pa (敞口 = 大气压)
pv = 2339.0       # 20C 水的饱和蒸气压 Pa
NPSHr = 3.0       # 泵必需的净正吸入压头 m (厂家给定)
hf_s = 0.5        # 吸入管路损失 m
Hg = (p0 - pv) / (rho * g) - NPSHr - hf_s
print(f"  Hg = (p0-pv)/(rho*g) - NPSHr - hf_s")
print(f"     = ({p0}-{pv})/(1000*9.81) - {NPSHr} - {hf_s}")
print(f"     = {(p0-pv)/(rho*g):.3f} - {NPSHr} - {hf_s} = {Hg:.3f} m")
print(f"  -> max suction lift above liquid level = {Hg:.2f} m (else cavitation)")

# ============ 画图：泵曲线 + 管路曲线 + 工作点 + 效率 ============
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(Q * 3600, H, "b-", lw=2, label="pump H-Q")
ax.plot(Q * 3600, dz + K * Q**2, "g-", lw=2, label="system He-Q")
ax.plot(Qop * 3600, Hop, "ko", ms=8,
        label=f"operating point ({Qop*3600:.0f} m3/h, {Hop:.1f} m)")
ax2 = ax.twinx()
ax2.plot(Q * 3600, eta * 100, "r--", lw=1.5, label="efficiency %")
ax.set_xlabel("Q (m^3/h)")
ax.set_ylabel("H (m)")
ax2.set_ylabel("eta (%)")
ax.set_title("Centrifugal pump: characteristic & system curve")
ax.legend(loc="upper right")
ax2.legend(loc="center right")
ax.grid(alpha=0.3)
out = os.path.join(FIGDIR, "lec03_pump_curve.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"\n  figure saved: {out}")
print(f"  TOTAL runtime: {time.perf_counter() - T0:.2f}s")
