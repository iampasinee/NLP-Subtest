"""
app.py - Main entrypoint for Streamlit application "มีอะไร ทำอะไรดี"
Conforms to PRD Section 1, 5, 8, 9, 10.
Runnable with: streamlit run app.py
"""

import uuid
from typing import Any, Dict, List, Optional
import streamlit as st

from services.adapter import answer_request
from ui.components import (
    render_banner,
    render_clarification_options,
    render_header,
    render_recipe_card,
    render_sample_prompts,
    render_status_notice,
)
from ui.styles import get_custom_css

# Page Configuration conforming to Section 11
st.set_page_config(
    page_title="มีอะไร ทำอะไรดี — ผู้ช่วยเลือกเมนูจากวัตถุดิบที่มี",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply CSS styling
st.markdown(get_custom_css(), unsafe_allow_html=True)


def init_session_state() -> None:
    """Initialize all session state keys as per PRD Section 10."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "latest_recipe_ids" not in st.session_state:
        st.session_state.latest_recipe_ids = []
    if "selected_recipe_id" not in st.session_state:
        st.session_state.selected_recipe_id = None
    if "selected_recipe_name" not in st.session_state:
        st.session_state.selected_recipe_name = None
    if "last_request" not in st.session_state:
        st.session_state.last_request = None
    if "form_ingredients" not in st.session_state:
        st.session_state.form_ingredients = ""
    if "form_equipment" not in st.session_state:
        st.session_state.form_equipment = []
    if "form_require_all" not in st.session_state:
        st.session_state.form_require_all = False
    if "last_validation_error" not in st.session_state:
        st.session_state.last_validation_error = None


def reset_app_state() -> None:
    """Reset all session state back to initial screen as per Section 10."""
    st.session_state.messages = []
    st.session_state.latest_recipe_ids = []
    st.session_state.selected_recipe_id = None
    st.session_state.selected_recipe_name = None
    st.session_state.last_request = None
    st.session_state.form_ingredients = ""
    st.session_state.form_equipment = []
    st.session_state.form_require_all = False
    st.session_state.last_validation_error = None


def process_query(
    query_text: str,
    ingredients_text: str = "",
    equipment: Optional[List[str]] = None,
    require_all: bool = False,
    selected_recipe_id: Optional[str] = None,
) -> None:
    """
    Construct standardized request payload and invoke answer_request() once,
    storing the result into session messages to prevent re-invocation on reruns.
    """
    if equipment is None:
        equipment = []

    # Clean input tokens
    clean_query = query_text.strip()
    clean_ing_text = ingredients_text.strip()

    if not clean_query and not clean_ing_text:
        st.session_state.last_validation_error = "กรุณาระบุวัตถุดิบหรือคำถามก่อนค้น"
        return

    st.session_state.last_validation_error = None

    # Parse simple comma/space delimited tokens
    raw_tokens = [t.strip() for t in clean_ing_text.replace(",", " ").split() if t.strip()]
    if not raw_tokens and clean_query:
        raw_tokens = [t.strip() for t in clean_query.replace(",", " ").split() if t.strip()]

    request_id = f"req-{uuid.uuid4().hex[:8]}"

    # Prepare chat history for adapter
    history_payload = []
    for msg in st.session_state.messages[-4:]:
        history_payload.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", ""),
        })

    target_recipe_id = selected_recipe_id or st.session_state.selected_recipe_id

    req_payload = {
        "request_id": request_id,
        "query": clean_query or clean_ing_text,
        "available_ingredients": raw_tokens,
        "available_ingredients_text": clean_ing_text or clean_query,
        "equipment": equipment,
        "require_all_ingredients": require_all,
        "selected_recipe_id": target_recipe_id,
        "history": history_payload,
    }

    # Save last request for retry functionality
    st.session_state.last_request = req_payload

    # Record user message in history
    display_user_text = clean_query or f"ค้นวัตถุดิบ: {clean_ing_text}"
    if equipment:
        display_user_text += f" (อุปกรณ์: {', '.join(equipment)})"
    if require_all:
        display_user_text += " [ตัวกรอง: วัตถุดิบครบตามสูตร]"

    msg_user_id = f"msg_user_{uuid.uuid4().hex[:6]}"
    st.session_state.messages.append({
        "id": msg_user_id,
        "role": "user",
        "content": display_user_text,
    })

    # Call central adapter function
    response = answer_request(req_payload)

    # Store latest recipe IDs
    recipes = response.get("recipes", [])
    st.session_state.latest_recipe_ids = [r.get("recipe_id") for r in recipes if r.get("recipe_id")]

    # Append assistant response
    msg_asst_id = f"msg_asst_{uuid.uuid4().hex[:6]}"
    st.session_state.messages.append({
        "id": msg_asst_id,
        "role": "assistant",
        "response": response,
        "content": response.get("answer", ""),
    })


def main() -> None:
    init_session_state()

    # 5.1 Header & Reset
    render_header(on_reset=reset_app_state)

    # Preview Banner
    render_banner()

    # 5.2 Section: ข้อมูลที่ฉันมี (Input Section)
    with st.expander("📝 ระบุวัตถุดิบและอุปกรณ์ของคุณ (คลิกเพื่อแก้ไข)", expanded=(len(st.session_state.messages) == 0)):
        with st.form(key="search_form", clear_on_submit=False):
            st.markdown(
                """
                <label style="font-weight: 600; font-size: 0.95rem; color: #292524;">
                    มีวัตถุดิบอะไรบ้าง?
                </label>
                """,
                unsafe_allow_html=True,
            )
            ing_val = st.text_area(
                label="มีวัตถุดิบอะไรบ้าง?",
                value=st.session_state.form_ingredients,
                placeholder="เช่น ไข่ ข้าวสวย ต้นหอม น้ำมัน น้ำปลา",
                help="ระบุวัตถุดิบและเครื่องปรุงที่มี เพื่อให้ระบบตรวจสอบความครบถ้วนได้แม่นยำ",
                label_visibility="collapsed",
                height=90,
            )
            st.caption("💡 <em>ระบุเครื่องปรุงที่มีด้วย เพื่อให้รายการวัตถุดิบที่ขาดถูกต้อง</em>", unsafe_allow_html=True)

            eq_options = ["กระทะ", "หม้อ", "ไมโครเวฟ", "หม้อหุงข้าว", "หม้อทอดไร้น้ำมัน"]
            eq_val = st.multiselect(
                "อุปกรณ์ทำอาหารที่มี:",
                options=eq_options,
                default=st.session_state.form_equipment,
                help="หากไม่เลือก หมายถึงไม่จำกัดอุปกรณ์ (ทำได้ทุกประเภท)",
            )

            req_all_val = st.checkbox(
                "แสดงเฉพาะเมนูที่วัตถุดิบครบตามสูตร",
                value=st.session_state.form_require_all,
                help="กรองเฉพาะสูตรที่คุณมีวัตถุดิบครบทุกรายการ",
            )

            submit_btn = st.form_submit_button("🔍 ค้นเมนู", type="primary", use_container_width=True)

            if submit_btn:
                st.session_state.form_ingredients = ing_val
                st.session_state.form_equipment = eq_val
                st.session_state.form_require_all = req_all_val
                process_query(
                    query_text="",
                    ingredients_text=ing_val,
                    equipment=eq_val,
                    require_all=req_all_val,
                )
                st.rerun()

    # Validation message if user pressed search without input
    if st.session_state.last_validation_error:
        st.warning(f"⚠️ {st.session_state.last_validation_error}")

    # Active Recipe Context Badge (if user clicked "ถามต่อเกี่ยวกับเมนูนี้")
    if st.session_state.selected_recipe_name:
        col_ctx1, col_ctx2 = st.columns([5, 1])
        with col_ctx1:
            st.info(f"📌 กำลังเจาะจงถามเกี่ยวกับเมนู: **{st.session_state.selected_recipe_name}**")
        with col_ctx2:
            if st.button("✖️ ปลดเลือก", key="btn_clear_selected_recipe"):
                st.session_state.selected_recipe_id = None
                st.session_state.selected_recipe_name = None
                st.rerun()

    # 5.3 Initial state prompts (if no search history yet)
    if len(st.session_state.messages) == 0:
        def on_sample_select(text: str, eq: List[str], req_all: bool) -> None:
            st.session_state.form_ingredients = text
            st.session_state.form_equipment = eq
            st.session_state.form_require_all = req_all
            process_query(query_text=text, ingredients_text=text, equipment=eq, require_all=req_all)

        render_sample_prompts(on_select=on_sample_select)

    # 5.4 Search Results & Chat History
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        with st.chat_message(role, avatar="🧑‍🍳" if role == "user" else "🍳"):
            if role == "user":
                st.write(msg.get("content", ""))
            else:
                resp = msg.get("response", {})
                status = resp.get("status", "ok")
                answer = resp.get("answer", "")
                recipes = resp.get("recipes", [])
                sources = resp.get("sources", [])
                error_code = resp.get("error_code")
                clarify_opts = resp.get("clarification_options", [])
                msg_id = msg.get("id", "msg")

                # Show short summary answer text
                if answer:
                    st.write(answer)

                # Show status notices (error, no_match, insufficient_context)
                if status in ["no_match", "insufficient_context", "error"]:
                    def make_retry_cb():
                        def retry_action():
                            if st.session_state.last_request:
                                req = st.session_state.last_request
                                process_query(
                                    query_text=req.get("query", ""),
                                    ingredients_text=req.get("available_ingredients_text", ""),
                                    equipment=req.get("equipment", []),
                                    require_all=req.get("require_all_ingredients", False),
                                    selected_recipe_id=req.get("selected_recipe_id"),
                                )
                        return retry_action

                    render_status_notice(
                        status=status,
                        answer="",
                        error_code=error_code,
                        on_retry=make_retry_cb(),
                        message_id=msg_id,
                    )

                # Show clarification options if ambiguous
                if status == "needs_clarification" and clarify_opts:
                    def on_clarify_choose(r_id: str, r_name: str) -> None:
                        st.session_state.selected_recipe_id = r_id
                        st.session_state.selected_recipe_name = r_name
                        process_query(
                            query_text=f"ขอดูวิธีทำของ {r_name}",
                            selected_recipe_id=r_id,
                        )

                    render_clarification_options(
                        options=clarify_opts,
                        message_id=msg_id,
                        on_choose=on_clarify_choose,
                    )

                # Show Recipe Cards (up to 3 as specified in PRD Section 5.4)
                if recipes:
                    for idx, rec in enumerate(recipes[:3]):
                        def make_select_cb(r_id: str, r_name: str):
                            def select_action(rid: str, rname: str):
                                st.session_state.selected_recipe_id = rid
                                st.session_state.selected_recipe_name = rname
                            return select_action

                        render_recipe_card(
                            recipe=rec,
                            sources=sources,
                            card_index=idx,
                            message_id=msg_id,
                            on_select_recipe=lambda rid, rname: (
                                setattr(st.session_state, "selected_recipe_id", rid),
                                setattr(st.session_state, "selected_recipe_name", rname),
                            ),
                        )

    # 5.4 Bottom Chat Input
    chat_prompt = st.chat_input("ถามต่อเกี่ยวกับเมนู หรือบอกวัตถุดิบเพิ่มเติม...")
    if chat_prompt:
        process_query(
            query_text=chat_prompt,
            ingredients_text=st.session_state.form_ingredients,
            equipment=st.session_state.form_equipment,
            require_all=st.session_state.form_require_all,
            selected_recipe_id=st.session_state.selected_recipe_id,
        )
        st.rerun()


if __name__ == "__main__":
    main()
