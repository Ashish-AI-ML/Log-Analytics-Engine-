#!/usr/bin/env python3
"""
Synthetic Log File Generator.

Generates realistic server log files with configurable size for
performance and integration testing.

Usage::

    python tests/generate_logs.py --lines 1000000 --output test_logs.log
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# --- Realistic data pools ------------------------------------------------

IPS = [
    "192.168.1.10",
    "192.168.1.11",
    "10.0.0.1",
    "10.0.0.2",
    "172.16.0.5",
    "172.16.0.8",
    "192.168.0.100",
    "10.10.10.10",
    "10.0.0.50",
    "192.168.2.25",
]

INFO_MESSAGES = [
    "User login successful",
    "Page /dashboard loaded",
    "API request completed in 120ms",
    "Session started for user admin",
    "Cache refreshed successfully",
    "Scheduled job executed",
    "Health check passed",
    "Data sync completed",
    "Configuration reloaded",
    "New connection accepted",
]

WARNING_MESSAGES = [
    "High memory usage detected (85%)",
    "Slow query execution (>2s)",
    "Disk usage above 70%",
    "Connection pool nearing capacity",
    "Deprecated API endpoint called",
    "Rate limit threshold approaching",
    "SSL certificate expires in 30 days",
    "Response time degraded",
]

ERROR_MESSAGES = [
    "Connection timeout on port 8080",
    "Database connection failed",
    "Authentication token expired",
    "Out of memory exception",
    "File not found: /data/config.yaml",
    "Permission denied accessing /var/log",
    "Null pointer exception in module auth",
    "Service unavailable: payment-gateway",
    "Socket read timeout after 30s",
    "Internal server error on /api/v2/users",
]

MALFORMED_LINES = [
    "this is not a valid log line",
    "RANDOM GARBAGE 12345",
    "---",
    "",
    "2024-01-15 BADTIME ERROR 999.999.999.999 broken",
    "partial line without enough fields",
]


def generate_log_file(
    output_path: str,
    num_lines: int = 100_000,
    malformed_pct: float = 2.0,
    seed: int = 42,
) -> None:
    """Generate a synthetic log file.

    Parameters
    ----------
    output_path : str
        Destination file path.
    num_lines : int
        Total number of lines to generate.
    malformed_pct : float
        Percentage of lines that should be malformed (0–100).
    seed : int
        Random seed for reproducibility.
    """
    random.seed(seed)

    base_time = datetime(2024, 1, 15, 0, 0, 0)
    level_weights = {"INFO": 60, "WARNING": 25, "ERROR": 15}
    levels = list(level_weights.keys())
    weights = list(level_weights.values())

    malformed_count = int(num_lines * malformed_pct / 100)
    # Indices where malformed lines will be inserted
    malformed_indices = set(random.sample(range(num_lines), min(malformed_count, num_lines)))

    with open(output_path, "w", encoding="utf-8") as fh:
        for i in range(num_lines):
            if i in malformed_indices:
                fh.write(random.choice(MALFORMED_LINES) + "\n")
                continue

            # Advance timestamp slightly
            ts = base_time + timedelta(seconds=i)
            timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

            level = random.choices(levels, weights=weights, k=1)[0]
            ip = random.choice(IPS)

            if level == "INFO":
                message = random.choice(INFO_MESSAGES)
            elif level == "WARNING":
                message = random.choice(WARNING_MESSAGES)
            else:
                message = random.choice(ERROR_MESSAGES)

            fh.write(f"{timestamp} {level} {ip} {message}\n")

    print(f"Generated {num_lines:,} lines -> {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic log files.")
    parser.add_argument("--lines", type=int, default=100_000, help="Number of lines (default: 100,000)")
    parser.add_argument("--output", default="test_logs.log", help="Output file path (default: test_logs.log)")
    parser.add_argument("--malformed-pct", type=float, default=2.0, help="Percent of malformed lines (default: 2.0)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    generate_log_file(args.output, args.lines, args.malformed_pct, args.seed)


if __name__ == "__main__":
    main()
