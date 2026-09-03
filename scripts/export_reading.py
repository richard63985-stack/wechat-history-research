#!/usr/bin/env python3
"""Export a read-only SQLite snapshot, dated Markdown and Excel input JSON."""

import argparse
from collections import Counter, defaultdict
from contextlib import closing
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sqlite3
import tempfile
import unicodedata
from urllib.parse import quote, urlsplit


LABELS = {"full": "全文", "summary": "仅摘要", "metadata": "仅目录", "failed": "获取失败"}


def md(value):
    text = html.escape(str(value or ""), quote=False)
    return re.sub(r"([\\`*_{}\[\]<>#!|])", r"\\\1", text)


def safe_title(title):
    title = unicodedata.normalize("NFC", title)
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title)
    return re.sub(r"\s+", " ", title).strip(" .")[:36].rstrip(" .") or "无标题"


def offset(value):
    if not re.fullmatch(r"[+-]\d{2}:\d{2}", value):
        raise ValueError("UTC offset must be +/-HH:MM")
    hours, minutes = map(int, value[1:].split(":"))
    if minutes > 59 or hours * 60 + minutes > 14 * 60:
        raise ValueError("UTC offset outside supported range")
    return timezone(timedelta(minutes=(hours * 60 + minutes) * (1 if value[0] == "+" else -1)))


def read_rows(db):
    with closing(sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        rows = [dict(r) for r in con.execute("SELECT * FROM articles ORDER BY published_at DESC, original_id")]
        analyses = {r["original_id"]: dict(r) for r in con.execute("SELECT * FROM article_analysis")} if "article_analysis" in tables else {}
    return rows, analyses


def normalize(rows, analyses, tz):
    result, ids, accounts = [], set(), set()
    for raw in rows:
        article_id = str(raw["original_id"] or "")
        if not article_id or article_id in ids:
            raise ValueError("Missing or duplicate article ID")
        ids.add(article_id)
        account = raw.get("account_name", raw.get("mp_name", ""))
        account_id = str(raw.get("account_id", raw.get("book_id", "")))
        accounts.add((account, account_id))
        analysis = analyses.get(raw["original_id"], {})
        body, summary = raw.get("body") or "", raw.get("summary") or ""
        level = raw.get("content_level")
        if level is None:  # Legacy archive: body_status + available text, never rewrite its schema.
            level = "full" if raw.get("body_status") == "ok" and body.strip() else "summary" if summary.strip() else "metadata"
        if level not in LABELS or (level == "full" and not body.strip()) or (level == "summary" and not summary.strip()):
            raise ValueError("Invalid content level or missing corresponding text: " + article_id)
        timestamp = int(raw.get("published_at") or 0)
        date = datetime.fromtimestamp(timestamp, tz).strftime("%Y-%m-%d") if timestamp > 0 else "undated"
        title = str(raw.get("title") or "无标题")
        suffix = hashlib.sha256((account_id + "\0" + article_id).encode()).hexdigest()[:12]
        folder = f"articles/{date[:4]}/{date[5:7]}" if date != "undated" else "articles/undated"
        path = f"{folder}/{date}_{safe_title(title)}__{suffix}.md"
        labels = {}
        for field in ("themes", "entities"):
            labels[field] = json.loads(analysis.get(field + "_json") or "[]")
            if not isinstance(labels[field], list) or not all(isinstance(x, str) for x in labels[field]):
                raise ValueError("Expected JSON string list for " + field)
        url = raw.get("url") or ""
        if url and (urlsplit(url).scheme not in ("http", "https") or not urlsplit(url).netloc):
            raise ValueError("Unsupported source URL: " + article_id)
        result.append({
            "original_id": article_id, "account": account, "account_id": account_id,
            "date": date, "published_at": timestamp, "title": title, "url": url,
            "content_level": level, "content_label": LABELS[level], "body": body,
            "source_summary": summary, "synopsis": analysis.get("synopsis", ""),
            "core_view": analysis.get("core_view", ""), "primary_theme": analysis.get("primary_theme", ""),
            **labels, "analysis_method": analysis.get("method", ""),
            "attribution": analysis.get("attribution", ""), "fetched_at": raw.get("fetched_at", ""),
            "error": raw.get("error", ""), "body_chars": len(body), "md_path": path,
            "read_num": raw.get("read_num"), "like_num": raw.get("like_num"),
        })
    if not result or len(accounts) != 1:
        raise ValueError("Export requires one nonempty account archive")
    if len({r["md_path"].casefold() for r in result}) != len(result):
        raise ValueError("Filename collision")
    return result


def article_markdown(row):
    metadata = {k: row[k] for k in ("original_id", "account", "date", "content_level", "url")}
    header = "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in metadata.items()) + "\n---\n\n"
    parts = [header + "# " + md(row["title"]),
             f"[返回本月目录](index.md) · {row['date']} · **{row['content_label']}**",
             f"来源：<{quote(row['url'], safe=':/?&=%+#')}>" if row["url"] else "来源：未提供原文链接",
             "本文是数据库采集文字的阅读副本，不包含原网页图片与版式。"]
    if row["content_level"] != "full":
        parts.append("> **未取得全文。以下仅呈现实际取得的摘要或目录信息，不构成完整文章。**")
    parts += ["## 已有研究提炼（非原文）", "主要主题：" + md(row["primary_theme"] or "未分类"),
              "涉及实体：" + md("、".join(row["entities"]) or "未提取"),
              "摘要：" + md(row["synopsis"] or "尚无研究摘要"),
              "核心观点：" + md(row["core_view"] or "尚无观点提炼")]
    if row["analysis_method"]:
        parts.append("提炼方法：" + md(row["analysis_method"]))
    if row["attribution"]:
        parts.append("观点归属：" + md(row["attribution"]))
    if row["content_level"] == "full":
        parts += ["## 采集正文", md(row["body"])]
    elif row["content_level"] == "summary":
        parts += ["## 来源摘要（非全文）", md(row["source_summary"])]
    else:
        parts += ["## 内容状态", "未取得正文或可用摘要，仅保留目录记录。"]
    return "\n\n".join(parts) + "\n"


def export(db, out, utc_offset="+08:00"):
    if not db.is_file():
        raise ValueError("Database does not exist")
    out.mkdir(parents=True, exist_ok=False)  # New immutable batch; never overwrite a user's notes.
    (out / "data").mkdir()
    snapshot = out / "data/archive.sqlite"
    with closing(sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)) as source:
        with closing(sqlite3.connect(snapshot)) as target:
            source.backup(target)
    rows = normalize(*read_rows(snapshot), offset(utc_offset))
    months = defaultdict(list)
    for row in rows:
        path = out / row["md_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        content = article_markdown(row)
        path.write_text(content, encoding="utf-8")
        row["md_sha256"] = hashlib.sha256(content.encode()).hexdigest()
        months[path.parent.relative_to(out).as_posix()].append(row)
    for folder, articles in months.items():
        back = "../" * len(Path(folder).parts) + "index.md"
        lines = [f"# {articles[0]['date'][:7]} 文章目录", f"[返回总览]({back})", "| 日期 | 标题 | 内容等级 |", "|---|---|---|"]
        lines += [f"| {a['date']} | [{md(a['title'])}]({quote(Path(a['md_path']).name)}) | {a['content_label']} |" for a in articles]
        (out / folder / "index.md").write_text("\n\n".join(lines[:2]) + "\n\n" + "\n".join(lines[2:]) + "\n", encoding="utf-8")
    counts = dict(Counter(r["content_level"] for r in rows))
    dates = [r["date"] for r in rows if r["date"] != "undated"]
    payload = {"account": rows[0]["account"], "generated_at": datetime.now(timezone.utc).isoformat(),
               "utc_offset": utc_offset, "article_count": len(rows), "content_counts": counts,
               "earliest": min(dates) if dates else None, "latest": max(dates) if dates else None,
               "database": "data/archive.sqlite", "articles": [{k: v for k, v in r.items() if k != "body"} for r in rows]}
    (out / "data/reading.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {"account": payload["account"], "account_id": rows[0]["account_id"],
                "source": "local_sqlite_export", "access_scope": "源数据库当前样本，未重新采集",
                "article_count": len(rows), "body_full": counts.get("full", 0),
                "summary_only": counts.get("summary", 0), "metadata_only": counts.get("metadata", 0),
                "failed": counts.get("failed", 0), "earliest": payload["earliest"], "latest": payload["latest"],
                "generated_at": payload["generated_at"], "database": "data/archive.sqlite"}
    (out / "data/manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [f"# {md(payload['account'])} · 历史文章审阅入口", "",
             f"当前可访问 {len(rows)} 条记录；全文 {counts.get('full', 0)}，仅摘要 {counts.get('summary', 0)}，仅目录 {counts.get('metadata', 0)}，失败 {counts.get('failed', 0)}。",
             f"日期范围：{payload['earliest']} 至 {payload['latest']}；展示时区 UTC{utc_offset}。", "",
             "[Excel 总览](overview.xlsx) · [数据库快照](data/archive.sqlite) · [导出清单](data/reading.json)", "",
             "Excel 用于筛选与批注，Markdown 用于逐篇阅读；研究提炼与采集正文分开呈现。仅摘要、仅目录记录不能作为全文使用。",
             "同一批次保留不动；后续更新生成新批次。人工批注请另存，交接时复制整个批次目录以保留相对链接。", "",
             "## 按月阅读", "", "| 月份 | 文章数 | 全文数 |", "|---|---:|---:|"]
    for folder in sorted(months, reverse=True):
        items = months[folder]
        lines.append(f"| [{items[0]['date'][:7]}]({folder}/index.md) | {len(items)} | {sum(r['content_level'] == 'full' for r in items)} |")
    (out / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert len(list((out / "articles").rglob("*.md"))) == len(rows) + len(months)
    return payload


def self_check():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        db = root / "source.sqlite"
        with closing(sqlite3.connect(db)) as con, con:
            con.execute("CREATE TABLE articles (original_id TEXT PRIMARY KEY, account_name TEXT, title TEXT, published_at INTEGER, url TEXT, body TEXT, summary TEXT, content_level TEXT)")
            con.executemany("INSERT INTO articles VALUES (?,?,?,?,?,?,?,?)", [
                ("a", "测试账号", '同名:/\\?*"标题', 1735689600, "https://example.com/a", "第一段\n\n第二段", "", "full"),
                ("b", "测试账号", '同名:/\\?*"标题', 1735689600, "https://example.com/b", "", "来源摘要", "summary"),
                ("c", "测试账号", "CON", 0, "", "", "", "metadata"),
            ])
        source_hash = hashlib.sha256(db.read_bytes()).hexdigest()
        data = export(db, root / "out")
        assert data["article_count"] == 3 and data["content_counts"]["full"] == 1
        assert len({r["md_path"] for r in data["articles"]}) == 3
        for row in data["articles"]:
            assert not re.search(r'[<>:"\\|?*]', row["md_path"])
            assert (root / "out" / row["md_path"]).is_file()
        assert "未取得全文" in (root / "out" / data["articles"][1]["md_path"]).read_text(encoding="utf-8")
        try:
            export(db, root / "out")
        except FileExistsError:
            pass
        else:
            raise AssertionError("Existing batch was overwritten")
        assert hashlib.sha256(db.read_bytes()).hexdigest() == source_hash
        legacy = [{"original_id": "old", "mp_name": "测试账号", "title": "=1+1", "published_at": 1, "body_status": "empty", "summary": "仅摘要"}]
        assert normalize(legacy, {}, offset("+08:00"))[0]["content_level"] == "summary"
    print("reading export self-check passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path)
    parser.add_argument("--out", type=Path, help="New batch directory; existing paths are refused")
    parser.add_argument("--utc-offset", default="+08:00")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        self_check()
    elif args.db and args.out:
        data = export(args.db, args.out, args.utc_offset)
        print(json.dumps({"articles": data["article_count"], "levels": data["content_counts"], "out": str(args.out)}, ensure_ascii=False))
    else:
        parser.error("Provide --db and --out, or --self-check")
