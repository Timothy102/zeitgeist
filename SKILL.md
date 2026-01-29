---
name: zeitgeist
description: Deep cultural research across Reddit and X — give your agent cultural awareness about any niche, right now
argument-hint: "[niche/vertical/audience]" or no argument for general culture
allowed-tools: Bash, Read, Write, WebSearch
---

# Zeitgeist: Deep Cultural Research

Synthesize what's actually happening in culture right now — the conversations, the creators, the vibes — into context your agent can reference for cultural fluency.

## Usage

```
/zeitgeist [niche, vertical, or audience]
```

Examples:
- `/zeitgeist sneaker culture`
- `/zeitgeist millennial parents`  
- `/zeitgeist indie beauty brands`
- `/zeitgeist` (no argument = general cultural snapshot)

---

## STEP 1: Parse Input

Extract from user's request:
- **FOCUS**: The niche, vertical, or audience (default: "general culture")
- **DEPTH**: `--quick`, default, or `--deep`

```
FOCUS = [extracted or "general culture"]
DEPTH = [quick | standard | deep]
```

---

## STEP 2: Detect Sources

Check available sources in priority order:

### Check 1: MCP Servers
```bash
cat ~/.config/claude/claude_desktop_config.json 2>/dev/null | grep -qE '"reddit|twitter|x-mcp"' && echo "MCP_FOUND" || echo "NO_MCP"
```

Look for: `mcp-server-reddit`, `reddit-mcp`, `mcp-twikit`, `twitter-mcp`, `x-mcp`

### Check 2: API Keys
```bash
cat ~/.config/zeitgeist/.env 2>/dev/null
```

Look for: `OPENAI_API_KEY` (Reddit), `XAI_API_KEY` (X)

### Check 3: Native Fallback
Claude's WebSearch is always available.

**Set modes:**
```
REDDIT_MODE = mcp > api > web
X_MODE = mcp > api > web
```

---

## STEP 3: Run Research

### If API keys available:

```bash
python3 ~/.claude/skills/zeitgeist/scripts/zeitgeist.py "$FOCUS" --emit=compact
```

### If MCP available:

Use MCP tools directly for Reddit/X searches.

### If web-only:

Run parallel WebSearch queries:
```
"[FOCUS] site:reddit.com discussion 2024"
"[FOCUS] site:twitter.com OR site:x.com"
"[FOCUS] trending opinions"
```

---

## STEP 4: Research Streams

Cover these areas for the FOCUS:

### A. The Conversation
What people are actually discussing.
- Debates and hot takes
- Memes and references
- Whether building, peaking, or fading

### B. Who's Shaping Taste
Creators having a moment.
- Names and handles
- Why they resonate
- Rising vs established

### C. Sentiment
The vibes and emotional register.
- Optimism, fatigue, excitement, cynicism
- Specific frustrations
- Direction of shift

### D. Formats & Trends
What content is circulating.
- Viral formats and templates
- Participation opportunities
- Saturation level

---

## STEP 4.5: Relevance & Quality Filtering

### High-Signal Content (INCLUDE):
- High engagement relative to community size
- Comment sections with substantive discussion
- First-hand experiences and authentic opinions
- Specific recommendations with reasoning
- Contrarian takes that sparked real debate
- Creator content being referenced elsewhere
- Threads where people are teaching each other

### Noise (EXCLUDE):
- Generic questions with no meaningful discussion
- Self-promotion without community response
- Reposts, recycled content, engagement farming
- Off-topic tangents within threads
- Bot activity or coordinated posting
- Surface-level "hot takes" with no substance
- Listicles and aggregator content

### Platform-Specific Quality Signals:
- **Reddit**: Comment quality > raw upvotes; AMA/discussion threads > link posts; nested reply depth indicates real engagement
- **X**: Quote tweets with original takes > naked retweets; threads > single tweets; ratio of replies to likes indicates controversy vs consensus

### Cross-Platform Validation:
Same signal appearing on Reddit + X = high confidence. Different framing of same insight across platforms = real trend, not platform artifact.

---

## STEP 4.6: Two-Phase Research (Critical)

### Phase 1: Wide Scan — Identify What Matters

First pass: Absorb the landscape. Don't commit to anything yet.

- Skim 20-30 sources quickly
- Note recurring themes, names, tensions
- Identify which threads have the deepest engagement
- Flag content where people are genuinely arguing or teaching
- Look for the 3-5 topics that keep surfacing

**Ask yourself:** "What are the 3 things this community clearly cares about right now?"

### Phase 2: Deep Dive — Extract Real Language

Once you've identified high-signal threads, GO BACK IN.

- Read full comment chains, not just top comments
- Capture **verbatim language** — the exact words people use
- Note specific frustrations, wishes, complaints
- Pull direct quotes that capture sentiment
- Find the comments where someone says "finally someone said it"

**What to extract:**
```
- Exact phrases people use to describe their problems
- Specific product/creator names being praised or criticized  
- The "yeah but" responses that reveal nuance
- Questions that keep getting asked (unmet needs)
- Inside jokes and references (cultural fluency markers)
```

### Why This Matters:

Surface-level research gives you: "People are talking about X"

Deep research gives you: "People are frustrated that [exact quote] and they're switching to [specific alternative] because [their words]"

The second version is actually useful. The first is noise.

**DO NOT** summarize or clean up the language. The raw words are the insight. "This product is mid" tells you more than "users expressed moderate dissatisfaction."

---

## STEP 5: Synthesize

### Pattern Detection
- Signal in 3+ sources → High confidence
- Reddit + X alignment → Cross-platform validation
- Engagement metrics weight the signal

### Freshness
- < 24h: Full weight
- 1-7d: High weight  
- 1-4w: Moderate weight
- > 4w: Archive

### Confidence
- **High**: Multiple sources + engagement data
- **Medium**: 2+ sources
- **Low**: Single source
- **Speculative**: Inference only

---

## STEP 6: Output

### Brief (default)
```
## Zeitgeist: [FOCUS]
*Generated [date]*

**The vibe:** [1-2 sentence summary]

**Top signals:**
1. [Signal + source + confidence]
2. [Signal + source + confidence]  
3. [Signal + source + confidence]

**Who to watch:** @handle1, @handle2, r/subreddit

**Coming up:** [Next relevant moment]
```

### Stats footer
```
---
✅ Research complete
├─ 🟠 Reddit: {n} threads │ {upvotes} upvotes
├─ 🔵 X: {n} posts │ {likes} likes
└─ Mode: [mcp | api | web]
```

---

## STEP 7: Follow-up

Offer:
- "Go deeper on [specific signal]"
- "Who else is talking about [topic]"
- "Save as reference doc"

Remember for session:
```
ZEITGEIST_FOCUS = [focus]
KEY_SIGNALS = [top 5]
WATCH_LIST = [creators]
```

---

## Setup

### Option 1: API Keys (Recommended)
```bash
mkdir -p ~/.config/zeitgeist
cat > ~/.config/zeitgeist/.env << 'EOF'
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
EOF
chmod 600 ~/.config/zeitgeist/.env
```

### Option 2: MCP Servers
Add to Claude config:
```json
{
  "mcpServers": {
    "reddit": {"command": "uvx", "args": ["mcp-server-reddit"]},
    "twitter": {"command": "uvx", "args": ["mcp-twikit"]}
  }
}
```

### Option 3: No Setup
Works with WebSearch fallback (no engagement metrics).

---

## Anti-Patterns

- **DON'T** project assumptions — report what research found
- **DON'T** treat all sources equally — engagement signals matter
- **DON'T** skip freshness weighting
- **DON'T** conflate platform trends with niche signals
- **DON'T** optimize for speed over depth
