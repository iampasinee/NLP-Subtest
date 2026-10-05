from pathlib import Path
import streamlit as st
from groq import Groq, AuthenticationError, APITimeoutError, RateLimitError, APIConnectionError, APIStatusError
from rag import (MODEL, NO_DATA, Retriever, candidates, extract_names, fingerprint,
                 load_recipes, render_answer, select_with_llm, update_pantry)

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='ครัวคิดให้ · ผู้ช่วยเลือกเมนู', page_icon='🍲', layout='centered')

@st.cache_resource(max_entries=1)
def embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL, device='cpu', cache_folder=str(ROOT / '.cache' / 'models'))

@st.cache_resource(max_entries=2)
def knowledge_index(digest):
    return Retriever(load_recipes(ROOT / 'data'), embedding_model())

def configuration():
    try:
        key = st.secrets['GROQ_API_KEY']
        model = st.secrets.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
        return (key if key and key != 'YOUR_GROQ_API_KEY' else None), model
    except (KeyError, FileNotFoundError):
        return None, 'llama-3.3-70b-versatile'

st.title('🍲 ครัวคิดให้')
st.write('มีอะไรในครัววันนี้? เลือกเมนูจากสูตรในเอกสาร พร้อมดูสิ่งที่ขาดและหลักฐานทุกคำตอบ')
st.caption('โครงงาน RAG • สูตรตัวอย่างที่สร้างโดย AI ต้องตรวจทานก่อนใช้จริง')
key, model_name = configuration()
if not key:
    st.info('ยังไม่ได้ตั้งค่า Groq API: สร้าง .streamlit/secrets.toml ตาม secrets.example.toml แล้วใส่ GROQ_API_KEY หรือเพิ่มใน Secrets บน Community Cloud คุณยังเปิดดูคลังสูตรได้ แต่ระบบจะไม่สร้างคำตอบจาก LLM')
recipes = load_recipes(ROOT / 'data')
names = {i['name'] for r in recipes for i in r['ingredients']}
equipment_names = {e for r in recipes for e in r['equipment']}
with st.sidebar:
    st.header('ของที่มีในครัว')
    pantry_text = st.text_area('วัตถุดิบเพิ่มเติม', placeholder='ไข่, ข้าวสวย, ซีอิ๊วขาว, น้ำมันพืช')
    equipment = st.multiselect('อุปกรณ์ที่มี (ไม่เลือก = ยังไม่ตรวจ)', sorted(equipment_names))
    st.caption('หากเลือกอุปกรณ์ ต้องเลือกทั้งหมดที่มี เช่น ไมโครเวฟ ถ้วย ช้อน มีด ระบบไม่สมมติว่ามีอุปกรณ์อื่น')
    st.caption('ตรวจชื่อวัตถุดิบรวมเครื่องปรุง แต่ยังไม่ตรวจว่าปริมาณที่มีเพียงพอ')
    if st.button('เริ่มบทสนทนาใหม่', width='stretch'):
        st.session_state.messages = []; st.session_state.previous = []; st.session_state.pantry = set()
        st.rerun()
    st.caption(f'คลังสูตร {len(recipes)} เมนู · CPU · {model_name}')
    with st.expander('เปิดดูคลังสูตร'):
        for r in recipes:
            st.write(f"{r['recipe_id']} · {r['name']}")
            st.json(r, expanded=False)

for name, default in [('messages', []), ('previous', []), ('pantry', set())]:
    if name not in st.session_state:
        st.session_state[name] = default

def show_message(m):
    with st.chat_message(m['role']):
        st.markdown(m['content'])
        if m.get('evidence'):
            with st.expander('ดูหลักฐานอ้างอิงและคะแนนความคล้าย'):
                for h in m['evidence']:
                    r = h['recipe']
                    st.caption(f"{r['document']} • {r['name']} [{r['recipe_id']}] • similarity {h['score']:.3f} (ไม่ใช่ความมั่นใจ)")
                    st.text(h['hit']['text'])
                    st.json(r, expanded=False)

for message in st.session_state.messages:
    show_message(message)
examples = ['มีไข่ ข้าวสวย และต้นหอม ทำอะไรได้บ้าง', 'ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง', 'เมนูที่สองทำอย่างไร']
with st.expander('ลองถามแบบนี้'):
    example_query = None
    for q in examples:
        if st.button(q, width='stretch'):
            example_query = q
query = st.chat_input('พิมพ์วัตถุดิบหรือถามเกี่ยวกับสูตร…', max_chars=2000, submit_mode='disable') or example_query
if query:
    user = dict(role='user', content=query)
    st.session_state.messages.append(user); show_message(user)
    answer = dict(role='assistant', content='', evidence=[])
    if not key:
        answer['content'] = 'ยังไม่ได้เรียก LLM กรุณาตั้งค่า GROQ_API_KEY ตามข้อความด้านบน'
    else:
        try:
            with st.spinner('ค้นสูตรและตรวจเงื่อนไขจากเอกสาร…'):
                retriever = knowledge_index(fingerprint(ROOT / 'data'))
                st.session_state.pantry = update_pantry(query, st.session_state.pantry, names, recipes)
                pantry = st.session_state.pantry | extract_names(pantry_text, names)
                eq = set(equipment)
                if not eq and 'ไมโครเวฟ' in query and any(s in query for s in ['เฉพาะ', 'เท่านั้น']):
                    eq = {'ไมโครเวฟ'}
                hits = candidates(retriever, query, pantry, eq, st.session_state.previous)
                selected = select_with_llm(Groq(api_key=key, timeout=30, max_retries=0), model_name, query, hits) if hits else []
                answer['content'] = render_answer(selected); answer['evidence'] = selected
                st.session_state.previous = [h['recipe']['recipe_id'] for h in selected]
        except AuthenticationError:
            answer['content'] = 'Groq API Key ไม่ถูกต้อง กรุณาตรวจค่าใน Secrets'
        except RateLimitError:
            answer['content'] = 'ใช้งานถึงขีดจำกัดของ Groq แล้ว กรุณาลองใหม่ภายหลัง'
        except APITimeoutError:
            answer['content'] = 'Groq ใช้เวลาตอบนานเกินกำหนด กรุณาลองใหม่'
        except (APIConnectionError, APIStatusError):
            answer['content'] = 'เชื่อมต่อ Groq ไม่สำเร็จ กรุณาตรวจการเชื่อมต่อและชื่อโมเดลใน Secrets'
        except ValueError:
            answer['content'] = 'คำตอบหรือข้อมูลไม่ผ่านการตรวจสอบ จึงไม่แสดงคำตอบ กรุณาลองใหม่หรือตรวจคลังเอกสาร'
        except Exception:
            answer['content'] = 'โหลดโมเดลหรือค้นหาไม่สำเร็จ กรุณาตรวจ dependencies และการดาวน์โหลดโมเดลครั้งแรก'
    st.session_state.messages.append(answer); show_message(answer)
