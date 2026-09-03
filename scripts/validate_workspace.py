#!/usr/bin/env python3
"""Validate a WeChat history archive and its conclusion-first HTML report."""

from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile
from html.parser import HTMLParser
from pathlib import Path


LEVELS = {"full", "summary", "metadata", "failed"}
REQUIRED_COLUMNS = {
    "original_id", "account_name", "title", "published_at", "url",
    "content_level", "source_type", "fetched_at",
}
REQUIRED_SECTIONS = {
    "executive-summary", "history-evolution", "theme-map", "recent-changes",
    "current-period", "timeline", "entity-index", "research-rules", "methodology",
}
WORK_NOTES = ("下一步", "待补充", "建议的使用方式", "Further Questions", "TODO", "草稿")


class ReportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: set[str] = set()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        section = values.get("data-section")
        if section:
            self.sections.add(section)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")


def validate(db_path: Path, manifest_path: Path, html_path: Path) -> dict[str, object]:
    for path in (db_path, manifest_path, html_path):
        if not path.is_file():
            raise ValueError(f"missing file: {path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    connection = sqlite3.connect(db_path)
    try:
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if "articles" not in tables:
            raise ValueError("missing table: articles")
        columns = {row[1] for row in connection.execute("PRAGMA table_info(articles)")}
        missing_columns = REQUIRED_COLUMNS - columns
        if missing_columns:
            raise ValueError(f"missing article columns: {sorted(missing_columns)}")
        rows = connection.execute(
            "SELECT content_level, COUNT(*) FROM articles GROUP BY content_level"
        ).fetchall()
        counts = dict(rows)
        unknown = set(counts) - LEVELS
        if unknown:
            raise ValueError(f"unknown content levels: {sorted(unknown)}")
        total = sum(counts.values())
        date_min, date_max = connection.execute(
            "SELECT MIN(published_at), MAX(published_at) FROM articles"
        ).fetchone()
    finally:
        connection.close()

    expected = {
        "article_count": total,
        "body_full": counts.get("full", 0),
        "summary_only": counts.get("summary", 0),
        "metadata_only": counts.get("metadata", 0),
        "failed": counts.get("failed", 0),
    }
    mismatches = {key: (manifest.get(key), value) for key, value in expected.items()
                  if manifest.get(key) != value}
    if mismatches:
        raise ValueError(f"manifest mismatch: {mismatches}")
    if total == 0 or not date_min or not date_max:
        raise ValueError("archive has no dated articles")

    html = html_path.read_text(encoding="utf-8")
    parser = ReportParser()
    parser.feed(html)
    missing_sections = REQUIRED_SECTIONS - parser.sections
    if missing_sections:
        raise ValueError(f"missing report sections: {sorted(missing_sections)}")
    notes = [token for token in WORK_NOTES if token.lower() in html.lower()]
    if notes:
        raise ValueError(f"work-note language found: {notes}")
    bad_links = [url for url in parser.links if not url.startswith(("https://", "http://"))]
    if bad_links:
        raise ValueError(f"non-http links found: {bad_links[:3]}")

    return {
        "status": "PASS",
        "articles": total,
        "content_levels": {level: counts.get(level, 0) for level in sorted(LEVELS)},
        "date_range_unix": [date_min, date_max],
        "report_sections": len(parser.sections),
        "report_links": len(parser.links),
    }


def self_check() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        db = root / "archive.sqlite"
        connection = sqlite3.connect(db)
        connection.execute(
            """CREATE TABLE articles (
                original_id TEXT PRIMARY KEY, account_name TEXT NOT NULL,
                title TEXT NOT NULL, published_at INTEGER NOT NULL, url TEXT NOT NULL,
                content_level TEXT NOT NULL, source_type TEXT NOT NULL,
                fetched_at TEXT NOT NULL
            )"""
        )
        connection.execute(
            "INSERT INTO articles VALUES (?,?,?,?,?,?,?,?)",
            ("id-1", "样例公众号", "样例文章", 1, "https://example.com/1",
             "full", "local_html", "2026-01-01T00:00:00+08:00"),
        )
        connection.commit()
        connection.close()
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({
            "article_count": 1, "body_full": 1, "summary_only": 0,
            "metadata_only": 0, "failed": 0,
        }, ensure_ascii=False), encoding="utf-8")
        html = root / "report.html"
        sections = "".join(f'<section data-section="{name}"></section>'
                           for name in sorted(REQUIRED_SECTIONS))
        html.write_text(f'<html><body>{sections}<a href="https://example.com">原文</a></body></html>',
                        encoding="utf-8")
        assert validate(db, manifest, html)["status"] == "PASS"
    print("self-check passed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--html", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        self_check()
        return
    if not all((args.db, args.manifest, args.html)):
        parser.error("--db, --manifest and --html are required")
    print(json.dumps(validate(args.db, args.manifest, args.html), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
