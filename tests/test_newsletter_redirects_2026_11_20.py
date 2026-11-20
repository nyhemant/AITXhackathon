"""2026-11-20: the robot-check page and the bad-address page forward (old links keep working)."""

from __future__ import annotations

import unittest

from busyparent_agent.url_aliases import redirect_location


class OldNewsletterPagesForward(unittest.TestCase):
    def test_one_more_step_goes_to_the_printables_hub(self):
        for path in ("/newsletter/one-more-step", "/newsletter/one-more-step/"):
            self.assertEqual(redirect_location(path), "/printables/")

    def test_oops_folds_into_try_again_and_keeps_the_reason(self):
        self.assertEqual(redirect_location("/newsletter/oops/", "reason=email"), "/newsletter/try-again/?reason=email")
        self.assertEqual(redirect_location("/newsletter/oops"), "/newsletter/try-again/")

    def test_kept_pages_do_not_redirect(self):
        for path in ("/newsletter/try-again/", "/newsletter/thanks/", "/newsletter/sample/"):
            self.assertIsNone(redirect_location(path))


if __name__ == "__main__":
    unittest.main()
