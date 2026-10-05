"""
ui/components.py - Modular UI components for Streamlit frontend.
Conforms to PRD Section 5, 6, 7, 8, 10.
"""

from typing import Any, Callable, Dict, List, Optional
import streamlit as st


def render_header(on_reset: Callable[[], None]) -> None:
    """Render application header with title, description, and reset button."""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2px;">
                <span style="font-size: 2rem;">🍳</span>
                <h1 style="margin: 0; font-size: 1.85rem; font-weight: 700; color: #292524; letter-spacing: -0.02em;">
                    มีอะไร ทำอะไรดี
                </h1>
            </div>
            <p style="margin: 0 0 12px 0; font-size: 1rem; color: #655C54;">
                ค้นเมนูจากวัตถุดิบที่มี พร้อมสูตรและแหล่งอ้างอิง
            </p>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.write("")
        if st.button("🔄 เริ่มใหม่", key="btn_reset_header", help="ล้างประวัติการค้นหาและเริ่มต้นใหม่"):
            on_reset()
            st.rerun()


def render_banner() -> None:
    """Render small preview banner indicating mock mode."""
    st.markdown(
        """
        <div class="demo-banner">
            <span>ℹ️</span>
            <span><strong>โหมดตัวอย่าง</strong> — ยังไม่ได้เชื่อมระบบค้นเอกสารจริง (ข้อมูลทั้งหมดเป็น Fixture เพื่อทดสอบ UI)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sample_prompts(on_select: Callable[[str, List[str], bool], None]) -> None:
    """
    Render 3 deterministic sample prompt buttons as specified in PRD Section 5.3:
    1. “มีไข่ ข้าวสวย และต้นหอม”
    2. “มีเต้าหู้กับเห็ด ใช้ได้แค่ไมโครเวฟ”
    3. “ขอดูขั้นตอนของเมนูตัวอย่าง”
    """
    st.markdown(
        """
        <div style="margin-top: 14px; margin-bottom: 10px;">
            <p style="font-size: 1.05rem; font-weight: 600; color: #292524; margin-bottom: 8px;">
                👋 วันนี้มีอะไรอยู่ในครัวบ้าง?
            </p>
            <p style="font-size: 0.88rem; color: #655C54; margin-bottom: 10px;">
                ลองกดเลือกตัวอย่างคำถามเพื่อดูการทำงานของระบบ:
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(
            "🥚 มีไข่ ข้าวสวย และต้นหอม",
            key="sample_prompt_1",
            use_container_width=True,
            help="ทดสอบกรณีมีวัตถุดิบหลักแต่ยังขาดเครื่องปรุง",
        ):
            on_select("มีไข่ ข้าวสวย และต้นหอม", [], False)
            st.rerun()

    with c2:
        if st.button(
            "🍲 มีเต้าหู้กับเห็ด ใช้ได้แค่ไมโครเวฟ",
            key="sample_prompt_2",
            use_container_width=True,
            help="ทดสอบกรณีระบุอุปกรณ์ไมโครเวฟและวัตถุดิบ",
        ):
            on_select("เต้าหู้ เห็ด ซีอิ๊วขาว", ["ไมโครเวฟ"], False)
            st.rerun()

    with c3:
        if st.button(
            "📖 ขอดูขั้นตอนของเมนูตัวอย่าง",
            key="sample_prompt_3",
            use_container_width=True,
            help="ทดสอบการแสดงผลสูตรตัวอย่างและข้อความหลักฐาน",
        ):
            on_select("ขอดูขั้นตอนของเมนูตัวอย่าง", [], False)
            st.rerun()


def render_recipe_card(
    recipe: Dict[str, Any],
    sources: List[Dict[str, Any]],
    card_index: int,
    message_id: str,
    on_select_recipe: Optional[Callable[[str, str], None]] = None,
) -> None:
    """
    Render a single recipe card conforming to PRD Section 6 & 7.
    """
    name = recipe.get("name", "ไม่มีชื่อเมนู")
    match_status = recipe.get("ingredient_match", "unknown")
    matched_ingredients = recipe.get("matched_ingredients", [])
    missing_ingredients = recipe.get("missing_ingredients", [])
    quantity_check = recipe.get("quantity_check", "unknown")
    equipment_list = recipe.get("equipment", [])
    equipment_match = recipe.get("equipment_match", "unknown")
    servings = recipe.get("servings")
    ingredients = recipe.get("ingredients", [])
    steps = recipe.get("steps", [])
    recipe_id = recipe.get("recipe_id", f"rec_{card_index}")

    # Determine badge styling & text
    if match_status == "complete":
        badge_html = '<span class="badge-complete">✓ วัตถุดิบครบตามสูตร</span>'
    elif match_status == "missing":
        missing_count = len(missing_ingredients)
        badge_html = f'<span class="badge-missing">⚠️ ยังขาด {missing_count} รายการ</span>'
    else:
        badge_html = '<span class="badge-unknown">ℹ️ ข้อมูลยังไม่พอ</span>'

    # Format equipment text
    eq_str = ", ".join(equipment_list) if equipment_list else "ไม่ระบุ"
    if equipment_match == "compatible":
        eq_status_text = f"✅ อุปกรณ์ตรงกับสูตร ({eq_str})"
    elif equipment_match == "incompatible":
        eq_status_text = f"❌ อุปกรณ์ไม่ตรงกับสูตร (สูตรกำหนดใช้: {eq_str})"
    elif equipment_match == "unrestricted":
        eq_status_text = f"🍳 อุปกรณ์ที่สูตรใช้: {eq_str}"
    else:
        eq_status_text = "❓ ไม่ทราบข้อมูลอุปกรณ์"

    # Servings text
    servings_text = servings if servings else "สูตรไม่ได้ระบุจำนวนเสิร์ฟ"

    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)

    # Header row with title and badge
    st.markdown(
        f"""
        <div class="recipe-header">
            <h3 class="recipe-title">{name}</h3>
            <div>{badge_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Servings & Equipment info
    st.markdown(
        f"""
        <div style="font-size: 13.5px; color: #57534E; margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 14px;">
            <span>🍽️ <strong>จำนวนเสิร์ฟ:</strong> {servings_text}</span>
            <span>{eq_status_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Matched & Missing ingredients breakdown
    col_matched, col_missing = st.columns(2)
    with col_matched:
        matched_str = ", ".join(matched_ingredients) if matched_ingredients else "ไม่มีระบุ"
        st.markdown(
            f"""
            <div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 10px; height: 100%;">
                <p style="margin: 0 0 4px 0; font-size: 13px; font-weight: 600; color: #166534;">
                    ✓ วัตถุดิบที่คุณมี:
                </p>
                <p class="ingredient-matched" style="margin: 0;">{matched_str}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_missing:
        if missing_ingredients:
            missing_str = ", ".join(missing_ingredients)
            st.markdown(
                f"""
                <div style="background-color: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 10px; height: 100%;">
                    <p style="margin: 0 0 4px 0; font-size: 13px; font-weight: 600; color: #991B1B;">
                        ⚠️ วัตถุดิบหรือเครื่องปรุงที่ยังขาด:
                    </p>
                    <p class="ingredient-missing" style="margin: 0;">{missing_str}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px; height: 100%;">
                    <p style="margin: 0; font-size: 13px; color: #475569;">
                        🎉 ไม่มีวัตถุดิบที่ขาดตามสูตร
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Quantity disclaimer if unknown
    if quantity_check == "unknown":
        st.markdown(
            """
            <div class="qty-disclaimer">
                ⚠️ <em>หมายเหตุ: ตรวจสอบเฉพาะรายชื่อวัตถุดิบ ยังไม่ได้ตรวจว่าปริมาณที่คุณมีเพียงพอตามสูตรหรือไม่</em>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Expandable recipe details: Ingredients & Steps
    with st.expander(f"📖 ดูวิธีทำและส่วนผสมทั้งหมด ({name})"):
        st.markdown(
            """
            <div style="font-size: 14px; font-weight: 600; color: #292524; margin-bottom: 6px;">
                ส่วนผสมตามสูตรต้นฉบับ:
            </div>
            """,
            unsafe_allow_html=True,
        )
        if ingredients:
            for ing in ingredients:
                ing_name = ing.get("name", "")
                ing_amount = ing.get("amount", "")
                st.markdown(f"- **{ing_name}**: {ing_amount}")
        else:
            st.caption("ไม่มีข้อมูลส่วนผสมในคลังตัวอย่าง")

        st.markdown(
            """
            <div style="font-size: 14px; font-weight: 600; color: #292524; margin-top: 12px; margin-bottom: 6px;">
                ขั้นตอนการทำ:
            </div>
            """,
            unsafe_allow_html=True,
        )
        if steps:
            for s_idx, step in enumerate(steps, 1):
                st.markdown(f"**{s_idx}.** {step}")
        else:
            st.caption("ไม่มีขั้นตอนในคลังตัวอย่าง")

    # Expandable evidence / citations as required by PRD Section 7
    recipe_sources = [s for s in sources if s.get("recipe_id") == recipe_id]
    if not recipe_sources and sources:
        # Fallback to general sources if specific recipe_id match not found
        recipe_sources = sources

    with st.expander("🔍 ดูหลักฐานจากสูตร (Evidence & Citations)"):
        if recipe_sources:
            for src in recipe_sources:
                doc_name = src.get("document_name", "สูตรตัวอย่างสำหรับทดสอบหน้าจอ")
                section = src.get("section", name)
                page = src.get("page")
                page_str = f" | หน้า: {page}" if page is not None else ""
                excerpt = src.get("excerpt", "ไม่มีข้อความหลักฐาน")
                source_url = src.get("source_url")

                st.markdown(
                    f"""
                    <div class="source-box">
                        <div style="font-weight: 600; color: #292524;">
                            📄 {doc_name} &bull; หัวข้อ: {section}{page_str}
                        </div>
                        <div class="source-excerpt">{excerpt}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if source_url:
                    st.markdown(f"[🔗 แหล่งที่มาต้นฉบับ]({source_url})")
                else:
                    st.caption("🔒 ข้อมูลออฟไลน์ในคลังตัวอย่าง (ไม่มี URL ภายนอก)")
        else:
            st.info("ไม่มีหลักฐานประกอบผลลัพธ์นี้")

    # Action row: Follow-up button
    col_act1, _ = st.columns([2, 3])
    with col_act1:
        btn_key = f"btn_followup_{message_id}_{recipe_id}_{card_index}"
        if st.button(
            f"💬 ถามต่อเกี่ยวกับเมนูนี้",
            key=btn_key,
            help=f"เลือกเมนู '{name}' เพื่อเจาะจงถามขั้นตอนหรือคำถามต่อเนื่อง",
        ):
            if on_select_recipe:
                on_select_recipe(recipe_id, name)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_clarification_options(
    options: List[Dict[str, str]],
    message_id: str,
    on_choose: Callable[[str, str], None],
) -> None:
    """Render options when assistant needs clarification on which recipe the user means."""
    st.markdown(
        """
        <div class="clarify-box">
            <p style="font-weight: 600; color: #854D0E; margin-bottom: 8px;">
                ❓ กรุณาเลือกเมนูที่คุณต้องการถามต่อ:
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(len(options))
    for idx, opt in enumerate(options):
        r_id = opt.get("recipe_id", "")
        r_name = opt.get("name", f"เมนูที่ {idx+1}")
        with cols[idx]:
            if st.button(
                f"👉 {r_name}",
                key=f"clarify_opt_{message_id}_{r_id}_{idx}",
                use_container_width=True,
            ):
                on_choose(r_id, r_name)
                st.rerun()


def render_status_notice(
    status: str,
    answer: str,
    error_code: Optional[str] = None,
    on_retry: Optional[Callable[[], None]] = None,
    message_id: str = "status",
) -> None:
    """Render formatted alerts for no_match, insufficient_context, error, etc."""
    if status == "no_match":
        st.warning(f"🔍 {answer}")
    elif status == "insufficient_context":
        st.info(f"ℹ️ {answer}")
    elif status == "error":
        st.error(f"❌ {answer}" + (f" (รหัส: `{error_code}`)" if error_code else ""))
        if on_retry:
            if st.button("🔄 ลองใหม่อีกครั้ง (Retry)", key=f"retry_btn_{message_id}"):
                on_retry()
                st.rerun()
