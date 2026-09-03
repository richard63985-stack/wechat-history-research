# 首次运行指南

读者可以是使用者，也可以是执行本 Skill 的智能体。这里负责“第一次如何启动”；正式数据与报告规则以 [SKILL.md](SKILL.md) 及其引用文件为准。

## 安装与调用

### 通用方式：直接读取本地指令

把整个仓库下载或克隆到本地工具目录，文件夹命名为 `wechat-history-research`。保留全部配套文件，确保 `SKILL.md` 直接位于该文件夹内，而不是又嵌套一层；使用 GitHub 的 Download ZIP 时，解压后检查这一层级。

让当前 coding agent 完整读取该 `SKILL.md` 和本指南，并按步骤读取引用文件，即可按同一工作流执行。此方式不要求特定的 Skill 菜单或 `/`、`$` 命令，但仍需要文件访问、脚本执行和任务所需的工具权限；它不会自动注册一个快捷命令。

### 原生 Skills 方式：按运行环境选择

以下是本地运行环境的推荐目录；每个表格路径都指向**整个仓库文件夹**，其下直接包含 `SKILL.md`。选项目级或用户级其中一种即可。官方说明核对于 **2026-09-03**，不是各环境完整流程的实测认证。

| 运行环境 | 项目级目录（相对项目根目录） | 用户级目录 | 如何调用与核对 |
| --- | --- | --- | --- |
| Codex | `.agents/skills/wechat-history-research/` | `~/.agents/skills/wechat-history-research/` | CLI / IDE 中使用 `$wechat-history-research`；其他界面从 Skills 选择器选择，或按路径读取。[官方说明](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code | `.claude/skills/wechat-history-research/` | `~/.claude/skills/wechat-history-research/` | 输入 `/wechat-history-research`，再给出本次任务。[官方说明](https://code.claude.com/docs/en/skills) |
| Cursor | `.cursor/skills/wechat-history-research/` | `~/.cursor/skills/wechat-history-research/` | 在 Skills 列表核对后，在 Agent 对话中输入 `/wechat-history-research` 或明确要求使用该 Skill。[官方说明](https://cursor.com/docs/skills) |
| OpenCode | `.opencode/skills/wechat-history-research/` | `~/.config/opencode/skills/wechat-history-research/` | 告诉智能体“用 skill 工具加载 wechat-history-research”；不假定会自动创建同名斜杠命令。[官方说明](https://opencode.ai/docs/skills/) |

Cursor 与 OpenCode 也支持 `.agents/skills`，可与 Codex 共用一份；Claude Code 采用上表的 `.claude/skills`。已有可识别的安装无需复制多份。`agents/openai.yaml` 仅是可选 OpenAI 界面信息，不要求其他环境解析它。

**Windows / macOS 手动安装示例**：以下以 Claude Code 的用户级目录为例，其他工具换成上表对应目录。需要 Git；目录已存在时先比较，不覆盖本地修改。

macOS 终端：

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/richard63985-stack/wechat-history-research.git "$HOME/.claude/skills/wechat-history-research"
python3 "$HOME/.claude/skills/wechat-history-research/scripts/validate_workspace.py" --self-check
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
git clone https://github.com/richard63985-stack/wechat-history-research.git "$env:USERPROFILE\.claude\skills\wechat-history-research"
py -3 "$env:USERPROFILE\.claude\skills\wechat-history-research\scripts\validate_workspace.py" --self-check
```

表格中的 `~` 代表**智能体实际运行环境的用户目录**：macOS 通常是 `/Users/用户名`，Windows 原生运行时通常对应 `$env:USERPROFILE`。WSL、SSH、容器或云端任务使用各自的文件系统，不能默认读取本机 Skill 或浏览器登录态。Python 命令不可用时先查找已有解释器。安装后检查 Skill 列表；未显示时刷新或重启当前工具，仍不可见则使用按路径读取方式。

Codex 也可用其 `skill-installer` 安装本仓库，指定仓库内路径 `.`、安装名称 `wechat-history-research`。这是 Codex 的可选便利入口，不是其他环境的安装前提。

## 1. 准备一个独立研究文件夹

在当前智能体中打开或指定研究文件夹，例如 `Documents/wechat-research`。**不要把安装目录或这个公共仓库当作数据输出目录**。

准备以下信息：

- 目标公众号名称；
- 一篇能打开的公众号文章链接；
- 可选：微信读书网页阅读链接、已有本地导出；
- 是否需要市场表现验证；
- 希望覆盖的时间范围。未指定时按当前渠道可访问历史处理。

公众号文章数、市场截止日和报告年份从本次数据生成，不沿用旧案例数字。

## 2. 先检查环境，不急着采集

智能体应先定位当前 Skill 目录并完整阅读主指令，然后检查：

1. Skill 已能被发现，或用户已明确给出其本地 `SKILL.md` 路径。
2. 当前操作系统、可用 Python 3.10+ 解释器及研究目录写入权限。
3. 可用的浏览器控制能力：内置浏览器、已配置的浏览器工具或 MCP 均按本环境的实际能力使用；普通网页检索不等于可以操作已登录微信读书。没有浏览器能力时可先处理用户提供的本地归档。
4. 表格生成和预览能力是否齐备；若需 PDF，再检查打印和逐页渲染工具。遵循交付规范选择现有工具，不要求安装某家平台的私有依赖。

从 **Skill 目录**运行离线自检：

```text
python scripts/validate_workspace.py --self-check
```

macOS 可用 `python3`，Windows 可用 `py -3`；在研究目录运行时，应把脚本路径替换为实际 Skill 目录下的绝对路径。预期输出 `self-check passed`。无需 `pip install`，也无需输入 API Key。

缺少工具时先说明缺的是哪一项，以及能否用现有工具替代。需要新安装、额外权限或付费时，按所在环境的审批流程处理；不修改全局浏览器配置。

## 3. 登录与最小验证

可以先直接访问种子文章。若采用微信读书路线，打开 [微信读书网页](https://weread.qq.com/)，由使用者手动扫码登录；智能体只操作用户有权访问的页面。

优先使用已有受控会话。新启动自动化浏览器时使用项目专用配置。不得索要微信密码、在对话中粘贴 Cookie，或读取默认 Chrome/Edge 凭证库。

第一次真实验证必须同时取得：

| 检查 | 成功标准 |
| --- | --- |
| 目录 | 至少一页目标公众号目录，含稳定 ID、标题和发布日期 |
| 正文 | 至少一篇实际正文，核对标题与文章 ID；不是摘要、登录页或错误提示 |
| 来源 | 记录来源、采集时间和是否需要登录，不记录认证内容 |

验证失败时给出“失败阶段、已经取得什么、仍缺什么”，保留已有内容。出现访问验证、限流或登录失效时停止该路线，不绕过限制，不连续反复请求。

## 4. 选择本次运行范围

下面提示词不依赖特定调用语法。已原生安装时，可在前面加上表中对应的调用；否则填写本地 `SKILL.md` 路径。

### 只做首跑验证

```text
使用 wechat-history-research，完整读取其 SKILL.md 和 FIRST_RUN.md。
若未自动识别，Skill 路径：【本地 SKILL.md 的绝对路径】。
研究输出目录：【独立研究目录】
公众号：【名称】
种子文章：【链接】
这次只验证一页目录和一篇正文。报告可用渠道、限制和缺少的权限，
不要批量采集，也不要生成整份研究报告。
```

### 验证后完成研究

```text
使用 wechat-history-research，完整读取其 SKILL.md 和 FIRST_RUN.md。
若未自动识别，Skill 路径：【本地 SKILL.md 的绝对路径】。
研究输出目录：【独立研究目录】
公众号：【名称】
种子文章：【链接】
请在当前研究目录完成：可访问历史归档、观点数据库、核心时间线、
主题地图、公司/机构/产品索引、过去一年观点变化，以及当年分阶段的
结论化 HTML/PDF 报告。同时生成 Excel 总览、按年月归档的逐篇 MD，
建立 index.md 阅读入口。先验证目录和正文，通过后继续。
仅在需要我扫码、选择付费服务或补充授权时暂停；现有结果不要覆盖。
```

需要金融验证时补充：“对原文可检验的方向和标的，结合公开市场表现做验证，区分价格结果与基本面证据。”

## 5. 数据落地与最终验收

一个公众号一个研究目录。根目录 `index.md` 是人类入口；`work/` 保留主库与原始响应；`outputs/<交付批次>/` 保留可移动的 Excel、MD、索引、数据快照及报告。具体树形结构和增量规则以 [目录和阅读交付规范](references/workspace-layout.md) 为准。

智能体需要适配现有采集器或导入文件，本仓库没有 `collect` / `login` / `generate-pdf` 一键命令；不要虚构这些命令。旧数据库字段与新规范不同，先备份并明确映射，不能只改字段名让校验通过。

运行基础校验后，另外核对文章去重、内容真实性、所有关键数字和最终 PDF 全页。交付应明确哪些检查通过、哪些没有完成；“脚本 PASS”不等于“研究已验收”。

如果已有数据库，只需发送：“使用本 Skill，把【数据库路径】导出为新的阅读包：Excel 总览、按日期和标题归档的逐篇 MD、index.md；不要重新采集，不覆盖旧文件。” 纯 Python 导出能独立运行；Excel 还需要所在环境的表格能力，详见上述规范。

## 常见问题

| 现象 | 处理 |
| --- | --- |
| Skill 不出现在列表 | 核对安装位置、文件夹层级和 `SKILL.md`；重启后仍不可见时让智能体报告实际扫描路径，避免重复安装同名版本 |
| `/wechat-history-research` 没有生效 | 各环境调用语法不同；按上表调用，或直接指定本地 `SKILL.md` 路径，不把 Skill 当作所有环境共有的斜杠命令 |
| 找不到 `@oai/artifact-tool` | 这是可选 Excel 示例的私有依赖；改用当前环境已有的表格工具，按同一字段和验收规范生成真正的 `.xlsx`，无需为此安装 Codex |
| Python 命令找不到 | 让智能体定位现有解释器；没有时再说明安装需求 |
| 手机上空白、网页能读 | 使用已验证的网页路线；无需先认定手机故障 |
| 单篇能读、目录取不到 | 只证明单篇通路，不能开始宣称完整采集；尝试用户提供的目录或本地导出 |
| 平台显示 500+，实际少于它 | 核对去重和分页，保留差额；写“当前可访问 N 篇” |
| 弹出 Chrome Safe Storage | 取消此次凭证读取，让智能体检查是否误用默认配置，改用受控会话或隔离配置 |
| Windows 的某个浏览器工具不可用 | 使用该环境现有的受控浏览器能力或本地导入；不要假定 macOS 的工具可以原样调用 |
| PDF 已生成但浏览器不退出 | 先验证文件，再只结束本次隔离打印进程，不能批量结束 Chrome/Edge |
| 校验提示工作备注式措辞 | 人工确认是否为正文备注或原文引用；修改表达或说明误报，不把词语检查当成内容质量判断 |

以后增量更新时，明确给出已有数据库路径和新的截止日，复用稳定文章 ID，仅补新增或缺失数据；本 Skill 不会自行创建定时任务。
