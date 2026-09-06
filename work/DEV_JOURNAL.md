# DEV_JOURNAL — 研发流水（过程与改主意）

> **定位**：三层分离之第三层。事实链（数字/边/频率）以 `work/derived/*.yaml` 为准；决策与登记以 `work/PROJECT_LEDGER.md` 为准；**本文件只记"试了什么、炸了什么、为什么改主意"**，每条结尾指回 ledger 章节 / D 编号 / yaml，不复制内容。
> **防追号**：查数字→yaml；查决策→ledger；查"当时怎么想的"→本文件。三者地图见 ledger §9。
> **写法**：按时间倒序不必要，正序；失败与改主意必须记，成功只记一句。

## 2026-09-03

### J1 开局重定向：这不是"逆向题"，是"报告题"
读 Assignment 四节 + 手写≥5000 字要求 + chat1 头脑风暴素材（只当参考、不当决策）。一度跟着 chat1 的框把任务当成"NP-hard 拓扑逆向"，读完 Assignment 才发现逆向只服务 ②.2 的流程图，报告主体（②.1 原理/指标、②.3 设备结构图、④ 体会安全）根本不依赖逆向。改主意：全任务地图 W1–W5，逆向降为子任务。
→ 指向：ledger §1、§4（09-03 路线拍板）、§8 取材映射。

### J2 源尊重机制：先立规矩再碰数据
user 要求"把两张图当数据源尊重、任何处理明说"。于是改名、只修 6 处不改变拓扑的错别字、冻结+SHA256、standing rule"未登记=未发生"。中途发现 Get-FileHash 给大写、hashlib 给小写，差点误报漂移 → 统一小写并登记为 case-only 处理。
→ 指向：ledger §2.1–§2.4。

### J3 person2 机械解析：三处脚本自我纠错
初版关键词规则把"催化塔下塔**进料器**"里的"塔"当成自身类型（假阳性）、漏收"重沸器"（E-3506/E-3513 误报 mismatch）、geom 留字符串。三次小修后机械判定与人工核对清单完全对齐，才敢信脚本。
→ 指向：D1、D8。

### J4 person1 转录：从逐条置信度改判为断言制
第一版给每条边标 high/medium/low + pending，等 user 逐条确认。user 反馈"太麻烦做不完、模糊处我直接断言"。改主意：断言制（责任在 user），但**真追不到的仍留 unknown 不伪造**——这条底线没让。
→ 指向：D2、ledger §4（person1 断言制）。

## 2026-09-04

### J5 person1 redraw 入冻与无向覆盖
user 自己重画了 person1（drawio），声明全图无向。解析时发现个别边漏写 `endArrow=none`，逐边判定会把它误判成有向 → 改用源级 `--all-undirected` 覆盖，并把"覆盖"本身登记（不偷偷改语义）。
→ 指向：D3、ledger §2.2。

### J6 stray 文件：差点当成第二个 person2 源
raw_material 里冒出一份 terriblemapping_person2.drawio，哈希与冻结版不同，一度以为是人改过。diff 后发现仅 mxGraphModel 的 dx/dy 视图偏移不同 → 内容等价重复存档、非源 → 移 trash。教训：哈希不同 ≠ 内容不同，先 diff 再下结论。
→ 指向：ledger §2.2、§6。

### J7 L2 合并吐出的反直觉事实：corroborated=0
预期两人图会有重叠连线互相印证，结果**边层面零重叠**、只重叠节点 tag。第一反应是合并脚本坏了，核对后确认是真的：两人各画了互不相交的半张。把它从"bug 嫌疑"改判为"测绘缺陷证据"C3。
→ 指向：D4、ledger §5 C3。

### J8 ortools 段错误：换枪不换目标
CP-SAT 连最小模型都 0xC0000005 访问违例（与建模无关，wheel 问题）。没有恋战调试 ortools，改纯 Python 全枚举（P0/P0h），P2 起改 scipy MILP(HiGHS)。副作用是好事：全枚举给精确频率，比 k-best 采样更强。
→ 指向：ledger §4（ortools 弃用）、D8。

### J9 P0 infeasible：先当 bug 查，后当结论用
P0 严格版 128/128 infeasible。第一版建模把"漏画"当成矛盾，模型被憋死——这是建模错，不是数据错。加 hidden-edge 派生变量（P0h）后正确表达"缺约 17 条边"。infeasible 本身保留为实证：盲逆在闭合公理下不可解。
→ 指向：D5、D6、ledger §5。

### J10 P2 的"全稳定"是假象：自我纠错一次
P2 首轮 stable=40、ambiguous=0，差点写成"歧义已解决"。复查发现该轮没给观测边怀疑能力（无 drop 变量），"全稳定"是方法造成的构造性假象。加 drop 变量后歧义显形为 3 簇。由此定下 C1/C2 两条必须进报告的 caveat，并立下"稳定≠可信"（两悬空附着 48/48 稳定却是度数逼出的跨单元几何巧合，不采纳）。
→ 指向：D7、ledger §5 C1/C2。

### J11 文档合并：user 追编号追累了
provenance（机器登记）与 ledger（叙述）互引编号，user 抱怨追号累。合并为 PROJECT_LEDGER 单一台账，编号 §/D/C/A 全文件唯一。当时担心"叙述被压扁"，现在由本 journal 承接叙事，三层各司其职。
→ 指向：ledger §9。

### J12 P4 拍板与背书检索：命中与未命中都要记
A1–A6 user 拍板（4/6 按 agent 理解、5=最小必需且试出来）。背书两轮 WebSearch：档2 前半与档3 催化蒸馏内件命中（摘要级）；**档2 后半（萃取/回收序列）未命中 → 降级"推断"**，按约定当场告知 user 而不悄悄用。命中判定规则写成 hit_rule，避免以后"看到设备名就算命中"的滑坡。
→ 指向：D10、D11（含 derivation）、ledger §4。

### J13 P4 最小补集三轮迭代
v1 infeasible：加缺口诊断打印，定位 C4 原料混合罐（p2 未标号节点）度数缺口且无候选可达 → 补 c8/c9。v2 得 8 解：真最小 6 条×2，分歧是 c8 xor c9（混合罐进/出二选一）。v3 按档1 惯例"feed drum 有进有出"把该罐度数要求设为 2 → 唯一最小 7 条。关键判断：这个特例是**惯例**不是乐观补全，所以不违反 A5。
→ 指向：D12、solver_result_P4.yaml meta.derivation。

### J14 三层分离落地
user 问"流水和单一事实分开了吗"——答没有，于是立本文件。规则：yaml=数字 SSOT（推导进各自 meta.derivation）、ledger=决策 SSOT（保持薄）、journal=过程与改主意（本文件）。以后任何"当时为什么"写这里，任何"现在是什么"写 ledger/yaml。
→ 指向：ledger §9（三层地图）。

### J15 W2 Tier 0 衡算：先讲数再算，闭合即检验
手写组分衡算而非上模拟器（Tier 0 定位：给报告数字+检验流程自洽）。每个输入数先写清"是什么/凭什么"：basis 取 100 kmol/h 让 mol% 直接读成 kmol/h；异丁烯 0.25 与醇烯比 1.1、萃取 99%、产品带甲醇 0.2 mol%、萃取水 80 kmol/h 全部 assumed（无该厂实测）；只有转化率 90–95% 有文献摘要级背书（D11）。第一版就闭合 err=0——这不是运气，是构造上水回路闭合+无损失假设；真正被检验的是"每条流都有去处"（与 D12 最小补集互证）。敏感性 X=0.90 时 MTBE −5.3%，量级稳定。
→ 指向：D14、ledger §4。

### J16 W4 工具改判：手搓 SVG 被取消，回到 Q1 选型表
我第一版想手写 SVG 画方框图（无依赖、布局可控），写到一半被 user 取消，并指向 QnAnExperience Q1 的 B 类选型表。改判：主图用 **pyflowsheet 0.2.2 + pathfinding==1.0.1**（钉版坑表里早记过；真化工图标比方框专业），md 内联用 **Mermaid**，手抄规格用分区 md 清单；pyDEXPI 留作"标准符号导出"可选备用（时间紧未用）；graphviz 因缺 dot.exe、IDAES/DWSIM/Aspen 因 Tier 0 已够而本轮不用。0.77s 出图，36 单元/31 流。
→ 指向：D15、personal/QnAnExperience.md Q1 表。

### J17 W3 报告底稿：字数不够就补真肉，不灌水
首版 CJK 4079 字，低于手抄 5000 要求。补的四段都是内容而非填充：开停车与巡检要点（把"每个测点背后是一个可能出问题的物理环节"讲透）、第五类典型设备（容器/回流罐，补"不承担主任务却决定平稳运行"的角度）、现场安全条件具体观察（陡梯/翘边覆盖物/胶布管/追断管事例，作为建议的事实依据）、方法名词白话解释（度数闭合/最小补集/prior-driven/多解歧义）。补后 5214 字。写作纪律：所有数字标来源档位，所有"看不到"如实写"内件不可见/依据文献整理"。
→ 指向：D16、ledger §8。

### J18 报告改判为"逆向报告体"：先讲底子，再讲结论
user 指出：纯客观声明体对两个被短时间探图绕晕的学生没有可信度——读者会问"图怎么来的、为什么信它"。改判：① 二、实习内容开头加 §0 叙事节（现场条件→两人各画半张→连线零重叠→度数闭合自检缺约17条→最小补集7条+裁决3处→衡算闭合0→可复现指针），把"不准"放在最前面而不是藏进附录；② 正文加三类归属标注 [观测]/[文献n]/[推断]，声明体降级为有出处的叙述；③ 参考文献按 GB/T 7714 式编号 [1]–[11]（"假装有 zotero"），正文带 [n] 引注，列了的都被引（补 [3] 旁证句）；④ 图从"只有 mermaid 文本"改为 5 张 SVG 嵌入（md 渲染即见成品），②.3 三张结构图真画。改后 6361 字。
→ 指向：D16、D15、report.md §0 与参考文献。

### J19 加 MCM 式 Our Work 总览图（图6）
user 问"要不要加一张 MCM 那样放在 our work 的图说明都干了什么和模型架构"。判断：要——语义现成（L0→L4 + P0→P4 + 验证 + 产出），只缺画；且它补 §0 最后一块（读者看完叙事一眼看到全貌与模型卡）。四泳道+侧栏三块（模型卡/背书与局限/复现脊），虚线框标计划中（Tier 0.5+鲁棒性）。放 §0 末尾而非附录：附录留表格，§0 是叙事锚。手抄提示：可简化为四泳道方框+箭头。
→ 指向：D15、report.md §0 图6。

### J20 Tier 0.5 + 鲁棒性跑完，虚线框转实线；两个"反直觉但诚实"的发现
能量粗估：催化蒸馏 1221 kW vs 甲醇回收 71.7 kW（差 17 倍，与物料结构一致→量级可信）；蒸汽 114 kg/h。敏感性 36 组：MTBE 1587–2512 kg/h；**纯度恒 99.93 wt%**——因为它只由"产品带甲醇 0.2 mol%"假设决定，对四参数不敏感；这不是稳健性好，而是"纯度数字=假设的直接产物"，报告里明说而非藏。LOO 两个发现：① prior 13 条里 3 条对度数闭合**冗余**（拿掉仍闭合）→ 它们是"工艺合理性补画"不是"闭合必需"，降格表述、不作骨架证据；② 观测 39 条里 9 条关键、30 条可被候选池吸收 → 单条观测误差不推翻全图。图6 虚线框转实线并写数字。
→ 指向：D17、report.md 附录、图6。

### J21 图6 渲染失败：裸 & 使 SVG 不 well-formed
user 报"ourwork 图渲染失败"。诊断：xml.etree 解析六张 SVG，仅 work_overview.svg 在 col 7588 报错——侧栏标签"背书分档 & 局限"的裸 `&` 未转义（XML 要求 &amp;）。修法：两个出图脚本加 esc()（& < > 转义）应用于所有文本；标签改"背书分档与局限"。重生成后六张全 OK。教训：手写 SVG 时任何文本进 XML 前必须转义；以后出图脚本自带校验步（parse 一遍再交付）。
→ 指向：D15、make_work_overview.py / make_block_and_structures.py。

### J22→J23 PNG 内联是个假问题：回退 SVG，PNG 降为附件备份
user 要求"全导 PNG、内联换 PNG"。实施中连踩两坑：reportlab 5.x renderPM 需 rlPyCairo（补装 pycairo 后可用）；cairo 后端无中文字体→豆腐块→注入 font-family 后又触发逐文本字体扫描，单张小图 37s、全量分钟级。此时 user 点破关键事实：**md 编辑器渲染 SVG 时中文一直正常，坏的只有图6 的裸 &**。结论：字体问题只存在于 cairo/PNG 路径，SVG 路径无此问题 → PNG 内联是为不存在的问题开坑。回退：六张内联全部回 SVG；make_png_exports.py 保留为附件包/打印的可选工具（后台跑完的 PNG 作副产品），不进正文、不进关键路径。教训：先确认"谁在看、用什么渲染"，再选格式；别在渲染链上叠依赖。
→ 指向：D15、report.md 图1–6、make_png_exports.py。

### J24 换 agent 把 flow_main 改成全框版 → 回档 fin1 恢复图标版；厘清"原图 vs 结果图"
user 换了一个 agent，其 v2 把 flow_main.svg 改成全线框（无化工设备符号）。判断：错——图2 的职责是"带设备符号的规范工艺流程图"（②.2 要求），设备符号承载单元操作语义；全框拓扑是图1 flow_block 的职责，v2 等于把图2 做成第二张图1、信息更少。处置：git 回档到 fin1（HEAD 本即 fin1，仅清未提交残留；v2 脚本与备份 svg 移 personal/trash 保命）。同时厘清三层图定位：测绘原图=raw_material 冻结三件（不改一笔）；逆向结果图=flow_main.svg（线型标来源）；块级拓扑=flow_block.svg。并在 §0 加附图A（person1 现场照片原样嵌入）使"原图 vs 结果图"一眼可对照。
→ 指向：D15、D16、report.md §0 附图A、personal/trash/make_flow_diagram_v2.py。

### J25 图2 改 PNG 的根因 + 图7 说人话版
根因确认：user 的 md 编辑器对 pyflowsheet 产出的 <path>/<circle> 设备符号渲染不良（显示成框框），而 PNG 光栅能正确显示图标 → 图2 内联改 PNG（user 手改，尊重），SVG 原件保留；纯 rect+text 的图（图1/图6/图7/struct×3）编辑器渲染正常，继续 SVG。新增图7 work_overview_plain.svg（make_work_overview_plain.py）：与图6 同结构（四泳道+三侧栏）但全日常说法（"每台设备必须有进有出"代替"度数闭合公理"、"承认有没画出来的线"代替"+漏画变量"、侧栏=补线/说话/查账三条规矩）；原版不删；手抄时图6/图7 二选一。PNG 全量重转（含图7）放后台跑（cairo 慢路，分钟级），仅作附件备份。
→ 指向：D15、report.md 图2/图7、make_png_exports.py。

### J26 report2 修缮终稿：引用重排/注释统一/删冗图/去 AI 腔/§0 收口语
user 五点要求逐条落实于 report2.md：① 引用按首次出现顺序重排（映射 11→1,1→2,7→3,4-6 不变,9→7,2→8,3→9,8→10,10→11；逗号列表 [1,3]/[1,8] 正则漏配需手动补 [2,9]/[2,10]；参考文献列表二次按新号排序——第一次按旧键排错，已修）；② 注释统一 blockquote（§0 归属说明、图件与手抄指引）；③ 删不用图：术语版总览 work_overview.svg/png 删除，report2 图6 换说人话版 plain.svg；report.md 标 superseded 保留作历史底稿；struct_*.png 与 flow_main.png 保留作附件/打印备份（report2 不嵌）；④ 去"不是…而是…"句式六处；⑤ §0 由口语改书面（"拼不出一个说得通的流程"→"无法闭合成自洽流程"等）。校验：CJK 6821、嵌入 6 张、正文引注 1,2,3,4-6,7,8… 与列表 1–11 顺序一致。
→ 指向：D16、report2.md、personal/trash 无新增（删除件为 figures/work_overview.svg|png）。

### J27 流程图全量版 flow_main_full（独立新脚本，旧版不动）
user 指认旧 flow_main 有三类问题并要求"画全、不覆盖旧的、尽可能用库"。分析结论（先分析后动手）：拓扑无线画反、线型与数据一致；真问题= A 遗漏 13 条观测边+8 个单元未入图、B 孤岛（P-3502/P-3503 已声明、P-3505A 未声明）、C 渲染糊（stream 编号标签叠字）。处置：新脚本 make_flow_diagram_full.py（复制扩展旧脚本）→ flow_main_full.svg/png：补 8 单元（某管道汇合/某黑盒/E-3509/E-3510/T-3509/T-3508/V-3504 + ✕三台符号化）、补 13 条观测实线（S20–S32）、P-3505A 不再孤立、stream 标签隐藏。
踩坑两连：① showTitle=False 在 0.2.2 无效 → 改 textColor 隐藏；② textColor 传字符串被 svgwrite 拒（'rgbrgb'/'rgb#ff'），读源码发现 svgcontext 把 color 拼进 `rgb{...}`，须传三元组 (255,255,255)。callout 中文在 cairo 下豆腐 → callout 改纯英文。callout 位置两次调整避开设备。
残留（接受并声明）：密集区单元 id 标签彼此靠近（自动布局所致，放大可读）；pyflowsheet 的 SVG 不渲染单元中文名（只画 id），中文名以 flow_handcopy.md 与 mermaid 为准。旧 make_flow_diagram.py / flow_main.svg / flow_main.png 全部保留未动。
复核审计（user 追问"还有漏的吗"）：逐条对账 merged 39 条非自环观测边 → 漏画 0；**多画 1 条 S09（R-3501B→V-3502）**——旧版把"某管道汇合"当透明直连，全量版补 S21+S22 后该线无据，已删（streams 44→43）。未画 8 条全为声明项：P-3505B 入口断口、T-3508 出口断口、MEH 萃取水自环、E-302 未知端、person1 四个未标注框间 4 边。单元口径：merged 52 实体 vs 图 46 = 7 个声明不立节点（断了?×2、放空?、person1 未标注×4）+ 混合罐双实体（p1r C4 与 p2 混合罐，candidate_align）画一个。prior 11 条全画；可选 prior 2 条与 P-3502/3 prior 声明不画。
→ 指向：D15、figures/flow_main_full.svg|png、make_flow_diagram_full.py。

### J28 线框对照图 flow_main_wire（平行于图2，消渲染歧义）
user 要求"再出一个没有渲染歧义的线框图，平行于图2 对照看"。做法：make_flow_diagram_wire.py **import make_flow_diagram_full 复用 U/OBS/PRIOR/UTIL**（同源保证两图拓扑不漂移；import 顺带幂等重生成 full svg），画矩形框（id+中文名在框内）+ 框边中点直线，线型语义同图2，不画 stream 编号，callout 声明同图2（含第 4 处歧义）。46 框/43 边与图2 一致。
取舍：wire 只出 SVG 不进 PNG 名单——纯 rect+text 的 SVG 编辑器/浏览器可直接渲染；cairo 中文慢路为 46 个中文框标签跑分钟级（240s 超时实测），不为它等。PNG 只为 pyflowsheet 图标图（flow_main_full）存在。
→ 指向：D15、figures/flow_main_wire.svg、make_flow_diagram_wire.py。
