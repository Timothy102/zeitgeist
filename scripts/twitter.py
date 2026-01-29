"""
X/Twitter research module.
Supports: MCP, API (xAI native search), native web fallback, mock mode
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from sources import get_api_key

# Fixtures path
FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


async def search_x(focus: str, mode: str = "web", count: int = 20, debug: bool = False, mock: bool = False) -> dict:
    """
    Search X for cultural signals.
    
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
        return await search_x_mock(focus, count, debug)
    elif mode == "mcp":
        return await search_x_mcp(focus, count, debug)
    elif mode == "api":
        return await search_x_api(focus, count, debug)
    else:
        return await search_x_web(focus, count, debug)


async def search_x_mock(focus: str, count: int, debug: bool) -> dict:
    """Load results from fixtures."""
    fixture_path = FIXTURES_DIR / "x_sample.json"
    
    if debug:
        print(f"[x] loading mock data from {fixture_path}", file=sys.stderr)
    
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
            print(f"[x] mock error: {e}", file=sys.stderr)
        return {"results": [], "stats": {"mode": "mock", "error": str(e)}}


async def search_x_mcp(focus: str, count: int, debug: bool) -> dict:
    """Use X MCP server."""
    # MCP calls are handled by the agent directly
    return {
        "results": [],
        "stats": {"mode": "mcp", "note": "MCP calls handled by agent"}
    }


async def search_x_api(focus: str, count: int, debug: bool) -> dict:
    """Use xAI API with native X search."""
    import httpx
    
    api_key = get_api_key("XAI_API_KEY")
    if not api_key:
        if debug:
            print("[x] no XAI_API_KEY", file=sys.stderr)
        return {"results": [], "stats": {"error": "no api key"}}
    
    results = []
    
    async with httpx.AsyncClient(timeout=60) as client:
        if debug:
            print(f"[x] searching: {focus}", file=sys.stderr)
        
        try:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "grok-2-latest",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You have access to real-time X/Twitter data. Search and return results as JSON."
                        },
                        {
                            "role": "user", 
                            "content": f"""Search X/Twitter for posts about "{focus}" from the last 30 days.
                            
Return the top {count} most engaging posts as a JSON array with these fields:
- text: the post text (first 280 chars)
- author: @handle
- likes: number
- reposts: number  
- replies: number
- url: post URL
- created: date string

Return ONLY the JSON array, no other text."""
                        }
                    ],
                    "search": True,  # Enable X search
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                parsed = parse_x_response(text, debug)
                results.extend(parsed)
            elif debug:
                print(f"[x] API error: {response.status_code}", file=sys.stderr)
                
        except Exception as e:
            if debug:
                print(f"[x] request error: {e}", file=sys.stderr)
    
    return {
        "results": results[:count],
        "stats": {"mode": "api"}
    }


async def search_x_web(focus: str, count: int, debug: bool) -> dict:
    """
    Web fallback - returns search queries for agent to execute.
    """
    queries = [
        f'"{focus}" site:twitter.com OR site:x.com',
        f'{focus} trending twitter',
        f'{focus} viral tweet',
    ]
    
    return {
        "results": [],
        "stats": {
            "mode": "web",
            "queries": queries,
            "note": "Run these queries with WebSearch tool"
        }
    }


def parse_x_response(text: str, debug: bool = False) -> list:
    """Parse X results from API response."""
    results = []
    
    try:
        # Look for JSON array in response
        start = text.find('[')
        end = text.rfind(']') + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            for item in data:
                results.append({
                    "text": item.get("text", "")[:280],
                    "author": item.get("author", "").lstrip("@"),
                    "likes": int(item.get("likes", 0)),
                    "reposts": int(item.get("reposts", item.get("retweets", 0))),
                    "replies": int(item.get("replies", 0)),
                    "url": item.get("url", ""),
                    "created": item.get("created", ""),
                    "source": "x",
                })
    except:
        if debug:
            print("[x] failed to parse JSON response", file=sys.stderr)
    
    return results
