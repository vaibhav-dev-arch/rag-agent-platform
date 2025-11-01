#!/usr/bin/env python3
"""
RAG Agent Platform CLI script.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from __main__ import main

if __name__ == "__main__":
    main()
