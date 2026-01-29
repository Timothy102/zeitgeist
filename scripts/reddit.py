"""
Reddit research module.
Supports: MCP, API (OpenAI web search), native web fallback, mock mode
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sources import get_api_key

# Fixtures path
FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


async def search_reddit(focus: str, mode: str = "web", count: int = 25, debug: bool = False, mock: bool = False) -> dict:
    """
    Search Reddit for cultural signals.
    
    Args:
        focus: Topic/niche to research
        mode: "mcp", "api", or "web"
        count: Number of results
        debug: Print debug info
        mock: Use fixtures instead of real API calls
    
    Returns:
        {"results": [...], "stats": {...}}
    """
    if mock:
        return await search_reddit_mock(focus, count, debug)
    elif mode == "mcp":
        return await search_reddit_mcp(focus, count, debug)
    elif mode == "api":
        return await search_reddit_api(focus, count, debug)
    else:
        return await search_reddit_web(focus, count, debug)


async def search_reddit_mock(focus: str, count: int, debug: bool) -> dict:
    """Load results from fixtures."""
    fixture_path = FIXTURES_DIR / "reddit_sample.json"
    
    if debug:
        print(f"[reddit] loading mock data from {fixture_path}", file=sys.stderr)
    
    if not fixture_path.exists():
        return {"results": [], "stats": {"mode": "mock", "error": "fixture not found"}}
    
    try:
        with open(fixture_path) as f:
            data = json.load(f)
        
        results = data.get("results", [])[:count]
        return {
            "results": results,
            "stats": {"mode": "mock", "count": len(results)}
        }
    except Exception as e:
        if debug:
            print(f"[reddit] mock error: {e}", file=sys.stderr)
        return {"results": [], "stats": {"mode": "mock", "error": str(e)}}


async def search_reddit_mcp(focus: str, count: int, debug: bool) -> dict:
    """Use Reddit MCP server."""
    # MCP calls are handled by the agent directly
    # This is a placeholder for structured output
    return {
        "results": [],
        "stats": {"mode": "mcp", "note": "MCP calls handled by agent"}
    }


async def search_reddit_api(focus: str, count: int, debug: bool) -> dict:
    """Use OpenAI API with web search for Reddit."""
    import httpx
    
    api_key = get_api_key("OPENAI_API_KEY")
    if not api_key:
        if debug:
            print("[reddit] no OPENAI_API_KEY", file=sys.stderr)
        return {"results": [], "stats": {"error": "no api key"}}
    
    # Build search queries
    queries = [
        f"{focus} site:reddit.com",
        f"{focus} reddit discussion",
        f"{focus} reddit what do you think",
    ]
    
    results = []
    
    async with httpx.AsyncClient(timeout=60) as client:
        for query in queries[:2]:  # Limit queries
            if debug:
                print(f"[reddit] query: {query}", file=sys.stderr)
            
            try:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "tools": [{"type": "web_search_preview"}],
                        "input": f"Search Reddit for: {query}. Return the top posts with titles, subreddits, upvotes, and comment counts. Format as JSON array.",
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Parse response for Reddit posts
                    text = data.get("output", [{}])[0].get("content", [{}])[0].get("text", "")
                    parsed = parse_reddit_response(text, debug)
                    results.extend(parsed)
                elif debug:
                    print(f"[reddit] API error: {response.status_code}", file=sys.stderr)
                    
            except Exception as e:
                if debug:
                    print(f"[reddit] request error: {e}", file=sys.stderr)
    
    return {
        "results": results[:count],
        "stats": {"mode": "api", "queries": len(queries)}
    }


async def search_reddit_web(focus: str, count: int, debug: bool) -> dict:
    """
    Web fallback - returns search queries for agent to execute.
    The agent should run these with WebSearch tool.
    """
    queries = [
        f'"{focus}" site:reddit.com',
        f'{focus} discussion reddit 2024',
        f'{focus} recommendations reddit',
    ]
    
    return {
        "results": [],
        "stats": {
            "mode": "web",
            "queries": queries,
            "note": "Run these queries with WebSearch tool"
        }
    }


def parse_reddit_response(text: str, debug: bool = False) -> list:
    """Parse Reddit results from API response."""
    results = []
    
    # Try to extract JSON
    try:
        # Look for JSON array in response
        start = text.find('[')
        end = text.rfind(']') + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            for item in data:
                results.append({
                    "title": item.get("title", ""),
                    "subreddit": item.get("subreddit", "").replace("r/", ""),
                    "score": int(item.get("upvotes", item.get("score", 0))),
                    "num_comments": int(item.get("comments", item.get("num_comments", 0))),
                    "url": item.get("url", ""),
                    "created": item.get("created", ""),
                    "source": "reddit",
                })
    except:
        if debug:
            print("[reddit] failed to parse JSON response", file=sys.stderr)
    
    return results
