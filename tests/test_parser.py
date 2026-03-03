"""Unit tests for the Line Parser & Validation Layer."""

from __future__ import annotations

import pytest

from src.parser import ParsedLog, parse_line


class TestParseLineValid:
    """Tests for correctly formatted log lines."""

    def test_info_line(self):
        line = "2024-01-15 10:23:45 INFO 192.168.1.10 User login successful"
        result = parse_line(line)
        assert result is not None
        assert result.timestamp == "2024-01-15 10:23:45"
        assert result.level == "INFO"
        assert result.ip == "192.168.1.10"
        assert result.message == "User login successful"

    def test_warning_line(self):
        line = "2024-06-30 23:59:59 WARNING 10.0.0.1 High memory usage detected"
        result = parse_line(line)
        assert result is not None
        assert result.level == "WARNING"

    def test_error_line(self):
        line = "2024-01-01 00:00:00 ERROR 172.16.0.5 Connection timeout on port 8080"
        result = parse_line(line)
        assert result is not None
        assert result.level == "ERROR"
        assert result.message == "Connection timeout on port 8080"

    def test_message_with_spaces(self):
        line = "2024-01-15 10:00:00 INFO 10.0.0.1 This is a really long message with many words"
        result = parse_line(line)
        assert result is not None
        assert result.message == "This is a really long message with many words"


class TestParseLineInvalid:
    """Tests for malformed or edge-case lines."""

    def test_blank_line(self):
        assert parse_line("") is None

    def test_whitespace_only(self):
        assert parse_line("   \t  ") is None

    def test_too_few_tokens(self):
        assert parse_line("2024-01-15 10:00:00 ERROR") is None

    def test_four_tokens_missing_message(self):
        assert parse_line("2024-01-15 10:00:00 ERROR 10.0.0.1") is None

    def test_invalid_timestamp(self):
        assert parse_line("NOT-A-DATE 10:00:00 ERROR 10.0.0.1 Msg") is None

    def test_invalid_ip(self):
        assert parse_line("2024-01-15 10:00:00 ERROR not.an.ip Msg") is None

    def test_invalid_ip_format(self):
        assert parse_line("2024-01-15 10:00:00 ERROR 999.999.999 Msg") is None

    def test_garbage_line(self):
        assert parse_line("this is not a valid log line at all") is None


class TestParseLineUnknownLevel:
    """Tests for unknown/non-standard log levels."""

    def test_debug_becomes_other(self):
        line = "2024-01-15 10:00:00 DEBUG 10.0.0.1 Debug message"
        result = parse_line(line)
        assert result is not None
        assert result.level == "OTHER"

    def test_critical_becomes_other(self):
        line = "2024-01-15 10:00:00 CRITICAL 10.0.0.1 Critical failure"
        result = parse_line(line)
        assert result is not None
        assert result.level == "OTHER"

    def test_lowercase_level_normalised(self):
        line = "2024-01-15 10:00:00 info 10.0.0.1 Lowercase level"
        result = parse_line(line)
        assert result is not None
        assert result.level == "INFO"
