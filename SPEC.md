# Zeitgeist Technical Specification

## Overview

Zeitgeist is a Claude Code skill that performs deep cultural research across Reddit and X (Twitter). It synthesizes trending conversations, creators, and sentiment into context that agents can reference for cultural fluency.

**Key features:**
- Multi-platform research (Reddit + X)
- Engagement-weighted scoring with freshness decay
- Three operating modes: MCP, API, Web fallback
- 24-hour TTL caching
- Mock mode for testing/demos

## Architecture

```
zeitgeist/
├── SKILL.md              # Claude skill definition
├── scripts/
│   ├── zeitgeist.py      # Main CLI entrypoint
│   ├── sources.py        # Source detection (MCP/API/Web)
│   ├── reddit.py         # Reddit research module
│   ├── twitter.py        # X research module
│   ├── cache.py          # File-based cache with TTL
│   ├── score.py          # Engagement scoring & deduplication
│   └── render.py         # Output formatting (compact/json/full)
├── fixtures/
│   ├── reddit_sample.json
│   └── x_sample.json
└── tests/
    └── ...
```

## Source Detection Priority

The skill automatically detects available data sources in priority order:

1. **MCP Servers** (Best) - Direct platform access via Claude config
2. **API Keys** (Recommended) - OpenAI for Reddit, xAI for X
3. **Web Search** (Fallback) - Claude's native WebSearch

### MCP Detection
```bash
~/.config/claude/claude_desktop_config.json
```
Looks for: `mcp-server-reddit`, `reddit-mcp`, `mcp-twikit`, `twitter-mcp`, `x-mcp`

### API Key Detection
```bash
~/.config/zeitgeist/.env
```
Variables: `OPENAI_API_KEY`, `XAI_API_KEY`

## Scoring Algorithm

### Engagement Score

**Reddit:**
```
engagement = upvotes * 1.0 + comments * 2.0
```

**X:**
```
engagement = likes * 1.0 + reposts * 3.0 + replies * 2.0
```

### Freshness Multiplier

| Age | Multiplier |
|-----|------------|
| < 24h | 1.0 |
| 1-7 days | 0.8 |
| 1-2 weeks | 0.6 |
| 2-4 weeks | 0.4 |
| > 4 weeks | 0.2 |

### Final Score
```
zeitgeist_score = engagement * freshness
```

## Deduplication

Results are deduplicated by fingerprint:
- **Reddit:** `(subreddit, title[:50].lower())`
- **X:** `(author, text[:50].lower())`

## Caching

- **Location:** `~/.cache/zeitgeist/`
- **TTL:** 24 hours
- **Key:** MD5 hash of normalized focus string (first 12 chars)
- **Bypass:** `--refresh` flag

## CLI Reference

```bash
python3 scripts/zeitgeist.py [FOCUS] [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `FOCUS` | Niche, vertical, or audience (default: "general culture") |

### Options

| Flag | Description |
|------|-------------|
| `--emit=compact` | Agent-friendly output (default) |
| `--emit=json` | Raw JSON data |
| `--emit=full` | Full markdown report |
| `--quick` | Surface scan (10 results per platform) |
| `--deep` | Comprehensive research (50 Reddit, 40 X) |
| `--refresh` | Bypass cache |
| `--mock` | Use fixture data |
| `--reddit-only` | Only search Reddit |
| `--x-only` | Only search X |
| `--debug` | Verbose output |

## Output Formats

### Compact (Default)

```
## Zeitgeist: [focus]
*Generated [date]*

**Top signals:**
1. [title] — r/[subreddit] ([score] upvotes)
2. "[text]..." — @[author] ([likes] likes)

**Who to watch:** r/sub1, @author1

---
✅ Research complete
├─ 🟠 Reddit: [n] threads │ [upvotes] upvotes
├─ 🔵 X: [n] posts │ [likes] likes
└─ Mode: [mcp|api|web|mock]
```

### JSON

Full structured data with all results and metadata.

### Full Markdown

Detailed report with individual post breakdowns.

## Integration

### Invoke from Claude Code

```
/zeitgeist [topic]
```

### Programmatic Usage

```python
from scripts.zeitgeist import research, process_results
from scripts.sources import detect_sources

sources = detect_sources("both")
results = await research("indie beauty", sources, {"reddit": 25, "x": 20, "label": "standard"})
results = process_results(results)
```

## Error Handling

- API failures are caught and logged (with `--debug`)
- Failed platforms return empty results with error in stats
- Cache corruption returns `None`, triggering fresh fetch
- Unknown date formats default to 0.5 freshness multiplier
