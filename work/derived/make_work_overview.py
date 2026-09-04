# -*- coding: utf-8 -*-
"""W4 补图：图6 工作总览（MCM 式 Our Work / 模型架构一图流）。

内容四条泳道：数据与冻结 → 求解梯 P0→P4 → 验证 → 产出；侧栏三块：模型卡 / 背书与局限 / 复现脊。
虚线框 = 计划中（Tier 0.5 能量衡算 + 敏感性 + leave-one-out）。
plain SVG 手写坐标（与框图/结构图同风格）；嵌入 report.md §0 末尾。
登记：work/PROJECT_LEDGER.md §7（D15 扩展）。
"""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)

W, H = 1240, 860
p = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
     '<rect width="%d" height="%d" fill="white"/>' % (W, H),
     '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
     '<path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>']


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, label, fill="#fff", stroke="#111", dash=None, size=12):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    out = ['<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="1.6"%s/>' % (x, y, w, h, fill, stroke, d)]
    segs = label.split("\n")
    ty = y + h / 2 - 7 * (len(segs) - 1)
    for i, s in enumerate(segs):
        out.append('<text x="%s" y="%s" font-size="%s" text-anchor="middle" fill="#111">%s</text>' % (x + w / 2, ty + i * 15, size, esc(s)))
    return "".join(out)


def arr(x1, y1, x2, y2, label=None, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    s = '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#111" stroke-width="1.8"%s marker-end="url(#ar)"/>' % (x1, y1, x2, y2, d)
    if label:
        s += '<text x="%s" y="%s" font-size="11" fill="#666">%s</text>' % ((x1 + x2) / 2 - 30, (y1 + y2) / 2 - 4, label)
    return s


def txt(x, y, s, size=13, color="#111"):
    return '<text x="%s" y="%s" font-size="%s" fill="%s">%s</text>' % (x, y, size, color, esc(s))


p.append(txt(20, 30, "图6  本报告的工作总览与模型架构（Our Work）", 16))

# Lane A 数据与冻结
p.append(txt(20, 70, "① 数据与冻结", 14))
p.append(box(20, 85, 200, 70, "现场记录 ×2\nperson1 照片+重画(无向声明)\nperson2 电子草图 | 1.5h/无图/假管"))
p.append(box(250, 85, 150, 70, "冻结 + SHA256\n处理登记台账\n未登记=未发生"))
p.append(box(430, 85, 170, 70, "L1 机械解析\n节点/边/几何/介质标签\n不裁决不脑补"))
p.append(box(630, 85, 190, 70, "L2 位号对齐合并\n发现: 两人连线零重叠\n重号/缺号/未知 登记为假设"))
p.append(arr(220, 120, 250, 120))
p.append(arr(400, 120, 430, 120))
p.append(arr(600, 120, 630, 120))

# Lane B 求解梯
p.append(txt(20, 200, "② 求解梯（盲逆 → 先验）", 14))
p.append(box(20, 215, 190, 80, "P0 度数闭合公理\n泵一进一出/塔罐≥1管\n128 假设世界全 infeasible"))
p.append(box(240, 215, 180, 80, "P0h +漏画变量\n可行, 但缺 ≈17 条\n未画连线(量化缺口)"))
p.append(box(450, 215, 190, 80, "P2 +drop 变量\n40 观测边全自洽(零丢弃)\n显形 3 处多解歧义簇"))
p.append(box(670, 215, 200, 80, "P4 标准工艺裁决+最小补集\n补 7 条(唯一最小解)\n裁决 3 处 | 共 13 条 prior"))
p.append(arr(210, 255, 240, 255, "加漏画变量"))
p.append(arr(420, 255, 450, 255, "加drop变量"))
p.append(arr(640, 255, 670, 255, "裁决+枚举"))

# Lane C 验证
p.append(txt(20, 340, "③ 验证", 14))
p.append(box(20, 355, 260, 70, "Tier 0 稳态物料衡算\n进=出, 闭合误差 0\nMTBE 2093.6 kg/h @X=0.95"))
p.append(box(320, 355, 300, 70, "Tier 0.5 能量衡算 + 敏感性网格\n+ leave-one-out 拓扑鲁棒性\n[已完成: 1221kW / 9关键边]"))
p.append(arr(280, 390, 320, 390))
p.append(arr(450, 295, 450, 355, "流程定稿后"))

# Lane D 产出
p.append(txt(20, 470, "④ 产出", 14))
p.append(box(20, 485, 220, 70, "流程图/框图/结构图/总览×6\n线型: 实=观测 虚=prior\n点划=公用 ✕=缺陷 ?=未知"))
p.append(box(270, 485, 200, 70, "报告四节正文\n§0 逆向叙事 + 归属标注\n[观测]/[文献n]/[推断]"))
p.append(box(500, 485, 200, 70, "电子附件复现包\n脚本+yaml+图+规则清单\n随作业提交(课程渠道)"))
p.append(arr(150, 425, 130, 485))
p.append(arr(280, 390, 370, 485))

# 侧栏
p.append(box(900, 85, 320, 150, "模型卡\n变量: drop(观测边真假) / attach(悬空端)\nfunctional(假管) / merge(重号同一?)\n约束: 度数闭合 + 端口物理\n目标: min 补画边数\n枚举: 整数割列全部最小解", size=12))
p.append(box(900, 260, 320, 120, "背书分档与局限\n档1 单元惯例 | 档2 工艺序列(前半文献/后半推断)\n档3 内件专利 | 局限六条进报告\n无背书=标推断, 不禁用", size=12))
p.append(box(900, 405, 320, 120, "复现脊\nPROJECT_LEDGER(决策) + DEV_JOURNAL(改主意)\n+ derived/*.yaml(数字 SSOT)\nprivate 期=存证+备份; 成绩后公开", size=12))
p.append(arr(820, 120, 900, 120, dash="6,4"))
p.append(arr(870, 255, 900, 300, dash="6,4"))
p.append(arr(700, 520, 900, 465, dash="6,4"))

p.append(txt(20, 600, "读法: ①→② 是'从两张不准的手绘图到一张自洽流程图'的主线; ②→③ 是'流程要过衡算才算数'; ③→④ 是'数字与图进报告';", 12, "#666"))
p.append(txt(20, 620, "侧栏三块贯穿全程: 模型卡定义'算什么', 背书与局限定义'凭什麼/不能说什么', 复现脊定义'怎么查账'。", 12, "#666"))
p.append("</svg>")

open(os.path.join(FIG, "work_overview.svg"), "w", encoding="utf-8").write("".join(p))
print("[ok] wrote work_overview.svg")
