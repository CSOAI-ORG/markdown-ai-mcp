<div align="center">

# Markdown Ai MCP

**Markdown AI MCP Server — Markdown processing tools.**

[![PyPI](https://img.shields.io/pypi/v/meok-markdown-ai-mcp)](https://pypi.org/project/meok-markdown-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Markdown AI MCP Server — Markdown processing tools.

## Tools

| Tool | Description |
|------|-------------|
| `convert_to_html` | Convert Markdown to HTML (supports headers, bold, italic, links, code, lists). |
| `generate_toc` | Generate a table of contents from Markdown headers. |
| `lint_markdown` | Lint Markdown for common issues. |
| `format_table` | Format data as a Markdown table. headers: comma-separated. rows: semicolon-separ |

## Installation

```bash
pip install meok-markdown-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "markdown-ai": {
      "command": "python",
      "args": ["-m", "meok_markdown_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
