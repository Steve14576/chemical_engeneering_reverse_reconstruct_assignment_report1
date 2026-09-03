# 规模纪律：第 01 讲验证脚本，目标 < 5 秒。纯 numpy + networkx，不依赖重型框架。
# 目的：验证第 01 讲正文里出现的每一个实测数字——(1) 精馏塔总物料+组分衡算；
#       (2) networkx "带置信度约束图" 雏形能建、能查泵的进出口度数。
# 归档：lec01-01（第 01 讲第 1 个脚本）。
import time
import numpy as np
import networkx as nx

T0 = time.perf_counter()

# ============ 实验 1：稳态物料衡算（精馏塔总体 + 轻组分）============
# 原理：稳态、无反应 -> 进=出。总量 F = D + W；轻组分 F*xF = D*xD + W*xW
print("=== EXP1: steady-state mass balance (distillation overall) ===")
F = 100.0   # 进料流量 kmol/h
xF = 0.50   # 进料轻组分摩尔分数
xD = 0.95   # 塔顶馏出液
xW = 0.05   # 塔底釜液

# 解二元一次方程组：F=D+W, F*xF=D*xD+W*xW
# 代入 W=F-D:  F*xF = D*xD + (F-D)*xW  ->  D = F*(xF-xW)/(xD-xW)
D = F * (xF - xW) / (xD - xW)
W = F - D
print(f"  given F={F}, xF={xF}, xD={xD}, xW={xW}")
print(f"  D = F*(xF-xW)/(xD-xW) = {D:.4f} kmol/h")
print(f"  W = F - D            = {W:.4f} kmol/h")

# 回代校核：总量守恒 + 组分守恒
bal_total = F - (D + W)
bal_light = F * xF - (D * xD + W * xW)
print(f"  check total  F-(D+W)          = {bal_total:.2e} (expect ~0)")
print(f"  check light  F*xF-(D*xD+W*xW) = {bal_light:.2e} (expect ~0)")
ok1 = abs(bal_total) < 1e-9 and abs(bal_light) < 1e-9
print(f"  -> {'[OK]' if ok1 else '[FAIL]'} both balances close; D={D:.1f}, W={W:.1f}")

# 回收率（轻组分进到塔顶的比例）——报告里常用的一个指标
recovery = D * xD / (F * xF)
print(f"  light-component recovery to stream D = {recovery*100:.2f}%")

# ============ 实验 2：networkx "带置信度约束图" 雏形 ============
# 把现场碎片观察建成图：节点=设备，边=管线片段，边属性=置信度/是否假管
print(f"\n=== EXP2: networkx confidence-tagged constraint graph (t={time.perf_counter()-T0:.1f}s) ===")
G = nx.MultiDiGraph()
G.add_node("T-101", kind="tank")
G.add_node("P-101", kind="pump")
G.add_node("E-101", kind="hex")

# 边: (起点, 终点, 置信度, 是否确认, 备注)
edges = [
    ("T-101", "P-101", "high", True,  "两端都直接看到"),
    ("P-101", "E-101", "medium", False, "出口拐弯后被遮挡，按走向推测"),
    ("E-101", "T-101", "low", False, "疑似回流，也可能是假管"),
]
for a, b, conf, confirmed, note in edges:
    G.add_edge(a, b, confidence=conf, confirmed=confirmed, note=note)

print(f"  nodes: {list(G.nodes)}")
print(f"  edges: {[(u, v, d['confidence']) for u, v, d in G.edges(data=True)]}")

# 软约束检查：泵必须有入口(in_degree>=1)和出口(out_degree>=1)
for n, kind in G.nodes(data="kind"):
    if kind == "pump":
        ind, outd = G.in_degree(n), G.out_degree(n)
        ok = ind >= 1 and outd >= 1
        print(f"  pump {n}: in_degree={ind}, out_degree={outd} -> {'[OK]' if ok else '[WARN]'} pump in/out port constraint")

# 统计"稳定连接"（confirmed=True）vs "待定连接"
stable = [(u, v) for u, v, d in G.edges(data=True) if d["confirmed"]]
pending = [(u, v) for u, v, d in G.edges(data=True) if not d["confirmed"]]
print(f"  stable(confirmed) edges : {stable}")
print(f"  pending(inferred/unknown) edges: {pending}")
print(f"  -> [OK] graph built; {len(stable)} stable + {len(pending)} pending edges")

print(f"\n  TOTAL runtime: {time.perf_counter()-T0:.2f}s")
