"""
services/mock_adapter.py - Mock RAG Adapter with fixture scenario matching.
Conforms to PRD Section 9, 10, 13.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from services.adapter import BaseRAGAdapter


class MockAdapter(BaseRAGAdapter):
    """
    Mock adapter that serves predictable fixture scenarios.
    Does NOT pretend to be an LLM or semantic index.
    Explicitly tags responses with is_mock=True.
    """

    def __init__(self, fixtures_path: Optional[str] = None):
        if fixtures_path is None:
            base_dir = Path(__file__).parent.parent
            fixtures_path = str(base_dir / "fixtures" / "scenarios.json")

        self.fixtures_path = fixtures_path
        self.scenarios = self._load_fixtures()

    def _load_fixtures(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.fixtures_path):
            return []
        try:
            with open(self.fixtures_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("scenarios", [])
        except Exception:
            return []

    def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        for sc in self.scenarios:
            if sc.get("id") == scenario_id:
                return sc.get("response")
        return None

    def answer_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match request against deterministic fixture scenarios.
        """
        query = (request.get("query") or "").strip().lower()
        ingredients = [i.lower() for i in request.get("available_ingredients", [])]
        ingredients_text = (request.get("available_ingredients_text") or "").strip().lower()
        equipment = [e.lower() for e in request.get("equipment", [])]
        require_all = bool(request.get("require_all_ingredients", False))
        selected_recipe_id = request.get("selected_recipe_id")

        full_text = f"{query} {ingredients_text} {' '.join(ingredients)}".lower()

        # Check explicit error simulation (Scenario 10)
        if any(w in full_text for w in ["error", "จำลอง error", "ข้อผิดพลาด", "พัง"]):
            return self._build_response("scenario_10_error_retry")

        # Check filter complete no match (Scenario 5)
        # When require_all_ingredients is True, but user doesn't have seasonings
        if require_all and not any(w in full_text for w in ["ซีอิ๊วขาว", "น้ำมันพืช", "น้ำมันงา", "น้ำปลา"]):
            return self._build_response("scenario_5_filter_complete_no_match")

        # Check ambiguous follow-up (Scenario 9)
        if any(w in query for w in ["กี่นาที", "ทำยากไหม", "ใช้เวลาเท่าไหร่", "ทำยังไงนะ"]):
            # If no single recipe is selected, ask for clarification
            if not selected_recipe_id:
                return self._build_response("scenario_9_ambiguous_follow_up")

        # Check nutrition / insufficient context (Scenario 7)
        if any(w in query for w in ["แคลอรี่", "กี่แคล", "โปรตีน", "โซเดียม", "สารอาหาร", "โภชนาการ"]):
            return self._build_response("scenario_7_insufficient_context")

        # Check follow-up for 2nd recipe (Scenario 8)
        if any(w in query for w in ["เมนูที่สอง", "เมนูที่ 2", "เมนู 2", "จานที่สอง"]) or selected_recipe_id == "demo-002":
            return self._build_response("scenario_8_follow_up_second_recipe")

        # Check follow-up for 1st recipe specifically
        if selected_recipe_id == "demo-001" or any(w in query for w in ["เมนูแรก", "เมนูที่ 1", "ข้าวผัดไข่"]):
            return self._build_response("scenario_1_complete_unknown_qty")

        # Check long text / null fields demo (Scenario 11)
        if any(w in full_text for w in ["ขอดูขั้นตอนของเมนูตัวอย่าง", "เมนูตัวอย่าง", "สูตรยาว", "ต้มยำ", "ปลากระป๋อง", "null"]):
            return self._build_response("scenario_11_long_text_null_fields")

        # Check equipment incompatible (Scenario 4)
        if "หม้อหุงข้าว" in equipment and not any(eq in ["กระทะ", "ไมโครเวฟ"] for eq in equipment):
            if any(w in full_text for w in ["ข้าวผัด", "ไข่"]):
                return self._build_response("scenario_4_equipment_incompatible")

        # Check equipment compatible microwave (Scenario 3)
        if "ไมโครเวฟ" in equipment or any(w in full_text for w in ["เต้าหู้", "เห็ด", "ไมโครเวฟ"]):
            return self._build_response("scenario_3_equipment_compatible")

        # Check no match scenario (Scenario 6)
        if any(w in full_text for w in ["แซลมอน", "วาซาบิ", "ชีสเค้ก", "สปาเก็ตตี้", "สเต็ก", "ทรัฟเฟิล"]):
            return self._build_response("scenario_6_no_match_general")

        # Check complete ingredients with seasonings (Scenario 1)
        has_egg = "ไข่" in full_text
        has_rice = "ข้าว" in full_text
        has_scallion = "ต้นหอม" in full_text
        has_oil = any(w in full_text for w in ["น้ำมัน", "น้ำมันพืช"])
        has_sauce = any(w in full_text for w in ["ซีอิ๊ว", "ซีอิ๊วขาว", "น้ำปลา"])

        if has_egg and has_rice and has_scallion and has_oil and has_sauce:
            return self._build_response("scenario_1_complete_unknown_qty")

        # Has main ingredients but missing seasonings (Scenario 2)
        if has_egg or has_rice:
            return self._build_response("scenario_2_missing_condiments")

        # Fallback for out-of-fixture query as explicitly stated in PRD Section 9:
        # "คำถามนอก fixture ให้แสดงว่า 'โหมดตัวอย่างยังไม่รองรับคำถามนี้'"
        return {
            "status": "no_match",
            "answer": "โหมดตัวอย่างยังไม่รองรับคำถามนี้ (ในโหมดตัวอย่างมีสูตรจำลองสำหรับ: ไข่, ข้าวสวย, ต้นหอม, เต้าหู้, เห็ด, ปลากระป๋อง)",
            "recipes": [],
            "sources": [],
            "is_mock": True,
            "error_code": None,
            "clarification_options": []
        }

    def _build_response(self, scenario_id: str) -> Dict[str, Any]:
        resp = self.get_scenario_by_id(scenario_id)
        if resp:
            # Return a copy
            return json.loads(json.dumps(resp))
        return {
            "status": "error",
            "answer": "ไม่พบข้อมูล scenario ตัวอย่างในระบบ",
            "recipes": [],
            "sources": [],
            "is_mock": True,
            "error_code": "SCENARIO_NOT_FOUND",
            "clarification_options": []
        }
