# QnAnExperience

> 一些知识性问题与具体工程问题的追问和答疑，它们流落在原始上下文中比较零散，甚至仍未成型，现在沉淀。一般都是追加式，当然也不排除删改。
> 不同条目具体地分点，一定要分点。且这是用户的追问和答疑，不是agent的默认的过程记录册。
> 此文档的定位就是卡片笔记，适当的也要引原文出处(如果有的话)。但是也不要怕单个点写长，如果它本身就值得详细讲的话。此文档可以应对"不知道自己不知道什么"的问题，通过用户自己问，或者从实践中意识到的，明确或有待发掘的好问题，对它们尽可能见一个记一个。
>
> - 知识性的内容全都是事实性的没有太多依赖问题，追加式。不要官腔，面向给用户的，怎么清楚怎么讲。
> - 工程性内容可能有返工但是一般不直接覆盖，所以要写清楚前提条件，删改也要写清楚当时是为什么现在是为什么，有点像ADR的意思但是没那么官腔和死板格式与行业黑话，否则用户看不懂。这条适用于当这个项目是具体的工程项目。如果这是学习项目，那反正，思路也能借鉴。
>

---

## Q1 — 化工原理的「算 / 画 / 衡算」该怎么分层解耦，各层用什么工具

> **起因**（本次会话的追问链）：要做一份偏「化工实训逆向拓扑作业」角度的化工原理教程，先问「教材里的图能不能用 python 画」→ 追问「流程图这类有没有化工专用方案（python / 外部软件 / MCP / API）」→ 最后要求把「算、画、严谨演算到底谁管谁、什么时候换工具」整个走一遍。这条卡片沉淀的是最后那套**分层解耦心智模型**，前面的分类与选型核实是它的支撑材料。
>
> **语境框定**：以下工具选型是**调研语境下的分析与建议**，其中标注「候选·未核实」的（尤其 MCP / 第三方 skill）一律按未验证候选对待，**不是项目已拍板决策**。最终落地哪几层、锁哪些库，待用户明确敲定（见文末待定钩子）。

### 1. 先把「图」分三类，python 可行性差别很大

| 类别 | 典型图 | python 生态能画吗 |
|---|---|---|
| **A. 数据曲线 / 相图 / 操作线图** | McCabe-Thiele 阶梯图、x-y 气液平衡、T-x-y、泵特性曲线(H-Q/N-Q/η-Q)、Moody 摩擦系数图、沸腾曲线、干燥速率曲线、湿空气焓湿图(H-I)、杜林图、三角形相图、吸附等温线、壁面温度分布 | ✅ **完全能，且应该用 python 画**（本质是「给方程→算点→连线」，还能和数值解互相验证） |
| **B. 流程示意图 (PFD/P&ID)** | 精馏/吸收/萃取/干燥流程、多效蒸发流程、带回流的连续精馏 | ⚠️ **有化工专用方案**（见第 4 点），别硬用 matplotlib 手搓坐标 |
| **C. 设备结构剖面图** | 离心泵剖视、列管/板式换热器、旋风分离器、塔板(筛板/浮阀/泡罩)、填料塔、蒸发器、干燥器 | ❌ **python 基本不擅长**；用户已明确**不强求**（「这不是机械项目」）。真要走，用 drawio / tikz / 引用标准教材图，不用 AI 生成图进正式教材 |

### 2. 核心澄清：这是**两条正交的轴**，别搅在一起

一开始容易把「算 vs 画」和「通用 vs 专用 vs 外部」混成一团。拆开就清楚了：

- **轴一「算 vs 画」——解耦**：**算**产出数字/图结构（点、边、置信度、理论板数…）；**画**只把已算好的结果渲染成像素。**绘图库不参与计算**。这就是「解耦、轻量、适合大规模图搜索」的由来。
- **轴二「通用生态 → 化工专用 → 外部重器」——严谨度/重量的阶梯**：
  - 通用：numpy / scipy / matplotlib / networkx（透明、轻、可复现）
  - 化工专用：pyflowsheet（画流程图）、pyDEXPI（P&ID 标准数据/图）、DWSIM / IDAES（流程模拟衡算）
  - 外部重器：Aspen Plus（COM/API）、Aspen MCP（候选·研究阶段）
- **易混点**：「化工专用库」里**既有画图的（pyflowsheet）也有算衡算的（DWSIM/IDAES）**，它们不是一回事、处在不同阶段。

### 3. 三层流水线（用「精馏」贯穿）

| 阶段 | 干什么 | 用什么 | 层 |
|---|---|---|---|
| **① 讲原理 + 算** | 正文讲 McCabe-Thiele：给平衡数据，逐板算理论板数、操作线、q 线 | numpy / scipy | 通用·算 |
| **② 画曲线图(A 类)** | 把①的结果画成 x-y 阶梯图 | matplotlib | 通用·画 |
| **③ 画流程图(B 类)** | 画「进料→塔→冷凝器→回流→再沸器」PFD | pyflowsheet / Mermaid | 化工专用·画 |
| **④（可选）严谨衡算** | 「图上连得通」≠「物料/能量衡算成立」；要真验证流程能跑，上流程模拟做严格逐板+衡算 | DWSIM(Py API) / IDAES(Pyomo) / Aspen / Aspen MCP | 化工专用·算 → 外部重器 |

**作业那条线同构、并行**：①' 建约束图(networkx：节点=设备/阀门、边=管线、属性=确认/推测/冲突/未知) → ②' 图搜索/求解(OR-Tools CP-SAT) → ③' 画候选拓扑(graphviz 自动布局 / networkx.draw / 清理版用 pyflowsheet) → ④'（可选）验证衡算(同④)。

**规模注**：作业那种几十个节点，networkx + CP-SAT 足够；上千节点才需 igraph/C++，此场景用不上。

### 4. B 类工具选型核实结果

| 工具 | 是什么 | 已核实能力 | 适配 / 坑 | 状态 |
|---|---|---|---|---|
| **pyflowsheet**（MIT, 2020） | 代码画 PFD → SVG | 自带真实化工单元图标(Vessel 含 tubes/bed 内件、Distillation 塔含冷凝器/再沸器/填料、Pump、Compressor、Valve、HeatExchanger、Mixer、Splitter、StreamFlag)；Dijkstra 自动布线+手动 override；可把 matplotlib 图/pandas 表嵌进同一张 SVG | **教材 B 类最对口**；坑：作者自称 alpha、API 每个 release 可能变→**必须锁版本** | 已核实(读 GitHub README) |
| **pyDEXPI**（AGPL-3.0, TU Delft, 2025） | 实现 DEXPI 工业标准的 P&ID 数据模型(Pydantic) | 载 Proteus XML→解析成 NetworkX MultiDiGraph；GraphAbstractor 抽象成 complete/process/conceptual 三级拓扑；导出 SVG；合成 P&ID 生成 | **作业逆向拓扑最对口**（本身就是「P&ID→图」）；坑：AGPL copyleft(自用无妨)、需 DEXPI 输入或手工建模 | 已核实(读 GitHub README) |
| **networkx + graphviz** | 通用图建模/布局 | 节点/边/属性建模，自动布局出图 | 作业「带不确定性约束图」的底座 | 通用常识 |
| **IDAES-PSE**（开源, 基于 Pyomo） | 流程建模 + Flowsheet Visualizer | 渲染流程图为工程图、导出 SVG + 物流表 | 想让「图即模型(带衡算)」时的 python 原生路；坑：重、学习曲线陡、静态 SVG 导出有摩擦(社区 discussion #1311) | 部分核实(官方文档检索) |
| **DWSIM**（开源模拟器, 跨平台） | 流程编辑器 + Python Automation API | `Flowsheet` 类暴露所有对象，可从 python 驱动建模出真实流程 | Windows 友好；要装模拟器本体 | 部分核实(官网/wiki 检索) |
| **Aspen Plus**（商业） | COM/自动化(pywin32) | 可编程建流程并导出 | 要 license | 常识 |
| **Aspen Plus MCP server** | LLM agent 用自然语言经 MCP+python 桥接 Aspen 跑模拟 | — | 据 2026 arXiv + ScienceDirect 同名文；**全文未读到**(sciencedirect 403、arxiv TLS 超时) | **候选·未核实** |
| **「PFD/P&ID Generator」Claude Code skill**（MCP Market） | agent 技能，自动生成标准过程图+设备清单 | — | 第三方、质量未验证 | **候选·未核实** |
| **Mermaid / Graphviz DOT / D2** | markdown 原生 / diagram-as-code | `.md` 内直接渲染、可 diff、零依赖 | 教材块级教学示意最省维护；**非 ISA 标准符号**，教学够用 | 通用常识 |

**旁证**：pyDEXPI 背后 TU Delft 有整组研究——ChatP&ID(LLM 与 P&ID 图交互)、P&ID 图上规则自动纠错、流程拓扑生成式补全，与「碎片观察→逆向拓扑→标注不确定性」的作业角度高度同构，可作背景补课材料。

### 5. 分层建议（对准两个需求）

- **教材 B 类教学流程图** → 主力 **pyflowsheet**(锁版本，能把 A 类曲线嵌进同一张 SVG)，轻量内联用 **Mermaid**。
- **作业逆向拓扑** → **networkx** 做约束图底座 + **CP-SAT** 求解，**pyDEXPI** 作方法论参照，出图用 graphviz / pyflowsheet。
- **要不要跑到「能算衡算」** → 要则选 **DWSIM(Py API)**（开源、Win 友好）；IDAES 更 python-native 但更重。**这一层可选、非必需**，取决于作业停在「拓扑+讲清原理」还是要「跑严格衡算」。

### 6. 一句话总结

> **算**（通用 numpy/scipy/networkx，轻量透明）→ **画**（曲线 matplotlib、流程 pyflowsheet）→（可选）**严谨衡算**（DWSIM/IDAES/Aspen/MCP）。三层各管各的，前一层输出是后一层输入，谁也不越界。

### 出处

- 本次会话追问链（图可行性 → B 类选型 → 分层走一遍）。
- 背景任务：`work/coffeehour_chat_refs/chat1_极限挑战逆天作业1_glm5.1.md`（拓扑逆向、networkx + OR-Tools CP-SAT、「先逆向后进 aspen 跑」等，属头脑风暴素材，按未验证候选对待）。
- Web 核实：pyflowsheet(GitHub README)、pyDEXPI(GitHub README)、IDAES(官方文档 + discussion #1311)、DWSIM(官网 + Automation wiki)；Aspen MCP / Claude PFD skill 仅检索命中、全文未读到，标候选·未核实。

### 待定钩子

- 教程最终**落地哪几层**（④严谨衡算做不做）、**锁哪些库的具体版本**——待用户拍板后写死，勿在此提前定论。
- 当前 `pyproject.toml` 仅有 `pyyaml`；numpy/scipy/matplotlib/pyflowsheet 等**尚未安装**，开工需先按 uv + 本地 `.venv` 加依赖。