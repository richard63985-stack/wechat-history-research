# 公众号历史研究 · WeChat History Research

将一个微信公众号**当前可访问的历史文章**整理为观点数据库、核心时间线、主题地图、公司/产品索引，以及结论化 HTML / PDF 研究报告。

这是面向 **Coding Agent 的通用工作流 Skill**，包含指令、数据规范、本地校验和阅读导出脚本，不绑定某一家模型或编程工具。采用 `SKILL.md` 入口，可由支持 Agent Skills 的运行环境加载，也可由具备本地文件读取和脚本执行能力的智能体按路径读取后执行。

**不是免登录爬虫，也不附带可直接批量抓取任意公众号的采集器**。实际采集由智能体根据可用浏览器、授权和数据源完成，首次使用必须验证目标公众号。

[首次运行指南](FIRST_RUN.md) · [智能体执行指令](SKILL.md)

## 能得到什么

| 交付 | 内容 |
| --- | --- |
| 历史观点数据库 | SQLite 原始语料与逐篇摘要、观点、来源、证据等级 |
| Excel 总览 | 可筛选文章目录、内容覆盖、按月统计、MD 链接与人工审阅列 |
| 逐篇 Markdown 与 index.md | 按年月及“日期＋标题＋短ID”归档，一篇一文件，从入口逐月阅读 |
| 核心观点时间线 | 关键观点在不同阶段的延续、转折与变化 |
| 主题地图 | 主题分布、重点方向及关注度迁移 |
| 公司 / 机构 / 产品索引 | 实体归一化、出现文章与原文链接 |
| 过去一年观点变化 | 最近 12 个月与此前 12 个月对比 |
| 总括研究报告 | 当年分阶段结论、核心判断、同版 HTML / PDF |
| 可选的市场验证 | 文章观点与标的、基准的后续表现对照 |

核心顺序是：**先验证目录和正文 → 归档与去重 → 逐篇研究 → 跨篇聚合 → 导出阅读包 → 写终稿 → 验收**。总量、全文覆盖率和来源限制始终可复核；摘要不冒充全文，价格同向不写成因果证明。

## 在不同 Coding Agent 中使用

这里的 **harness（运行环境）**，指承载智能体、提供文件、终端和浏览器等工具的软件，例如 Codex、Claude Code、Cursor 或 OpenCode。工作流相同，安装入口和可调用工具由各环境决定。

| 层级 | 通用范围 |
| --- | --- |
| 研究流程、数据和交付规范 | 共用同一份 `SKILL.md` 与 `references/`，无需为每个工具改写 |
| SQLite 校验、逐篇 MD 和目录导出 | Python 3.10+ 标准库脚本，不依赖 Codex 或模型 API |
| 采集、Excel、PDF | 使用当前环境具备的浏览器、表格和打印工具，首次运行需验证 |
| 可选环境适配 | `agents/openai.yaml` 是 OpenAI 界面元数据；`build_overview.mjs` 仅供提供其依赖的环境使用，不是通用流程的必需组件 |

### 安装与启动

将下面这段话发给你正在使用的 coding agent：

```text
请从以下仓库安装 wechat-history-research，先阅读其中 FIRST_RUN.md 的安装说明：
https://github.com/richard63985-stack/wechat-history-research
完整保留 SKILL.md、references/、scripts/ 和配套文件。
按你当前运行环境的 Skills 目录安装；若不支持自动发现，就保存到本地工具目录，
告诉我 SKILL.md 的绝对路径，并在使用时完整读取它。
已存在同名 Skill 时先比较，不覆盖我的本地修改。
安装后运行离线自检；本次先不登录、采集或生成报告。
```

具体安装目录、调用示例及 Windows / macOS 命令见 [首次运行指南：安装与调用](FIRST_RUN.md#安装与调用)。其中分别列出 Codex、Claude Code、Cursor 和 OpenCode 的官方入口；其他环境可使用按本地路径读取的通用方式。原生加载说明经过官方文档核对，**不等于这些环境都已完成整条研究流程的实机测试**。

## 第一次怎么用

在你使用的智能体中打开**独立的本地研究文件夹**，不要把文章原文或报告写进这个公共仓库。准备公众号名称和一篇文章链接，再发送以下通用指令；原生 Skill 的快捷调用方式见首次运行指南。

```text
使用 wechat-history-research。
完整读取已安装 Skill 的 SKILL.md 和 FIRST_RUN.md；若未自动识别，
从【填写本地 SKILL.md 的绝对路径】读取，并按步骤读取其引用文件。
研究输出目录：【填写独立研究目录】
公众号名称：【填写名称】
种子文章链接：【粘贴链接】
目标：梳理该公众号当前可访问的历史文章，输出观点数据库、时间线、
主题地图、公司/产品索引、过去一年观点变化和结论化 HTML/PDF 报告。
同时输出 Excel 总览、按年月归档的逐篇 MD，以及 index.md 阅读入口。
请先验证一页目录和一篇正文；验证通过后继续完成。
遇到扫码登录、付费服务或缺少权限时告诉我，不要导出浏览器凭证。
```

首次环境检查、扫码登录、成功标准和常见问题见 [FIRST_RUN.md](FIRST_RUN.md)。市场验证是可选项，需要时在请求中补充“结合文章观点和实际市场表现验证”。

## 文件放在哪里

每个公众号使用独立研究目录，**不是 Skill 安装目录**。`work/` 保存主库和原始响应，`outputs/<交付批次>/` 保存本次 Excel、逐篇 MD、数据快照及报告；根目录 `index.md` 指向最新验收批次并保留历史入口。

完整文件夹树、文件命名、Excel 字段及更新规则见 [目录和阅读交付规范](references/workspace-layout.md)。新批次不覆盖旧批次，因此旧 Excel/MD 上的批注会保留；批注不会自动同步回数据库。整包移动才能保留本地阅读链接。

已有 SQLite 可以直接导出阅读文件，无需重新登录或抓取：

```text
python scripts/export_reading.py --db <已有数据库.sqlite> --out <新的批次目录>
python scripts/export_reading.py --self-check
```

上述命令从 Skill 目录运行；在研究目录中运行时使用脚本的绝对路径。脚本生成逐篇 MD、目录、数据库快照及 Excel 输入 JSON；**Excel 需再由当前环境的表格工具生成**，不能把 JSON 改后缀当作 Excel。工具选择、可选 builder 及验收要求见[目录和阅读交付规范](references/workspace-layout.md#执行)。

## 环境与测试边界

- **研究执行**：需要能读取本地指令、执行脚本的 coding agent，以及本次任务所需的浏览器、文件和报告工具。仅能聊天或搜索网页的界面不能独立完成全部流程。安装 Skill 本身不会安装浏览器插件、采集器或模型服务。
- **Python 自检与 MD 导出**：仅依赖标准库，不需要 API Key、不联网，也不读取真实浏览器数据。Excel 与 PDF 是独立输出步骤，缺少某个示例工具的依赖时可选择符合交付规范的现有工具，不必切换到 Codex。
- **跨平台与实测**：指令针对 Windows / macOS 编写；现有验证来自 macOS / Codex 环境，包括 Python 离线自检和真实语料阅读导出。Windows 及其他 harness 尚未完成全流程实机验证；脚本自检通过不代表微信接口可用。首次使用须在目标电脑验证。
- **费用**：Skill 本身没有服务收费接口；运行智能体可能消耗现有产品额度。外部付费数据或模型服务须另行取得用户同意。

在仓库根目录可执行：

```bash
python scripts/validate_workspace.py --self-check
python scripts/validate_workspace.py --db /path/to/archive.sqlite --manifest /path/to/manifest.json --html /path/to/report.html
```

第一条仅创建临时样本并输出 `self-check passed`。第二条检查基础字段、内容等级计数、manifest 一致性、章节标记和部分工作备注式措辞。它**不验证正文真实性、研究结论、市场数据或 PDF 版面**；这些仍需独立核查。

## 仓库内容

```text
SKILL.md                       智能体主流程
FIRST_RUN.md                   首次运行步骤与可复制指令
agents/openai.yaml             可选 OpenAI 界面元数据，其他环境无需使用
references/data-contract.md    SQLite 与 manifest 规范
references/platform-auth.md    平台适配和认证边界
references/report-contract.md  结论化报告与 PDF 验收规范
references/workspace-layout.md 存放位置、阅读交付与增量规则
scripts/validate_workspace.py  纯 Python 本地基础校验
scripts/export_reading.py      SQLite→逐篇 MD、目录与表格输入
scripts/build_overview.mjs     可选 Excel 示例，需要宿主表格依赖
```

## 隐私、授权与已知限制

- 仓库只发布 Skill 和通用文档，不包含公众号原文、私人研究报告、数据库、会话、Cookie 或浏览器配置。
- 微信读书是否收录、登录状态、分页行为和访问频率限制都可能改变；单篇可读不等于历史目录完整可取。遇到验证、限制或授权失败，应停止当前采集并说明原因，使用合规本地导出等回退路线。
- 已登录页面可在受控会话内使用；不复制默认浏览器配置，不自动解密系统钥匙串，不把凭证上传到第三方。
- 文章版权归原权利人。个人访问权限不代表获得转载、公开分发或商业使用授权。本项目与微信、微信读书、腾讯及 OpenAI 无隶属关系。
- Skill 代码与文档采用 [MIT License](LICENSE)，允许按许可证复用、修改和分发；该授权不涵盖第三方文章、平台内容或用户的私有研究数据。

提交 Issue 时只提供脱敏错误、系统和工具版本、失败阶段；不要上传 Cookie、二维码、完整网页响应或私人数据库。
