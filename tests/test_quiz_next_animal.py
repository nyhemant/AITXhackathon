"""Quiz finish offers a photo next-animal link at every tier."""
import unittest
from pathlib import Path

JS = Path(__file__).resolve().parents[1] / "static" / "field-pack" / "js" / "study-card.js"


class QuizNextAnimalTest(unittest.TestCase):
    def test_finish_next_html_has_photo_next_animal(self):
        js = JS.read_text(encoding="utf-8")
        self.assertIn("function finishNextHtml(root, cardId, level)", js)
        body = js.split("function finishNextHtml(root, cardId, level)", 1)[1]
        body = body.split("function paintFinish", 1)[0]
        self.assertIn("next_animal", body)
        self.assertIn("#from=quiz-next", body)
        self.assertIn("Meet a new animal", body)
        self.assertIn("FPStudyPickTryNextIds", body)
        self.assertIn("-320-v1.webp", body)
