"""Unit tests for the Aggregation Engine."""

from __future__ import annotations

import pytest

from src.aggregator import LogAggregator
from src.parser import ParsedLog


def _make_entry(
    timestamp: str = "2024-01-15 10:00:00",
    level: str = "INFO",
    ip: str = "10.0.0.1",
    message: str = "Test message",
) -> ParsedLog:
    return ParsedLog(timestamp=timestamp, level=level, ip=ip, message=message)


class TestLogAggregator:
    """Core aggregation tests."""

    def test_empty_aggregator(self):
        agg = LogAggregator()
        summary = agg.get_summary()
        assert summary["total_logs"] == 0
        assert summary["info"] == 0
        assert summary["warning"] == 0
        assert summary["error"] == 0
        assert summary["most_frequent_ip"] is None
        assert summary["top_errors"] == []
        assert summary["first_timestamp"] is None
        assert summary["last_timestamp"] is None

    def test_single_info_entry(self):
        agg = LogAggregator()
        agg.process(_make_entry(level="INFO"))
        summary = agg.get_summary()
        assert summary["total_logs"] == 1
        assert summary["info"] == 1

    def test_level_counts(self):
        agg = LogAggregator()
        agg.process(_make_entry(level="INFO"))
        agg.process(_make_entry(level="INFO"))
        agg.process(_make_entry(level="WARNING"))
        agg.process(_make_entry(level="ERROR", message="Err1"))
        summary = agg.get_summary()
        assert summary["total_logs"] == 4
        assert summary["info"] == 2
        assert summary["warning"] == 1
        assert summary["error"] == 1

    def test_most_frequent_ip(self):
        agg = LogAggregator()
        for _ in range(5):
            agg.process(_make_entry(ip="192.168.1.10"))
        for _ in range(3):
            agg.process(_make_entry(ip="10.0.0.1"))
        agg.process(_make_entry(ip="172.16.0.5"))
        summary = agg.get_summary()
        assert summary["most_frequent_ip"] == "192.168.1.10"

    def test_top_errors(self):
        agg = LogAggregator()
        errors = [
            ("Connection timeout", 5),
            ("DB failed", 3),
            ("Auth expired", 2),
            ("Rare error", 1),
        ]
        for msg, count in errors:
            for _ in range(count):
                agg.process(_make_entry(level="ERROR", message=msg))
        summary = agg.get_summary()
        top = summary["top_errors"]
        assert len(top) == 3
        assert top[0] == ("Connection timeout", 5)
        assert top[1] == ("DB failed", 3)
        assert top[2] == ("Auth expired", 2)

    def test_fewer_than_3_errors(self):
        agg = LogAggregator()
        agg.process(_make_entry(level="ERROR", message="Only error"))
        summary = agg.get_summary()
        assert len(summary["top_errors"]) == 1

    def test_timestamps(self):
        agg = LogAggregator()
        agg.process(_make_entry(timestamp="2024-01-15 08:00:00"))
        agg.process(_make_entry(timestamp="2024-01-15 23:59:59"))
        agg.process(_make_entry(timestamp="2024-01-15 12:00:00"))
        summary = agg.get_summary()
        assert summary["first_timestamp"] == "2024-01-15 08:00:00"
        assert summary["last_timestamp"] == "2024-01-15 23:59:59"

    def test_malformed_counter(self):
        agg = LogAggregator()
        agg.record_malformed()
        agg.record_malformed()
        summary = agg.get_summary()
        assert summary["malformed_count"] == 2

    def test_other_level(self):
        agg = LogAggregator()
        agg.process(_make_entry(level="OTHER"))
        summary = agg.get_summary()
        assert summary["other"] == 1
