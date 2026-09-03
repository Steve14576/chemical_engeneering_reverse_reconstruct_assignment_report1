# 规模纪律：第 11 讲验证脚本，目标 < 5 秒。纯 Python + networkx + matplotlib。
# 零外部求解器依赖：7 变量 2^7=128 种组合，穷举比任何求解器配置都快。
# 目的：验证第 11 讲正文——(1) 候选边建模(2) 硬约束(端口≤1)+软约束(泵/换热器加分)
#       (3) k-best 枚举(4) 稳定边频率(5) 敏感性分析(6) 画结果图。
# 归档：lec11-01。真实大规模问题应用 OR-Tools CP-SAT 或 MILP。
import os, time, itertools
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.perf_counter()
HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)

print("=== LEC11: topology reverse-engineering (exhaustive search) ===")

# ============ 1. 数据 ============
candidates = [
    ("T_bot", "P_in", 70, False),   # 0 罐→泵
    ("P_out", "E_in", 50, False),   # 1 泵→换热器
    ("E_out", "S_in", 50, False),   # 2 换热器→外输
    ("E_out", "P_out", 45, False),  # 3 回流
    ("E_out", "T_bot", 40, False),  # 4 旁路
    ("P_out", "S_in", 55, False),   # 5 泵直送外输
    ("T_bot", "S_in", 30, False),   # 6 罐直送外输（弱观察）
]
nvars = len(candidates)
ports = ["T_bot", "P_in", "P_out", "E_in", "E_out", "S_in"]
desc = ["T_bot->P_in (70)", "P_out->E_in (50)", "E_out->S_in (50)",
        "E_out->P_out (45,recycle)", "E_out->T_bot (40,bypass)",
        "P_out->S_in (55,alt)", "T_bot->S_in (30,weak)"]
print("  candidates:")
for i in range(nvars):  print(f"    [{i}] {desc[i]}")

# ============ 2. 穷举所有合法解 ============
def is_valid(mask):
    for i in range(nvars):
        if candidates[i][3] and not (mask>>i & 1): return False
    for p in ports:
        if sum(1 for i,(a,b,_,_) in enumerate(candidates)
               if (a==p or b==p) and (mask>>i & 1)) > 1: return False
    return True

def tot_score(mask):
    s = sum(candidates[i][2] for i in range(nvars) if mask>>i & 1)
    # 软约束加分：泵进出口都连通 +20
    p_in = sum(1 for i,(a,b,_,_) in enumerate(candidates)
               if (a=="P_in" or b=="P_in") and (mask>>i & 1))
    p_out = sum(1 for i,(a,b,_,_) in enumerate(candidates)
                if (a=="P_out" or b=="P_out") and (mask>>i & 1))
    if p_in>=1 and p_out>=1: s += 20
    # 换热器两侧都连通 +20
    e_in = sum(1 for i,(a,b,_,_) in enumerate(candidates)
               if (a=="E_in" or b=="E_in") and (mask>>i & 1))
    e_out = sum(1 for i,(a,b,_,_) in enumerate(candidates)
                if (a=="E_out" or b=="E_out") and (mask>>i & 1))
    if e_in>=1 and e_out>=1: s += 20
    return s

valid = [(m, tot_score(m)) for m in range(1<<nvars) if is_valid(m)]
valid.sort(key=lambda x:-x[1])
print(f"\n  total valid solutions: {len(valid)}")
ns = min(len(valid), 10)

# ============ 3. 最优解 ============
best_mask, best_sc = valid[0]
print(f"\n-- Step 1: optimal (score={best_sc}) --")
for i in range(nvars):
    if best_mask>>i & 1: print(f"  [{i}] {desc[i]}")

# ============ 4. K-best ============
print(f"\n-- Step 2: top-{ns} solutions --")
top_masks = [m for m,_ in valid[:ns]]
for k,(m,sc) in enumerate(valid[:ns]):
    ed = [i for i in range(nvars) if m>>i & 1]
    print(f"  #{k+1:2d}  score={sc:3d}  edges={ed}")

# ============ 5. 稳定边频率 ============
print(f"\n-- Step 3: stable edge freq ({ns} solutions) --")
freq = {i: sum(1 for m in top_masks if m>>i & 1) for i in range(nvars)}
stable   = [i for i in range(nvars) if freq[i]==ns]
unstable = [i for i in range(nvars) if 0<freq[i]<ns]
never    = [i for i in range(nvars) if freq[i]==0]
print("  STABLE(100%):", [f"{i}:{desc[i][:20]}" for i in stable])
print("  UNSTABLE:",     [f"{i}:{desc[i][:20]} fr={freq[i]}" for i in unstable])
print("  NEVER:",        [f"{i}:{desc[i][:20]}" for i in never])

# ============ 6. 敏感性分析 ============
print(f"\n-- Step 4: sensitivity (drop edge[0], score 70->0) --")
scores_b = [candidates[i][2] for i in range(nvars)]
scores_b[0] = 0
def tot_score_b(mask):
    s = sum(scores_b[i] for i in range(nvars) if mask>>i & 1)
    p_in = sum(1 for i,(a,b,_,_) in enumerate(candidates)
               if (a=="P_in" or b=="P_in") and (mask>>i & 1))
    p_out = sum(1 for i,(a,b,_,_) in enumerate(candidates)
                if (a=="P_out" or b=="P_out") and (mask>>i & 1))
    if p_in>=1 and p_out>=1: s+=20
    e_in = sum(1 for i,(a,b,_,_) in enumerate(candidates)
               if (a=="E_in" or b=="E_in") and (mask>>i & 1))
    e_out = sum(1 for i,(a,b,_,_) in enumerate(candidates)
                if (a=="E_out" or b=="E_out") and (mask>>i & 1))
    if e_in>=1 and e_out>=1: s+=20
    return s
valid_b = [(m, tot_score_b(m)) for m in range(1<<nvars) if is_valid(m)]
valid_b.sort(key=lambda x:-x[1])
if valid_b:
    bm, bs = valid_b[0]
    sel2 = [i for i in range(nvars) if bm>>i & 1]
    lost = set(i for i in range(nvars) if best_mask>>i & 1) - set(sel2)
    print(f"  new best score={bs}  edges={sel2}")
    print(f"  lost: {[desc[i] for i in lost]}" if lost else "  same edges (robust)")
else:
    print("  no solution after dropping [0] (fragile)")

# ============ 7. 画拓扑图 ============
print("\n-- Step 5: topology figure --")
nodem = {"T_bot":"T-101","P_in":"P-101","P_out":"P-101",
         "E_in":"E-101","E_out":"E-101","S_in":"Stream"}
G = nx.MultiDiGraph()
for nod in ["T-101","P-101","E-101","Stream"]: G.add_node(nod)
for i in range(nvars):
    if best_mask>>i & 1:
        a,b,_,_ = candidates[i]
        style = "solid" if i in stable else "dashed"
        G.add_edge(nodem[a], nodem[b], style=style)
pos = {"T-101":(0,0),"P-101":(2,0),"E-101":(4,0),"Stream":(6,0)}
fig,ax = plt.subplots(figsize=(6,3))
for u,v,d in G.edges(data=True):
    c = "black" if d["style"]=="solid" else "red"
    ls = "-" if d["style"]=="solid" else "--"
    ax.annotate("", xy=pos[v], xytext=pos[u],
                arrowprops=dict(arrowstyle="->", color=c, lw=1.5, ls=ls))
for n,p in pos.items():
    ax.plot(p[0],p[1],"o",ms=14,color="lightblue",mec="black",mew=1)
    ax.text(p[0],p[1]-0.35,n,ha="center",fontsize=10,fontweight="bold")
ax.set_xlim(-0.5,6.5); ax.set_ylim(-1,1)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title(f"Topology: {len(stable)} stable(solid) + {len(unstable)} unstable(dashed)  score={best_sc}")
out = os.path.join(FIGDIR,"lec11_topology.png")
fig.savefig(out,dpi=150,bbox_inches="tight")
print(f"  figure saved: {out}")
print(f"  TOTAL runtime: {time.perf_counter()-T0:.2f}s")