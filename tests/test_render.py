"""Tests for render module."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from render import render_compact, render_json, render_markdown, determine_mode


class TestDetermineMode:
    def test_mock_mode(self):
        assert determine_mode({"reddit": "mock", "x": "api"}) == "mock"
        assert determine_mode({"reddit": "api", "x": "mock"}) == "mock"

    def test_mcp_mode(self):
        assert determine_mode({"reddit": "mcp", "x": "web"}) == "mcp"

    def test_api_mode(self):
        assert determine_mode({"reddit": "api", "x": "web"}) == "api"

    def test_web_mode(self):
        assert determine_mode({"reddit": "web", "x": "web"}) == "web"

    def test_empty_sources(self):
        assert determine_mode({}) == "web"


class TestRenderCompact:
    @pytest.fixture
    def sample_data(self):
        return {
            "focus": "indie beauty",
            "timestamp": "2026-01-15T10:00:00",
            "sources": {"reddit": "api", "x": "api"},
            "reddit": {
                "results": [
                    {
                        "title": "Best indie brands 2026",
                        "subreddit": "SkincareAddiction",
                        "score": 2400,
                        "zeitgeist_score": 2400,
                    }
                ]
            },
            "x": {
                "results": [
                    {
                        "text": "These indie brands are amazing",
                        "author": "beautyexpert",
                        "likes": 890,
                        "zeitgeist_score": 890,
                    }
                ]
            },
            "stats": {
                "reddit": {"count": 1, "upvotes": 2400, "subreddits": ["SkincareAddiction"]},
                "x": {"count": 1, "likes": 890, "authors": ["beautyexpert"]},
            },
        }

    def test_includes_focus(self, sample_data):
        output = render_compact(sample_data)
        assert "indie beauty" in output

    def test_includes_timestamp(self, sample_data):
        output = render_compact(sample_data)
        assert "2026-01-15" in output

    def test_includes_top_signals(self, sample_data):
        output = render_compact(sample_data)
        assert "Top signals" in output
        assert "Best indie brands" in output

    def test_includes_who_to_watch(self, sample_data):
        output = render_compact(sample_data)
        assert "Who to watch" in output
        assert "r/SkincareAddiction" in output
        assert "@beautyexpert" in output

    def test_includes_stats_footer(self, sample_data):
        output = render_compact(sample_data)
        assert "Research complete" in output
        assert "Reddit:" in output
        assert "X:" in output

    def test_shows_mode(self, sample_data):
        output = render_compact(sample_data)
        assert "Mode: api" in output

    def test_handles_empty_results(self):
        data = {
            "focus": "test",
            "timestamp": "2026-01-15",
            "sources": {"reddit": "web", "x": "web"},
            "reddit": {"results": []},
            "x": {"results": []},
            "stats": {"reddit": {"count": 0}, "x": {"count": 0}},
        }
        output = render_compact(data)
        assert "test" in output
        assert "Mode: web" in output


class TestRenderJson:
    def test_returns_valid_json(self):
        data = {"focus": "test", "results": [1, 2, 3]}
        output = render_json(data)
        parsed = json.loads(output)
        assert parsed["focus"] == "test"

    def test_pretty_prints(self):
        data = {"a": 1, "b": 2}
        output = render_json(data)
        assert "\n" in output


class TestRenderMarkdown:
    @pytest.fixture
    def sample_data(self):
        return {
            "focus": "sneaker culture",
            "timestamp": "2026-01-15T10:00:00",
            "reddit": {
                "results": [
                    {
                        "title": "New Jordan Release",
                        "subreddit": "Sneakers",
                        "score": 5000,
                        "num_comments": 300,
                        "url": "https://reddit.com/r/Sneakers/123",
                    }
                ]
            },
            "x": {
                "results": [
                    {
                        "text": "These sneakers are fire",
                        "author": "sneakerhead",
                        "likes": 1200,
                        "reposts": 50,
                        "url": "https://x.com/sneakerhead/456",
                    }
                ]
            },
            "stats": {},
        }

    def test_includes_title(self, sample_data):
        output = render_markdown(sample_data)
        assert "# Zeitgeist Report: sneaker culture" in output

    def test_includes_reddit_section(self, sample_data):
        output = render_markdown(sample_data)
        assert "## Reddit" in output
        assert "New Jordan Release" in output
        assert "r/Sneakers" in output

    def test_includes_x_section(self, sample_data):
        output = render_markdown(sample_data)
        assert "## X / Twitter" in output
        assert "@sneakerhead" in output
        assert "These sneakers are fire" in output

    def test_includes_stats_section(self, sample_data):
        output = render_markdown(sample_data)
        assert "## Stats" in output
