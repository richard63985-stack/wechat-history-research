# 公众号历史研究 · WeChat History Research

将一个微信公众号**当前可访问的历史文章**整理为观点数据库、核心时间线、主题地图、公司/产品索引，以及结论化 HTML / PDF 研究报告。

这是供 Codex 使用的 **工作流 Skill**，包含指令、数据规范和一个本地校验脚本；**不是免登录爬虫，也不附带可直接批量抓取任意公众号的采集器**。实际采集由智能体根据可用浏览器、授权和数据源完成，首次使用必须验证目标公众号。

[首次运行指南](FIRST_RUN.md) · [智能体执行指令](SKILL.md)

## 能得到什么

| 交付 | 内容 |
| --- | --- |
| 历史观点数据库 | SQLite 原始语料与逐篇摘要、观点、来源、证据等级 |
| 核心观点时间线 | 关键观点在不同阶段的延续、转折与变化 |
| 主题地图 | 主题分布、重点方向及关注度迁移 |
| 公司 / 机构 / 产品索引 | 实体归一化、出现文章与原文链接 |
| 过去一年观点变化 | 最近 12 个月与此前 12 个月对比 |
| 总括研究报告 | 当年分阶段结论、核心判断、同版 HTML / PDF |
| 可选的市场验证 | 文章观点与标的、基准的后续表现对照 |

核心顺序是：**先验证目录和正文 → 归档与去重 → 逐篇研究 → 跨篇聚合 → 写终稿 → 验收 PDF**。总量、全文覆盖率和来源限制始终可复核；摘要不冒充全文，价格同向不写成因果证明。

## 安装

### 推荐：让 Codex 安装

将下面这段话发给 Codex：

```text
请使用 skill-installer，从以下仓库安装 wechat-history-research：
https://github.com/richard63985-stack/wechat-history-research
SKILL.md 位于仓库根目录，路径为 .，安装名称为 wechat-history-research。
如果已经存在同名 Skill，请先比较版本，不覆盖我的本地修改。
```

### 手动安装

需要 Git；运行校验脚本还需要 Python 3.10+。以下命令适用于**尚未安装同名 Skill**的新环境；目标目录存在时应先比较，不强制覆盖。

macOS 终端：

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/richard63985-stack/wechat-history-research.git "$HOME/.agents/skills/wechat-history-research"
python3 "$HOME/.agents/skills/wechat-history-research/scripts/validate_workspace.py" --self-check
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
git clone https://github.com/richard63985-stack/wechat-history-research.git "$env:USERPROFILE\.agents\skills\wechat-history-research"
py -3 "$env:USERPROFILE\.agents\skills\wechat-history-research\scripts\validate_workspace.py" --self-check
```

如 Python 启动器不可用，让 Codex 查找已有 Python，不必为此重复安装。使用 WSL 时按 **Codex 实际运行环境**选择安装位置，不混用 Windows 和 WSL 的用户目录。

本指南采用当前官方文档的用户级目录 `.agents/skills`。已有版本也可能位于 `.codex/skills`，若已被识别，无需重复安装。安装后在新任务中调用；未显示时重启 Codex。安装位置和调用方式参见 [OpenAI 官方 Skills 文档](https://learn.chatgpt.com/docs/build-skills)。

## 第一次怎么用

在**独立的本地研究文件夹**中创建 Codex 任务，不要把文章原文或报告写进这个公共仓库。准备公众号名称和一篇文章链接，再发送：

```text
使用 $wechat-history-research，并先阅读 FIRST_RUN.md。
公众号名称：【填写名称】
种子文章链接：【粘贴链接】
目标：梳理该公众号当前可访问的历史文章，输出观点数据库、时间线、
主题地图、公司/产品索引、过去一年观点变化和结论化 HTML/PDF 报告。
请先验证一页目录和一篇正文；验证通过后继续完成。
遇到扫码登录、付费服务或缺少权限时告诉我，不要导出浏览器凭证。
```

首次环境检查、扫码登录、成功标准和常见问题见 [FIRST_RUN.md](FIRST_RUN.md)。市场验证是可选项，需要时在请求中补充“结合文章观点和实际市场表现验证”。

## 环境与测试边界

- **研究执行**：需要支持本地 Skill 的 Codex，以及相应的浏览器 / 文件 / PDF 能力。安装 Skill 本身不会安装浏览器插件、采集器或模型服务。
- **脚本自检**：仅依赖 Python 标准库，不需要 API Key，不联网，也不读取真实浏览器数据。
- **跨平台**：指令针对 Windows / macOS 编写，发布前已在 macOS 通过 Python 离线自检。Windows 尚未实机验证；脚本自检通过不代表微信接口可用，也不代表完整采集或 PDF 流程已实测。首次使用须在目标电脑验证。
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
agents/openai.yaml             Codex 界面信息
references/data-contract.md    SQLite 与 manifest 规范
references/platform-auth.md    平台适配和认证边界
references/report-contract.md  结论化报告与 PDF 验收规范
scripts/validate_workspace.py  纯 Python 本地基础校验
```

## 隐私、授权与已知限制

- 仓库只发布 Skill 和通用文档，不包含公众号原文、私人研究报告、数据库、会话、Cookie 或浏览器配置。
- 微信读书是否收录、登录状态、分页行为和访问频率限制都可能改变；单篇可读不等于历史目录完整可取。遇到验证、限制或授权失败，应停止当前采集并说明原因，使用合规本地导出等回退路线。
- 已登录页面可在受控会话内使用；不复制默认浏览器配置，不自动解密系统钥匙串，不把凭证上传到第三方。
- 文章版权归原权利人。个人访问权限不代表获得转载、公开分发或商业使用授权。本项目与微信、微信读书、腾讯及 OpenAI 无隶属关系。
- Skill 代码与文档采用 [MIT License](LICENSE)，允许按许可证复用、修改和分发；该授权不涵盖第三方文章、平台内容或用户的私有研究数据。

提交 Issue 时只提供脱敏错误、系统和工具版本、失败阶段；不要上传 Cookie、二维码、完整网页响应或私人数据库。
