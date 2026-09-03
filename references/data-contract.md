# 数据契约

在新项目中使用下面的最小 SQLite 结构。可以增加字段或索引，但不要改变状态含义；路径一律保存为项目相对路径。

```sql
CREATE TABLE IF NOT EXISTS articles (
    original_id TEXT PRIMARY KEY,
    account_name TEXT NOT NULL,
    account_id TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    author TEXT NOT NULL DEFAULT '',
    published_at INTEGER NOT NULL DEFAULT 0,
    url TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    content_level TEXT NOT NULL,
    source_type TEXT NOT NULL,
    raw_path TEXT NOT NULL DEFAULT '',
    content_sha256 TEXT NOT NULL DEFAULT '',
    error TEXT NOT NULL DEFAULT '',
    fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS article_analysis (
    original_id TEXT PRIMARY KEY,
    synopsis TEXT NOT NULL,
    core_view TEXT NOT NULL,
    primary_theme TEXT NOT NULL,
    themes_json TEXT NOT NULL,
    entities_json TEXT NOT NULL,
    attribution TEXT NOT NULL,
    evidence_level TEXT NOT NULL,
    analyzed_at TEXT NOT NULL,
    FOREIGN KEY(original_id) REFERENCES articles(original_id)
);

CREATE TABLE IF NOT EXISTS article_themes (
    original_id TEXT NOT NULL,
    theme TEXT NOT NULL,
    score REAL NOT NULL,
    rank INTEGER NOT NULL,
    PRIMARY KEY(original_id, theme)
);

CREATE TABLE IF NOT EXISTS article_entities (
    original_id TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    mentions INTEGER NOT NULL,
    PRIMARY KEY(original_id, entity_name)
);
```

## 状态

`content_level` 只能取：

- `full`：取得可用正文；
- `summary`：只有目录摘要；
- `metadata`：只有标题、日期、链接等元数据；
- `failed`：目录记录存在，但正文和摘要均不可用。

`evidence_level` 沿用同一等级。只有 `full` 可以作为强观点证据；`summary` 必须在引用处标注为摘要级。

`source_type` 记录实际来源，如 `official_export`、`weread_web`、`local_html`、`local_json` 或已验证的第三方来源名。

## Manifest

数据库同目录保存 UTF-8 JSON manifest：

```json
{
  "account": "公众号名称",
  "account_id": "平台稳定标识",
  "source": "weread_web",
  "access_scope": "当前渠道可访问历史",
  "article_count": 0,
  "body_full": 0,
  "summary_only": 0,
  "metadata_only": 0,
  "failed": 0,
  "earliest": null,
  "latest": null,
  "generated_at": "ISO-8601",
  "database": "data/archive.sqlite"
}
```

四种内容等级之和必须等于 `article_count`。manifest 的日期来自数据库，而不是文件时间。

## 幂等与证据

- `original_id` 是唯一键；重复采集执行 upsert，不新增重复行。
- 原始响应按文章或分页落盘，保存 SHA-256；数据库中的清洗正文不是唯一证据。
- 每篇正文单独提交或按小批次提交，避免中断后全部回滚。
- 错误写入 `error`，重试成功后清空；失败记录仍保留在目录中。
- 发布日期保留原始时间戳；展示时再按项目时区格式化。
