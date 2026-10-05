"""
ui/styles.py - Visual design tokens and custom CSS for Streamlit.
Conforms to PRD Section 11.
"""

CUSTOM_CSS = """
<style>
/* Load Google Fonts Sarabun */
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Sarabun', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #292524;
}

/* App Background */
.stApp {
    background-color: #FFF9F2;
}

/* Banner */
.demo-banner {
    background-color: #FEF3C7;
    border: 1px solid #FCD34D;
    color: #92400E;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 14px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Recipe Card Box */
.recipe-card {
    background-color: #FFFFFF;
    border: 1px solid #E6DDD2;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(41, 37, 36, 0.04);
}

.recipe-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
}

.recipe-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #292524;
    line-height: 1.35;
    margin: 0;
}

/* Status Badges */
.badge-complete {
    background-color: #DCFCE7;
    color: #166534;
    border: 1px solid #86EFAC;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
}

.badge-missing {
    background-color: #FEF3C7;
    color: #854D0E;
    border: 1px solid #FDE047;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
}

.badge-unknown {
    background-color: #F3F4F6;
    color: #4B5563;
    border: 1px solid #D1D5DB;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
}

/* Ingredient lists */
.ingredient-matched {
    color: #166534;
    font-size: 14px;
    line-height: 1.5;
}

.ingredient-missing {
    color: #B91C1C;
    font-weight: 500;
    font-size: 14px;
    line-height: 1.5;
}

/* Quantity warning disclaimer */
.qty-disclaimer {
    font-size: 12.5px;
    color: #655C54;
    background-color: #FAF5F0;
    border-left: 3px solid #D97706;
    padding: 6px 10px;
    border-radius: 0 6px 6px 0;
    margin: 8px 0;
}

/* Source Citation Box */
.source-box {
    background-color: #FAF5F0;
    border: 1px solid #E6DDD2;
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 13.5px;
    color: #44403C;
    margin-top: 8px;
}

.source-excerpt {
    background-color: #FFFFFF;
    border-left: 3px solid #A8421B;
    padding: 8px 12px;
    margin-top: 6px;
    font-size: 13px;
    color: #57534E;
    white-space: pre-wrap;
    word-break: break-word;
}

/* Primary Button Styling */
button[kind="primary"] {
    background-color: #A8421B !important;
    border-color: #A8421B !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}

button[kind="primary"]:hover {
    background-color: #8D3716 !important;
    border-color: #8D3716 !important;
}

/* Sample Prompt Chips */
.sample-prompt-btn {
    background-color: #FFFFFF;
    border: 1px solid #E6DDD2;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    color: #44403C;
    text-align: left;
    transition: all 0.15s ease;
    cursor: pointer;
    margin-bottom: 8px;
}

.sample-prompt-btn:hover {
    border-color: #A8421B;
    color: #A8421B;
    background-color: #FFF9F2;
}

/* Clarification Options */
.clarify-box {
    background-color: #FEF9C3;
    border: 1px solid #FDE047;
    border-radius: 10px;
    padding: 14px;
    margin-top: 8px;
}
</style>
"""


def get_custom_css() -> str:
    """Return CSS string for injecting via st.markdown(unsafe_allow_html=True)."""
    return CUSTOM_CSS
