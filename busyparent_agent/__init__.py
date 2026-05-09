"""Import bridge for running the src package from a fresh clone.

The real package code lives in src/busyparent_agent. This small bridge keeps the
hackathon command simple:

    python -m busyparent_agent.app
"""

from pathlib import Path

SRC_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "busyparent_agent"

if SRC_PACKAGE.exists():
    __path__.append(str(SRC_PACKAGE))
