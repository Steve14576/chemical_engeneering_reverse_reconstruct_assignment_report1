# -*- coding: utf-8 -*-
"""W4 线框对照图 flow_main_wire（平行于图2 flow_main_full，同拓扑不同画法）。

目的：消除 pyflowsheet 自动布线的渲染歧义（线挤同一走廊、标签叠字），给一张
"矩形+直线、标签在框内"的线框图，与图2 对照核拓扑。
同源保证：直接 import make_flow_diagram_full 复用其 U/OBS/PRIOR/UTIL（import 会顺带
重生成 flow_main_full.svg，幂等、无副作用风险），两图拓扑列表不可能漂移。
画法：矩形框（id+中文名在框内）；边为框边中点直线（按方向选边），线型语义同图2
（实=观测、虚=prior、点划=公用）；不画 stream 编号；callout 声明同图2。
CJK 由 make_png_exports 注入 font-family 解决。
登记：work/PROJECT_LEDGER.md §7（D15 扩展）、DEV_JOURNAL J28。
"""
from __future__ import annotations

import os

import make_flow_diagram_full as F  # noqa: F401  (side effect: regen flow_main_full.svg, idempotent)

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")

# ---- 单元框布局（复用 full 版坐标，放大框体以容纳标签） ----
boxes = {}
for u in F.U:
    x, y = u.position
    w, h = getattr(u, "size", (40, 40))
    w = max(w * 1.6, 90)
    h = max(h * 1.15, 46)
    boxes[u.id] = {"name": u.name, "x": x - w / 2, "y": y - h / 2, "w": w, "h": h}

SW, SH = 1500, 860
p = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (SW, SH, SW, SH),
     '<rect width="%d" height="%d" fill="white"/>' % (SW, SH)]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def anchor(bx, tx, ty):
    """从框 bx 朝目标中心 (tx,ty) 的边框交点。"""
    cx, cy = bx["x"] + bx["w"] / 2, bx["y"] + bx["h"] / 2
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (bx["w"] / 2) / abs(dx) if dx else 1e9
    sy = (bx["h"] / 2) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


# ---- 边 ----
def edge(a, b, dash=None):
    ba, bb = boxes[a], boxes[b]
    ca = (ba["x"] + ba["w"] / 2, ba["y"] + ba["h"] / 2)
    cb = (bb["x"] + bb["w"] / 2, bb["y"] + bb["h"] / 2)
    x1, y1 = anchor(ba, *cb)
    x2, y2 = anchor(bb, *ca)
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#111" stroke-width="1.6"%s/>' % (x1, y1, x2, y2, d)


for sid, a, ap, b, bp in F.OBS:
    p.append(edge(a, b))
for sid, a, ap, b, bp in F.PRIOR:
    p.append(edge(a, b, "7,4"))
for sid, a, ap, b, bp in F.UTIL:
    p.append(edge(a, b, "2,3,8,3"))

# ---- 单元框 + 标签 ----
for uid, bx in boxes.items():
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#111" stroke-width="1.5"/>'
             % (bx["x"], bx["y"], bx["w"], bx["h"]))
    segs = bx["name"].split(" ")
    label = uid if not bx["name"] else bx["name"]
    lines = [uid] + ([label] if label != uid else [])
    ty = bx["y"] + bx["h"] / 2 - 6 * (len(lines) - 1)
    for i, s in enumerate(lines):
        p.append('<text x="%.1f" y="%.1f" font-size="11" text-anchor="middle" fill="#111">%s</text>'
                 % (bx["x"] + bx["w"] / 2, ty + i * 13, esc(s)))

# ---- 图例与声明（同图2口径） ----
p.append('<text x="10" y="16" font-size="13" fill="#111">%s</text>' % esc("LEGEND: solid=observed(field)  dashed=prior-driven  dash-dot=utility   wireframe twin of flow_main_full (same topology)"))
p.append('<text x="10" y="32" font-size="12" fill="#666">%s</text>' % esc("X-marked units = declared unclosed survey defect; arrows omitted on purpose (layout-only in fig2, not direction claims)"))
p.append('<text x="10" y="806" font-size="12" fill="#666">%s</text>' % esc("? E-302 unknown dangling end; P-3505B inlet & T-3508 outlet broken ends; E-3513 vent end; MEH extraction-water self-loop: declared, not drawn"))
p.append('<text x="10" y="822" font-size="12" fill="#666">%s</text>' % esc("person1 four unlabeled boxes kept as candidates, not nodes; P-3502/P-3503 prior edges not drawn (clutter)"))
p.append('<text x="10" y="838" font-size="12" fill="#666">%s</text>' % esc("R-3501A outlet: series-to-B vs parallel-to-junction = union of two surveys, unresolved (4th ambiguity)"))

out = os.path.join(FIG, "flow_main_wire.svg")
with open(out, "w", encoding="utf-8") as f:
    f.write("".join(p) + "</svg>")
print("[ok] svg=%s  boxes=%d edges=%d" % (out, len(boxes), len(F.OBS) + len(F.PRIOR) + len(F.UTIL)))
