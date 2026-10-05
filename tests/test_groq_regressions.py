import io
import json
import logging
from types import SimpleNamespace
import pytest
from configuration import read_configuration
from diagnostics import logger, log_event, log_failure
from rag import (DEFAULT_GROQ_MODEL, PIPELINE_VERSION, LLMParseError, LLMValidationError,
                 LLMNoSelectionError, candidates, completion_text, validate_selection,
                 select_with_llm, update_pantry, fingerprint)
from test_rag import recipes, model, retriever, fake_client

@pytest.mark.parametrize('query', ['ไข่', 'ไข่ไก่', 'มีไข่ ข้าวสวย และต้นหอม ทำอะไรได้บ้าง', 'ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง'])
def test_reported_queries_reach_context(query, recipes, retriever):
    names = {i['name'] for r in recipes for i in r['ingredients']}
    pantry = update_pantry(query, set(), names, recipes)
    hits = candidates(retriever, query, pantry, set())
    assert hits
    assert all(h['recipe']['document'] == 'recipes.md' for h in hits)
    if 'กี่ฟอง' in query:
        assert pantry == set()
        assert hits[0]['recipe']['recipe_id'] == 'R04'
        assert {'name': 'ไข่ไก่', 'quantity': '1 ฟอง'} in hits[0]['recipe']['ingredients']
    else:
        assert all('ไข่ไก่' in [i['name'] for i in h['recipe']['ingredients']] for h in hits)
        assert any(h['missing'] for h in hits)
        assert all(h['equipment_status'] == 'ยังไม่ได้ระบุอุปกรณ์ที่มี' for h in hits)

def test_short_query_normalization_without_ui(retriever):
    for q in ['ไข่', 'ไข่ไก่']:
        assert candidates(retriever, q, set(), set())
    assert not candidates(retriever, 'ไข่เป็ด', set(), set())
    assert not candidates(retriever, 'ไข่ปลา', set(), set())

@pytest.mark.parametrize('query', ['ขอสูตรพิซซ่าไข่', 'ข้าวผัดไข่มีกี่แคลอรี'])
def test_unsupported_stays_rejected(query, retriever):
    assert candidates(retriever, query, {'ไข่ไก่'}, set()) == []

def test_secrets_model_override_and_default():
    assert read_configuration({}) == (None, DEFAULT_GROQ_MODEL)
    assert read_configuration({'GROQ_API_KEY': ' TEST_PLACEHOLDER ', 'GROQ_MODEL': 'openai/gpt-oss-120b'}) == ('TEST_PLACEHOLDER', 'openai/gpt-oss-120b')
    assert read_configuration({'GROQ_MODEL': 'llama-3.3-70b-versatile'})[1] == 'llama-3.3-70b-versatile'

def test_cache_key_changes_for_pipeline_implementation(monkeypatch, tmp_path):
    import rag
    (tmp_path / 'recipes.md').write_text('# document')
    before = fingerprint(tmp_path)
    monkeypatch.setattr(rag, 'PIPELINE_VERSION', PIPELINE_VERSION + '-changed-parser')
    assert fingerprint(tmp_path) != before

def test_cache_key_changes_for_helper_source_without_revision(monkeypatch, tmp_path):
    import rag
    source = tmp_path / 'helper.py'
    source.write_text('parser implementation 1')
    monkeypatch.setattr(rag, '__file__', str(source))
    before = fingerprint(tmp_path)
    source.write_text('parser implementation 2')
    assert fingerprint(tmp_path) != before

def test_cache_key_same_across_windows_and_cloud_line_endings(tmp_path):
    p = tmp_path / 'recipes.md'
    p.write_bytes(b'# recipes\n\n')
    before = fingerprint(tmp_path)
    p.write_bytes(b'# recipes\r\n\r\n')
    assert fingerprint(tmp_path) == before

def test_gpt_oss_parameters_and_compact_context(retriever):
    hits = candidates(retriever, 'ไข่ไก่', set(), set())
    seen = {}
    def create(**kwargs):
        seen.update(kwargs)
        ids = [hits[0]['recipe']['recipe_id']]
        return SimpleNamespace(choices=[SimpleNamespace(finish_reason='stop', message=SimpleNamespace(content=json.dumps({'recipe_ids': ids, 'citations': ids})))])
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    assert select_with_llm(client, DEFAULT_GROQ_MODEL, 'ไข่ไก่', hits)
    assert seen['stream'] is False and seen['reasoning_effort'] == 'low'
    assert seen['max_completion_tokens'] == 2048 and 'max_tokens' not in seen
    assert seen['include_reasoning'] is False and 'reasoning_format' not in seen
    assert seen['response_format']['json_schema']['strict'] is True
    context = json.loads(seen['messages'][1]['content'])
    assert context['intent'] == 'ingredient_recommendation'
    assert all('_sections' not in r for r in context['CONTEXT'])
    assert all(r['steps'] and r['ingredients'] for r in context['CONTEXT'])

def test_stream_fragments_combined_before_json_parse(retriever):
    def delta(text, finish=None):
        return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=text), finish_reason=finish)])
    fragments = [delta('{"recipe_ids":['), delta('"R04"],"citations":'), delta('["R04"]}'), delta(None, 'stop')]
    text = completion_text(iter(fragments), stream=True)
    hits = candidates(retriever, 'ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง', set(), set())
    assert validate_selection(text, hits)[0]['recipe']['recipe_id'] == 'R04'

@pytest.mark.parametrize('content,finish', [('', 'stop'), ('{}', 'length')])
def test_empty_or_truncated_content_is_parse_error(content, finish):
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content), finish_reason=finish)])
    with pytest.raises(LLMParseError):
        completion_text(response)

def test_empty_selection_is_not_document_not_found(retriever):
    hits = candidates(retriever, 'ไข่ไก่', set(), set())
    with pytest.raises(LLMNoSelectionError):
        select_with_llm(fake_client({'recipe_ids': [], 'citations': []}), DEFAULT_GROQ_MODEL, 'ไข่ไก่', hits)

def test_valid_citations_can_be_in_different_order(retriever):
    hits = candidates(retriever, 'ไข่ไก่', set(), set())
    ids = [h['recipe']['recipe_id'] for h in hits]
    chosen = validate_selection(json.dumps({'recipe_ids': ids, 'citations': list(reversed(ids))}), hits)
    assert [h['recipe']['recipe_id'] for h in chosen] == ids
    with pytest.raises(LLMValidationError):
        validate_selection('{"recipe_ids":["FAKE"],"citations":["FAKE"]}', hits)

def test_logs_drop_credentials_and_error_body(monkeypatch):
    output = io.StringIO()
    handler = logging.StreamHandler(output)
    monkeypatch.setattr(logger, 'handlers', [handler])
    log_event('test', model='openai/gpt-oss-120b', api_key='PRIVATE_KEY', Authorization='PRIVATE_HEADER', secrets='PRIVATE_SECRETS')
    log_failure('test', ValueError('PRIVATE_BODY'), 'openai/gpt-oss-120b')
    assert 'PRIVATE' not in output.getvalue()
    assert 'ValueError' in output.getvalue()

@pytest.mark.parametrize('scenario,expected', [
    ('empty_selection', 'พบสูตรที่เกี่ยวข้อง'),
    ('invalid_json', 'อ่าน JSON ไม่ได้'),
    ('invalid_ids', 'ไม่ผ่านการตรวจรหัสสูตร'),
    ('http_400', 'HTTP 400'),
])
def test_ui_distinguishes_groq_failure_from_no_document(monkeypatch, model, scenario, expected):
    import groq
    import httpx
    import sentence_transformers
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    from rag import NO_DATA
    monkeypatch.setattr(sentence_transformers, 'SentenceTransformer', lambda *a, **kw: model)
    def create(**kwargs):
        if scenario == 'http_400':
            request = httpx.Request('POST', 'https://api.groq.com/openai/v1/chat/completions')
            raise groq.BadRequestError('PRIVATE_DIAGNOSTIC', response=httpx.Response(400, request=request), body=None)
        text = {'empty_selection': '{"recipe_ids":[],"citations":[]}', 'invalid_json': '{broken',
                'invalid_ids': '{"recipe_ids":["FAKE"],"citations":["FAKE"]}'}[scenario]
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text), finish_reason='stop')])
    monkeypatch.setattr(groq, 'Groq', lambda **kw: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30)
    at.secrets['GROQ_API_KEY'] = 'SIMULATED_PLACEHOLDER'
    at.secrets['GROQ_MODEL'] = DEFAULT_GROQ_MODEL
    at.run()
    at.chat_input[0].set_value('ไข่ไก่').run()
    assert not at.exception
    answer = at.session_state['messages'][-1]['content']
    assert expected in answer and answer != NO_DATA
    assert 'PRIVATE' not in answer
    trace = at.session_state['messages'][-1]['response']['retrieval']
    assert trace['top_k'] == 3 and len(trace['retrieved_chunks']) == 3
