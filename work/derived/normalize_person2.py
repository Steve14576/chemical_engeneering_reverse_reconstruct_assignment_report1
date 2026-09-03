# -*- coding: utf-8 -*-
"""person2 冻结 drawio 的机械归一化（mechanical normalize）。

性质声明：本脚本只做**机械**转换，不含任何工艺解释 / 脑补：
  - 先校验冻结源 SHA256，不一致即 abort（防漂移）；
  - 从 mxCell 原样抽取 节点 / 边 / 边介质标签 / 几何；
  - 位号状态（ok / duplicate / missing / unknown_marker）与
    "位号字母 vs 名字关键词" 的不一致，均按**字符串规则**机械判定，
    不人工裁决、不修改源；
  - 中文功能名与介质标签原样保留，仅作为字段携带（Stage-2 先验用），
    本脚本不据其改写任何拓扑。
衍生物：work/derived/person2.normalized.yaml（处理方式登记见 SOURCE_PROVENANCE.md）。
"""
from __future__ import annotations

import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "work" / "raw_material" / "imperfectmapping_person2.drawio"
OUT = ROOT / "work" / "derived" / "person2.normalized.yaml"
EXPECTED_SHA = "3cf04c0b7a1dc28a8f45f5f422e02b6c111e3592da0b8dd5c45cb9459f5e9d3a"  # 小写惯例

# 位号形如 E-302 / T-3501A / V-402 / P-3505 / FV301
TAG_RE = re.compile(r"^[A-Z]{1,2}-?[0-9]{3,4}[A-Z]?$")
# 现场未知标记（person2 自标），机械识别为 unknown_marker
UNKNOWN_SET = {"断了？", "某黑盒管线", "放空？", "某管道汇合"}
# 名字关键词 -> 名字所暗示的位号字母。
# 规则：关键词必须出现在名字**结尾**才算“自身类型”（避免“催化塔下塔进料器”里的“塔”被误认为自身是塔）；
# 多个结尾匹配时取最长者。
NAME_KW = [
    ("反应器", "R"), ("换热器", "E"), ("冷却器", "E"), ("冷凝器", "E"),
    ("再沸器", "E"), ("重沸器", "E"), ("加热器", "E"), ("加热釜", "E"),
    ("泵", "P"), ("塔", "T"), ("罐", "V"),
]
LETTER_SHAPE = {
    "T": "column", "E": "exchanger", "V": "vessel",
    "P": "pump", "R": "reactor", "F": "furnace", "C": "compressor",
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def split_value(v: str | None) -> tuple[str, str | None]:
    """'E-302<div>解吸塔冷凝器</div>' -> ('E-302', '解吸塔冷凝器')；无 div 则 name=None。"""
    if not v:
        return "", None
    parts = v.split("<div>")
    head = parts[0].strip()
    if len(parts) == 1:
        return head, None
    name = re.sub(r"<[^>]+>", " ", "<div>".join(parts[1:]))
    name = re.sub(r"\s+", " ", name).strip()
    return head, (name or None)


def name_implied_letter(name: str | None) -> str | None:
    if not name:
        return None
    best = None
    for kw, letter in NAME_KW:
        if name.endswith(kw) and (best is None or len(kw) > len(best[0])):
            best = (kw, letter)
    return best[1] if best else None


def main() -> int:
    actual = sha256(RAW)
    if actual != EXPECTED_SHA:
        print(f"[abort] sha256 mismatch:\n  expect {EXPECTED_SHA}\n  actual {actual}", file=sys.stderr)
        return 1

    root = ET.parse(RAW).getroot()
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    edge_media: dict[str, str] = {}

    for c in root.iter("mxCell"):
        cid = c.get("id")
        style = c.get("style") or ""
        val = c.get("value")
        geom = c.find("mxGeometry")

        # 边上的介质标签（connectable=0 且 style 含 edgeLabel，parent 指向边）
        if c.get("connectable") == "0" and "edgeLabel" in style:
            if val:
                edge_media[c.get("parent")] = val
            continue

        if c.get("vertex") == "1":
            head, name = split_value(val)
            g = {}
            if geom is not None:
                g = {
                    k: (float(geom.get(k)) if geom.get(k) is not None else None)
                    for k in ("x", "y", "width", "height")
                }
            nodes[cid] = {"cell_id": cid, "raw_head": head, "name_zh": name, "geom": g}
        elif c.get("edge") == "1":
            src, dst = c.get("source"), c.get("target")
            waypoints = []
            if geom is not None:
                arr = geom.find("Array")
                if arr is not None:
                    waypoints = [
                        {"x": float(p.get("x")), "y": float(p.get("y"))}
                        for p in arr.findall("mxPoint")
                    ]
                if src is None and geom.find("mxPoint[@as='sourcePoint']") is not None:
                    src = None  # 仅有游离 sourcePoint，无锚定节点
                if dst is None and geom.find("mxPoint[@as='targetPoint']") is not None:
                    dst = None  # 仅有游离 targetPoint，无锚定节点
            edges.append({
                "cell_id": cid, "src_cell": src, "dst_cell": dst,
                "media_label": None, "waypoints": waypoints,
            })

    # 位号状态（机械判定）
    tag_count: dict[str, int] = {}
    for n in nodes.values():
        head = n["raw_head"]
        if head in UNKNOWN_SET:
            n["tag"], n["tag_status"] = None, "unknown_marker"
        elif TAG_RE.match(head):
            n["tag"], n["tag_status"] = head, "ok"
        else:
            n["tag"], n["tag_status"] = None, "missing"
        if n["tag"]:
            tag_count[n["tag"]] = tag_count.get(n["tag"], 0) + 1
    for n in nodes.values():
        if n["tag"] and tag_count[n["tag"]] > 1:
            n["tag_status"] = "duplicate"

    # 位号字母 vs 名字关键词 的不一致（机械判定，不裁决）
    for n in nodes.values():
        n["prefix_type_mismatch"] = None
        letter = re.match(r"([A-Z]{1,2})", n["tag"]).group(1) if n["tag"] else None
        implied = name_implied_letter(n["name_zh"])
        if letter and implied and letter != implied:
            n["prefix_type_mismatch"] = {"tag_letter": letter, "name_implies": implied}
        n["shape_class"] = LETTER_SHAPE.get(letter, "unknown") if letter else "unknown"

    # 边介质标签回填 + 端点解析为 tag + 度数
    cell_tag = {cid: n["tag"] for cid, n in nodes.items()}
    degree = {cid: {"in": 0, "out": 0} for cid in nodes}
    for e in edges:
        e["media_label"] = edge_media.get(e["cell_id"])
        e["src_tag"] = cell_tag.get(e["src_cell"]) if e["src_cell"] else None
        e["dst_tag"] = cell_tag.get(e["dst_cell"]) if e["dst_cell"] else None
        if e["src_cell"] in degree:
            degree[e["src_cell"]]["out"] += 1
        if e["dst_cell"] in degree:
            degree[e["dst_cell"]]["in"] += 1
    for n in nodes.values():
        n["degree"] = degree[n["cell_id"]]

    doc = {
        "source": {
            "id": "person2",
            "raw_file": "work/raw_material/imperfectmapping_person2.drawio",
            "raw_sha256": EXPECTED_SHA,
            "transform": "mechanical_xml_parse",
            "transform_script": "work/derived/normalize_person2.py",
            "fidelity": "lossless_for_drawio_content",
            "note": "中文功能名/介质标签原样携带，仅作 Stage-2 先验，不参与本步拓扑判定",
        },
        "nodes": [nodes[cid] for cid in nodes],
        "edges": edges,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)

    dup = sorted(t for t, c in tag_count.items() if c > 1)
    mismatch = [n["tag"] or n["raw_head"] for n in nodes.values() if n["prefix_type_mismatch"]]
    missing = [n["raw_head"] for n in nodes.values() if n["tag_status"] == "missing"]
    unknown = [n["raw_head"] for n in nodes.values() if n["tag_status"] == "unknown_marker"]
    print(f"[ok] wrote {OUT.relative_to(ROOT)}")
    print(f"  nodes={len(nodes)} edges={len(edges)} media_labels={len(edge_media)}")
    print(f"  duplicate_tags={dup}")
    print(f"  prefix_type_mismatch={mismatch}")
    print(f"  missing_tag={missing}")
    print(f"  unknown_marker={unknown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
