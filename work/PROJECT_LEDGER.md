# PROJECT_LEDGER — 认识实习报告项目 唯一台账

> **合并说明**：本文件于 2026-09-04 由 `work/raw_material/SOURCE_PROVENANCE.md`（机器登记版）与 `work/derived/PROCESS_LEDGER.md`（叙述版）合并而成（user 要求"文档放一起、别追编号"）。此后项目内**只有这一份台账**；方法论补课卡片在 `personal/QnAnExperience.md`（Q2），其出处只指向本文件章节。
> **编号约定（全文件唯一，不跨文件追号）**：§1–§9 章节；D1–D9 衍生物登记；C1–C3 必须写进报告的 caveat；A1–A6 先验裁决项。
> **数值原件**：`work/derived/solver_result_*.yaml`、`work/derived/observations.merged.yaml`（本台账只解读，不复制数字以外的结论）。

## §1 任务与现场约束

- 交付物：认识实习报告，**手写 ≥5000 字**；工作流为 md 起草→迭代→单向手抄。四节：①实习目的；②实习内容（工艺原理/原料来源/产品指标/操作规程；流程概要+框图+流程图；≥3 张典型单元设备结构图）；③收获体会+安全生产+对学校建议。
- 现场：某 MTBE（甲基叔丁基醚）实训装置，双层、楼梯陡、二楼窄、人多；存在假管/悬空管/断管/胶布缠管，意图不明；**无图纸**；观察窗口 1.5 小时后清场；教师只讲大致原理、不让问。
- 小组原 3 人，1 人退出，现余 person1 与 person2（=user）。person3 片段缺失。
- deadline：自 2026-09-04 起约 34 小时。

## §2 数据源与冻结（L0）

### §2.1 冻结源表

| 文件 | SHA256（小写） | 冻结日期 |
|---|---|---|
| work/raw_material/imperfectmapping_person1.jpg | dca46e3161f80f5ab3698ce2e06dfdbe04ea3ac505da1ac81d50461bd9c54dc5 | 2026-09-03 |
| work/raw_material/imperfectmapping_person2.drawio | 3cf04c0b7a1dc28a8f45f5f422e02b6c111e3592da0b8dd5c45cb9459f5e9d3a | 2026-09-03 |
| work/raw_material/terriblemapping_person1.drawio | 5479f6bb6bde37f5055bc64bb53f5638cac2e6797d20ebcd037f468f497362bb | 2026-09-04 |

### §2.2 冻结源补充说明

- `terriblemapping_person1.drawio` = user 于 2026-09-04 **重画的 person1**（drawio）。user 声明全图无向；解析以 `--all-undirected` 源级覆盖（个别边漏写 endArrow=none），覆盖行为已登记（D3）。命名沿用旧前缀 terriblemapping，系 user 选择，不改名。
- `terriblemapping_person2.drawio`（原 work/raw_material/）= 与冻结版 `imperfectmapping_person2.drawio` **内容等价**的重复存档（仅 mxGraphModel dx/dy 视图偏移不同：1563/1089 vs 1544/1041）。**非独立源**；2026-09-04 经 user 同意移至 `personal/trash/terriblemapping_person2.drawio`。
- `imperfectmapping_person1.jpg` 仍为 person1 的现场原始记录；`terriblemapping_person1.drawio` 是其重画数字化，二者关系见 D2/D3。

### §2.3 standing rule

- 上表文件为**现场原始记录**，冻结后不再修改。
- 任何下游使用（解析、转格式、对账、求解、出图）前，先重算 SHA256 与本表比对，检测意外漂移。
- 对源或其衍生物的**任何处理**都必须：① 在本文件登记（§7 / §2.4）；② 在下游产物中明说。未登记 = 未发生。

### §2.4 冻结前/冻结后编辑日志（case 与错别字等）

- 操作者 user（pre-freeze）：文件改名 terriblemapping_* → imperfectmapping_*（person1.jpg / person2.drawio）；仅修 6 处 A 类纯错别字（不改变拓扑/位号/连接）：`E302`→`E-302`、`醚后C4键`→`醚后C4罐`、`某管道会和`→`某管道汇合`、`MBTE`→`MTBE`×3。
- 操作者 agent：SHA256 大小写归一（case-only；Get-FileHash 大写、hashlib 小写，值不变），本表与下游统一小写。
- B–G 类不一致（位号-类型不符、重号、缺号、同名、配对不齐、未知标记）**一律保留原样**进模型当不确定性，不在源上擅自"修正"。

## §3 层级约定（tier）

L0 raw 冻结源 → L1 数字化/转录（normalized yaml）→ L2 跨源对账合并（observations.merged）→ L3 求解（solver_result_*）→ L4 报告图与正文。每层只由上一层生成，生成方式登记于 §7。

## §4 决策日志（日期 + 原因）

### 2026-09-03
- **路线拍板：约束求解硬刚 + 两段式（盲逆→先验）**。原因：user 要求"先盲逆看是否可解，再引入标准 MTBE 先验"，使"逆向方法本身"可被实证检验（做得出=方法可靠；做不出=证明观测不足后才查先验），而非直接抄答案。
- **盲边界定义**：盲=禁用 MTBE 特有序列/介质归属/功能名；允许=tag、外形类别、观测连通、断管/胶布/悬空痕迹、通用端口物理。原因：否则"盲逆成功"是过度宣称。
- **person1 断言制**：不做逐条置信度留活路，模糊处 user 直接断言、责任在 user；但真追不到的（端点不可见/涂鸦/未画）仍留 unknown **不伪造**。原因：逐条 hedging 成本过高做不完；伪造不可接受。
- **源尊重 + 处理明说 + 冻结**：见 §2.3。
- **统一格式 = YAML 每源一份**（work/derived/）。原因：JSON 无注释、CSV/md 表格装不下嵌套与逐条元数据。
- **交付策略**：纸自包含（打印附录：原始草图+干净图+关键表）；github 仅作 grading 后补充仓。原因：老师不点链接；grading 前公开有学术诚信风险；public=永久。
- **全任务地图 W1–W5** 与 **W2 Tier 0 手写衡算必做最先**、**强先验 fallback 为计划内分支**。原因：逆向只是报告一小块；②.1/②.3/④ 不依赖 W1。
- **穷举不裁决哲学**：无向边→方向变量；重号→H_same/H_segment/H_distinct 三假设全枚举；假管→functional 变量；漏画→候选补边；能都试就都试，不擅自定论。

### 2026-09-04
- person1 redraw 入冻（§2.1）；无向声明以 `--all-undirected` 源级覆盖落实（D3）。
- stray person2 判定非源（§2.2）。
- normalize 脚本泛化为 `normalize_drawio.py`；旧 `normalize_person2.py` 标 SUPERSEDED 暂留（D8）。
- L2 政策：tag 精确对齐；重号/缺号/未标注源内限定；**缺席≠冲突**；假设只登记不裁决；photo 断言版排除（对照）。
- **ortools 弃用**：本环境 ortools 9.15.6755 的 `CpSolver.Solve` 对最小模型即 0xC0000005 访问违例（与建模无关）→ L3 改纯 Python 全枚举（P0/P0h），P2 改 MILP via `scipy.optimize.milp` (HiGHS)。
- **W1 冻结于 P2**：不再加深；歧义簇与可疑附着交 P4 强先验裁决（§6）。
- P4 先验裁决清单 A1–A6 提出，**待 user 拍板**（§6）。
- 台账合并：SOURCE_PROVENANCE + PROCESS_LEDGER → 本文件（§9）。
- **P4 拍板（user）**：A1–A3 行；A4/A6 按 agent 理解；A5 = 最小必需补集且"补也试出来"（枚举最小补集 + W2 衡算检验，禁止最乐观补全）；白名单未补充（维持 6 处错别字）；stray 重复文件移 trash。裁决数据落 D10。
- **先验背书检索（2026-09-04，WebSearch 两轮）**：档2 前半（醚化+催化蒸馏）与档3 催化蒸馏内件命中（摘要级 URL 见 D11）；**档2 后半（甲醇萃取+甲醇回收序列）未直接命中 → 降级"档2-弱·行业通用配置·推断"，已告知 user**；档3 其余内件待收（速通手册优先）。
- **P4 最小补集枚举完成（D12）**：唯一最小补集 7 条；feed drum（C4 原料混合罐）按档1 惯例度数=2 消除 c8/c9 二选一分歧（非乐观补全）。
- **W2 Tier 0 衡算完成（D14）**：闭合 err=0，A5 检验环通过（流程每条流都有去处、质量闭合；只证自洽+量级合理，不证"真"）。转化率取文献摘要级 90–95%，其余假设标 assumed。

## §5 求解梯与结果解读

| 层 | 设定 | 结果 | 解读 |
|---|---|---|---|
| P0 严格 | 盲 + 度数闭合公理，128 假设世界全枚举 | 128/128 infeasible（degree_deficit） | **盲逆在闭合公理下不可解**之实证：观测边不够闭合任何功能拓扑 |
| P0h | 承认漏画（hidden-edge 派生整数） | 27648 最优世界；stable=40、absent=0；hidden_need 15–18（均值 16.7） | 观测边互相自洽；但**至少缺约 17 条未画边**才能闭合。漏画缺口被量化 |
| P2 | 观测边 drop 变量 + 通用精馏/命名语法候选 hidden 边（19 条）+ 悬空附着；4 combo × 整数割 12 解 = 48 解 | 观测边 drop_freq 全 0；稳定语法推断 3 条；歧义簇 3 个 | 观测边彼此自洽（求解器不肯丢任何一条）；语法补出稳定骨架；歧义被精确显形 |

**P2 稳定骨架**：观测 40 条 + P-3511—V-3506、P-3501—V-3501、E-3505—T-3512。
**P2 歧义簇**：① E-3506（催化蒸馏塔重沸器）↔下塔 24 / ↔上塔 24（重号三假设的化身）；② P-3511 出口 4 选（V-3504 16 / T-3508 16 / 甲醇回收塔 12 / V-3502 4）；③ P-3501 出口 4 选（E-3512 16 / T-3502 12 / 甲醇回收塔 12 / E-3513 8）。

**必须写进报告的 caveat**：
- **C1（构造性 stable）**：P0h 的 stable=40/ambiguous=0 是构造性的（该层把观测边当公理、无 drop 变量），不等于歧义已解决。
- **C2（稳定≠可信）**：两悬空端附着虽 48/48 稳定，却是度数闭合逼出的跨单元几何 artifact（E-302 悬空线→C4 原料混合罐；蒸汽线端点→E-3508），不采纳为工艺事实。
- **C3（缺席≠冲突 / corroborated=0）**：两源在边层面零重叠、仅在节点 tag 重叠——两人各自记录了互不相交的连线集合；交叉验证在边层面为空集。此即测绘缺陷证据之一。

## §6 待办 / 未裁决

- **P4 先验裁决（user 拍板 2026-09-04；数据见 D10 `work/derived/prior_decisions_P4.yaml`）**：
  - A1 采纳 E-3506—T-3501B（下塔）；A2 采纳 P-3511—E-3501；A3 采纳 P-3501—E-3501（user：行）。
  - A4 按 agent 理解：E-302 悬空线留 unknown 不连；蒸汽线 = 公用工程进 E-3513 管程、不作工艺边。
  - A5 **最小必需补集**：只补"物料必须有去处"逼出的边；在标准骨架候选内枚举最小补集（与歧义枚举同法），交 W2 Tier 0 衡算检验；可加可不加一律不补；禁止最乐观补全；每条标 prior-driven。
  - A6 按 agent 理解：甲醇回收塔→TMP-MEOHCOL；P-3505→P-3505A（上塔进料泵）/P-3505B（下塔进料器）两台；只改标签不改连线。
  - 依据=教科书级 MTBE 骨架；与观测冲突处以观测为准并进"测绘缺陷分析"。
- ~~stray person2 移 trash~~：已完成（2026-09-04，移至 `personal/trash/terriblemapping_person2.drawio`）。
- L2 白名单：**已关闭**——user 未补充，维持 6 处错别字。
- Aspen license 有无：未知（决定 W2 Tier 2 存不存在）。
- ②.3 三张设备结构图的教材参考：未收。含义 = 每张结构图需可引用出处（书/文献图或描述）；先验背书分四档与无背书处理见 `personal/QnAnExperience.md` Q3。
- person1 photo-L1 与 redraw 的分歧（300 系中段邻接互斥、redraw 丢弃 U1/U2/U4）：不裁决，进缺陷分析。

## §7 衍生物与产物登记

| ID | 路径 | 层 | 生成方式 | 摘要 |
|---|---|---|---|---|
| D1 | work/derived/person2.normalized.yaml | L1 | `normalize_drawio.py` 机械解析冻结 person2 drawio | 45 节点/29 边/6 介质；duplicate=[P-3505,T-3501A]；mismatch=[E-3502,T-3512,T-3509,V-3503,T-3508]；unknown_marker=5；300 系 degree 全 0 系源未画线，非解析丢失 |
| D2 | work/derived/person1.normalized.yaml | L1 | agent 目视 jpg 转录 + user 断言（`user_asserted_digitization`） | photo 断言版；**仅作对照/历史**，已被 D3 取代为 person1 的声音；断言责任在 user；unknown 不伪造 |
| D3 | work/derived/person1_redraw.normalized.yaml | L1 | `normalize_drawio.py --all-undirected` 机械解析冻结 redraw | 16 节点（12 标签+4 unlabeled 空框）/13 边全无向/0 介质；missing=[C4]（不合位号正则，原样保留不脑补） |
| D4 | work/derived/observations.merged.yaml | L2 | `merge_observations.py` 机械合并 D1+D3 | 52 实体/40 边（corroborated=0、single=40）/2 悬空/dup_groups=[P-3505,T-3501A]/direction_vars=12/functional_vars=5；政策：tag 精确对齐、缺席≠冲突、假设只登记不裁决、D2 排除 |
| D5 | work/derived/solver_result_P0.yaml | L3 | `solve_topology.py`（纯 Python 全枚举） | 128/128 infeasible（degree_deficit） |
| D6 | work/derived/solver_result_P0h.yaml | L3 | 同上 + `--allow-hidden` | 27648 最优世界；stable=40、absent=0；hidden_need 15/18/16.70 |
| D7 | work/derived/solver_result_P2.yaml | L3 | `solve_topology_p2.py`（MILP via scipy/HiGHS） | 48 解；观测边 drop 全 0；稳定语法推断 3 条；歧义簇 3 个；W1 于此冻结 |
| D8 | work/derived/normalize_drawio.py、merge_observations.py、solve_topology.py、solve_topology_p2.py | 工具 | 可复跑脚本 | normalize_drawio 取代 normalize_person2.py（后者 SUPERSEDED 暂留）；ortools 弃用见 §4 |
| D9 | 本文件 work/PROJECT_LEDGER.md | 台账 | 合并自 SOURCE_PROVENANCE + PROCESS_LEDGER | 唯一台账；旧编号映射见 §9 |
| D10 | work/derived/prior_decisions_P4.yaml | P4 输入 | user 拍板转录（agent 记录，2026-09-04） | A1–A6 裁决数据 + 白名单（已关闭）+ stray 处置；全条目 prior-driven 声明与局限 |
| D11 | work/derived/prior_backing.yaml | P4 背书 | WebSearch 两轮（2026-09-04） | 档2 前半命中 4 URL（摘要级）；档2 后半未直接命中→降级推断；档3 催化蒸馏内件命中 4 URL；档3 其余待收；档1 不需外部背书 |
| D12 | work/derived/solver_result_P4.yaml + solve_closure_P4.py | L3/P4 | MILP 最小补集枚举（HiGHS） | 唯一最小补集 7 条：c1 E-3508—T-3512；c2/c3 P-3502—T-3501B/E-3506；c4/c5 P-3503—T-3501B/E-3506；c8 混合罐—P-3511；c9 V-3506—混合罐。不闭合白名单 E-3502/E-3503/FV301 声明为测绘缺陷 |
| D13 | work/DEV_JOURNAL.md | 流水 | 研发流水（J1–J14） | 过程与改主意叙事；指回本文件与 yaml，不复制内容 |
| D14 | work/derived/balance_T0.yaml + balance_T0.py | W2/Tier0 | 手写稳态组分衡算 | 闭合 err=0；MTBE 2093.6 kg/h @X0.95（纯度 99.93 wt% 计算值）；醚后C4 MeOH 485 ppm(mol)；新鲜甲醇 23.835 / 循环 3.665 kmol/h；吨耗理论 0.3635 t/t；敏感性 X0.90→1983.4 kg/h。假设逐条标 literature摘要级/assumed |

## §8 报告取材映射

- ②.2 框图+流程图 ← P2 稳定骨架 + A1–A6 先验边（**标 prior-driven**）+ "prior vs 观测"缺陷分析。
- ②.1 工艺原理/原料/产品指标/操作规程 ← W2 Tier 0 衡算（待做）+ 文献。
- ②.3 ≥3 设备结构图 ← 教材标准结构（固定床醚化反应器/催化蒸馏塔/管壳换热器或离心泵），不依赖 W1。
- ④ 体会/安全/建议 ← 现场真实观察（陡梯/窄台/拥挤/假管/无交底/未告知任务）+ §5 的 C1–C3 与 corroborated=0 证据。
- 方法/讨论/附录 ← 本台账 §4–§6 + solver yaml + 两张原始草图（打印附录）。

## §9 文档合并史与旧编号映射

- 2026-09-04：`work/raw_material/SOURCE_PROVENANCE.md` 与 `work/derived/PROCESS_LEDGER.md` 合并为本文件；旧两份删除。
- 旧 provenance 衍生物条目 1–10 → 本文件 D1–D9（case 归一并入 §2.4；旧条目 10"PROCESS_LEDGER 文档"即本文件 D9）。
- 旧 ledger §0–§7 → 本文件 §1–§8。
- 知识卡片 `personal/QnAnExperience.md` Q2 的出处已改指本文件章节；Q2 不承担项目台账职能。
- **废弃产物警示**：`personal/trash/dc/report.md` 与 `field_reconciliation.md` 为早期废弃草稿，其中的标签合并结论（如"T-302 与 T-3501A 同塔""E-3509 与 E-350S 同冷却器"）**已废弃、不作数**，不得回流进本报告；当前口径以 §5/§6/D10 为准。
- **三层分离（2026-09-04，D13）**：事实链 = `work/derived/*.yaml`（数字 SSOT，推导进各自 `meta.derivation`）；登记册 = 本文件（决策 SSOT，保持薄）；研发流水 = `work/DEV_JOURNAL.md`（J1–Jn，过程与改主意）。查数字→yaml；查决策→本文件；查"当时怎么想的"→journal。
