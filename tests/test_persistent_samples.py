import copy
import json
import streamlit as st
from streamlit.testing.v1 import AppTest
from tests.test_rag import model
from tests.test_presentation import ROOT, selecting_client
from presentation import EXAMPLES, UNANSWERABLE_EXAMPLES
from submission import enqueue, take, finish

def test_queue_consumes_once_and_allows_same_text_after_completion():
    state = {}
    assert enqueue(state, 'ไข่ไก่')
    first = take(state)
    assert take(state) is None
    assert not enqueue(state, 'ไข่ไก่')  # Still processing, even after queue is consumed.
    finish(state)
    assert enqueue(state, 'ไข่ไก่')
    second = take(state)
    assert first['question'] == second['question'] and first['id'] != second['id']

def test_persistent_samples_repeat_once_and_use_current_k(monkeypatch, model):
    import groq
    import sentence_transformers
    from rag import Retriever
    searches = []
    original_search = Retriever.search_chunks
    def search_chunks(self, query, top_k=40):
        searches.append(top_k)
        return original_search(self, query, top_k)
    monkeypatch.setattr(Retriever, 'search_chunks', search_chunks)
    client = selecting_client()
    original = client.chat.completions.create
    calls = []
    def create(**kwargs):
        calls.append(json.loads(kwargs['messages'][1]['content']))
        assert st.session_state.request_processing
        assert 'pending_submission' not in st.session_state
        assert not enqueue(st.session_state, EXAMPLES[0][2])
        return original(**kwargs)
    client.chat.completions.create = create
    monkeypatch.setattr(sentence_transformers, 'SentenceTransformer', lambda *a, **kw: model)
    monkeypatch.setattr(groq, 'Groq', lambda **kw: client)
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
    at.secrets['GROQ_API_KEY'] = 'SIMULATED_PLACEHOLDER'
    at.run()
    assert len([b for b in at.main.button if b.key and b.key.startswith('sample_')]) == len(EXAMPLES)
    assert len([b for b in at.sidebar.button if b.key and b.key.startswith('sidebar_sample_')]) == len(EXAMPLES)
    assert len([b for b in at.sidebar.button if b.key and b.key.startswith('sidebar_unsupported_')]) == len(UNANSWERABLE_EXAMPLES)
    at.sidebar.text_area(key='form_ingredients').set_value('ทูน่ากระป๋อง').run()
    at.button(key='show_sidebar_samples').click().run()
    assert not at.exception and not calls
    assert at.session_state['sample_questions_open']
    at.sidebar.button(key='sidebar_sample_0').click().run()
    assert not at.exception and len(calls) == 1
    assert len(at.session_state['messages']) == 2
    first = copy.deepcopy(at.session_state['messages'][-1])
    assert first['response']['retrieval']['top_k'] == 3
    assert calls[-1]['available_ingredients'] == ['ข้าวสวย', 'ต้นหอม', 'ไข่ไก่']
    assert at.sidebar.text_area(key='form_ingredients').value == 'ทูน่ากระป๋อง'
    assert not any(b.key and b.key.startswith('sample_') for b in at.main.button)
    assert not at.sidebar.button(key='sidebar_sample_0').disabled
    at.run()
    assert len(calls) == 1  # Plain rerun never replays the click.
    at.sidebar.slider(key='search_top_k').set_value(5).run()
    at.sidebar.button(key='sidebar_sample_0').click().run()
    assert not at.exception and len(calls) == 2
    assert len(at.session_state['messages']) == 4
    assert at.session_state['messages'][-1]['query'] == first['query']
    assert at.session_state['messages'][-1]['id'] != first['id']
    assert calls[-1]['top_k'] == 5
    assert at.session_state['messages'][1] == first
    second = copy.deepcopy(at.session_state['messages'][-1])
    search_count = len(searches)
    at.button(key=f"evidence_turn_{first['id']}").click().run()
    assert not at.exception and len(calls) == 2
    assert len(searches) == search_count
    assert at.session_state['messages'][-1] == second
    at.sidebar.button(key='sidebar_unsupported_0').click().run()
    assert not at.exception and len(at.session_state['messages']) == 6
    assert at.session_state['messages'][-1]['response']['status'] == 'insufficient_context'
    assert at.session_state['messages'][-1]['response']['retrieval']['top_k'] == 5
    assert len(calls) == 2  # Document refusal stays distinct and does not invoke Groq.
    assert not at.session_state['request_processing']

def test_submission_widgets_disabled_during_request_and_reenabled(monkeypatch, model):
    import groq
    import sentence_transformers
    client = selecting_client()
    original_create = client.chat.completions.create
    original_button = st.button
    busy_buttons = {}
    def button(*args, **kwargs):
        if st.session_state.get('request_processing'):
            busy_buttons[kwargs.get('key')] = kwargs.get('disabled', False)
        return original_button(*args, **kwargs)
    monkeypatch.setattr(st, 'button', button)
    def create(**kwargs):
        assert busy_buttons['search_saved']
        assert all(busy_buttons[f'sidebar_sample_{n}'] for n in range(len(EXAMPLES)))
        assert all(busy_buttons[f'sidebar_unsupported_{n}'] for n in range(len(UNANSWERABLE_EXAMPLES)))
        assert all(busy_buttons[f'sample_{n}'] for n in range(len(EXAMPLES)))
        return original_create(**kwargs)
    client.chat.completions.create = create
    monkeypatch.setattr(sentence_transformers, 'SentenceTransformer', lambda *a, **kw: model)
    monkeypatch.setattr(groq, 'Groq', lambda **kw: client)
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
    at.secrets['GROQ_API_KEY'] = 'SIMULATED_PLACEHOLDER'
    at.run().button(key='sample_1').click().run()
    assert not at.exception
    assert at.session_state['messages'][-1]['response']['status'] == 'ok'
    assert not at.sidebar.button(key='sidebar_sample_1').disabled
    assert not at.chat_input[0].disabled
