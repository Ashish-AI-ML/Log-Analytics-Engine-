"""Unit tests for the Summary Builder & Output Formatter."""

from __future__ import annotations

import pytest

from src.formatter import format_summary


def _empty_summary():
    return {
        "total_logs": 0,
        "info": 0,
        "warning": 0,
        "error": 0,
        "other": 0,
        "most_frequent_ip": None,
        "top_errors": [],
        "first_timestamp": None,
        "last_timestamp": None,
        "malformed_count": 0,
    }


class TestFormatSummary:
    """Tests for output formatting."""

    def test_empty_file_output(self):
        report = format_summary(_empty_summary())
        assert "Total Logs: 0" in report
        assert "INFO: 0" in report
        assert "WARNING: 0" in report
        assert "ERROR: 0" in report
        assert "Most Frequent IP: None" in report
        assert "Top 3 Errors: None" in report
        assert "First Log Time: None" in report
        assert "Last Log Time: None" in report
        # No malformed line should appear when count is 0.
        assert "Malformed" not in report

    def test_normal_output(self):
        summary = {
            "total_logs": 100,
            "info": 60,
            "warning": 25,
            "error": 15,
            "other": 0,
            "most_frequent_ip": "192.168.1.10",
            "top_errors": [
                ("Connection timeout", 8),
                ("DB failed", 5),
                ("Auth expired", 2),
            ],
            "first_timestamp": "2024-01-15 00:00:01",
            "last_timestamp": "2024-01-15 23:59:59",
            "malformed_count": 0,
        }
        report = format_summary(summary)
        assert "Total Logs: 100" in report
        assert "INFO: 60" in report
        assert "Most Frequent IP: 192.168.1.10" in report
        assert "1. Connection timeout (8)" in report
        assert "2. DB failed (5)" in report
        assert "3. Auth expired (2)" in report
        assert "First Log Time: 2024-01-15 00:00:01" in report
        assert "Last Log Time: 2024-01-15 23:59:59" in report

    def test_fewer_than_three_errors(self):
        summary = _empty_summary()
        summary["total_logs"] = 5
        summary["error"] = 1
        summary["top_errors"] = [("Only error", 1)]
        report = format_summary(summary)
        assert "1. Only error (1)" in report
        assert "2." not in report

    def test_malformed_shown_when_nonzero(self):
        summary = _empty_summary()
        summary["malformed_count"] = 42
        report = format_summary(summary)
        assert "Malformed Lines Skipped: 42" in report

    def test_output_line_order(self):
        """Ensure output lines appear in the correct order."""
        summary = {
            "total_logs": 10,
            "info": 5,
            "warning": 3,
            "error": 2,
            "other": 0,
            "most_frequent_ip": "10.0.0.1",
            "top_errors": [("Err", 2)],
            "first_timestamp": "2024-01-01 00:00:00",
            "last_timestamp": "2024-12-31 23:59:59",
            "malformed_count": 0,
        }
        report = format_summary(summary)
        lines = report.split("\n")
        assert lines[0].startswith("Total Logs:")
        assert lines[1].startswith("INFO:")
        assert lines[2].startswith("WARNING:")
        assert lines[3].startswith("ERROR:")
        assert lines[4].startswith("Most Frequent IP:")
