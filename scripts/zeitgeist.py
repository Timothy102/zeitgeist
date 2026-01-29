#!/usr/bin/env python3
"""
Zeitgeist: Deep Cultural Research
Research Reddit and X for cultural signals, synthesize into context.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from sources import detect_sources
from reddit import search_reddit
from twitter import search_x
from cache import get_cache, set_cache, cache_key
from score import score_results, dedupe_results
from render import render_compact, render_json, render_full


def parse_args():
    parser = argparse.ArgumentParser(description="Zeitgeist: Cultural Research")
    parser.add_argument("focus", nargs="?", default="general culture",
                        help="Niche, vertical, or audience to research")
    parser.add_argument("--emit", choices=["compact", "json", "full"], default="compact",
                        help="Output format")
    parser.add_argument("--quick", action="store_true", help="Quick scan")
    parser.add_argument("--deep", action="store_true", help="Deep research")
    parser.add_argument("--refresh", action="store_true", help="Bypass cache")
    parser.add_argument("--mock", action="store_true", help="Use fixtures instead of real API calls")
    parser.add_argument("--reddit-only", action="store_true")
    parser.add_argument("--x-only", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def get_depth(args):
    if args.quick:
        return {"reddit": 10, "x": 10, "label": "quick"}
    elif args.deep:
        return {"reddit": 50, "x": 40, "label": "deep"}
    return {"reddit": 25, "x": 20, "label": "standard"}


async def research(focus: str, sources: dict, depth: dict, debug: bool = False, mock: bool = False):
    """Run parallel research across platforms."""
    results = {
        "focus": focus,
        "timestamp": datetime.now().isoformat(),
        "depth": depth["label"],
        "sources": sources if not mock else {"reddit": "mock", "x": "mock"},
        "reddit": {"results": [], "stats": {}},
        "x": {"results": [], "stats": {}},
    }
    
    tasks = []
    
    if sources["reddit"] != "none":
        if debug:
            print(f"[reddit] mode={sources['reddit']} mock={mock}", file=sys.stderr)
        tasks.append(("reddit", search_reddit(
            focus, mode=sources["reddit"], count=depth["reddit"], debug=debug, mock=mock
        )))
    
    if sources["x"] != "none":
        if debug:
            print(f"[x] mode={sources['x']} mock={mock}", file=sys.stderr)
        tasks.append(("x", search_x(
            focus, mode=sources["x"], count=depth["x"], debug=debug, mock=mock
        )))
    
    for name, coro in tasks:
        try:
            data = await coro
            results[name] = data
        except Exception as e:
            if debug:
                print(f"[{name}] error: {e}", file=sys.stderr)
            results[name] = {"results": [], "stats": {"error": str(e)}}
    
    return results


def process_results(results: dict) -> dict:
    """Score, dedupe, and compute stats."""
    # Score and dedupe
    results["reddit"]["results"] = dedupe_results(
        score_results(results["reddit"].get("results", []), "reddit")
    )
    results["x"]["results"] = dedupe_results(
        score_results(results["x"].get("results", []), "x")
    )
    
    # Compute aggregate stats
    reddit_results = results["reddit"]["results"]
    x_results = results["x"]["results"]
    
    results["stats"] = {
        "reddit": {
            "count": len(reddit_results),
            "upvotes": sum(r.get("score", 0) for r in reddit_results),
            "comments": sum(r.get("num_comments", 0) for r in reddit_results),
            "subreddits": list(set(r.get("subreddit", "") for r in reddit_results if r.get("subreddit"))),
        },
        "x": {
            "count": len(x_results),
            "likes": sum(r.get("likes", 0) for r in x_results),
            "reposts": sum(r.get("reposts", 0) for r in x_results),
            "authors": list(set(r.get("author", "") for r in x_results if r.get("author"))),
        }
    }
    
    return results


def main():
    args = parse_args()
    
    if args.debug:
        print(f"[zeitgeist] focus='{args.focus}'", file=sys.stderr)
    
    # Check cache
    key = cache_key(args.focus)
    if not args.refresh:
        cached = get_cache(key)
        if cached:
            if args.debug:
                print("[zeitgeist] cache hit", file=sys.stderr)
            if args.emit == "json":
                print(render_json(cached))
            elif args.emit == "full":
                print(render_full(cached))
            else:
                print(render_compact(cached))
            return
    
    # Detect sources
    preference = "both"
    if args.reddit_only:
        preference = "reddit"
    elif args.x_only:
        preference = "x"
    
    sources = detect_sources(preference)
    
    if args.debug:
        print(f"[zeitgeist] sources={sources}", file=sys.stderr)
    
    depth = get_depth(args)
    
    # Run research
    results = asyncio.run(research(args.focus, sources, depth, args.debug, args.mock))
    
    # Process
    results = process_results(results)
    
    # Cache
    set_cache(key, results)
    
    # Output
    if args.emit == "json":
        print(render_json(results))
    elif args.emit == "full":
        print(render_full(results))
    else:
        print(render_compact(results))


if __name__ == "__main__":
    main()
