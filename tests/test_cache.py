"""Tests for cache module."""

import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from cache import cache_key, get_cache, set_cache, clear_cache, CACHE_TTL


class TestCacheKey:
    def test_generates_consistent_key(self):
        key1 = cache_key("sneaker culture")
        key2 = cache_key("sneaker culture")
        assert key1 == key2

    def test_normalizes_case(self):
        key1 = cache_key("Sneaker Culture")
        key2 = cache_key("sneaker culture")
        assert key1 == key2

    def test_normalizes_whitespace(self):
        key1 = cache_key("  sneaker culture  ")
        key2 = cache_key("sneaker culture")
        assert key1 == key2

    def test_different_inputs_different_keys(self):
        key1 = cache_key("sneaker culture")
        key2 = cache_key("indie beauty")
        assert key1 != key2

    def test_returns_12_char_string(self):
        key = cache_key("test topic")
        assert len(key) == 12
        assert key.isalnum()


class TestCacheOperations:
    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        with patch("cache.CACHE_DIR", tmp_path):
            yield tmp_path

    def test_set_and_get_cache(self, temp_cache_dir):
        with patch("cache.CACHE_DIR", temp_cache_dir):
            test_data = {"focus": "test", "results": [1, 2, 3]}
            set_cache("testkey123", test_data)

            result = get_cache("testkey123")
            assert result is not None
            assert result["focus"] == "test"
            assert result["results"] == [1, 2, 3]

    def test_get_missing_cache_returns_none(self, temp_cache_dir):
        with patch("cache.CACHE_DIR", temp_cache_dir):
            result = get_cache("nonexistent")
            assert result is None

    def test_expired_cache_returns_none(self, temp_cache_dir):
        with patch("cache.CACHE_DIR", temp_cache_dir):
            cache_file = temp_cache_dir / "expired123.json"
            old_time = (datetime.now() - timedelta(hours=25)).isoformat()
            cache_file.write_text(json.dumps({"_cached_at": old_time, "data": "old"}))

            result = get_cache("expired123")
            assert result is None

    def test_fresh_cache_returns_data(self, temp_cache_dir):
        with patch("cache.CACHE_DIR", temp_cache_dir):
            cache_file = temp_cache_dir / "fresh12345.json"
            fresh_time = (datetime.now() - timedelta(hours=1)).isoformat()
            cache_file.write_text(json.dumps({"_cached_at": fresh_time, "data": "fresh"}))

            result = get_cache("fresh12345")
            assert result is not None
            assert result["data"] == "fresh"

    def test_clear_cache(self, temp_cache_dir):
        with patch("cache.CACHE_DIR", temp_cache_dir):
            (temp_cache_dir / "file1.json").write_text("{}")
            (temp_cache_dir / "file2.json").write_text("{}")

            count = clear_cache()
            assert count == 2
            assert list(temp_cache_dir.glob("*.json")) == []

    def test_clear_empty_cache(self, temp_cache_dir):
        with patch("cache.CACHE_DIR", temp_cache_dir):
            count = clear_cache()
            assert count == 0
