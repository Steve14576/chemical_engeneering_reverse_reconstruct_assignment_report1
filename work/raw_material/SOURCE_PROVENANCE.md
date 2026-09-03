# SOURCE_PROVENANCE — 冻结源与处理声明

本文件是 raw_material 数据源 provenance 的唯一落点。目的：冻结现场原始记录，并声明对其做过的 / 将做的任何处理。

## 冻结源（immutable）

| 文件 | SHA256 | 冻结日期 |
|---|---|---|
| imperfectmapping_person1.jpg | dca46e3161f80f5ab3698ce2e06dfdbe04ea3ac505da1ac81d50461bd9c54dc5 | 2026-09-03 |
| imperfectmapping_person2.drawio | 3cf04c0b7a1dc28a8f45f5f422e02b6c111e3592da0b8dd5c45cb9459f5e9d3a | 2026-09-03 |
| terriblemapping_person1.drawio | 5479f6bb6bde37f5055bc64bb53f5638cac2e6797d20ebcd037f468f497362bb | 2026-09-04 |

### 冻结源补充说明

- `terriblemapping_person1.drawio` = user 于 2026-09-04 **重画的 person1**（drawio）。user 声明全图无向；解析以 `--all-undirected` 源级覆盖（个别边漏写 endArrow=none）。命名沿用旧前缀 terriblemapping，系 user 选择，不改名。
- `terriblemapping_person2.drawio` = 与冻结版 `imperfectmapping_person2.drawio` **内容等价**的重复存档（仅 mxGraphModel dx/dy 视图偏移不同：1563/1089 vs 1544/1041）。**非独立源**，不参与任何下游；建议移 personal/trash（待 user 同意）。
- `imperfectmapping_person1.jpg` 仍为 person1 的现场原始记录；`terriblemapping_person1.drawio` 是其重画数字化，二者关系见衍生物登记第 6 条。

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
4. **衍生物 `work/derived/person1_redraw.normalized.yaml`（L1, 机械）**
   - 生成方式：`normalize_drawio.py --all-undirected` 对冻结的 `terriblemapping_person1.drawio` 机械解析。
   - 摘要：nodes=16（12 标签 + 4 unlabeled 空框）、edges=13 全无向、media_labels=0；missing=[C4]（"C4" 不合位号正则，原样保留为 missing，不脑补位号）；无 duplicate / mismatch / unknown_marker。
   - 无向语义：user 声明全图无向，方向一律待 L3 枚举；src/dst 顺序不携带方向信息。
5. **脚本泛化（2026-09-04）**：`normalize_drawio.py`（参数化：--raw/--sha/--out/--source-id/--all-undirected）取代 `normalize_person2.py`（后者标 SUPERSEDED 暂留不删）。`person2.normalized.yaml` 已用新脚本复跑：节点/边/判定摘要与旧版一致（45/29/6；duplicate=[P-3505,T-3501A]；mismatch=[E-3502,T-3512,T-3509,V-3503,T-3508]；unknown_marker=5），仅 schema 扩展——边加 `directed` 字段、度数改为 `{incident, dir_in, dir_out}`、source 加 `level`/`edge_semantics`。
6. **person1 两版 L1 的关系**：`person1.normalized.yaml`（photo 断言版）保留作对照/历史；`person1_redraw.normalized.yaml` 为 person1 的**新 L1 输入**。二者在 300 系中段实质分歧（E-301/E-302/V-301/T-302/E-303 邻接关系互斥），且 redraw 丢弃了 photo-L1 的 U1/U2/U4 候选。**分歧不裁决**，进 L2 冲突集 + L3 枚举。
7. **衍生物 `work/derived/observations.merged.yaml`（L2）**
   - 生成方式：`merge_observations.py` 机械合并 person1_redraw + person2 两份 L1。
   - 政策：tag 精确对齐；重号/缺号/未标注源内限定；**缺席≠冲突**（person2 的 300 系 degree=0 是没画不是反对）；假设只登记不裁决；photo 断言版排除（仅作对照）。
   - 摘要：entities=52、edges=40（**corroborated=0**、single=40）、dangles=2、dup_groups=[P-3505, T-3501A]、direction_vars=12、functional_vars=5。
   - **重要事实**：两源在"边"层面零重叠（corroborated=0），重叠仅在节点 tag——两人各自记录了互不相交的连线集合。交叉验证在边层面为空集，合并实为并集+节点对齐；此即测绘缺陷证据之一，进报告"测绘问题分析"。
8. **衍生物 `work/derived/solver_result_P0.yaml` / `solver_result_P0h.yaml`（L3）**
   - 求解器：`solve_topology.py` v2，**纯 Python 全枚举**（外层 128 假设世界 × 内层悬空附着全枚举）。**CP-SAT/ortools 弃用**：本环境 ortools 9.15.6755 的 `CpSolver.Solve` 对最小模型即触发 0xC0000005 访问违例（与建模无关），已 `uv remove ortools`。
   - P0 严格：128 世界全 infeasible（reason=degree_deficit）→ **盲逆在闭合公理下不可解**之实证。
   - P0h（`--allow-hidden` 承认漏画）：27648 最优世界；stable=40、ambiguous=0、absent=0；hidden_need min/max/mean = 15/18/16.70（即至少约 17 条未观测边才能闭合度数）。
   - **构造性 caveat**：P0h 把观测边当公理（尚无 drop/fake 变量），故 stable=40/ambiguous=0 **不表示歧义已解决**；不确定性集中于 hidden 边与悬空附着（dangle 附着频率均匀 = P0 对其完全无信息）。显形歧义需 P2（观测边 drop 变量 + 工艺语法候选 hidden 边）。
9. **衍生物 `work/derived/solver_result_P2.yaml`（L3, P2）；W1 于此冻结**
   - 求解器：`solve_topology_p2.py`，MILP via `scipy.optimize.milp` (HiGHS)；观测边 drop 变量（罚 1000）+ 通用精馏/命名语法候选 hidden 边（罚 100，19 条）+ 悬空附着 one-hot + slack（罚 5000）；重号合并外层 4 combo × 整数割枚举 12 解 = 48 解。
   - 结果：观测边 40 条 drop_freq 全 0（观测边彼此自洽）；稳定语法推断 3 条（P-3511—V-3506、P-3501—V-3501、E-3505—T-3512）；歧义簇 3 个（E-3506↔上/下塔 24:24；P-3511 出口 4 选；P-3501 出口 4 选）。
   - **稳定≠可信**：两悬空端附着虽 48/48 稳定，但为度数闭合逼出的跨单元几何 artifact（E-302 悬空线→C4 原料混合罐；蒸汽线端点→E-3508），不采纳为工艺事实，进先验复核清单。
   - W1 冻结结论三层实证：① P0 盲逆 infeasible；② P0h hidden_need 15–18；③ P2 观测自洽 + 稳定骨架 + 3 歧义簇 + 2 可疑附着。歧义簇与可疑附着交 P4 强先验裁决（user 拍板后）。
