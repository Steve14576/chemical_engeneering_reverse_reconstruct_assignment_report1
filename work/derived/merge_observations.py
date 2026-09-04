# -*- coding: utf-8 -*-
"""L2 跨源对账合并：person1_redraw + person2 两份 L1 → observations.merged.yaml。

性质声明（机械合并，不裁决）：
  - 实体对齐仅按 **tag 精确匹配**；重号/缺号/未标注/未知标记一律源内限定 key，不跨源强行合并；
  - 边按实体对归并，逐源保留方向主张；两源都主张 = corroborated，单源 = single；
    **缺席不等于冲突**（person2 的 300 系 degree=0 是没画，不是反对）；
  - 重名三假设（H_same/H_segment/H_distinct）、functional 变量、candidate_align 只**登记为假设**，
    交由 L3 枚举，本脚本不预选、不修改任何 L1；
  - person1 photo 断言版不参与合并（已被 redraw 取代为 person1 的声音），其分歧见 work/PROJECT_LEDGER.md §7（D2/D3）与 §6。
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
P1R = ROOT / "work/derived/person1_redraw.normalized.yaml"
P2 = ROOT / "work/derived/person2.normalized.yaml"
OUT = ROOT / "work/derived/observations.merged.yaml"


def load(p: Path) -> dict:
    with p.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def entity_key(src: str, n: dict, dup_tags: set[str]) -> str:
    tag = n.get("tag")
    if tag and n.get("tag_status") == "ok":
        return tag
    if tag and n.get("tag_status") == "duplicate":
        return f"{src}::{n['cell_id']}"  # 重号：源内限定，交 L3 三假设
    return f"{src}::{n['cell_id']}"


def main() -> int:
    p1r, p2 = load(P1R), load(P2)

    entities: dict[str, dict] = {}
    dup_groups: dict[str, list[str]] = {}

    for src, doc in (("p1r", p1r), ("p2", p2)):
        tags = [n["tag"] for n in doc["nodes"] if n.get("tag")]
        dup_tags = {t for t in tags if tags.count(t) > 1}
        for n in doc["nodes"]:
            key = entity_key(src, n, dup_tags)
            e = entities.setdefault(key, {
                "id": key, "alias_tags": [], "shape_class": "unknown",
                "name_zh": None, "sources": [], "geom": {}, "tag_status": n.get("tag_status"),
            })
            if n.get("tag"):
                if n["tag"] not in e["alias_tags"]:
                    e["alias_tags"].append(n["tag"])
                if n["tag_status"] == "duplicate":
                    dup_groups.setdefault(n["tag"], []).append(key)
            if n.get("name_zh"):
                e["name_zh"] = n["name_zh"]
            if n.get("shape_class") and e["shape_class"] == "unknown":
                e["shape_class"] = n["shape_class"]
            if src not in e["sources"]:
                e["sources"].append(src)
            e["geom"][src] = n.get("geom")

    # 边归并
    merged_edges: dict[str, dict] = {}
    dangles: list[dict] = []
    for src, doc in (("p1r", p1r), ("p2", p2)):
        key_of = {n["cell_id"]: entity_key(src, n, {t for t in [x.get("tag") for x in doc["nodes"] if x.get("tag")] if [x.get("tag") for x in doc["nodes"]].count(t) > 1}) for n in doc["nodes"]}
        for e in doc["edges"]:
            a = key_of.get(e["src_cell"]) if e["src_cell"] else None
            b = key_of.get(e["dst_cell"]) if e["dst_cell"] else None
            if a is None or b is None:
                dangles.append({
                    "source": src, "cell_id": e["cell_id"],
                    "anchored": a or b, "directed_claim": e.get("directed"),
                    "media_label": e.get("media_label"),
                })
                continue
            pair = tuple(sorted((a, b)))
            eid = "E::" + pair[0] + "::" + pair[1]
            m = merged_edges.setdefault(eid, {
                "id": eid, "a": pair[0], "b": pair[1], "claims": [],
            })
            m["claims"].append({
                "source": src, "from": e["src_cell"] and a, "to": e["dst_cell"] and b,
                "directed": e.get("directed"), "media_label": e.get("media_label"),
            })
    for m in merged_edges.values():
        srcs = {c["source"] for c in m["claims"]}
        m["support"] = "corroborated" if len(srcs) >= 2 else "single"
        m["undirected_any"] = any(c["directed"] is False for c in m["claims"])

    # 假设登记（不预选）
    hypotheses = {
        "duplicate_identity": [
            {"tag": t, "members": ms,
             "hypotheses": ["H_same", "H_segment", "H_distinct_misnomer"]}
            for t, ms in sorted(dup_groups.items())
        ],
        "direction": [
            {"edge": m["id"], "domain": "enumerate",
             "claims": [c["source"] for c in m["claims"] if c["directed"]]}
            for m in merged_edges.values() if m["undirected_any"] or not any(c["directed"] for c in m["claims"])
        ],
        "functional": [
            {"entity": k, "reason": "unknown_marker/断管/胶布/悬空，是否功能管待枚举"}
            for k, e in entities.items()
            if e["tag_status"] == "unknown_marker"
        ],
        "candidate_align": [
            {"a": "p1r::kW8mp5fpktJNJ6bN1REy-14", "b": "p2::5D5qHUWBTGfa0SRdJl68-5",
             "note": "person1 的 C4 ↔ person2 未标号 C4原料混合罐；候选对齐，不强制"},
        ],
    }

    doc_out = {
        "meta": {
            "level": "L2",
            "inputs": ["work/derived/person1_redraw.normalized.yaml", "work/derived/person2.normalized.yaml"],
            "merge_script": "work/derived/merge_observations.py",
            "policy": "tag 精确对齐；重号/缺号/未标注源内限定；缺席≠冲突；假设只登记不裁决",
            "excluded": ["person1.normalized.yaml (photo 断言版, 已被 redraw 取代, 仅作对照)"],
        },
        "entities": [entities[k] for k in entities],
        "edges": [merged_edges[k] for k in merged_edges],
        "dangles": dangles,
        "hypotheses": hypotheses,
    }
    with OUT.open("w", encoding="utf-8") as f:
        yaml.safe_dump(doc_out, f, allow_unicode=True, sort_keys=False)

    corr = sum(1 for m in merged_edges.values() if m["support"] == "corroborated")
    print(f"[ok] wrote {OUT.relative_to(ROOT)}")
    print(f"  entities={len(entities)} edges={len(merged_edges)} (corroborated={corr}, single={len(merged_edges)-corr})")
    print(f"  dangles={len(dangles)} dup_groups={sorted(dup_groups)}")
    print(f"  direction_vars={len(hypotheses['direction'])} functional_vars={len(hypotheses['functional'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
