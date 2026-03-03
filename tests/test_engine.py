"""Integration tests for the Log Analytics Engine (end-to-end)."""

from __future__ import annotations

import os
import tempfile

import pytest

from src.engine import LogAnalyticsEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_temp_log(content: str) -> str:
    """Write *content* to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".log")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

VALID_LOG = """\
2024-01-15 08:00:00 INFO 192.168.1.10 User login successful
2024-01-15 08:00:01 INFO 192.168.1.10 Page /dashboard loaded
2024-01-15 08:00:02 WARNING 10.0.0.1 High memory usage detected
2024-01-15 08:00:03 ERROR 172.16.0.5 Connection timeout on port 8080
2024-01-15 08:00:04 ERROR 172.16.0.5 Connection timeout on port 8080
2024-01-15 08:00:05 ERROR 192.168.1.10 Database connection failed
2024-01-15 08:00:06 INFO 10.0.0.1 Health check passed
"""

MALFORMED_LOG = """\
this is garbage
another bad line
not a log entry
"""

MIXED_LOG = """\
2024-01-15 10:00:00 INFO 10.0.0.1 Good line 1
garbage line here
2024-01-15 10:00:02 ERROR 10.0.0.1 Server crashed

2024-01-15 10:00:03 INFO 10.0.0.1 Good line 2
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEngineEndToEnd:

    def test_valid_file(self):
        path = _write_temp_log(VALID_LOG)
        try:
            engine = LogAnalyticsEngine()
            summary = engine.get_raw_summary(path)
            assert summary["total_logs"] == 7
            assert summary["info"] == 3
            assert summary["warning"] == 1
            assert summary["error"] == 3
            assert summary["most_frequent_ip"] == "192.168.1.10"
            assert summary["first_timestamp"] == "2024-01-15 08:00:00"
            assert summary["last_timestamp"] == "2024-01-15 08:00:06"
            # Top error
            assert summary["top_errors"][0][0] == "Connection timeout on port 8080"
            assert summary["top_errors"][0][1] == 2
        finally:
            os.unlink(path)

    def test_empty_file(self):
        path = _write_temp_log("")
        try:
            engine = LogAnalyticsEngine()
            summary = engine.get_raw_summary(path)
            assert summary["total_logs"] == 0
            assert summary["most_frequent_ip"] is None
            assert summary["top_errors"] == []
            assert summary["first_timestamp"] is None
            assert summary["last_timestamp"] is None
        finally:
            os.unlink(path)

    def test_all_malformed(self):
        path = _write_temp_log(MALFORMED_LOG)
        try:
            engine = LogAnalyticsEngine()
            summary = engine.get_raw_summary(path)
            assert summary["total_logs"] == 0
            assert summary["malformed_count"] == 3
        finally:
            os.unlink(path)

    def test_mixed_valid_and_malformed(self):
        path = _write_temp_log(MIXED_LOG)
        try:
            engine = LogAnalyticsEngine()
            summary = engine.get_raw_summary(path)
            assert summary["total_logs"] == 3
            assert summary["malformed_count"] == 1  # "garbage line here"
            assert summary["error"] == 1
        finally:
            os.unlink(path)

    def test_formatted_report(self):
        path = _write_temp_log(VALID_LOG)
        try:
            engine = LogAnalyticsEngine()
            report = engine.analyze(path)
            assert "Total Logs: 7" in report
            assert "Most Frequent IP: 192.168.1.10" in report
            assert "Connection timeout on port 8080" in report
        finally:
            os.unlink(path)

    def test_only_info_logs(self):
        content = """\
2024-01-15 08:00:00 INFO 10.0.0.1 Message one
2024-01-15 08:00:01 INFO 10.0.0.1 Message two
"""
        path = _write_temp_log(content)
        try:
            engine = LogAnalyticsEngine()
            summary = engine.get_raw_summary(path)
            assert summary["total_logs"] == 2
            assert summary["info"] == 2
            assert summary["error"] == 0
            assert summary["top_errors"] == []
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        engine = LogAnalyticsEngine()
        with pytest.raises(FileNotFoundError):
            engine.analyze("/nonexistent/path/fake.log")
