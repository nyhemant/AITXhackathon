"""The verify-kzk skill script must at least compile (an indentation slip shipped in #482)."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VerifySkillCompiles(unittest.TestCase):
    def test_verify_script_compiles(self):
        for path in sorted((ROOT / ".cursor" / "skills").glob("*/scripts/*.py")):
            with self.subTest(path=path.name):
                compile(path.read_text(encoding="utf-8"), str(path), "exec")


if __name__ == "__main__":
    unittest.main()
