"""
services/adapter.py - Interface and adapter factory for RAG / Mock culinary assistant.
Conforms to PRD Section 9 & 12.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import os


class BaseRAGAdapter(ABC):
    """
    Abstract interface for culinary recipe RAG.
    Any future RAG implementation (e.g., SentenceTransformer + FAISS + Groq)
    MUST implement this interface without modifying the Streamlit UI components.
    """

    @abstractmethod
    def answer_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the user query and return a structured recipe response.

        Request schema:
        {
            "request_id": str,
            "query": str,
            "available_ingredients": List[str],
            "available_ingredients_text": str,
            "equipment": List[str],
            "require_all_ingredients": bool,
            "selected_recipe_id": Optional[str],
            "history": List[Dict[str, str]]
        }

        Response schema:
        {
            "status": "ok" | "no_match" | "insufficient_context" | "needs_clarification" | "error",
            "answer": str,
            "recipes": List[RecipeDict],
            "sources": List[SourceDict],
            "is_mock": bool,
            "error_code": Optional[str],
            "clarification_options": Optional[List[Dict[str, str]]]
        }
        """
        pass


def get_adapter() -> BaseRAGAdapter:
    """
    Factory function to obtain the active adapter.
    Defaults to MockAdapter.
    When LIVE_RAG_ENABLED is set to 'true', it attempts to load LiveRAGAdapter.
    If live adapter is not configured, it returns an unconfigured status as per PRD Section 8.
    """
    adapter_mode = os.getenv("RAG_ADAPTER_MODE", "mock").lower()

    if adapter_mode == "live":
        try:
            from services.live_adapter import LiveRAGAdapter
            return LiveRAGAdapter()
        except ImportError:
            class UnconfiguredLiveAdapter(BaseRAGAdapter):
                def answer_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
                    return {
                        "status": "error",
                        "answer": "ระบบยังไม่พร้อมให้บริการ (Live RAG Adapter ยังไม่ได้ติดตั้ง หรือขาดการตั้งค่า Environment)",
                        "recipes": [],
                        "sources": [],
                        "is_mock": False,
                        "error_code": "LIVE_ADAPTER_NOT_CONFIGURED",
                        "clarification_options": []
                    }
            return UnconfiguredLiveAdapter()

    # Default: mock adapter
    from services.mock_adapter import MockAdapter
    return MockAdapter()


def answer_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience entrypoint function required by PRD Section 9.
    """
    adapter = get_adapter()
    return adapter.answer_request(request)
