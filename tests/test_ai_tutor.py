# tests/test_ai_tutor.py - Tests for AI weather tutor module
import unittest
from modules.ai_tutor import process_question, get_greeting, KNOWLEDGE_BASE

class TestAITutor(unittest.TestCase):

    def test_process_question_knowledge_base(self):
        # Tsunami question
        res = process_question("What is a tsunami?", lang="en")
        self.assertIn("answer", res)
        self.assertIn("tsunami", res["answer"].lower())
        self.assertIn("powered_by", res)

    def test_process_question_cyclone(self):
        res = process_question("Tell me about cyclone categories", lang="en")
        self.assertIn("answer", res)
        self.assertIn("cyclone", res["answer"].lower())

    def test_get_greeting(self):
        greeting = get_greeting("en")
        self.assertIn("WeatherSense AI", greeting)

    def test_knowledge_base_integrity(self):
        self.assertIn("tsunami", KNOWLEDGE_BASE)
        self.assertIn("cyclone", KNOWLEDGE_BASE)
        for key, item in KNOWLEDGE_BASE.items():
            self.assertIn("keywords", item)
            self.assertIn("answer", item)

if __name__ == "__main__":
    unittest.main()
