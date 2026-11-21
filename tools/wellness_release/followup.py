"""Load and render the next wellness collection from individual editorial records."""

import json
from html import escape
from pathlib import Path

SOURCE_DATE = 'November 21, 2026'
DATA = Path(__file__).with_name('followup')


def load_records():
    records = {}
    for path in sorted(DATA.glob('*.jsonl')):
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            key = record['article'][1]
            if key in records:
                raise ValueError(f'Duplicate follow-up guide: {key}')
            records[key] = record
    return records


RECORDS = load_records()


def render_body(record):
    table = record['table']
    caption, headers, *rows = table
    head = ''.join(f'<th scope="col">{escape(str(item))}</th>' for item in headers)
    body = []
    for label, *cells in rows:
        if len(cells) + 1 != len(headers):
            raise ValueError(f'Mismatched table cells for {record["article"][1]}')
        row = ''.join(f'<td>{escape(str(cell))}</td>' for cell in cells)
        body.append(f'<tr><th scope="row">{escape(str(label))}</th>{row}</tr>')
    intro, heading, explanation, takeaway = record['copy']
    path, label = record['related']
    return (
        f'<p>{escape(intro)}</p>\n<table><caption>{escape(caption)}</caption>'
        f'<thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>\n'
        f'<h2>{escape(heading)}</h2>\n<p>{escape(explanation)}</p>\n'
        f'<p>{escape(takeaway)} <a href="{escape(path, quote=True)}">{escape(label)}</a>.</p>'
    )
