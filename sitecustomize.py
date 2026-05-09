"""Make the src/ package importable when running from the repo root."""

from pathlib import Path
import sys

SRC = Path(__file__).resolve().parent / "src"

if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
