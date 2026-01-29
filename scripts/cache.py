"""
Simple file-based cache with TTL.
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "zeitgeist"
CACHE_TTL = timedelta(hours=24)


def cache_key(focus: str) -> str:
    """Generate cache key from focus."""
    normalized = focus.lower().strip()
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def get_cache(key: str) -> dict | None:
    """Get cached results if fresh."""
    cache_file = CACHE_DIR / f"{key}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file) as f:
            data = json.load(f)
        
        # Check TTL
        cached_at = datetime.fromisoformat(data.get("_cached_at", "2000-01-01"))
        if datetime.now() - cached_at > CACHE_TTL:
            return None
        
        return data
    except:
        return None


def set_cache(key: str, data: dict) -> None:
    """Cache results."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    data["_cached_at"] = datetime.now().isoformat()
    
    cache_file = CACHE_DIR / f"{key}.json"
    with open(cache_file, "w") as f:
        json.dump(data, f)


def clear_cache() -> int:
    """Clear all cached results. Returns count cleared."""
    if not CACHE_DIR.exists():
        return 0
    
    count = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
        count += 1
    
    return count
