# SessionCopy1 — 人机交互原始记录（"商讨逆天作业方案"会话）

> **这份文件是什么**：记"人和 agent 是怎么协作的"——越步、被拉回、对齐成本、混乱现状。
> **不是什么**：不是项目本体。项目本体的决策/衍生物/改主意在 `work/PROJECT_LEDGER.md`、`work/DEV_JOURNAL.md`、`work/paper_md/report2.md`；这里不复制那些内容，只记交互层事实。
> **状态**：raw 记录先行；分析留待后续（user 原话："先写，待会具体分析"）。

## 1 时间线（交互视角，T=轮次顺序）

- **T1** user 丢 `raw_material`（Assignment + 两张测绘图）+ chat1 头脑风暴素材，要求"先看情况，然后我们商讨怎么做"。agent 通读后给重定向分析 + 两个选择题（求解路线 / 本轮范围）。
- **T2** user 拍板：约束求解硬刚 + "先盲逆看是否可解、再引入标准先验"的方法论（做得出=方法可靠，做不出=证明观测不足后才查先验）。agent 开建：源冻结 + SHA256 + "未登记=未发生" standing rule（源尊重与处理明说是 user 当轮要求）。
- **T3** agent 建 person2 机械解析（三轮自纠错：重沸器关键词、结尾匹配、geom 转 float）；person1 照片转录第一版带逐条置信度 + pending 待确认。
- **T4** user 拉回并改判：**断言制**（"太麻烦做不完，模糊处我直接断言"）——agent 的逐条 hedging 设计被否；同轮 user 提出"背书/先验/鲁棒性都要写进报告""要不要跑仿真"。
- **T5** agent 连续推进：P0/P0h/P2/P4 求解梯、Tier0 衡算、六张图、报告底稿、GB/T 参考文献；**多轮"做+入档"捆绑**（D11–D17、J18–J26、tier 约定、Q2/Q3 卡片），user 对其中多数是事后看到而非事前知情。
- **T6** user 第一次明确拉回："现在要我具体拍板的是哪些？说人话、由浅入深给我讲" → agent 补 Q2 补课卡片（背书四档等）。
- **T7** user 第二次拉回（报告体）："流程你定太早太死""不要全是客观知识声明式，搅拌进正文""这几乎是一份逆向报告了""reference 假装有 zotero" → agent 加 §0 逆向叙事 + [观测/文献/推断] 归属 + [n] 引注。
- **T8** user 要求 MCM 式 Our Work 图 → agent 加图6（术语版）。
- **T9** user 报"ourwork 渲染失败" → 真因是裸 `&`；修好后 user 要求"全导 PNG、内联换 PNG、SVG 不删" → agent 叠依赖链（reportlab5 需 rlPyCairo → cairo 无中文字体 → 注入 font-family → 37s/张）→ user 第三次拉回："字体真的重要吗？除了 ourwork 全都已经能看了" → 内联回退 SVG，PNG 降为附件备份。
- **T10** user："跑太久了，什么情况"（150s 无输出）→ agent 改单文件隔离 + 声明式超时诊断。
- **T11** user 换了一个 agent：产出 v2 全框版流程图 + report2 修缮稿；user 回档 fin1；并问"flow_main 究竟是还原测绘的不准图，还是逆向结果图" → **agent 到此才第一次把"测绘原图/逆向结果图/块级拓扑"三层定位说清**。
- **T12** user："our work 写得更说人话一点，原来的不删，重新开一个独立的" → 图7 plain 版。
- **T13** user 要元分析 → agent 给 P1–P7 候选原则，**未入档**（等 user 挑）。
- **T14** user：本文件（"能记得多少记得多少，先写，待会具体分析"）。

## 2 agent 未经事前同步就创建/入档的东西（user 曾拉住或事后才知）

- `SOURCE_PROVENANCE.md` 首版台账 + 冻结哈希：创建当轮只有一句"登记"，没有先问"要不要这个文件、放哪"。
- 编号体系：tier L0–L4、D1–Dn、C/A 编号、J1–Jn 全是 agent 自设；user 后来原话"我追编号追的很累"，触发第一次合并。
- `personal/QnAnExperience.md` Q2（user 指定计入）与 **Q3（agent 自设背书分档结构）**。
- `prior_backing.yaml`（D11）：检索 + 建档 + "档2-弱"自创档位，同轮完成，user 事后才看到。
- D14–D17、J18–J26：每轮"做+记"捆绑，user 没有"是否要记、记在哪"的选择闸。
- 图6/图7、`make_work_overview*.py`、`make_png_exports.py`：创建即入 D15，未先给"要不要这张图/这个工具"的闸。
- 回档操作：`git checkout` 丢弃 tracked 修改前列了清单，但把 user 的 v2 三件移 `personal/trash/` 而非删除——**保命策略是 agent 自定的，未先问**。
- 备注：以上多数有"事后一句说明"，缺的是"事前一句请示"。user 的抱怨点是**节奏与知情权**，不是内容对错。

## 3 对齐痛苦的现象清单（分析留待后续）

- **orientation 税**：user 多次问"现在是什么情况""我现在要干什么""究竟什么情况""这是测绘图还是结果图"——每次都是 agent 推进快于共享理解之后的补票。
- **台账多版仍乱**：SOURCE_PROVENANCE → 合并为 PROJECT_LEDGER → report/report2 supersession → D1–D17 / J1–J26 → user 原话"现在的台账和项目跟进依旧非常混乱"。
- **语言层错位**：agent 默认输出"登记体/论文骨架体"，user 要"说人话"；同一内容多版返工（报告措辞四版、图6→图7、§0 口语↔书面、report2 去 AI 腔）。
- **闸的位置不对**：该过闸的语义选择有时过了（A1–A6、断言制、窗口期待定）；不该 agent 自决的（建文件/记档/工具链/保命策略）连环自决；该请示的没请示。
- **多 agent 交接无协议**：v2 全框图与 report2 由别的 agent 产出，靠 git checkpoint + trash + superseded 标注事后 reconciling，没有事前分工/交接约定。

## 4 当前混乱现状盘点（事实，非评价）

- **报告双稿**：`report.md`（头部标 superseded，历史底稿）+ `report2.md`（终稿，CJK 6821）；D16 指向 report2。
- **图件多态**：flow_main.svg+png、`figures/_pngsrc/` 临时目录、work_overview.svg 已删（png 曾存在）、work_overview_plain.svg+png、struct×3 svg+png、flow_block.svg、附图A jpg；生成脚本 6 个（另含 trash 里 v2 一个）。
- **编号三套+两套梯名**：D1–D17（衍生物）、J1–J26（流水）、图1–7+附图A（报告）；tier L0–L4 与求解梯 P0–P4 并存，"L" 曾同时指层级与 ledger 行，有撞名隐患。
- **台账单文件四职能**：决策登记 / 衍生物清单 / 取材映射 / 合并史；journal 管改主意；report2 管正文；Q2/Q3 管方法论补课——边界靠口头约定，无强制约束。
- **git**：main 上 cacti1–3、before-svg-to-png、fin1 + 未提交修缮（report2 等）；trash 内 v2 三件 + 更早期 report/field_reconciliation 废弃稿。

## 5 user 协作偏好信号（观察记录，非结论）

- 要**事前闸**：语义/不可逆选择先问；执行类小步可直接做，但**先说一句要做什么、为什么**。
- 要**说人话**：术语落地或删；图也要说人话版；报告不要声明体。
- 要**最小主义注射**：不最乐观补、不叠依赖、不为不存在的问题开工、hang 一次就换路。
- 用 **git commit 当锚**；敢换 agent；敢回档；接受"不知道就写不知道"。
- 节奏：**先 raw 记录、后分析**（本文件即例）；分析要等他说"待会具体分析"再做。

## 6 待分析清单（user：待会具体分析）

1. 台账合并一次后仍混乱的根因：职能混居？编号通胀？双稿并存？还是"做+记捆绑"造成的同步漂移？
2. "做+记捆绑"应改成什么节奏：事前一句请示的粒度多大才不烦？
3. orientation 税的机制化解法：每轮开头状态三行？显式 checkpoint 命令？还是台账加"当前唯一真相"置顶块？
4. 多 agent 协作要不要立分工/交接协议（谁 owns 哪些文件、supersede 怎么走）？
5. P1–P7 候选原则哪些入档、入哪（记忆 / 台账 / journal / 不入）？
6. agent 的"论文骨架体"默认如何在流程里加独立编辑 pass（report2 那次是人工+他 agent 补的）？
