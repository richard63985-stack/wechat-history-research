# 跨平台与认证

## 认证原则

优先让用户在 Codex 内置浏览器或受控 Chrome 中手动登录微信读书，再在该会话中验证目录和正文。认证只用于用户有权访问的页面。

已有受控会话可以原位访问，不复制登录态。新启动自动化浏览器时使用项目专用、隔离的配置目录，例如 `work/browser-profile/`。不要复制或解析默认 Chrome/Edge 配置，不调用系统钥匙串解密 “Chrome Safe Storage”，不在日志、数据库、命令输出或报告中保存 Cookie、token、Bearer header。

若现有采集器只能接收 Cookie：

1. 先寻找浏览器会话内请求或本地导出路线。
2. 仍需 Cookie 时，向用户说明用途和风险，并取得明确授权。
3. 仅通过当前进程环境或受限临时文件传入，运行后清除；不得写入 Skill、源码或交付目录。

## Windows/macOS 兼容规则

- Python 使用运行当前脚本的解释器；调用子脚本时优先 `sys.executable`。
- 文件路径使用 `pathlib.Path`，本地 URL 使用 `Path.resolve().as_uri()`。
- SQLite、JSON、HTML 文件统一 UTF-8；CSV 若面向 Excel，可额外输出 UTF-8 BOM 版本。
- 不依赖 Bash 管道、PowerShell 专属语法或固定盘符完成核心流程。
- 临时目录使用系统临时目录或项目 `work/`，最终交付写入项目 `outputs/`。

## PDF 输出

优先使用环境已有的 PDF 能力。需要浏览器打印时，按平台探测 Chrome/Edge，不硬编码唯一位置：

- macOS 常见 Chrome：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`。
- Windows 依次检查 `PATH`、`ProgramFiles`、`ProgramFiles(x86)` 和 `LOCALAPPDATA` 下的 Chrome/Edge。

使用隔离打印配置目录，并加入 `--no-first-run`、`--no-default-browser-check`、`--no-pdf-header-footer`。只在不含登录态、仅渲染本地报告的临时打印配置中考虑 `--password-store=basic`，不将其用于登录或长期凭证存储。输出路径和 HTML URL 均使用绝对路径。

浏览器已写出 PDF 但进程未退出时，先确认 PDF 可打开，再定位命令行中包含该隔离配置路径的根进程；只终止这个根进程。不得按浏览器名称批量结束进程，以免影响用户正在使用的浏览器。

Windows 容易因文件锁导致覆盖失败；打印前使用新文件名，成功后再复制到最终文件。macOS 遇到钥匙串弹窗通常说明误用了默认浏览器 Cookie/Profile，应停止并改用隔离配置，而不是要求用户长期授权钥匙串访问。

## 最小健康检查

每个新公众号都要记录：

- 目录请求成功时间与返回条数；
- 一篇正文的标题、稳定 ID、正文字符数；
- 是否需要登录；
- 当前可见最早/最晚日期；
- 分页停止条件与重复 ID 数；
- 失败时的 HTTP 状态、页面类型或明确错误，不记录认证内容。
