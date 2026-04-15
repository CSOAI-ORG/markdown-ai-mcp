"""Markdown AI MCP Server — Markdown processing tools."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import re
import time
from typing import Any
from mcp.server.fastmcp import FastMCP

import json
from datetime import datetime, timezone
from collections import defaultdict

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None


mcp = FastMCP("markdown-ai", instructions="MEOK AI Labs MCP Server")
_calls: dict[str, list[float]] = {}
DAILY_LIMIT = 50

def _rate_check(tool: str) -> bool:
    now = time.time()
    _calls.setdefault(tool, [])
    _calls[tool] = [t for t in _calls[tool] if t > now - 86400]
    if len(_calls[tool]) >= DAILY_LIMIT:
        return False
    _calls[tool].append(now)
    return True

@mcp.tool()
def convert_to_html(markdown: str, api_key: str = "") -> dict[str, Any]:
    """Convert Markdown to HTML (supports headers, bold, italic, links, code, lists)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    if not _rate_check("convert_to_html"):
        return {"error": "Rate limit exceeded (50/day)"}
    html = markdown
    # Code blocks first
    html = re.sub(r'```(\w*)\n(.*?)```', lambda m: f'<pre><code class="language-{m.group(1)}">{m.group(2)}</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    # Headers
    for i in range(6, 0, -1):
        html = re.sub(rf'^{"#" * i}\s+(.+)$', rf'<h{i}>\1</h{i}>', html, flags=re.MULTILINE)
    # Bold and italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    # Links and images
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', html)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    # Horizontal rule
    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)
    # Blockquote
    html = re.sub(r'^>\s*(.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    # Unordered lists
    lines = html.split("\n")
    result, in_ul, in_ol = [], False, False
    for line in lines:
        ul_match = re.match(r'^[\-\*]\s+(.+)$', line)
        ol_match = re.match(r'^\d+\.\s+(.+)$', line)
        if ul_match:
            if not in_ul:
                result.append("<ul>")
                in_ul = True
            result.append(f"  <li>{ul_match.group(1)}</li>")
        elif ol_match:
            if not in_ol:
                result.append("<ol>")
                in_ol = True
            result.append(f"  <li>{ol_match.group(1)}</li>")
        else:
            if in_ul:
                result.append("</ul>")
                in_ul = False
            if in_ol:
                result.append("</ol>")
                in_ol = False
            if line.strip():
                result.append(f"<p>{line}</p>" if not line.startswith("<") else line)
            else:
                result.append("")
    if in_ul: result.append("</ul>")
    if in_ol: result.append("</ol>")
    html_out = "\n".join(result)
    return {"html": html_out, "input_length": len(markdown), "output_length": len(html_out)}

@mcp.tool()
def generate_toc(markdown: str, max_depth: int = 3, api_key: str = "") -> dict[str, Any]:
    """Generate a table of contents from Markdown headers."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    if not _rate_check("generate_toc"):
        return {"error": "Rate limit exceeded (50/day)"}
    headers = []
    for line in markdown.split("\n"):
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            if level <= max_depth:
                text = m.group(2).strip()
                slug = re.sub(r'[^\w\s-]', '', text.lower()).replace(' ', '-')
                headers.append({"level": level, "text": text, "slug": slug})
    toc_lines = []
    for h in headers:
        indent = "  " * (h["level"] - 1)
        toc_lines.append(f'{indent}- [{h["text"]}](#{h["slug"]})')
    return {"toc": "\n".join(toc_lines), "headers": headers, "header_count": len(headers)}

@mcp.tool()
def lint_markdown(markdown: str, api_key: str = "") -> dict[str, Any]:
    """Lint Markdown for common issues."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    if not _rate_check("lint_markdown"):
        return {"error": "Rate limit exceeded (50/day)"}
    issues = []
    lines = markdown.split("\n")
    for i, line in enumerate(lines, 1):
        if len(line) > 120:
            issues.append({"line": i, "rule": "line-length", "message": f"Line exceeds 120 chars ({len(line)})"})
        if line.rstrip() != line:
            issues.append({"line": i, "rule": "trailing-whitespace", "message": "Trailing whitespace"})
        if re.match(r'^#+[^\s]', line):
            issues.append({"line": i, "rule": "heading-space", "message": "No space after heading marker"})
        if '\t' in line:
            issues.append({"line": i, "rule": "no-tabs", "message": "Tab character found (use spaces)"})
    # Check for multiple blank lines
    for i in range(len(lines) - 1):
        if lines[i].strip() == "" and (i + 1 < len(lines) and lines[i + 1].strip() == ""):
            issues.append({"line": i + 1, "rule": "no-multiple-blanks", "message": "Multiple consecutive blank lines"})
    # Check for broken links
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'\[([^\]]*)\]\(([^)]*)\)', line):
            if not m.group(2):
                issues.append({"line": i, "rule": "no-empty-links", "message": f"Empty link URL for '{m.group(1)}'"})
    severity = "clean" if not issues else "warning" if len(issues) < 5 else "needs-attention"
    return {"issues": issues, "issue_count": len(issues), "severity": severity, "line_count": len(lines)}

@mcp.tool()
def format_table(headers: str, rows: str, alignment: str = "", api_key: str = "") -> dict[str, Any]:
    """Format data as a Markdown table. headers: comma-separated. rows: semicolon-separated rows of comma-separated values. alignment: L/C/R per column."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    if not _rate_check("format_table"):
        return {"error": "Rate limit exceeded (50/day)"}
    cols = [h.strip() for h in headers.split(",")]
    data_rows = [[c.strip() for c in row.split(",")] for row in rows.split(";") if row.strip()]
    aligns = list(alignment.upper()) if alignment else ["L"] * len(cols)
    while len(aligns) < len(cols):
        aligns.append("L")
    widths = [len(c) for c in cols]
    for row in data_rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
    def pad(text, width, align):
        if align == "C": return text.center(width)
        if align == "R": return text.rjust(width)
        return text.ljust(width)
    header_line = "| " + " | ".join(pad(c, widths[i], aligns[i]) for i, c in enumerate(cols)) + " |"
    sep_parts = []
    for i, w in enumerate(widths):
        if aligns[i] == "C": sep_parts.append(":" + "-" * (w) + ":")
        elif aligns[i] == "R": sep_parts.append("-" * (w + 1) + ":")
        else: sep_parts.append(":" + "-" * (w + 1))
    sep_line = "| " + " | ".join(sep_parts) + " |"
    row_lines = []
    for row in data_rows:
        padded = []
        for i in range(len(cols)):
            val = row[i] if i < len(row) else ""
            padded.append(pad(val, widths[i], aligns[i]))
        row_lines.append("| " + " | ".join(padded) + " |")
    table = "\n".join([header_line, sep_line] + row_lines)
    return {"table": table, "columns": len(cols), "rows": len(data_rows)}

if __name__ == "__main__":
    mcp.run()
