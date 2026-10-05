import copy
import json
import pytest
from streamlit.testing.v1 import AppTest
from tests.test_rag import recipes, model, retriever
from tests.test_presentation import selecting_client, ROOT
from rag import candidates, build_rag_messages
from request_state import plan_request
from presentation import EXAMPLES, UNANSWERABLE_EXAMPLES, LiveRecipeAdapter

def test_request_state_replaces_adds_and_preserves_followups(recipes):
    old = {'ไข่ไก่', 'ข้าวสวย', 'ต้นหอม'}
    new = plan_request('มาม่า ทำอะไรได้บ้าง', old, old, recipes)
    assert new['pantry'] == set() and new['unknown'] == ['มาม่า']
    assert plan_request('ไข่ไก่, ต้นหอม', {'นมจืด'}, old, recipes)['pantry'] == {'ไข่ไก่', 'ต้นหอม'}
    assert plan_request('มีไข่เพิ่ม', {'ข้าวสวย'}, set(), recipes)['pantry'] == {'ข้าวสวย', 'ไข่ไก่'}
    assert plan_request('เมนูนี้ใช้ไข่กี่ฟอง', set(), old, recipes)['pantry'] == old
    assert plan_request('ค้นเมนูจากของที่มี', {'นมจืด'}, old, recipes)['pantry'] == {'นมจืด'}
    assert plan_request('มาม่า, ไข่ ทำอะไรได้บ้าง', old, old, recipes)['unknown'] == ['มาม่า']
    assert plan_request('มาม่าทำอย่างไร', old, old, recipes)['unknown'] == ['มาม่า']

@pytest.mark.parametrize('k', [1, 3, 5])
def test_k_controls_actual_context_chunks_and_grounded_completion(retriever, k):
    trace = {}
    hits = candidates(retriever, EXAMPLES[0][2], {'ไข่ไก่', 'ข้าวสวย', 'ต้นหอม'}, set(), top_k=k, trace=trace)
    assert len(trace['retrieved_chunks']) == k
    messages = build_rag_messages(EXAMPLES[0][2], hits)
    payload = json.loads(messages[1]['content'])
    assert payload['top_k'] == k and len(payload['retrieved_chunks']) == k
    assert payload['CONTEXT'] and all(r['steps'] and r['ingredients'] for r in payload['CONTEXT'])
    assert len(hits) <= 3
    chunks = {c['chunk_id']: c for c in retriever.chunks}
    for item in trace['retrieved_chunks']:
        assert item['chunk'] == chunks[item['chunk']['chunk_id']]
    assert trace['additional_sections']
    for section in trace['additional_sections']:
        assert section['text'] == retriever.recipes[section['recipe_id']]['_sections'][section['section']]

@pytest.mark.parametrize('example', UNANSWERABLE_EXAMPLES)
def test_real_document_refusals_and_relevant_hits(retriever, example):
    response = LiveRecipeAdapter(retriever, None, 'unused').answer_request(example[2], set(), set(), top_k=5)
    assert response['status'] in ['no_match', 'insufficient_context']
    if 'กี่แคลอรี' in example[2] or 'ราคา' in example[2]:
        assert len(response['retrieval']['retrieved_chunks']) == 5

def test_sample_expectations_grounded_in_entire_corpus(recipes):
    corpus = '\n'.join(v for r in recipes for v in r['_sections'].values())
    assert not any(w in corpus for w in ['แคลอรี', 'ราคา', 'ต้นทุน', 'บาท', 'บะหมี่กึ่งสำเร็จรูป', 'มาม่า', 'พิซซ่า'])
    assert recipes[3]['recipe_id'] == 'R04'
    assert {'name': 'ไข่ไก่', 'quantity': '1 ฟอง'} in recipes[3]['ingredients']
    assert 'ไมโครเวฟ' in recipes[3]['_sections']['อุปกรณ์']

def test_ui_new_search_not_old_pantry_and_turn_evidence(monkeypatch, model):
    import groq
    import sentence_transformers
    calls = []
    base = selecting_client()
    original = base.chat.completions.create
    def create(**kw):
        calls.append(json.loads(kw['messages'][1]['content']))
        return original(**kw)
    base.chat.completions.create = create
    monkeypatch.setattr(sentence_transformers, 'SentenceTransformer', lambda *a, **kw: model)
    monkeypatch.setattr(groq, 'Groq', lambda **kw: base)
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
    at.secrets['GROQ_API_KEY'] = 'SIMULATED_PLACEHOLDER'
    at.run()
    at.text_area(key='form_ingredients').set_value('ไข่ ข้าวสวย ต้นหอม').run()
    at.chat_input[0].set_value('ไข่ไก่, ต้นหอม').run()
    assert not at.exception
    assert at.session_state['pantry'] == {'ไข่ไก่', 'ต้นหอม'}
    assert at.text_area(key='form_ingredients').value == 'ไข่ ข้าวสวย ต้นหอม'
    first = copy.deepcopy(at.session_state['messages'][-1]['response']['retrieval'])
    assert len(first['retrieved_chunks']) == 3
    at.slider(key='search_top_k').set_value(5).run()
    assert at.session_state['messages'][-1]['response']['retrieval'] == first
    at.chat_input[0].set_value('มาม่า ทำอะไรได้บ้าง').run()
    assert not at.exception
    response = at.session_state['messages'][-1]['response']
    assert response['status'] == 'no_match' and 'มาม่า' in response['answer']
    assert not response['recipes'] and at.session_state['selected_recipe_id'] is None
    assert len(calls) == 1  # Unsupported ingredient rejected before Groq, not disguised API error.
    assert at.session_state['pantry'] == set()
    at.chat_input[0].set_value('มีไข่เพิ่ม').run()
    assert not at.exception and at.session_state['messages'][-1]['response']['status'] == 'ok'
    assert calls[-1]['top_k'] == 5 and len(calls[-1]['retrieved_chunks']) == 5
    at.button(key='reset_header').click().run()
    assert not at.exception and at.session_state['messages'] == []
    assert at.slider(key='search_top_k').value == 5
    assert not at.text_area(key='form_ingredients').value
    at.text_area(key='form_ingredients').set_value('มาม่า, ไข่').run()
    at.button(key='search_saved').click().run()
    assert not at.exception
    assert at.session_state['messages'][-1]['response']['status'] == 'no_match'
    assert 'มาม่า' in at.session_state['messages'][-1]['content']
