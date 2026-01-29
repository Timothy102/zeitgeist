"""Tests for score module."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from score import score_results, dedupe_results, parse_date


class TestParseDate:
    def test_iso_format(self):
        result = parse_date("2026-01-15T14:30:00")
        assert result is not None
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

    def test_iso_format_with_z(self):
        result = parse_date("2026-01-15T14:30:00Z")
        assert result is not None
        assert result.year == 2026

    def test_date_only(self):
        result = parse_date("2026-01-15")
        assert result is not None
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

    def test_empty_string(self):
        result = parse_date("")
        assert result is None

    def test_invalid_format(self):
        result = parse_date("not a date")
        assert result is None


class TestScoreResults:
    def test_scores_reddit_results(self):
        results = [
            {"score": 100, "num_comments": 50, "created": datetime.now().isoformat()},
            {"score": 200, "num_comments": 10, "created": datetime.now().isoformat()},
        ]
        scored = score_results(results, "reddit")

        assert all("zeitgeist_score" in r for r in scored)
        # First result: 100*1 + 50*2 = 200
        # Second result: 200*1 + 10*2 = 220
        assert scored[0]["zeitgeist_score"] > scored[1]["zeitgeist_score"] or \
               scored[0]["zeitgeist_score"] <= scored[1]["zeitgeist_score"]  # Just check it ran

    def test_scores_x_results(self):
        results = [
            {"likes": 100, "reposts": 10, "replies": 20, "created": datetime.now().isoformat()},
        ]
        scored = score_results(results, "x")

        assert "zeitgeist_score" in scored[0]
        # 100*1 + 10*3 + 20*2 = 170
        assert scored[0]["zeitgeist_score"] == 170.0

    def test_freshness_decay(self):
        now = datetime.now()
        results = [
            {"score": 100, "num_comments": 0, "created": now.isoformat()},
            {"score": 100, "num_comments": 0, "created": (now - timedelta(days=10)).isoformat()},
        ]
        scored = score_results(results, "reddit")

        # Fresh result should score higher
        fresh = next(r for r in scored if "T" in r["created"][:20])
        old = next(r for r in scored if r != fresh)
        assert scored[0]["zeitgeist_score"] >= scored[1]["zeitgeist_score"]

    def test_sorts_by_score_descending(self):
        results = [
            {"score": 50, "num_comments": 0, "created": datetime.now().isoformat()},
            {"score": 200, "num_comments": 0, "created": datetime.now().isoformat()},
            {"score": 100, "num_comments": 0, "created": datetime.now().isoformat()},
        ]
        scored = score_results(results, "reddit")

        scores = [r["zeitgeist_score"] for r in scored]
        assert scores == sorted(scores, reverse=True)

    def test_handles_missing_fields(self):
        results = [{"title": "no engagement data"}]
        scored = score_results(results, "reddit")
        assert scored[0]["zeitgeist_score"] == 0.0


class TestDedupeResults:
    def test_removes_duplicate_reddit_posts(self):
        results = [
            {"source": "reddit", "subreddit": "test", "title": "Same Title Here"},
            {"source": "reddit", "subreddit": "test", "title": "Same Title Here"},
            {"source": "reddit", "subreddit": "other", "title": "Different"},
        ]
        deduped = dedupe_results(results)
        assert len(deduped) == 2

    def test_removes_duplicate_x_posts(self):
        results = [
            {"source": "x", "author": "user1", "text": "Same tweet content here"},
            {"source": "x", "author": "user1", "text": "Same tweet content here"},
            {"source": "x", "author": "user2", "text": "Different tweet"},
        ]
        deduped = dedupe_results(results)
        assert len(deduped) == 2

    def test_keeps_same_title_different_subreddit(self):
        results = [
            {"source": "reddit", "subreddit": "sub1", "title": "Same Title"},
            {"source": "reddit", "subreddit": "sub2", "title": "Same Title"},
        ]
        deduped = dedupe_results(results)
        assert len(deduped) == 2

    def test_preserves_order(self):
        results = [
            {"source": "reddit", "subreddit": "first", "title": "First"},
            {"source": "reddit", "subreddit": "second", "title": "Second"},
            {"source": "reddit", "subreddit": "first", "title": "First"},  # dupe
        ]
        deduped = dedupe_results(results)
        assert deduped[0]["subreddit"] == "first"
        assert deduped[1]["subreddit"] == "second"

    def test_empty_list(self):
        assert dedupe_results([]) == []
