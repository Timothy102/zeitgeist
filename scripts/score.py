"""
Engagement scoring and deduplication.
"""

from datetime import datetime, timedelta
from typing import List


def score_results(results: List[dict], platform: str) -> List[dict]:
    """
    Score results by engagement and freshness.
    
    Adds 'zeitgeist_score' to each result.
    """
    now = datetime.now()
    
    for r in results:
        # Base engagement score
        if platform == "reddit":
            engagement = (
                r.get("score", 0) * 1.0 +
                r.get("num_comments", 0) * 2.0  # Comments worth more
            )
        else:  # x
            engagement = (
                r.get("likes", 0) * 1.0 +
                r.get("reposts", 0) * 3.0 +  # Reposts worth more
                r.get("replies", 0) * 2.0
            )
        
        # Freshness multiplier
        created = parse_date(r.get("created", ""))
        if created:
            age = now - created
            if age < timedelta(hours=24):
                freshness = 1.0
            elif age < timedelta(days=7):
                freshness = 0.8
            elif age < timedelta(days=14):
                freshness = 0.6
            elif age < timedelta(days=30):
                freshness = 0.4
            else:
                freshness = 0.2
        else:
            freshness = 0.5  # Unknown date
        
        r["zeitgeist_score"] = engagement * freshness
    
    # Sort by score
    results.sort(key=lambda x: x.get("zeitgeist_score", 0), reverse=True)
    
    return results


def dedupe_results(results: List[dict]) -> List[dict]:
    """
    Remove duplicate/near-duplicate results.
    """
    seen = set()
    deduped = []
    
    for r in results:
        # Create fingerprint from key content
        if r.get("source") == "reddit":
            fp = (r.get("subreddit", ""), r.get("title", "")[:50].lower())
        else:
            fp = (r.get("author", ""), r.get("text", "")[:50].lower())
        
        if fp not in seen:
            seen.add(fp)
            deduped.append(r)
    
    return deduped


def parse_date(date_str: str) -> datetime | None:
    """Try to parse various date formats."""
    if not date_str:
        return None
    
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str[:19], fmt[:len(date_str)])
        except:
            continue
    
    return None
