# -*- coding: utf-8 -*-
"""W4 补图：框图(flow_block.svg) + 三张典型设备结构示意(struct_*.svg)。

说明：框图与结构图为**简化示意、非比例** SVG（plain SVG 手写坐标，不用 pyflowsheet——
pyflowsheet 强项是带标准单元符号的流程图 flow_main.svg，框图/剖面示意用方框线条更清楚）；
结构图内件依据文献（D11：催化蒸馏三段+捆包；固定床床层；管壳管束/折流板），现场内件不可见，已声明。
嵌入方式：report.md 以 ![](../derived/figures/xxx.svg) 嵌入，md 编辑器渲染即见成品。
登记：work/PROJECT_LEDGER.md §7（D15 扩展）。
"""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="white"/><defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker><marker id="ard" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#b00200"/></marker></defs>'


def box(x, y, w, h, label, fill="#fff", stroke="#111"):
    lines = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>']
    segs = label.split("\n")
    ty = y + h / 2 - 7 * (len(segs) - 1)
    for i, s in enumerate(segs):
        lines.append(f'<text x="{x+w/2}" y="{ty+i*15}" font-size="13" text-anchor="middle" fill="#111">{s}</text>')
    return "".join(lines)


def arr(x1, y1, x2, y2, dash=None, color="#111", marker="ar"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.8"{d} marker-end="url(#{marker})"/>'


def txt(x, y, s, size=12, color="#111"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{s}</text>'


# ---------------- 框图 ----------------
W, H = 1180, 620
p = [HEAD.format(w=W, h=H)]
p.append(txt(20, 30, "图1  MTBE 装置工艺框图（块级；虚线=循环/公用，实线=主物料）", 16))
p.append(box(30, 90, 130, 60, "混合C4原料\n(异丁烯~25mol%)"))
p.append(box(30, 210, 130, 60, "甲醇原料\n(外购)"))
p.append(box(210, 150, 120, 60, "原料罐/混合罐\n+进料泵+预热"))
p.append(box(380, 150, 130, 70, "醚化反应\nR-3501A/B\n(两段串联)"))
p.append(box(560, 120, 140, 130, "催化蒸馏塔\nT-3501(A上/B下)\n反应+分离耦合"))
p.append(box(760, 60, 130, 60, "MTBE产品\n(塔底, ~99.9wt%)"))
p.append(box(760, 210, 130, 60, "醚后C4\n(塔顶)"))
p.append(box(560, 330, 140, 70, "甲醇萃取塔\nT-3502\n(水萃取)"))
p.append(box(380, 330, 140, 70, "甲醇回收塔\nTMP-MEOHCOL"))
p.append(box(210, 330, 130, 60, "萃取水回路\n(闭路循环)"))
p.append(box(760, 330, 130, 60, "醚后C4产品\n(残甲醇~485ppm)"))
p.append(arr(160, 120, 210, 165))
p.append(arr(160, 240, 210, 195))
p.append(arr(330, 180, 380, 180))
p.append(arr(510, 180, 560, 180))
p.append(arr(700, 150, 760, 95))
p.append(arr(700, 210, 760, 235))
p.append(arr(825, 270, 825, 330))
p.append(arr(825, 360, 700, 360))
p.append(arr(560, 365, 520, 365))
p.append(arr(380, 365, 340, 360))
p.append(arr(275, 330, 275, 210, dash="6,4", color="#b00200", marker="ard"))
p.append(txt(285, 280, "甲醇循环", 12, "#b00200"))
p.append(arr(275, 390, 275, 470, dash="6,4", color="#b00200", marker="ard"))
p.append(arr(275, 470, 630, 470, dash="6,4", color="#b00200", marker="ard"))
p.append(arr(630, 470, 630, 400, dash="6,4", color="#b00200", marker="ard"))
p.append(txt(400, 460, "萃取水闭路", 12, "#b00200"))
p.append(txt(30, 560, "注：300 编号单元（V-302/T-301/E-301/E-302/T-302/V-301/E-303）功能未确认，未入框图，见流程图与局限清单。", 12, "#666"))
p.append("</svg>")
open(os.path.join(FIG, "flow_block.svg"), "w", encoding="utf-8").write("".join(p))

# ---------------- 结构1 固定床醚化反应器 ----------------
W, H = 520, 560
p = [HEAD.format(w=W, h=H)]
p.append(txt(20, 30, "图3  固定床醚化反应器 结构示意（简化·非比例）", 15))
p.append(box(180, 70, 160, 400, "", fill="#fff"))
p.append(arr(260, 40, 260, 70))
p.append(txt(270, 55, "原料进口(C4+MeOH)"))
p.append('<line x1="180" y1="110" x2="340" y2="110" stroke="#111" stroke-width="1.4"/>')
p.append(txt(350, 114, "进口分布器"))
p.append('<rect x="188" y="130" width="144" height="240" fill="#eee" stroke="#111" stroke-width="1.2"/>')
p.append(txt(260, 250, "催化剂床层", 13))
p.append(txt(260, 268, "(酸性树脂)", 12))
for yy in (160, 200, 240, 280, 320):
    p.append(f'<circle cx="215" cy="{yy}" r="3" fill="#111"/><circle cx="260" cy="{yy+15}" r="3" fill="#111"/><circle cx="305" cy="{yy}" r="3" fill="#111"/>')
p.append(txt(350, 200, "测温点(床层温升监控)"))
p.append('<line x1="180" y1="390" x2="340" y2="390" stroke="#111" stroke-width="1.4"/>')
p.append(txt(350, 394, "支撑栅板+出口滤网"))
p.append(arr(260, 470, 260, 510))
p.append(txt(270, 505, "产物出口(去催化蒸馏)"))
p.append(txt(30, 545, "内件不可见，依据工艺路线文献整理；现场仅确认外形与进出口接管。", 12, "#666"))
p.append("</svg>")
open(os.path.join(FIG, "struct_reactor.svg"), "w", encoding="utf-8").write("".join(p))

# ---------------- 结构2 催化蒸馏塔 ----------------
W, H = 640, 620
p = [HEAD.format(w=W, h=H)]
p.append(txt(20, 30, "图4  催化蒸馏塔 结构示意（三段+外接回路；简化·非比例）", 15))
p.append(box(240, 80, 120, 420, "", fill="#fff"))
p.append('<rect x="246" y="90" width="108" height="110" fill="#fff" stroke="#111" stroke-width="1.2"/>')
p.append(txt(300, 150, "精馏段", 13))
p.append('<rect x="246" y="210" width="108" height="150" fill="#eee" stroke="#111" stroke-width="1.2"/>')
p.append(txt(300, 275, "反应段", 13))
p.append(txt(300, 293, "(催化剂捆包)", 12))
for yy in (230, 265, 300, 335):
    p.append(f'<rect x="256" y="{yy}" width="88" height="18" fill="none" stroke="#111" stroke-width="1"/>')
p.append('<rect x="246" y="370" width="108" height="120" fill="#fff" stroke="#111" stroke-width="1.2"/>')
p.append(txt(300, 435, "提馏段", 13))
p.append(box(430, 60, 120, 50, "塔顶冷却器\nE-3507"))
p.append(box(430, 130, 120, 50, "回流罐\nV-3503"))
p.append(box(430, 470, 120, 50, "塔底再沸器\nE-3506"))
p.append(arr(360, 100, 430, 85))
p.append(arr(490, 110, 490, 130))
p.append(arr(430, 155, 360, 140, dash="6,4", color="#b00200", marker="ard"))
p.append(txt(370, 130, "回流", 12, "#b00200"))
p.append(arr(360, 480, 430, 495))
p.append(arr(430, 510, 360, 500, dash="6,4", color="#b00200", marker="ard"))
p.append(txt(370, 525, "汽相返回", 12, "#b00200"))
p.append(arr(180, 300, 240, 300))
p.append(txt(60, 290, "进料(反应产物)"))
p.append(arr(300, 60, 300, 30))
p.append(txt(310, 25, "塔顶: 醚后C4"))
p.append(arr(300, 500, 300, 560))
p.append(txt(310, 580, "塔底: MTBE"))
p.append(txt(30, 605, "捆包内件不可见，依据催化蒸馏专利文献整理；现场确认塔体分段与外接回路接管。", 12, "#666"))
p.append("</svg>")
open(os.path.join(FIG, "struct_catdist.svg"), "w", encoding="utf-8").write("".join(p))

# ---------------- 结构3 管壳式换热器(重沸器) ----------------
W, H = 640, 460
p = [HEAD.format(w=W, h=H)]
p.append(txt(20, 30, "图5  管壳式换热器/重沸器 结构示意（简化·非比例）", 15))
p.append('<rect x="120" y="140" width="400" height="140" fill="#fff" stroke="#111" stroke-width="1.6"/>')
for xx in (160, 220, 280, 340, 400, 460):
    p.append(f'<line x1="{xx}" y1="150" x2="{xx}" y2="270" stroke="#111" stroke-width="1"/>')
p.append(txt(320, 215, "管束", 13))
for xx in (190, 250, 310, 370, 430):
    p.append(f'<line x1="{xx}" y1="150" x2="{xx}" y2="270" stroke="#999" stroke-width="1" stroke-dasharray="4,3"/>')
p.append(txt(320, 240, "折流板(引导壳程横向冲刷)", 11, "#666"))
p.append('<line x1="120" y1="140" x2="120" y2="280" stroke="#111" stroke-width="2.4"/>')
p.append('<line x1="520" y1="140" x2="520" y2="280" stroke="#111" stroke-width="2.4"/>')
p.append(txt(90, 130, "管板"))
p.append(txt(530, 130, "管板"))
p.append(arr(60, 210, 120, 210))
p.append(txt(30, 200, "管程进口(蒸汽)"))
p.append(arr(120, 250, 60, 250))
p.append(txt(30, 270, "管程出口(凝水)"))
p.append(arr(320, 320, 320, 280))
p.append(txt(330, 330, "壳程进口(塔底物料)"))
p.append(arr(320, 140, 320, 90))
p.append(txt(330, 85, "壳程出口(汽液返回塔)"))
p.append(txt(30, 400, "现场记录 E-3513 介质标签: 管程蒸汽/壳程萃取水，与本典型结构一致。", 12, "#666"))
p.append(txt(30, 425, "管束/折流板内件不可见，依据化工原理换热器章节整理。", 12, "#666"))
p.append("</svg>")
open(os.path.join(FIG, "struct_hx.svg"), "w", encoding="utf-8").write("".join(p))

print("[ok] wrote flow_block.svg, struct_reactor.svg, struct_catdist.svg, struct_hx.svg")
