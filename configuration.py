import re
from rag import DEFAULT_GROQ_MODEL

def read_configuration(secrets):
    """Streamlit Secrets are the only credential source; no environment fallback."""
    try:
        model = secrets.get('GROQ_MODEL', DEFAULT_GROQ_MODEL)
        key = secrets.get('GROQ_API_KEY', '')
    except (KeyError, FileNotFoundError):
        return None, DEFAULT_GROQ_MODEL
    if not isinstance(model, str) or not re.fullmatch(r'[a-zA-Z0-9./_-]{1,80}', model) or model.startswith('gsk_'):
        raise ValueError('GROQ_MODEL ไม่ถูกต้อง')
    if not isinstance(key, str):
        raise ValueError('GROQ_API_KEY ต้องเป็นข้อความ')
    key = key.strip()
    return (key if key and key != 'YOUR_GROQ_API_KEY' else None), model
