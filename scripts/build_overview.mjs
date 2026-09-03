// Run with the spreadsheet runtime supplied by the host; do not install private packages.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const [input, output, previewDir] = process.argv.slice(2);
if (!input || !output || !previewDir) throw new Error('Usage: build_overview.mjs reading.json overview.xlsx preview-directory');
try {
  await fs.access(output);
  throw new Error('Output already exists; use a new batch to preserve review notes');
} catch (error) {
  if (error.code !== 'ENOENT') throw error;
}
const data = JSON.parse(await fs.readFile(input, 'utf8'));
const articles = data.articles;
assert(Array.isArray(articles) && articles.length > 0 && articles.length === data.article_count);
assert(new Set(articles.map(a => a.original_id)).size === articles.length);
for (const a of articles) {
  const local = path.relative(path.dirname(output), path.resolve(path.dirname(output), a.md_path));
  assert(!local.startsWith('..') && !path.isAbsolute(local), 'MD link escapes the batch');
  await fs.access(path.resolve(path.dirname(output), a.md_path));
}
const literal = value => typeof value === 'string' && /^[=+@-]/.test(value) ? "'" + value : value;
const preview = value => {
  const text = String(value || '').replace(/\s+/g, ' ');
  return literal(text.length > 120 ? text.slice(0, 120) + '…' : text);
};
const wb = Workbook.create();
const overview = wb.worksheets.add('总览');
const list = wb.worksheets.add('文章目录');
const last = articles.length + 4;
const cols = ['发布日期', '文章标题', '内容等级', '主主题', '研究摘要（预览）', '核心观点（预览）', '涉及公司／机构／产品', '本地阅读', '原文链接', '审阅状态', '审阅备注', '文章ID', '正文字数', 'MD相对路径'];
const rows = articles.map(a => [
  a.date === 'undated' ? null : new Date(a.date + 'T00:00:00Z'), literal(a.title), a.content_label,
  literal(a.primary_theme || '未分类'), preview(a.synopsis), preview(a.core_view),
  preview(a.entities.join('、')), null, literal(a.url), '未审阅', '', literal(a.original_id),
  a.body_chars, literal(a.md_path),
]);
list.getRange(`A5:N${last}`).values = rows;
list.getRange('A4:N4').values = [cols];
// ponytail: host previews cannot evaluate HYPERLINK; Excel resolves it, previews show the label.
list.getRange(`H5:H${last}`).formulas = articles.map(a => [`=IFERROR(HYPERLINK("${a.md_path.replace(/"/g, '""')}","打开MD"),"打开MD")`]);
list.getRange(`A5:A${last}`).setNumberFormat('yyyy-mm-dd');
list.getRange(`M5:M${last}`).setNumberFormat('#,##0');
list.getRange(`L5:L${last}`).setNumberFormat('@');
list.getRange(`J5:J${last}`).dataValidation = { rule: { type: 'list', values: ['未审阅', '已审阅', '需核对'] } };
const table = list.tables.add(`A4:N${last}`, true, 'ArticleInventory');
table.style = 'TableStyleLight9';
list.freezePanes.freezeRows(4);
list.freezePanes.freezeColumns(2);

const navy = '#17324D', teal = '#087F8C', muted = '#53657A';
for (const sheet of [overview, list]) {
  sheet.showGridLines = false;
}
list.getRange(`A1:N${last}`).format.font = { name: 'Arial', size: 11, color: '#243746' };
list.getRange(`A5:N${last}`).format.wrapText = true;
list.getRange(`A5:N${last}`).format.rowHeight = 88;
list.getRange(`A5:N${last}`).format.verticalAlignment = 'top';
const widths = [105, 370, 85, 160, 440, 440, 280, 95, 300, 95, 300, 220, 90, 470];
widths.forEach((width, col) => list.getRangeByIndexes(0, col, last, 1).format.columnWidthPx = width);
list.getRange('A1:D1').merge();
list.getRange('A1').values = [[literal(`${data.account} · 文章审阅目录`)]];
list.getRange('A1:N1').format = { fill: navy, font: { bold: true, color: '#FFFFFF', size: 20 }, rowHeight: 38 };
list.getRange('A2:D2').merge();
list.getRange('A2').values = [['筛选日期／主题／内容等级；本地阅读列打开 MD，黄色列填写批注。']];
list.getRange('A2:N2').format = { font: { color: muted, size: 11 }, rowHeight: 26 };
list.getRange('A4:N4').format = { fill: teal, font: { bold: true, color: '#FFFFFF' }, rowHeight: 30 };
list.getRange(`J5:K${last}`).format.fill = '#FFF3CF';
list.getRange(`H5:H${last}`).format.font = { color: '#087F8C' };
list.getRange(`C5:C${last}`).conditionalFormats.add('containsText', { text: '仅', format: { fill: '#FFF0DF', font: { color: '#9A5500' } } });

overview.getRange('A1:H80').format.font = { name: 'Arial', size: 11, color: '#243746' };
overview.getRange('A1:H80').format.columnWidthPx = 120;
overview.getRange('A1:H1').merge();
overview.getRange('A1').values = [[literal(`${data.account} · 历史文章总览`)]];
overview.getRange('A1:H1').format = { fill: navy, font: { bold: true, size: 22, color: '#FFFFFF' }, rowHeight: 45 };
overview.getRange('A2:H2').merge();
overview.getRange('A2').values = [[`资料日期 ${data.earliest || '未知'} — ${data.latest || '未知'}   |   仅统计本次可访问记录   |   UTC${data.utc_offset}`]];
overview.getRange('A2:H2').format = { font: { color: muted }, rowHeight: 28 };
overview.getRange('A4:B7').values = [['文章记录', null], ['取得全文', null], ['仅有摘要', null], ['仅目录／失败', null]];
overview.getRange('B4:B7').formulas = [
  [`=COUNTA('文章目录'!L5:L${last})`], [`=COUNTIF('文章目录'!C5:C${last},"全文")`],
  [`=COUNTIF('文章目录'!C5:C${last},"仅摘要")`], ['=B4-B5-B6'],
];
overview.getRange('D4:E6').values = [['全文覆盖率', null], ['已审阅', null], ['需核对', null]];
overview.getRange('E4:E6').formulas = [['=B5/B4'], [`=COUNTIF('文章目录'!J5:J${last},"已审阅")`], [`=COUNTIF('文章目录'!J5:J${last},"需核对")`]];
overview.getRange('B4:B7').setNumberFormat('#,##0');
overview.getRange('E4').setNumberFormat('0.0%');
overview.getRange('E5:E6').setNumberFormat('#,##0');
overview.getRange('A4:E7').format.rowHeight = 29;
overview.getRange('B4:B7').format.font = { bold: true, size: 18, color: teal };
overview.getRange('E4:E6').format.font = { bold: true, size: 18, color: teal };
const guidance = [
  '使用方法：在“文章目录”筛选日期、主题或内容等级；点击“打开MD”阅读全文，黄色列记录人工审阅。',
  '缺文说明：仅摘要／仅目录不是全文；MD 不包含原网页图片与版式。摘要与观点属于既有研究提炼。',
  '备份方法：保留整个批次文件夹；相对链接随文件夹一起移动。Excel 可能要求确认打开本地文件。',
  '更新规则：新采集生成新批次，旧批次与批注保留；Excel 修改不会自动写回数据库。',
];
guidance.forEach((text, i) => {
  const row = 9 + i;
  overview.getRange(`A${row}:H${row}`).merge();
  overview.getRange(`A${row}`).values = [[text]];
  overview.getRange(`A${row}:H${row}`).format = { wrapText: true, rowHeight: 34, font: { color: muted, size: 11 } };
});
overview.getRange('A14:C14').values = [['发布月份', '文章数', '全文数']];
overview.getRange('A14:C14').format = { fill: teal, font: { bold: true, color: '#FFFFFF' }, rowHeight: 28 };
const months = [...new Set(articles.filter(a => a.date !== 'undated').map(a => a.date.slice(0, 7)))].sort().reverse();
months.forEach((month, i) => {
  const row = i + 15;
  overview.getRange(`A${row}`).values = [[new Date(month + '-01T00:00:00Z')]];
  overview.getRange(`A${row}`).setNumberFormat('yyyy-mm');
  overview.getRange(`B${row}:C${row}`).formulas = [[
    `=COUNTIFS('文章目录'!A5:A${last},">="&A${row},'文章目录'!A5:A${last},"<"&DATE(YEAR(A${row}),MONTH(A${row})+1,1))`,
    `=COUNTIFS('文章目录'!A5:A${last},">="&A${row},'文章目录'!A5:A${last},"<"&DATE(YEAR(A${row}),MONTH(A${row})+1,1),'文章目录'!C5:C${last},"全文")`,
  ]];
});
overview.freezePanes.freezeRows(14);
assert.equal(overview.getRange('B4').values[0][0], articles.length);
assert.equal(overview.getRange('B5').values[0][0], articles.filter(a => a.content_level === 'full').length);
console.log((await wb.inspect({ kind: 'region', sheetId: '总览', range: 'A4:E7', maxChars: 1500, tableMaxRows: 4, tableMaxCols: 5 })).ndjson);
const errors = await wb.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A', options: { useRegex: true, maxResults: 20 }, maxChars: 2000 });
console.log(errors.ndjson);
assert(!/#REF!|#DIV\/0!|#VALUE!|#NAME\?|#N\/A/.test(errors.ndjson), 'Formula error scan failed');
await fs.mkdir(previewDir, { recursive: true });
for (const [sheetName, range, name] of [['总览', 'A1:H24', 'overview'], ['文章目录', 'A1:D9', 'articles'], ['文章目录', 'E4:K7', 'review']]) {
  const image = await wb.render({ sheetName, range, scale: 1.5, format: 'png' });
  await fs.writeFile(path.join(previewDir, name + '.png'), new Uint8Array(await image.arrayBuffer()));
}
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(output);
console.log(JSON.stringify({ output, articleCount: articles.length, sheets: ['总览', '文章目录'] }));
