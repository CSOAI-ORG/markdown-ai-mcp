# Markdown AI

> By [MEOK AI Labs](https://meok.ai) — Markdown processing, conversion, and linting tools

## Installation

```bash
pip install markdown-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `convert_to_html`
Convert Markdown to HTML (supports headers, bold, italic, links, code, lists).

**Parameters:**
- `markdown` (str): Markdown text to convert

### `generate_toc`
Generate a table of contents from Markdown headers.

**Parameters:**
- `markdown` (str): Markdown text
- `max_depth` (int): Maximum heading depth (default: 3)

### `lint_markdown`
Lint Markdown for common issues (line length, trailing whitespace, heading spacing, tabs, broken links).

**Parameters:**
- `markdown` (str): Markdown text to lint

### `format_table`
Format data as a Markdown table.

**Parameters:**
- `headers` (str): Comma-separated column headers
- `rows` (str): Semicolon-separated rows of comma-separated values
- `alignment` (str): L/C/R per column

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
