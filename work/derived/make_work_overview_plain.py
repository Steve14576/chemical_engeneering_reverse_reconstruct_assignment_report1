# -*- coding: utf-8 -*-
"""W4 补图：图7 工作总览·说人话版（独立新文件，原版 work_overview.svg 不删）。

与原版区别：去掉术语（L1/L2、度数闭合、leave-one-out、prior-driven 等），
全部换成日常说法；结构与原版同（四泳道+三侧栏），便于对照。
文本一律 esc() 转义后再进 XML（J21 教训）。
登记：work/PROJECT_LEDGER.md §7（D15 扩展）、DEV_JOURNAL J25。
"""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)

W, H = 1240, 780
p = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
     '<rect width="%d" height="%d" fill="white"/>' % (W, H),
     '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
     '<path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>']


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, label, fill="#fff", stroke="#111", size=12):
    out = ['<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x, y, w, h, fill, stroke)]
    segs = label.split("\n")
    ty = y + h / 2 - 7 * (len(segs) - 1)
    for i, s in enumerate(segs):
        out.append('<text x="%s" y="%s" font-size="%s" text-anchor="middle" fill="#111">%s</text>' % (x + w / 2, ty + i * 15, size, esc(s)))
    return "".join(out)


def arr(x1, y1, x2, y2, label=None):
    s = '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#111" stroke-width="1.8" marker-end="url(#ar)"/>' % (x1, y1, x2, y2)
    if label:
        s += '<text x="%s" y="%s" font-size="11" fill="#666">%s</text>' % ((x1 + x2) / 2 - 34, (y1 + y2) / 2 - 4, esc(label))
    return s


def txt(x, y, s, size=13, color="#111"):
    return '<text x="%s" y="%s" font-size="%s" fill="%s">%s</text>' % (x, y, size, color, esc(s))


p.append(txt(20, 30, "图7  我们到底干了什么（说人话版工作总览）", 16))

p.append(txt(20, 68, "① 现场拿到的东西，先记清楚", 14))
p.append(box(20, 82, 210, 74, "两张现场手绘图\n歪、缺线、有假管断管\n只有1.5小时、没图纸"))
p.append(box(260, 82, 180, 74, "把图抄成表格\n设备/连线/看不清的\n分开记，不改原图"))
p.append(box(470, 82, 190, 74, "两人表格拼一起\n发现：各画各的\n连线几乎不重叠"))
p.append(arr(230, 119, 260, 119))
p.append(arr(440, 119, 470, 119))

p.append(txt(20, 196, "② 检查图对不对，再补缺口", 14))
p.append(box(20, 210, 200, 84, "用硬规矩查图：\n每台设备必须有进有出\n→ 查不通，缺约17条线"))
p.append(box(250, 210, 180, 84, "承认有没画出来的线\n→ 能通了\n并算出缺哪17条"))
p.append(box(460, 210, 190, 84, "承认有画错的线\n→ 40条现场线都自洽\n剩3处选择题"))
p.append(box(680, 210, 200, 84, "按书上标准MTBE流程：\n做3处选择+最少补7条线\n验证过没有更少的补法"))
p.append(arr(220, 252, 250, 252, "加没画变量"))
p.append(arr(430, 252, 460, 252, "加画错变量"))
p.append(arr(650, 252, 680, 252, "书上标准+枚举"))

p.append(txt(20, 334, "③ 算账验证", 14))
p.append(box(20, 348, 240, 74, "物料对账：进=出\nMTBE 约 2.09 t/h\n（只证明自洽，不证明全真）"))
p.append(box(300, 348, 300, 74, "热负荷粗算 约1221 kW\n换参数看结果变多少\n逐条抽掉线看结论翻不翻"))
p.append(arr(260, 385, 300, 385))
p.append(arr(560, 294, 560, 348, "流程定稿后"))

p.append(txt(20, 462, "④ 交给老师什么", 14))
p.append(box(20, 476, 230, 74, "流程图/框图/结构图\n每种线标明来源：\n实=现场 虚=书上补 叉=不确定"))
p.append(box(280, 476, 200, 74, "报告正文\n每句话标：看到的/\n书上查的/我们推的"))
p.append(box(510, 476, 200, 74, "电子附件\n脚本+数据，可复跑\n改过什么主意都记了"))
p.append(arr(140, 422, 120, 476))
p.append(arr(450, 422, 380, 476))

p.append(box(920, 82, 300, 120, "补线的规矩\n不是想补就补：\n只在标准流程可能有的线里选\n补最少条数且验证唯一\n补的线在图上画虚线", size=12))
p.append(box(920, 226, 300, 110, "说话的规矩\n书上有据 → 写出处\n没据 → 标推断\n看不清 → 写未知，不编", size=12))
p.append(box(920, 360, 300, 110, "查账的规矩\n每步有记录、有哈希\n改主意记在流水里\n成绩前私有，成绩后公开", size=12))
p.append(arr(660, 119, 920, 119))
p.append(arr(880, 252, 920, 280))
p.append(arr(710, 513, 920, 415))

p.append(txt(20, 580, "一句话：两张不准的手绘图 → 查出错在哪、缺多少 → 按书上标准补缺口并标明 → 算账验证 → 交给老师。", 13))
p.append(txt(20, 602, "侧栏是三条纪律：补线规矩（怎么补）、说话规矩（怎么写字）、查账规矩（怎么复核）。", 12, "#666"))
p.append("</svg>")

open(os.path.join(FIG, "work_overview_plain.svg"), "w", encoding="utf-8").write("".join(p))
print("[ok] wrote work_overview_plain.svg")
