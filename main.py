#!/usr/bin/env python3
"""
Log Analytics Engine — CLI Entry Point.

Usage::

    python main.py <logfile> [--show-malformed]
"""

from __future__ import annotations

import argparse
import sys
import time

from src.engine import LogAnalyticsEngine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze server log files and produce structured summary reports.",
    )
    parser.add_argument(
        "logfile",
        help="Path to the log file to analyze.",
    )
    parser.add_argument(
        "--show-malformed",
        action="store_true",
        default=False,
        help="Include count of malformed/skipped lines in the report.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8).",
    )
    args = parser.parse_args()

    engine = LogAnalyticsEngine()

    start = time.perf_counter()
    try:
        report = engine.analyze(args.logfile, encoding=args.encoding)
    except FileNotFoundError:
        print(f"Error: File not found — {args.logfile}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied — {args.logfile}", file=sys.stderr)
        sys.exit(1)
    elapsed = time.perf_counter() - start

    print(report)
    print(f"\n[Processed in {elapsed:.3f}s]")


if __name__ == "__main__":
    main()
