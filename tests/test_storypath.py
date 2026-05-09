import json
import unittest

from busyparent_agent.adapters import mock_epic


ARYA = {
    "id": "arya",
    "name": "Arya",
    "age": 6,
    "reading_level": "early reader with parent support",
    "interests": ["space", "animals", "science", "brave characters", "drawing"],
    "favorite_moods": ["science", "bravery", "calm bedtime"],
    "repetition_preference": "moderate",
}
KUNAL = {
    "id": "kunal",
    "name": "Kunal",
    "age": 3,
    "reading_level": "preschool read-aloud",
    "interests": ["trucks", "dinosaurs", "silly sounds", "rhymes"],
    "favorite_moods": ["silly", "phonics", "short because parent is tired"],
    "repetition_preference": "high",
}


class StoryPathMockEpicTest(unittest.TestCase):
    def reading_history(self):
        with (mock_epic.DATA_DIR / "reading_history.json").open(encoding="utf-8") as file:
            return json.load(file)

    def test_catalog_depth_is_demo_realistic(self):
        books = mock_epic.get_catalog_books()

        self.assertGreaterEqual(len(books), 25)
        for book in books:
            self.assertIn("id", book)
            self.assertIn("title", book)
            self.assertIn("available", book)
            self.assertEqual(len(book["parent_prompts"]), 3)

    def test_unavailable_books_are_not_recommended(self):
        result = mock_epic.recommend_book(KUNAL, "silly", 8, self.reading_history())
        recommended_ids = [result["top_pick"]["book"]["id"]] + [
            item["book"]["id"] for item in result["alternatives"]
        ]

        self.assertNotIn("dragons-love-tacos", recommended_ids)
        self.assertTrue(all(item["book"]["available"] for item in [result["top_pick"], *result["alternatives"]]))

    def test_age_filtering_works_for_arya_vs_kunal(self):
        kunal_books = mock_epic.filter_books(KUNAL["age"], "science", 15)
        arya_books = mock_epic.filter_books(ARYA["age"], "phonics", 10)

        self.assertNotIn("ada-twist-scientist", {book["id"] for book in kunal_books})
        self.assertNotIn("little-blue-truck", {book["id"] for book in arya_books})

    def test_max_minutes_filtering_works(self):
        books = mock_epic.filter_books(KUNAL["age"], "calm bedtime", 5)

        self.assertTrue(books)
        self.assertTrue(all(book["read_minutes"] <= 5 for book in books))

    def test_recent_repeats_are_penalized_for_non_repeat_friendly_child(self):
        result = mock_epic.recommend_book(ARYA, "science", 12, self.reading_history())

        self.assertNotEqual(result["top_pick"]["book"]["id"], "ada-twist-scientist")
        ada = next(item for item in result["all_candidates"] if item["book"]["id"] == "ada-twist-scientist")
        self.assertIn("recently read -8", ada["reasons"])

    def test_mood_matching_works(self):
        result = mock_epic.recommend_book(KUNAL, "silly", 6, self.reading_history())

        top_book = result["top_pick"]["book"]
        self.assertIn("silly", top_book["mood_tags"])

    def test_recommendation_returns_one_top_pick_and_two_alternatives(self):
        result = mock_epic.recommend_book(KUNAL, "short because parent is tired", 6, self.reading_history())

        self.assertIsNotNone(result["top_pick"])
        self.assertEqual(len(result["alternatives"]), 2)
        self.assertNotIn(result["top_pick"], result["alternatives"])

    def test_search_books_matches_title_author_and_tags(self):
        science = mock_epic.search_books("space")
        author = mock_epic.search_books("Mo Willems")

        self.assertTrue(any(book["id"] == "mae-among-stars" for book in science))
        self.assertTrue(any(book["id"] == "dont-let-pigeon-drive-bus" for book in author))


if __name__ == "__main__":
    unittest.main()
