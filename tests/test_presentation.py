import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from streamlit.testing.v1 import AppTest
from tests.test_rag import recipes, model, retriever
from rag import candidates, DEFAULT_GROQ_MODEL
from presentation import EXAMPLES, LiveRecipeAdapter, map_answer, resolve_request

ROOT = Path(__file__).resolve().parents[1]

def selecting_client():
    def create(**kwargs):
        context = json.loads(kwargs['messages'][1]['content'])['CONTEXT']
        ids = [r['recipe_id'] for r in context][:3]
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(
            {'recipe_ids': ids, 'citations': ids})), finish_reason='stop')])
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

@pytest.mark.parametrize('example', EXAMPLES)
def test_examples_have_real_recipes(retriever, example):
    response = LiveRecipeAdapter(retriever, selecting_client(), DEFAULT_GROQ_MODEL).answer_request(example[2], set(), set())
    assert response['status'] == 'ok'
    assert 1 <= len(response['recipes']) <= 3
    assert all('recipes.md' in v['citation'] and v['recipe_id'] in v['citation'] for v in response['recipes'])

def test_fact_is_exact_short_and_equipment_unknown(retriever):
    q = EXAMPLES[1][2]
    response = map_answer(q, candidates(retriever, q, set(), set()), set(), set())
    assert response['kind'] == 'fact' and 'ไข่ไก่ 1 ฟอง' in response['answer']
    assert 'ขั้นตอน' not in response['content']
    view = response['recipes'][0]
    assert view['equipment_match'] == 'not_specified'
    assert view['quantity_check'] == 'unknown'
    assert all(p['text'] == view['recipe']['_sections'][p['section']] for p in view['evidence'])

def test_selected_followup_and_ambiguity(recipes, retriever):
    assert resolve_request('เมนูนี้ทำอย่างไร', recipes, ['R01', 'R04'])['status'] == 'needs_clarification'
    resolved = resolve_request('ใช้ไข่กี่ฟอง', recipes, ['R01', 'R04'], 'R04')
    assert resolved['target'] == 'R04' and 'ไข่ตุ๋นไมโครเวฟ' in resolved['query']
    response = LiveRecipeAdapter(retriever, selecting_client(), DEFAULT_GROQ_MODEL).answer_request(
        'ใช้ไข่กี่ฟอง', {'ไข่ไก่'}, set(), ['R01', 'R04'], 'R04')
    assert response['selected_recipe_id'] == 'R04' and '1 ฟอง' in response['answer']

@pytest.mark.parametrize('q,status', [('ขอสูตรพิซซ่าไข่', 'no_match'), ('ข้าวผัดไข่มีกี่แคลอรี', 'insufficient_context')])
def test_live_adapter_abstains_without_calling_api(retriever, q, status):
    response = LiveRecipeAdapter(retriever, None, DEFAULT_GROQ_MODEL).answer_request(q, {'ไข่ไก่'}, set())
    assert response['status'] == status and not response['recipes']

def test_ui_examples_cards_select_followup_reset(monkeypatch, model):
    import groq
    import sentence_transformers
    monkeypatch.setattr(sentence_transformers, 'SentenceTransformer', lambda *a, **kw: model)
    monkeypatch.setattr(groq, 'Groq', lambda **kw: selecting_client())
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
    at.secrets['GROQ_API_KEY'] = 'SIMULATED_PLACEHOLDER'
    at.run()
    assert not at.exception
    assert at.title[0].value == 'มีอะไร ทำอะไรดี'
    assert len([b for b in at.button if b.key and b.key.startswith('sample_')]) == len(EXAMPLES)
    at.button(key='sample_0').click().run()
    assert not at.exception
    response = at.session_state['messages'][-1]['response']
    assert response['kind'] == 'recommendation'
    assert 1 <= len(response['recipes']) <= 3
    assert any('ยังไม่ได้ระบุอุปกรณ์' in c.value for c in at.caption)
    assert any('recipes.md' in c.value for c in at.caption)
    assert any(e.label == 'ดูสูตรเต็ม' for e in at.expander)
    view = response['recipes'][0]
    select = next(b for b in at.button if b.key and b.key.startswith('select_') and b.key.endswith(view['recipe_id']))
    select.click().run()
    assert at.session_state['selected_recipe_id'] == view['recipe_id']
    pantry = at.session_state['pantry'].copy()
    at.chat_input[0].set_value('เมนูนี้ทำอย่างไร').run()
    assert not at.exception
    assert at.session_state['messages'][-1]['response']['kind'] == 'method'
    assert at.session_state['selected_recipe_id'] == view['recipe_id']
    assert at.session_state['pantry'] == pantry
    assert any(view['recipe']['steps'][0] in m.value for m in at.markdown)
    at.button(key='reset_header').click().run()
    assert not at.exception
    assert at.session_state['messages'] == [] and at.session_state['previous'] == []
    assert at.session_state['selected_recipe_id'] is None and not at.session_state['pantry']
    assert all(not t.value for t in at.text_area)
    assert at.multiselect[0].value == []

def test_ui_fact_has_evidence_without_full_recipe(monkeypatch, model):
    import groq
    import sentence_transformers
    monkeypatch.setattr(sentence_transformers, 'SentenceTransformer', lambda *a, **kw: model)
    monkeypatch.setattr(groq, 'Groq', lambda **kw: selecting_client())
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
    at.secrets['GROQ_API_KEY'] = 'SIMULATED_PLACEHOLDER'
    at.run().button(key='sample_1').click().run()
    assert not at.exception
    assert 'ไข่ไก่ 1 ฟอง' in at.session_state['messages'][-1]['content']
    assert any('R04' in c.value and 'recipes.md' in c.value for c in at.caption)
    assert not any(e.label == 'ดูสูตรเต็ม' for e in at.expander)
    assert any(b.label == 'ดูหลักฐาน' for b in at.button)
    assert not any(e.label.startswith('ดูหลักฐาน') for e in at.main.expander)
    assert at.session_state['pantry'] == set()
    at.chat_input[0].set_value('ใช้ไข่กี่ฟอง').run()
    assert not at.exception
    assert '1 ฟอง' in at.session_state['messages'][-1]['content']
    assert at.session_state['pantry'] == set()

def test_ui_ambiguous_followup_asks_and_resumes(monkeypatch, model):
    import groq
    import sentence_transformers
    monkeypatch.setattr(sentence_transformers, 'SentenceTransformer', lambda *a, **kw: model)
    monkeypatch.setattr(groq, 'Groq', lambda **kw: selecting_client())
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
    at.secrets['GROQ_API_KEY'] = 'SIMULATED_PLACEHOLDER'
    at.run().button(key='sample_0').click().run()
    at.chat_input[0].set_value('เมนูนี้ทำอย่างไร').run()
    assert not at.exception
    assert at.session_state['messages'][-1]['response']['status'] == 'needs_clarification'
    button = next(b for b in at.button if b.key and b.key.startswith('clarify_') and b.key.endswith('R01'))
    button.click().run()
    assert not at.exception
    assert at.session_state['messages'][-1]['response']['status'] == 'ok'
    assert at.session_state['selected_recipe_id'] == 'R01'
    assert at.session_state['pantry'] == {'ไข่ไก่', 'ข้าวสวย', 'ต้นหอม'}
