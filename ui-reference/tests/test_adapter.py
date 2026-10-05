"""
tests/test_adapter.py - Unit test suite for RAG adapter interface and mock scenarios.
Conforms to PRD Section 13 & 14 (FE-01, FE-02, FE-04, FE-05, FE-06, FE-07, FE-08, FE-09).
Run with: python3 -m unittest discover -s tests
"""

import unittest
from services.adapter import answer_request
from services.mock_adapter import MockAdapter


class TestMockAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = MockAdapter()

    def test_schema_validity(self):
        """Ensure adapter always returns keys matching Section 9 schema."""
        req = {
            "request_id": "test-req-001",
            "query": "ไข่ ข้าวสวย ต้นหอม น้ำมันพืช ซีอิ๊วขาว",
            "available_ingredients": ["ไข่", "ข้าวสวย", "ต้นหอม", "น้ำมันพืช", "ซีอิ๊วขาว"],
            "available_ingredients_text": "ไข่ ข้าวสวย ต้นหอม น้ำมันพืช ซีอิ๊วขาว",
            "equipment": ["กระทะ"],
            "require_all_ingredients": False,
            "selected_recipe_id": None,
            "history": [],
        }
        res = self.adapter.answer_request(req)
        self.assertIn("status", res)
        self.assertIn("answer", res)
        self.assertIn("recipes", res)
        self.assertIn("sources", res)
        self.assertTrue(res.get("is_mock"))
        self.assertEqual(res.get("status"), "ok")

        # Check recipe fields
        recipes = res.get("recipes", [])
        self.assertGreater(len(recipes), 0)
        r = recipes[0]
        self.assertIn("recipe_id", r)
        self.assertIn("name", r)
        self.assertIn("ingredient_match", r)
        self.assertIn("matched_ingredients", r)
        self.assertIn("missing_ingredients", r)
        self.assertIn("quantity_check", r)
        self.assertIn("equipment_match", r)
        self.assertIn("steps", r)

    def test_scenario_1_complete_ingredients(self):
        """Scenario 1: Complete ingredients, quantity unknown."""
        req = {
            "query": "ไข่ ข้าวสวย ต้นหอม น้ำมันพืช ซีอิ๊วขาว",
            "available_ingredients": ["ไข่", "ข้าวสวย", "ต้นหอม", "น้ำมันพืช", "ซีอิ๊วขาว"],
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["recipes"][0]["ingredient_match"], "complete")
        self.assertEqual(len(res["recipes"][0]["missing_ingredients"]), 0)
        self.assertEqual(res["recipes"][0]["quantity_check"], "unknown")

    def test_scenario_2_missing_condiments(self):
        """Scenario 2: Main ingredients present but condiments missing (oil/soy sauce)."""
        req = {
            "query": "มีไข่ ข้าวสวย และต้นหอม",
            "available_ingredients": ["ไข่", "ข้าวสวย", "ต้นหอม"],
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "ok")
        r = res["recipes"][0]
        self.assertEqual(r["ingredient_match"], "missing")
        self.assertIn("น้ำมันพืช", r["missing_ingredients"])
        self.assertIn("ซีอิ๊วขาว", r["missing_ingredients"])

    def test_scenario_3_equipment_compatible(self):
        """Scenario 3: Equipment microwave compatible with tofu dish."""
        req = {
            "query": "เต้าหู้ เห็ด ซีอิ๊วขาว",
            "equipment": ["ไมโครเวฟ"],
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "ok")
        r = res["recipes"][0]
        self.assertEqual(r["equipment_match"], "compatible")
        self.assertIn("ไมโครเวฟ", r["equipment"])

    def test_scenario_4_equipment_incompatible(self):
        """Scenario 4: User only has rice cooker, but recipe needs frying pan."""
        req = {
            "query": "ข้าวผัด ไข่",
            "equipment": ["หม้อหุงข้าว"],
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "ok")
        r = res["recipes"][0]
        self.assertEqual(r["equipment_match"], "incompatible")

    def test_scenario_5_filter_complete_no_match(self):
        """Scenario 5: require_all_ingredients is True, missing condiments -> no_match."""
        req = {
            "query": "ไข่ ข้าวสวย",
            "require_all_ingredients": True,
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "no_match")
        self.assertEqual(len(res["recipes"]), 0)

    def test_scenario_6_no_match_general(self):
        """Scenario 6: Search for ingredient not in mock repository."""
        req = {
            "query": "แซลมอน วาซาบิ",
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "no_match")
        self.assertEqual(len(res["recipes"]), 0)

    def test_scenario_7_insufficient_context(self):
        """Scenario 7: Ask about calories or nutrition."""
        req = {
            "query": "เมนูนี้มีกี่แคลอรี่ มีโปรตีนเท่าไหร่",
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "insufficient_context")

    def test_scenario_8_follow_up_second_recipe(self):
        """Scenario 8: Follow up on 2nd recipe."""
        req = {
            "query": "ขอดูวิธีทำเมนูที่สอง",
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["recipes"][0]["recipe_id"], "demo-002")

    def test_scenario_9_ambiguous_follow_up(self):
        """Scenario 9: Ambiguous follow-up without active recipe id."""
        req = {
            "query": "ใช้เวลากี่นาที ทำยากไหม",
            "selected_recipe_id": None,
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "needs_clarification")
        self.assertGreater(len(res.get("clarification_options", [])), 0)

    def test_scenario_10_error_retry(self):
        """Scenario 10: Error simulation."""
        req = {
            "query": "จำลอง error",
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "error")
        self.assertIsNotNone(res.get("error_code"))

    def test_scenario_11_long_text_and_nulls(self):
        """Scenario 11: Long name, null servings, null source url."""
        req = {
            "query": "ขอดูขั้นตอนของเมนูตัวอย่าง",
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "ok")
        r = res["recipes"][0]
        self.assertIsNone(r.get("servings"))
        self.assertGreater(len(r.get("name", "")), 40)
        self.assertIsNone(res["sources"][0].get("source_url"))

    def test_out_of_fixture_fallback(self):
        """Queries completely outside fixtures must return clear fallback as per Section 9."""
        req = {
            "query": "ขอสูตรพิซซ่าเตาอบแบบอิตาลีแท้",
        }
        res = self.adapter.answer_request(req)
        self.assertEqual(res["status"], "no_match")
        self.assertIn("โหมดตัวอย่างยังไม่รองรับคำถามนี้", res["answer"])


if __name__ == "__main__":
    unittest.main()
