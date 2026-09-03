# SOURCE_PROVENANCE — 冻结源与处理声明

本文件是 raw_material 数据源 provenance 的唯一落点。目的：冻结现场原始记录，并声明对其做过的 / 将做的任何处理。

## 冻结源（immutable）

| 文件 | SHA256 | 冻结日期 |
|---|---|---|
| imperfectmapping_person1.jpg | dca46e3161f80f5ab3698ce2e06dfdbe04ea3ac505da1ac81d50461bd9c54dc5 | 2026-09-03 |
| imperfectmapping_person2.drawio | 3cf04c0b7a1dc28a8f45f5f422e02b6c111e3592da0b8dd5c45cb9459f5e9d3a | 2026-09-03 |

##  standing rule

- 上表两文件为**现场原始记录**，冻结后不再修改。
- 任何下游使用（解析、转格式、对账、求解、出图）前，先重算 SHA256 与本表比对，检测意外漂移。
- 对源或其衍生物的**任何处理**都必须：① 在本文件登记；② 在下游产物（对账表 / 报告方法节）中明说。未登记 = 未发生。

## 层级（tier）约定

- **L0** = raw 冻结源（imperfectmapping_person1.jpg / _person2.drawio）。
- **L1** = 基于源的数字化/转录（person1.normalized.yaml、person2.normalized.yaml）。
- **L2** = 跨源对账合并（observations.merged，待建）。
- **L3** = 求解器输出（候选拓扑 / 边稳定性，待建）。
- **L4** = 报告图与正文（待建）。

每层只可由上一层生成，生成方式登记在本文件。

## 冻结前编辑日志（pre-freeze, 已声明）

操作者：user（person2 本人）。agent 对源文件零改动。

1. 文件改名：`terriblemapping_person1.jpg / _person2.drawio` → `imperfectmapping_person1.jpg / _person2.drawio`。
2. 仅修 A 类纯错别字（不改变拓扑/位号/连接），共 6 处，均在 person2.drawio：
   - `E302` → `E-302`（补连字符）
   - `醚后C4键` → `醚后C4罐`
   - `某管道会和` → `某管道汇合`
   - `MBTE` → `MTBE`（×3：E-3508、E-3505、T-3512 的名称内）

## 保留未改的已知异常（by decision, 不修）

位号-类型不符、重号（T-3501A×2、P-3505×2）、缺位号、同名不同号、配对不齐、未知标记（断了？/某黑盒管线/放空？/某管道汇合）、跨人缺口（person1 独有 T-301/V-302）等，**一律保留原样**，作为观测不确定性的一部分进入对账表编码为 ambiguous / candidate / unknown，不在源上擅自"修正"。明细见对账表（待建）。

## 衍生物与处理登记（post-freeze）

1. **SHA256 大小写归一（case-only）**：本表与下游统一用小写十六进制。操作者：agent。原因：`Get-FileHash` 输出大写、`hashlib` 输出小写；哈希值本身不变。
2. **衍生物 `work/derived/person2.normalized.yaml`**
   - 生成方式：`work/derived/normalize_person2.py`，`mechanical_xml_parse`（无工艺解释、无脑补）。
   - 脚本先校验 raw sha256（小写）再解析，不一致即 abort。
   - 机械判定规则（全部为字符串/结构规则，不人工裁决、不回改源）：
     - 位号识别 `TAG_RE`；未知标记集合 `UNKNOWN_SET={断了？, 某黑盒管线, 放空？, 某管道汇合}` → `unknown_marker`；无位号 → `missing`；同位号多次 → `duplicate`。
     - 位号字母 vs 名字自身类型：名字**以关键词结尾**才计（反应器R/换热器E/冷却器E/冷凝器E/再沸器E/重沸器E/加热器E/加热釜E/泵P/塔T/罐V），取最长结尾匹配；不一致 → `prefix_type_mismatch`（仅标记不修改）。
     - `shape_class` 由位号字母机械映射；几何 (x,y,w,h) 与边 waypoints 转 float 作空间 hint。
   - 中文功能名 / 边介质标签原样携带，仅作 Stage-2 先验，不参与本步拓扑判定。
   - 本次运行摘要：nodes=45, edges=29, media_labels=6；duplicate=[P-3505, T-3501A]；prefix_type_mismatch=[E-3502, T-3512, T-3509, V-3503, T-3508]；missing=2；unknown_marker=5。
   - **保真度说明**：person2 源中 300 系节点（E-302/E-301/T-302/V-301/E-303 等）degree 全为 0，是源本就没有画连线，**非解析丢失**。
   - 脚本规则迭代（均机械、已复跑验证）：① 补关键词"重沸器"；② 关键词改为"结尾匹配"（消除"催化塔下塔进料器"中"塔"指代目标塔造成的假阳性）；③ geom/waypoints cast 为 float。
3. **衍生物 `work/derived/person1.normalized.yaml`（L1, user 断言版）**
   - 生成方式：agent 目视 jpg 转录 + **user 对模糊处直接断言**；`transform: user_asserted_digitization`；断言责任在 user。
   - 断言政策（user 拍板 2026-09-03）：不做逐条置信度 / 不留活路，模糊处直接断言；真正追不到的（端点不可见/涂鸦/未画）仍留 unknowns 不伪造；未标注闭合形状仍不立为节点。
   - 交叉验证注意：本 L1 含 user 断言；person1-vs-person2 交叉验证时，断言项视为 user 判断而非 person1 独立观测。
   - 保真度：low_to_medium。person1 未画 3500 系其余设备；300 系多数连线追不实。
