"""CSS adapted from the reference's tokens, applied to real native containers."""
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700&display=swap');
[data-testid="stAppViewContainer"] { background: #FFF9F2; }
h1,h2,h3,p,button,input,textarea,[data-testid="stMarkdownContainer"],
[data-testid="stCaptionContainer"], [data-testid="stExpander"] summary {
  font-family: 'Sarabun', Tahoma, 'Noto Sans Thai', sans-serif;
}
.stMainBlockContainer { max-width: 980px; padding-top: 4rem; padding-bottom: 8rem; }
h1 { font-size: clamp(1.7rem, 4.8vw, 2.25rem) !important; letter-spacing: -.02em; }
.hero-kicker { color: #A8421B; font-size: .82rem; font-weight: 600; margin: 0; }
.hero-subtitle { color: #655C54; font-size: 1rem; margin-top: -.5rem; }
div[class*="st-key-recipe_card_"], div[class*="st-key-sample_card_"] {
  background: #FFF; border: 1px solid #E6DDD2; border-radius: 14px;
  padding: 18px; box-shadow: 0 2px 6px rgba(41,37,36,.035);
}
div[class*="st-key-sample_card_"] { height: 100%; }
.sample-icon { width: 42px; height: 42px; display: grid; place-items: center;
  background: #FFF2E6; border-radius: 12px; font-size: 1.5rem; margin-bottom: 12px; }
.card-title { font-weight: 700; font-size: 1.08rem; color: #292524; margin: 0 0 8px; }
.ingredient-panel { border-radius: 10px; padding: 12px; line-height: 1.65; height: 100%; }
.matched { background: #F0FDF4; border: 1px solid #BBF7D0; color: #166534; }
.missing { background: #FEF2F2; border: 1px solid #FECACA; color: #991B1B; }
.ingredient-panel p { margin: 0; font-size: .9rem; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 999px;
  background: #FFF3CC; color: #854D0E; font-size: .82rem; margin-bottom: 10px; }
.badge.complete { background: #DCFCE7; color: #166534; }
.quantity-note { background: #FAF5F0; border-left: 3px solid #D97706; border-radius: 6px;
  padding: 8px 12px; font-size: .8rem; color: #655C54; margin-top: 6px; }
button[kind="primary"] { background: #A8421B; border-color: #A8421B; color: white; border-radius: 10px; }
button[kind="secondary"] { border-radius: 10px; }
/* Role styling only affects keyed conversation turns, never the sidebar. */
.stMain div[class*="st-key-chat_user_"] [data-testid="stChatMessage"],
.stMain div[class*="st-key-chat_assistant_"] [data-testid="stChatMessage"] {
  background: transparent; padding: .25rem 0; gap: 10px; align-items: flex-start;
}
.stMain div[class*="st-key-chat_user_"] [data-testid="stChatMessage"] {
  flex-direction: row-reverse; width: fit-content; max-width: min(88%, 48rem); margin-left: auto;
}
.stMain div[class*="st-key-chat_user_"] [data-testid="stChatMessageContent"] {
  flex: 0 1 auto; width: auto; max-width: none; min-width: 0;
}
.stMain div[class*="st-key-chat_assistant_"] [data-testid="stChatMessageContent"] {
  min-width: 0; max-width: calc(100% - 3rem);
}
.chat-user-bubble {
  width: fit-content; max-width: 100%; box-sizing: border-box; border-radius: 16px;
  padding: .7rem 1rem; background: #292524; color: #FFFFFF;
  white-space: pre-wrap; overflow-wrap: anywhere; text-align: left;
  line-height: 1.7; font-family: 'Sarabun', Tahoma, 'Noto Sans Thai', sans-serif;
}
.stMain div[class*="st-key-assistant_bubble_"] {
  width: fit-content; max-width: 100%; box-sizing: border-box; border: 1px solid #E6DDD2;
  border-radius: 16px; padding: .7rem 1rem; background: #FFFFFF; color: #292524;
  text-align: left; overflow-wrap: anywhere; min-width: 0;
}
.stMain div[class*="st-key-assistant_bubble_"] p:last-child { margin-bottom: 0; }
/* Sidebar tabs wrap their Thai labels instead of creating a scrolling header. */
[data-testid="stSidebar"] [data-testid="stTabs"] [role="tablist"] { flex-wrap: wrap; }
[data-testid="stSidebar"] [role="tab"] { white-space: normal; height: auto; min-height: 2.5rem; }

[data-testid="stChatInput"] { border: 1px solid #D7B9A6; border-radius: 14px; }
[data-testid="stExpander"] { border-color: #E6DDD2; border-radius: 12px; background: white; }
[data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"],
.ingredient-panel, .card-title, .badge { overflow-wrap: anywhere; }
@media (max-width: 640px) {
  .stMainBlockContainer { padding: 4rem 1rem 8rem; }
  .stMain div[class*="st-key-chat_user_"] [data-testid="stChatMessage"] { max-width: 100%; }
  .chat-user-bubble, .stMain div[class*="st-key-assistant_bubble_"] { padding: .65rem .8rem; }
  .stMain div[class*="st-key-chat_user_"] [data-testid="stChatMessage"],
  .stMain div[class*="st-key-chat_assistant_"] [data-testid="stChatMessage"] { gap: 8px; }
  div[class*="st-key-recipe_card_"], div[class*="st-key-sample_card_"] { padding: 14px; }
  [data-testid="stMarkdownContainer"] table { width: 100%; }
}
"""
