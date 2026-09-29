#!/usr/bin/env python3
"""Entry point: python3 <skill-dir>/scripts/reel.py <command> ..."""

import sys
from pathlib import Path

if sys.version_info < (3, 10):
    sys.exit("demo-reel needs Python 3.10+")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reelkit.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
