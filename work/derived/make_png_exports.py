# -*- coding: utf-8 -*-
"""W4 导出：六张 SVG → PNG（内联改用 PNG；SVG 原件保留不删）。

工具链：svglib + reportlab.renderPM(rlPyCairo/pycairo)，Windows 轮子可用。
字体后处理（声明式）：cairo 后端默认字体不含中文 → 导出前给每个 <text> 注入
font-family="Microsoft YaHei, SimHei, sans-serif"（仅写入 figures/_pngsrc/ 临时副本，
SVG 原件不改）。pyflowsheet 产出的 flow_main.svg 同样经此注入。
已知取舍：svglib 不渲染 marker 箭头（箭头本就声明为"仅排版、非方向主张"）；
          个别 dasharray 在 PNG 里可能变实线，以 SVG 原件为准。
dpi=150。登记：work/PROJECT_LEDGER.md §7（D15 扩展）、DEV_JOURNAL J22。
"""
from __future__ import annotations

import os
import re

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
TMP = os.path.join(FIG, "_pngsrc")
FAMILY = "Microsoft YaHei"  # 单一 family：三名回退链疑似触发逐文本全系统字体扫描

NAMES = [
    "flow_block.svg",
    "flow_main.svg",
    "struct_reactor.svg",
    "struct_catdist.svg",
    "struct_hx.svg",
    "work_overview.svg",
    "work_overview_plain.svg",
]


def inject_font(svg_text: str) -> str:
    def repl(m):
        tag = m.group(0)
        if "font-family" in tag:
            return tag
        return tag[:-1] + f' font-family="{FAMILY}">'
    return re.sub(r"<text\b[^>]*>", repl, svg_text)


def register_cjk_fonts() -> None:
    """进程启动时一次性注册 CJK 字体文件，避免 rlPyCairo 对每个 <text> 做全系统字体扫描（会慢到分钟级）。"""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    cands = [
        ("Microsoft YaHei", r"C:\Windows\Fonts\msyh.ttc", 0),
        ("SimHei", r"C:\Windows\Fonts\simhei.ttf", None),
    ]
    for fam, path, idx in cands:
        try:
            if idx is None:
                pdfmetrics.registerFont(TTFont(fam, path))
            else:
                pdfmetrics.registerFont(TTFont(fam, path, subfontIndex=idx))
            print(f"[font] registered {fam} from {path}")
        except Exception as e:  # noqa: BLE001
            print(f"[font] skip {fam}: {e}")


def main() -> int:
    import sys
    import time
    only = sys.argv[1] if len(sys.argv) > 1 else None
    register_cjk_fonts()
    os.makedirs(TMP, exist_ok=True)
    for name in NAMES:
        if only and only not in name:
            continue
        t0 = time.perf_counter()
        src = os.path.join(FIG, name)
        tmp = os.path.join(TMP, name)
        dst = os.path.join(FIG, name.replace(".svg", ".png"))
        with open(src, encoding="utf-8") as f:
            raw = f.read()
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(inject_font(raw))
        drawing = svg2rlg(tmp)
        if drawing is None:
            print(f"[fail] {name}: svg2rlg returned None")
            continue
        renderPM.drawToFile(drawing, dst, fmt="PNG", dpi=150)
        print(f"[ok] {name} -> {os.path.basename(dst)} ({os.path.getsize(dst)} bytes) {time.perf_counter()-t0:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
