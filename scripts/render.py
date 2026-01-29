"""
Output rendering for zeitgeist results.
"""

import json
from datetime import datetime


def render_compact(data: dict) -> str:
    """Render compact output for agent consumption."""
    lines = []
    
    focus = data.get("focus", "general")
    timestamp = data.get("timestamp", datetime.now().isoformat())[:10]
    stats = data.get("stats", {})
    sources = data.get("sources", {})
    
    lines.append(f"## Zeitgeist: {focus}")
    lines.append(f"*Generated {timestamp}*")
    lines.append("")
    
    # Top signals - access results from nested structure
    all_results = []
    reddit_data = data.get("reddit", {})
    x_data = data.get("x", {})
    
    reddit_results = reddit_data.get("results", []) if isinstance(reddit_data, dict) else []
    x_results = x_data.get("results", []) if isinstance(x_data, dict) else []
    
    for r in reddit_results:
        r["_platform"] = "reddit"
        all_results.append(r)
    for r in x_results:
        r["_platform"] = "x"
        all_results.append(r)
    
    # Sort by score
    all_results.sort(key=lambda x: x.get("zeitgeist_score", 0), reverse=True)
    
    if all_results:
        lines.append("**Top signals:**")
        for i, r in enumerate(all_results[:5], 1):
            if r["_platform"] == "reddit":
                sub = r.get("subreddit", "?")
                score = r.get("score", 0)
                title = r.get("title", "")[:60]
                lines.append(f"{i}. {title} — r/{sub} ({score:,} upvotes)")
            else:
                author = r.get("author", "?")
                likes = r.get("likes", 0)
                text = r.get("text", "")[:60]
                lines.append(f'{i}. "{text}..." — @{author} ({likes:,} likes)')
        lines.append("")
    
    # Who to watch
    authors = []
    if stats.get("reddit", {}).get("subreddits"):
        authors.extend([f"r/{s}" for s in stats["reddit"]["subreddits"][:3]])
    if stats.get("x", {}).get("authors"):
        authors.extend([f"@{a}" for a in stats["x"]["authors"][:3]])
    
    if authors:
        lines.append(f"**Who to watch:** {', '.join(authors)}")
        lines.append("")
    
    # Stats footer
    lines.append("---")
    lines.append("✅ Research complete")
    
    reddit_stats = stats.get("reddit", {})
    x_stats = stats.get("x", {})
    
    if reddit_stats.get("count", 0) > 0:
        lines.append(f"├─ 🟠 Reddit: {reddit_stats['count']} threads │ {reddit_stats.get('upvotes', 0):,} upvotes")
    
    if x_stats.get("count", 0) > 0:
        lines.append(f"├─ 🔵 X: {x_stats['count']} posts │ {x_stats.get('likes', 0):,} likes")
    
    mode = determine_mode(sources)
    lines.append(f"└─ Mode: {mode}")
    
    # Hint if web-only or mock
    if mode == "web":
        lines.append("")
        lines.append("💡 Add API keys to ~/.config/zeitgeist/.env for engagement metrics")
    elif mode == "mock":
        lines.append("")
        lines.append("🧪 Running in mock mode with fixture data")
    
    return "\n".join(lines)


def render_json(data: dict) -> str:
    """Render JSON output."""
    return json.dumps(data, indent=2, default=str)


def render_markdown(data: dict) -> str:
    """Render full markdown output."""
    lines = []
    
    focus = data.get("focus", "general")
    timestamp = data.get("timestamp", datetime.now().isoformat())
    
    lines.append(f"# Zeitgeist Report: {focus}")
    lines.append(f"Generated: {timestamp}")
    lines.append("")
    
    # Reddit section - access results from nested structure
    reddit_data = data.get("reddit", {})
    reddit_results = reddit_data.get("results", []) if isinstance(reddit_data, dict) else []
    
    if reddit_results:
        lines.append("## Reddit")
        lines.append("")
        for r in reddit_results[:10]:
            title = r.get("title", "Untitled")
            sub = r.get("subreddit", "?")
            score = r.get("score", 0)
            comments = r.get("num_comments", 0)
            url = r.get("url", "")
            
            lines.append(f"### {title}")
            lines.append(f"- Subreddit: r/{sub}")
            lines.append(f"- Score: {score:,} upvotes, {comments:,} comments")
            if url:
                lines.append(f"- URL: {url}")
            lines.append("")
    
    # X section - access results from nested structure
    x_data = data.get("x", {})
    x_results = x_data.get("results", []) if isinstance(x_data, dict) else []
    
    if x_results:
        lines.append("## X / Twitter")
        lines.append("")
        for r in x_results[:10]:
            text = r.get("text", "")
            author = r.get("author", "?")
            likes = r.get("likes", 0)
            reposts = r.get("reposts", 0)
            url = r.get("url", "")
            
            lines.append(f"### @{author}")
            lines.append(f"> {text}")
            lines.append(f"- Engagement: {likes:,} likes, {reposts:,} reposts")
            if url:
                lines.append(f"- URL: {url}")
            lines.append("")
    
    # Stats
    lines.append("## Stats")
    lines.append("```")
    lines.append(json.dumps(data.get("stats", {}), indent=2))
    lines.append("```")
    
    return "\n".join(lines)


# Alias for backward compatibility
render_full = render_markdown


def determine_mode(sources: dict) -> str:
    """Determine display mode from source config."""
    reddit = sources.get("reddit", "web")
    x = sources.get("x", "web")
    
    # Check for mock indicators in the data
    if reddit == "mock" or x == "mock":
        return "mock"
    elif reddit == "mcp" or x == "mcp":
        return "mcp"
    elif reddit == "api" or x == "api":
        return "api"
    else:
        return "web"
