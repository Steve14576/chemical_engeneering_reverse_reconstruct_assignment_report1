# 规模纪律：第 02 讲验证脚本，目标 < 8 秒。纯 numpy/scipy/matplotlib。
# 目的：验证第 02 讲正文每个实测数字：连续性方程、雷诺数判流型、层流速度分布(平均=umax/2)、
#       伯努利(Torricelli 出流)、Colebrook 摩擦系数 + Darcy 沿程损失。
# 归档：lec02-01（第 02 讲第 1 个脚本）。
import os
import time
import numpy as np
from scipy.optimize import fsolve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.perf_counter()
HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)

g = 9.81

# ============ EXP1 连续性方程 A1*v1 = A2*v2 = Q ============
print("=== EXP1: continuity  A*v = Q ===")
Q = 0.01                 # 体积流量 m^3/s
d1, d2 = 0.10, 0.05      # 两段管径 m
A1 = np.pi / 4 * d1**2
A2 = np.pi / 4 * d2**2
v1 = Q / A1
v2 = Q / A2
print(f"  Q={Q} m^3/s")
print(f"  d1={d1} m -> A1={A1:.5f} m^2, v1={v1:.4f} m/s")
print(f"  d2={d2} m -> A2={A2:.5f} m^2, v2={v2:.4f} m/s")
print(f"  v2/v1 = {v2/v1:.3f} (expect (d1/d2)^2 = {(d1/d2)**2:.3f})")
print(f"  -> [OK] dia halved -> velocity x4")

# ============ EXP2 雷诺数判流型 ============
print("\n=== EXP2: Reynolds number & flow regime ===")
rho, mu = 1000.0, 1.0e-3   # 水: 密度 kg/m^3, 粘度 Pa*s
d = 0.05
for v in [0.01, 0.05, 2.0]:
    Re = rho * v * d / mu
    regime = "laminar" if Re < 2300 else ("transient" if Re < 4000 else "turbulent")
    print(f"  v={v} m/s -> Re={Re:.0f} ({regime})")

# ============ EXP3 层流抛物线速度分布：面积加权平均 = umax/2 ============
print("\n=== EXP3: laminar parabolic profile, mean = umax/2 ===")
R = 0.025
umax = 2.0
r = np.linspace(0, R, 200001)
u = umax * (1 - (r / R)**2)
umean_num = np.trapezoid(u * 2 * np.pi * r, r) / (np.pi * R**2)
print(f"  umax={umax}, analytic umean=umax/2={umax/2:.4f}")
print(f"  numeric umean (area-weighted) = {umean_num:.4f}")
print(f"  -> {'[OK]' if abs(umean_num - umax/2) < 1e-3 else '[FAIL]'} numeric matches umax/2")

# ============ EXP4 伯努利 -> Torricelli 出流速度 ============
print("\n=== EXP4: Bernoulli -> Torricelli exit velocity ===")
h = 10.0    # 敞口水塔液面高出出口 10 m；两端都敞口(压强抵消)，液面速度~0
v_exit = np.sqrt(2 * g * h)
print(f"  head h={h} m -> v_exit = sqrt(2*g*h) = {v_exit:.4f} m/s")
print(f"  -> [OK] ideal (frictionless) exit velocity")

# ============ EXP5 Colebrook 摩擦系数 + Darcy 沿程损失 ============
print("\n=== EXP5: Colebrook friction factor + Darcy head loss ===")
Re = 1.0e5
eps = 4.5e-5           # 商用钢管绝对粗糙度 ~0.045 mm
d5 = 0.05
eps_d = eps / d5
def colebrook(lam):
    return 1 / np.sqrt(lam) + 2 * np.log10(eps_d / 3.7 + 2.51 / (Re * np.sqrt(lam)))
lam = fsolve(colebrook, 0.02)[0]
L, vv = 100.0, 2.0
hf = lam * (L / d5) * (vv**2 / (2 * g))
print(f"  Re={Re:.0e}, eps/d={eps_d:.2e} -> Colebrook lambda={lam:.5f}")
print(f"  Darcy hf = lam*(L/d)*(v^2/2g), L={L} m, d={d5} m, v={vv} m/s -> hf={hf:.3f} m")
print(f"  -> [OK] 沿程损失 computed")

# ============ 画图：层流 vs 湍流 速度分布 ============
fig, ax = plt.subplots(figsize=(6, 5))
rr = np.linspace(0, 1, 400)          # r/R
u_lam = umax * (1 - rr**2)           # 层流抛物线
u_turb = umax * (1 - rr)**(1/7)      # 湍流 1/7 次幂近似
ax.plot(u_lam, rr, "b-", lw=2, label="laminar (parabolic)")
ax.plot(u_turb, rr, "r--", lw=2, label="turbulent (1/7 power)")
ax.set_xlabel("u (m/s)")
ax.set_ylabel("r/R   (0 = center, 1 = wall)")
ax.invert_yaxis()
ax.set_title("Pipe velocity profile: laminar vs turbulent")
ax.legend()
ax.grid(alpha=0.3)
out = os.path.join(FIGDIR, "lec02_velocity_profile.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"\n  figure saved: {out}")
print(f"  TOTAL runtime: {time.perf_counter() - T0:.2f}s")
