"""
Source detection: MCP > API > Web fallback
"""

import json
import os
from pathlib import Path


def load_env(path: Path) -> dict:
    """Load .env file."""
    env = {}
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"\'')
    return env


def check_mcp() -> dict:
    """Check for MCP server configs."""
    servers = {}
    paths = [
        Path.home() / ".config" / "claude" / "claude_desktop_config.json",
        Path.home() / ".claude" / "mcp.json",
        Path(".mcp.json"),
    ]
    
    for p in paths:
        if p.exists():
            try:
                with open(p) as f:
                    cfg = json.load(f)
                    servers.update(cfg.get("mcpServers", {}))
            except:
                pass
    
    return servers


def check_api_keys() -> dict:
    """Check for API keys."""
    keys = {}
    
    # Config file
    env_path = Path.home() / ".config" / "zeitgeist" / ".env"
    if env_path.exists():
        keys.update(load_env(env_path))
    
    # Environment overrides
    for k in ["OPENAI_API_KEY", "XAI_API_KEY"]:
        if os.environ.get(k):
            keys[k] = os.environ[k]
    
    return keys


def detect_sources(preference: str = "both") -> dict:
    """
    Detect best available source for each platform.
    
    Returns: {"reddit": mode, "x": mode}
    where mode is "mcp", "api", "web", or "none"
    """
    mcp = check_mcp()
    keys = check_api_keys()
    
    # Reddit MCP names
    has_reddit_mcp = any(n in mcp for n in [
        "reddit", "mcp-server-reddit", "reddit-mcp", "mcp-reddit"
    ])
    
    # X MCP names
    has_x_mcp = any(n in mcp for n in [
        "twitter", "x", "x-mcp", "mcp-twikit", "twitter-mcp"
    ])
    
    has_openai = bool(keys.get("OPENAI_API_KEY"))
    has_xai = bool(keys.get("XAI_API_KEY"))
    
    # Determine modes
    if preference in ["both", "reddit"]:
        if has_reddit_mcp:
            reddit = "mcp"
        elif has_openai:
            reddit = "api"
        else:
            reddit = "web"
    else:
        reddit = "none"
    
    if preference in ["both", "x"]:
        if has_x_mcp:
            x = "mcp"
        elif has_xai:
            x = "api"
        else:
            x = "web"
    else:
        x = "none"
    
    return {"reddit": reddit, "x": x}


def get_api_key(name: str) -> str:
    """Get specific API key."""
    keys = check_api_keys()
    return keys.get(name, "")
