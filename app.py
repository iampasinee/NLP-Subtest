from pathlib import Path
import streamlit as st
from groq import Groq, AuthenticationError, APITimeoutError, RateLimitError, APIConnectionError, APIStatusError
from rag import (MODEL, PIPELINE_VERSION, LLMParseError, LLMValidationError, LLMNoSelectionError, Retriever, extract_names, fingerprint,
                 load_recipes, update_pantry)
from configuration import read_configuration
from diagnostics import log_event, log_failure
from groq_support import smoke_test

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='มีอะไร ทำอะไรดี', page_icon='🍲', layout='centered')

@st.cache_resource(max_entries=1)
def embedding_model(model_name):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name, device='cpu', cache_folder=str(ROOT / '.cache' / 'models'))

@st.cache_resource(max_entries=2)
def knowledge_index(digest):
    log_event('index_build', doc_hash=digest[:12], pipeline_version=PIPELINE_VERSION)
    return Retriever(load_recipes(ROOT / 'data'), embedding_model(MODEL))

def configuration():
    return read_configuration(st.secrets)

from presentation import LiveRecipeAdapter, question_kind
from request_state import plan_request
from ui.styles import CSS
from ui.components import samples, answer_message

st.html('<style>' + CSS + '</style>')
for name, default in [('messages', []), ('previous', []), ('pantry', set()), ('selected_recipe_id', None)]:
    if name not in st.session_state:
        st.session_state[name] = default
for name, value in st.session_state.pop('pending_form_values', {}).items():
    st.session_state[name] = value

def reset():
    for name in ['messages', 'previous', 'pantry', 'selected_recipe_id', 'pending_query',
                 'form_ingredients', 'form_seasonings', 'form_equipment', 'pending_form_values']:
        st.session_state.pop(name, None)
    st.session_state.pop('form_snapshot', None)

def select_recipe(recipe_id):
    st.session_state.selected_recipe_id = recipe_id

def clarify(recipe_id, query):
    select_recipe(recipe_id)
    st.session_state.pending_query = query

left, right = st.columns([5, 1], gap='small')
with left:
    st.title('มีอะไร ทำอะไรดี')
    st.write('ค้นเมนูจากวัตถุดิบที่มี พร้อมสูตรและแหล่งอ้างอิง')
with right:
    st.button('เริ่มใหม่', key='reset_header', on_click=reset, width='stretch', wrap=True)
st.caption('สูตรตัวอย่างสร้างโดย AI ต้องตรวจทานก่อนใช้จริง')
try:
    key, model_name = configuration()
except ValueError as error:
    log_failure('configuration', error)
    st.error('รูปแบบค่า GROQ_MODEL หรือ GROQ_API_KEY ใน Secrets ไม่ถูกต้อง กรุณาตรวจการตั้งค่า')
    st.stop()
index_key = fingerprint(ROOT / 'data')
log_event('startup', model=model_name, pipeline_version=PIPELINE_VERSION, doc_hash=index_key[:12])
if not key:
    st.info('ยังไม่ได้ตั้งค่า Groq API: ใส่ GROQ_API_KEY ใน Streamlit Secrets ระบบจะยังไม่สร้างคำตอบจาก LLM')
recipes = load_recipes(ROOT / 'data')
names = {i['name'] for r in recipes for i in r['ingredients']}
seasonings = {i['name'] for r in recipes for i in r['ingredients'] if i['name'] in r['_sections']['เครื่องปรุง']}
equipment_names = {e for r in recipes for e in r['equipment']}
search_query = None
with st.expander('วัตถุดิบ เครื่องปรุง และอุปกรณ์ของคุณ', expanded=False):
    a, b = st.columns(2)
    with a:
        ingredients_text = st.text_area('วัตถุดิบที่มี', key='form_ingredients', placeholder='ไข่ ข้าวสวย ต้นหอม')
    with b:
        seasonings_text = st.text_area('เครื่องปรุงที่มี', key='form_seasonings', placeholder='ซีอิ๊วขาว น้ำมันพืช')
    equipment = st.multiselect('อุปกรณ์ที่มี', sorted(equipment_names), key='form_equipment')
    st.caption('ไม่เลือกอุปกรณ์ = ยังไม่ได้ระบุและไม่กรองอุปกรณ์ หากเลือก ให้ระบุทั้งหมดที่มี รวมถ้วย ช้อน มีด ตามจริง')
    st.caption('ตรวจชื่อวัตถุดิบรวมเครื่องปรุง ยังไม่ยืนยันว่าปริมาณที่มีเพียงพอ')
    if st.button('ค้นเมนูจากของที่มี', key='search_saved', type='primary', width='stretch'):
        search_query = 'ค้นเมนูจากของที่มี'
with st.expander('ตั้งค่าการค้นหา'):
    top_k = st.slider('จำนวนส่วนเอกสารที่ค้นคืน (Top-K)', 1, 10, 3, key='search_top_k')
    st.caption('K คือจำนวน chunks ที่ใช้ตั้งต้นบริบท ไม่ใช่จำนวนการ์ดเมนู สูตรเต็มของเมนูที่เกี่ยวข้องจะเพิ่มเป็นบริบทอีกส่วน')
with st.sidebar:
    with st.expander('สำหรับนักพัฒนา'):
        st.caption(f'คลังสูตร {len(recipes)} เมนู · CPU · {model_name}')
        st.caption(f'เวอร์ชัน {PIPELINE_VERSION} · index {index_key[:12]}')
        if st.button('ทดสอบ Groq โดยตรง', disabled=not key):
            try:
                smoke_test(Groq(api_key=key, timeout=30, max_retries=0), model_name)
                st.success('Groq ตอบข้อความทดสอบที่ไม่ว่างสำเร็จ')
            except Exception as error:
                log_failure('smoke', error, model_name)
                status = getattr(error, 'status_code', None)
                st.error(f'การทดสอบ Groq ไม่สำเร็จ: {type(error).__name__}' + (f' (HTTP {status})' if status else '') + ' ดู Cloud logs')

selected_id = st.session_state.selected_recipe_id
if selected_id:
    selected_name = next(r['name'] for r in recipes if r['recipe_id'] == selected_id)
    st.info(f'กำลังถามต่อเกี่ยวกับ {selected_name} [{selected_id}]')
    st.button('ยกเลิกการเลือกเมนู', on_click=select_recipe, args=(None,))
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        if message['role'] == 'user':
            st.markdown(message['content'])
        else:
            answer_message(message, select_recipe, clarify)
if st.session_state.messages:
    with st.expander('คำถามตัวอย่าง'):
        example_query = samples()
else:
    example_query = samples()
query = st.chat_input('พิมพ์วัตถุดิบ หรือถามเกี่ยวกับสูตร…', max_chars=2000, submit_mode='disable') or search_query or example_query or st.session_state.pop('pending_query', None)
if query:
    st.session_state.messages.append(dict(role='user', content=query))
    with st.chat_message('user'):
        st.markdown(query)
    answer = dict(role='assistant', id=str(len(st.session_state.messages)), query=query, content='')
    if not key:
        answer['content'] = 'ยังไม่ได้เรียก LLM กรุณาตั้งค่า GROQ_API_KEY ตามข้อความด้านบน'
    else:
        stage = 'index'
        adapter = None
        try:
            with st.spinner('กำลังค้นสูตรและตรวจข้อมูล…'):
                retriever = knowledge_index(index_key)
                form_pantry = extract_names(ingredients_text + ' ' + seasonings_text, names)
                form_changed = st.session_state.get('form_snapshot', sorted(form_pantry)) != sorted(form_pantry)
                current = form_pantry if form_changed else st.session_state.pantry
                plan = plan_request(query, form_pantry, current, recipes)
                if plan['intent'] in ['saved_search', 'addition']:
                    form_plan = plan_request(ingredients_text + ' ' + seasonings_text, set(), set(), recipes)
                    plan['unknown'] = list(dict.fromkeys(plan['unknown'] + form_plan['unknown']))
                st.session_state.form_snapshot = sorted(form_pantry)
                pantry = plan['pantry']
                st.session_state.pantry = pantry
                if plan['intent'] in ['new_search', 'saved_search', 'addition']:
                    st.session_state.selected_recipe_id = None
                    st.session_state.previous = []
                eq = set(equipment)
                if not eq and 'ไมโครเวฟ' in query and any(s in query for s in ['เฉพาะ', 'เท่านั้น']):
                    eq = {'ไมโครเวฟ'}
                answer['request'] = dict(intent=plan['intent'], ingredients=sorted(pantry), equipment=sorted(eq), top_k=top_k)
                stage = 'retrieval_or_groq'
                adapter = LiveRecipeAdapter(retriever, Groq(api_key=key, timeout=30, max_retries=0), model_name)
                response = adapter.answer_request(
                    query, pantry, eq, st.session_state.previous, st.session_state.selected_recipe_id, top_k=top_k, unknown=plan['unknown'])
                answer['response'] = response
                answer['content'] = response.get('content', response['answer'])
                if response['status'] == 'ok':
                    st.session_state.previous = [v['recipe_id'] for v in response['recipes']]
                    st.session_state.selected_recipe_id = response.get('selected_recipe_id')
        except AuthenticationError as error:
            log_failure('groq_api', error, model_name)
            answer['content'] = 'Groq API Key ไม่ถูกต้อง กรุณาตรวจค่าใน Secrets'
        except RateLimitError as error:
            log_failure('groq_api', error, model_name)
            answer['content'] = 'ใช้งานถึงขีดจำกัดของ Groq แล้ว กรุณาลองใหม่ภายหลัง'
        except APITimeoutError as error:
            log_failure('groq_api', error, model_name)
            answer['content'] = 'Groq ใช้เวลาตอบนานเกินกำหนด กรุณาลองใหม่'
        except APIConnectionError as error:
            log_failure('groq_api', error, model_name)
            answer['content'] = 'เชื่อมต่อ Groq ไม่สำเร็จ กรุณาตรวจการเชื่อมต่อและชื่อโมเดลใน Secrets'
        except APIStatusError as error:
            log_failure('groq_api', error, model_name)
            answer['content'] = f'Groq API ส่ง HTTP {error.status_code} กรุณาตรวจชื่อโมเดลและการตั้งค่า API ใน Secrets หรือดู Cloud logs'
        except LLMParseError as error:
            log_failure('groq_parse', error, model_name)
            answer['content'] = 'Groq ส่งคำตอบว่าง ไม่ครบ หรืออ่าน JSON ไม่ได้ กรุณาลองใหม่หรือตรวจ Cloud logs'
        except LLMValidationError as error:
            log_failure('groq_validation', error, model_name)
            answer['content'] = 'คำตอบ Groq ไม่ผ่านการตรวจรหัสสูตรหรือแหล่งอ้างอิง จึงยังไม่แสดงสูตร กรุณาลองใหม่'
        except LLMNoSelectionError as error:
            log_failure('groq_selection', error, model_name)
            answer['content'] = 'พบสูตรที่เกี่ยวข้องในเอกสาร แต่ Groq ยังไม่เลือกเมนูจาก Context กรุณาลองใหม่หรือระบุคำถามให้ชัดเจน'
        except ValueError as error:
            log_failure(stage, error, model_name)
            answer['content'] = 'คำตอบหรือข้อมูลไม่ผ่านการตรวจสอบ จึงไม่แสดงคำตอบ กรุณาลองใหม่หรือตรวจคลังเอกสาร'
        except Exception as error:
            log_failure(stage, error, model_name)
            answer['content'] = 'โหลดโมเดลหรือค้นหาไม่สำเร็จ กรุณาตรวจ dependencies และการดาวน์โหลดโมเดลครั้งแรก'
    if 'response' not in answer and key:
        answer['response'] = dict(status='error', answer=answer['content'])
        if adapter is not None and hasattr(adapter, 'last_trace'):
            answer['response']['retrieval'] = adapter.last_trace
            answer['response']['effective'] = answer.get('request', {})
    st.session_state.messages.append(answer)
    st.rerun()
