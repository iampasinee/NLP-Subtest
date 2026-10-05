import copy
from html import unescape
import pytest
from streamlit.testing.v1 import AppTest
from tests.test_rag import model
from tests.test_presentation import ROOT, selecting_client
from ui.components import user_bubble_html

@pytest.mark.parametrize('text', ['ไข่ไก่, ต้นหอม', 'มีไข่และต้นหอม อยากถามวิธีทำอาหารตามสูตร\n' * 100,
                                 '<script>alert("x")</script> & <img src=x onerror=alert(1)>'])
def test_user_bubble_preserves_thai_and_escapes_html(text):
    html = user_bubble_html(text)
    body = html.split('>', 1)[1].rsplit('</div>', 1)[0]
    assert unescape(body) == text
    assert '<script>' not in html and '<img' not in html

def test_short_long_roles_render_in_chronological_stream():
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=20)
    at.secrets['GROQ_API_KEY'] = ''
    at.run()
    at.session_state['messages'] = [
        dict(role='user', id='u1', content='ไข่ไก่, ต้นหอม'),
        dict(role='assistant', id='a1', content='กรุณาระบุเมนูที่ต้องการสอบถาม'),
        dict(role='user', id='u2', content='ข้อความภาษาไทยยาว <tag> &\n' * 100),
        dict(role='assistant', id='a2', content='คำตอบภาษาไทยยาวที่ต้องห่อข้อความตามความกว้างหน้าจอ\n\n' * 100),
    ]
    at.run()
    assert not at.exception
    assert [m.name for m in at.main.chat_message] == ['user', 'assistant', 'user', 'assistant']
    html = [e.proto.body for e in at.get('html')]
    assert any('&lt;tag&gt; &amp;' in body for body in html)
    # Native pinned chat input lives in Streamlit's bottom block, not AppTest.main.
    assert at.chat_input[0].key == 'chat_query'
    assert not at.main.text_area and len(at.sidebar.text_area) == 2
    assert not at.main.slider and at.sidebar.slider(key='search_top_k').value == 3

def test_evidence_selection_is_local_and_preserves_turns(monkeypatch, model):
    import groq
    import sentence_transformers
    client = selecting_client()
    original = client.chat.completions.create
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        return original(**kwargs)
    client.chat.completions.create = create
    monkeypatch.setattr(sentence_transformers, 'SentenceTransformer', lambda *a, **kw: model)
    monkeypatch.setattr(groq, 'Groq', lambda **kw: client)
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
    at.secrets['GROQ_API_KEY'] = 'SIMULATED_PLACEHOLDER'
    at.run()
    assert any('ยังไม่มีคำตอบ' in i.value for i in at.sidebar.info)
    at.button(key='sample_0').click().run()
    first = copy.deepcopy(at.session_state['messages'][-1])
    rid = first['response']['recipes'][0]['recipe_id']
    at.button(key=f"select_{first['id']}_{rid}").click().run()
    selected = at.session_state['selected_recipe_id']
    at.button(key=f"evidence_recipe_{first['id']}_{rid}").click().run()
    assert not at.exception
    assert at.session_state['selected_evidence_turn'] == first['id']
    assert at.session_state['selected_evidence_recipe'] == rid
    assert at.session_state['selected_recipe_id'] == selected
    assert at.session_state['sidebar_tabs'] == 'หลักฐานและแหล่งที่มา'
    assert len(calls) == 1
    assert not at.main.expander or all('หลักฐาน' not in e.label for e in at.main.expander)
    assert any(rid in c.value for c in at.sidebar.caption)
    assert any(f'กรองเฉพาะ {rid}:' in c.value for c in at.sidebar.caption)
    other_ids = {v['recipe_id'] for v in first['response']['recipes']} - {rid}
    assert not any(f' • {other} • ' in c.value for c in at.sidebar.caption for other in other_ids)
    at.sidebar.slider(key='search_top_k').set_value(5).run()
    assert at.session_state['messages'][-1] == first
    at.chat_input[0].set_value('ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง').run()
    second = copy.deepcopy(at.session_state['messages'][-1])
    assert second['response']['retrieval']['top_k'] == 5
    assert len(calls) == 2
    at.button(key=f"evidence_turn_{second['id']}").click().run()
    assert not at.exception
    assert at.session_state['selected_evidence_turn'] == second['id']
    assert at.session_state['selected_evidence_recipe'] is None
    assert any('Top-K ที่ใช้: 5' in c.value for c in at.sidebar.caption)
    at.sidebar.selectbox(key='evidence_turn_picker').set_value(first['id']).run()
    assert not at.exception and len(calls) == 2
    assert at.session_state['selected_evidence_turn'] == first['id']
    assert any('Top-K ที่ใช้: 3' in c.value for c in at.sidebar.caption)
    assert at.session_state['messages'][-1] == second
    assert len({m['id'] for m in at.session_state['messages']}) == len(at.session_state['messages'])
    at.button(key='reset_header').click().run()
    assert not at.exception and at.session_state['messages'] == []
    assert at.session_state['selected_evidence_turn'] is None
    assert at.session_state['selected_evidence_recipe'] is None
    assert at.sidebar.slider(key='search_top_k').value == 5
    assert all(not t.value for t in at.sidebar.text_area)
