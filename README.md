# /zeitgeist

**Give your agent cultural awareness about any niche, right now.**

Zeitgeist researches what's happening across Reddit and X — the conversations, creators, vibes, and sentiment — and synthesizes it into context your agent can reference.

## Install

```bash
git clone https://github.com/jacksoncorey/zeitgeist.git ~/.claude/skills/zeitgeist
```

## Usage

```
/zeitgeist [niche, vertical, or audience]
```

**Examples:**
- `/zeitgeist sneaker culture`
- `/zeitgeist millennial parents`
- `/zeitgeist indie beauty brands`
- `/zeitgeist` — general cultural snapshot

## What You Get

```
## Zeitgeist: indie beauty brands
*Generated 2026-01-27*

**The vibe:** Community fatigued by "clean beauty" marketing, excited about 
ingredient transparency. Skepticism toward celebrity brands peaking.

**Top signals:**
1. "Ingredient deck" reviews gaining traction — r/SkincareAddiction (2.4k upvotes)
2. Backlash against Sephora's indie shelf curation — @esteelaundry (890 likes)
3. Dupe culture hitting prestige indie brands — cross-platform

**Who to watch:** @caborles, @skincarebyhyram, r/Indiemakeupandmore

**Coming up:** Spring launches (Feb-Mar), Cosmoprof Bologna (March 20-22)

---
✅ Research complete
├─ 🟠 Reddit: 12 threads │ 8,420 upvotes
├─ 🔵 X: 18 posts │ 3,891 likes
└─ Mode: api
```

## Setup (Optional)

Zeitgeist works in three modes. More setup = richer data.

### Mode 1: API Keys (Recommended)

```bash
mkdir -p ~/.config/zeitgeist
cat > ~/.config/zeitgeist/.env << 'EOF'
# Reddit research via OpenAI web search
OPENAI_API_KEY=sk-...

# X research via xAI native search
XAI_API_KEY=xai-...
EOF
chmod 600 ~/.config/zeitgeist/.env
```

### Mode 2: MCP Servers (Best)

Add to your Claude config:

```json
{
  "mcpServers": {
    "reddit": {
      "command": "uvx",
      "args": ["mcp-server-reddit"]
    },
    "twitter": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/adhikasp/mcp-twikit", "mcp-twikit"],
      "env": {
        "TWITTER_USERNAME": "@you",
        "TWITTER_EMAIL": "you@email.com",
        "TWITTER_PASSWORD": "password"
      }
    }
  }
}
```

### Mode 3: No Setup

Works with Claude's native web search. Results without engagement metrics.

## Depth Options

| Flag | Description |
|------|-------------|
| `--quick` | Surface scan (fewer sources) |
| (default) | Standard depth |
| `--deep` | Comprehensive research |
| `--mock` | Use fixture data (for testing/demo) |
| `--refresh` | Bypass cache |
| `--emit=compact` | Agent-friendly output (default) |
| `--emit=json` | Raw JSON data |
| `--emit=full` | Full markdown report |

## Development

Test without API keys using mock mode:

```bash
python3 scripts/zeitgeist.py "indie beauty brands" --mock
```

Mock data lives in `fixtures/` — edit to test different scenarios.

## Requirements

- Claude Code with skills enabled
- Python 3.9+ (for API mode)
- (Optional) API keys or MCP servers

## Roadmap

- **v1** (current): Reddit + X
- **v2**: YouTube, TikTok
- **v3**: Media immersion

---

*Cultural fluency for agents — not from training data, from right now.*
