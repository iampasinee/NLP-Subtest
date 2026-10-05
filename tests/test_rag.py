import json
import hashlib
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from rag import (MODEL, Retriever, candidates, checks, extract_names, fingerprint,
                 load_recipes, make_chunks, render_answer, resolve_followup, select_with_llm, token_parts, update_pantry)
from scripts.validate_data import validate
from scripts.recipe_markdown import recipes_to_markdown

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(scope='session')
def recipes():
    return load_recipes(ROOT / 'data')

@pytest.fixture(scope='session')
def model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL, device='cpu', cache_folder=str(ROOT / '.cache/models'), local_files_only=True)

@pytest.fixture(scope='session')
def retriever(recipes, model):
    return Retriever(recipes, model)

def test_corpus():
    stats = validate(ROOT / 'data')
    assert stats['files'] == 1 and stats['recipes'] == 20
    assert stats['content_characters'] >= 15000

def test_all_original_fields_preserved(recipes):
    # Digest captured from the original 20 JSON files before migration.
    keys = ['recipe_id', 'name', 'ingredients', 'servings', 'equipment', 'steps', 'source', 'notes']
    original_fields = [{k: r[k] for k in keys} for r in recipes]
    digest = hashlib.sha256(json.dumps(original_fields, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()
    assert digest == 'fe348790469b369e665db64fdcf3cf1aaec3b500c3d6ed9b4097487e98f39d40'

def test_markdown_is_actual_source(tmp_path, recipes):
    (tmp_path / 'R01.json').write_text(json.dumps(recipes[0]), encoding='utf-8')
    assert load_recipes(tmp_path) == []  # No legacy JSON fallback.
    text = recipes_to_markdown([recipes[0]])
    text = text.replace('1 ถ้วย', '2 ถ้วย').replace(recipes[0]['steps'][0], 'ขั้นตอนใหม่จาก Markdown')
    (tmp_path / 'recipes.md').write_text(text, encoding='utf-8')
    loaded = load_recipes(tmp_path)[0]
    assert loaded['ingredients'][0]['quantity'] == '2 ถ้วย'
    assert loaded['steps'][0] == 'ขั้นตอนใหม่จาก Markdown'
    assert loaded['document'] == 'recipes.md'

@pytest.mark.parametrize('old,new', [
    ('### เครื่องปรุง', '### วัตถุดิบ'),
    ('| 4 | น้ำมันพืช', '| 1 | น้ำมันพืช'),
    ('1. แยกข้าวสวย', '2. แยกข้าวสวย'),
    ('## R01 —', '## R01 -'),
])
def test_reject_malformed_markdown(tmp_path, recipes, old, new):
    text = recipes_to_markdown([recipes[0]]).replace(old, new)
    (tmp_path / 'recipes.md').write_text(text, encoding='utf-8')
    with pytest.raises(ValueError):
        load_recipes(tmp_path)

def test_bad_schema_and_duplicate(tmp_path, recipes):
    (tmp_path / 'recipes.md').write_text('## R01 — สูตรไม่ครบ\n### วัตถุดิบ\nไข่', encoding='utf-8')
    with pytest.raises(ValueError):
        load_recipes(tmp_path)
    (tmp_path / 'recipes.md').write_text(recipes_to_markdown([recipes[0], recipes[0]]), encoding='utf-8')
    with pytest.raises(ValueError, match='ซ้ำ'):
        load_recipes(tmp_path)

def test_fingerprint_content_not_mtime(tmp_path):
    p = tmp_path / 'recipes.md'; p.write_text('# old')
    old = fingerprint(tmp_path); p.write_text('# changed')
    assert old != fingerprint(tmp_path)

def test_chunk_limit_and_no_lost_text(recipes, model):
    chunks = make_chunks(recipes, model)
    assert chunks and all(c['recipe_id'] and c['name'] and c['document'] == 'recipes.md' and c['section'] for c in chunks)
    assert {c['section'] for c in chunks} == {'วัตถุดิบ', 'เครื่องปรุง', 'จำนวนเสิร์ฟ', 'อุปกรณ์', 'ขั้นตอน', 'หมายเหตุ', 'แหล่งที่มา'}
    for r in recipes:
        for section, body in r['_sections'].items():
            matching = [c for c in chunks if c['recipe_id'] == r['recipe_id'] and c['section'] == section]
            prefix = f"{r['recipe_id']} {r['name']} {section}\n"
            assert ''.join(c['text'][len(prefix):] for c in matching) == body
    assert all(len(model.tokenizer.encode(c['text'])) <= model.max_seq_length for c in chunks)
    long = 'ต้นหอม ไข่ไก่ ซีอิ๊วขาว ' * 300
    parts = token_parts(long, model.tokenizer, model.max_seq_length)
    assert ''.join(parts) == long and len(parts) > 1

def test_semantic_index(retriever):
    hits = retriever.search('ข้าวผัดไข่ ข้าวสวย ต้นหอม')
    assert 'R01' in [h['recipe']['recipe_id'] for h in hits[:5]]
    vectors = np.vstack([retriever.index.reconstruct(i) for i in range(retriever.index.ntotal)])
    assert np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5)

def test_semantic_paraphrase(retriever):
    hits = retriever.search('อยากเอาข้าวสวยมาผัดกับไข่และต้นหอมในกระทะ')
    assert 'R01' in [h['recipe']['recipe_id'] for h in hits[:5]]

def test_top_k_and_empty(recipes, model, retriever, tmp_path):
    hits = retriever.search('ไข่', top_k=100000)
    assert len(hits) <= len(recipes) and len({h['recipe']['recipe_id'] for h in hits}) == len(hits)
    assert retriever.search('ไข่', top_k=0) == []
    assert load_recipes(tmp_path) == []
    assert Retriever([], model).search('ไข่', top_k=100) == []

def test_alias_and_negation():
    names = {'ไข่ไก่', 'น้ำมันพืช', 'น้ำปลา', 'ซีอิ๊วขาว', 'ต้นหอม'}
    assert extract_names('ไข่, ซีอิ้วขาว, หอมต้น', names) == {'ไข่ไก่', 'ซีอิ๊วขาว', 'ต้นหอม'}
    assert 'ไข่ไก่' not in extract_names('ไข่เป็ด ไข่เค็ม', names)
    assert extract_names('มีไข่, ไม่มีน้ำมันพืช, ขาดน้ำปลา', names) == {'ไข่ไก่'}
    assert extract_names('น้ำมันมะกอก น้ำซุป น้ำผึ้ง ไข่ปลา', names | {'น้ำ'}) == set()

def test_pantry_vs_recipe_name(recipes):
    names = {i['name'] for r in recipes for i in r['ingredients']}
    assert update_pantry('ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง', set(), names, recipes) == set()
    assert update_pantry('ข้าวผัดไข่ทำอย่างไร', set(), names, recipes) == set()
    assert update_pantry('ข้าวผัดไข่ทำอย่างไร มีไข่ ข้าวสวย ต้นหอม', {'น้ำปลา'}, names, recipes) == {'ไข่ไก่', 'ข้าวสวย', 'ต้นหอม'}

def test_seasonings_and_equipment(recipes):
    missing, eq = checks(recipes[0], {'ไข่ไก่', 'ข้าวสวย', 'ต้นหอม'}, {'ไมโครเวฟ'})
    assert set(missing) == {'น้ำมันพืช', 'ซีอิ๊วขาว'}
    assert 'กระทะ' in eq
    unknown = dict(recipes[0], equipment=[])
    assert 'ไม่เพียงพอ' in checks(unknown, set(), {'ไมโครเวฟ'})[1]

def test_followup(retriever):
    assert resolve_followup('เมนูที่สองทำอย่างไร', ['R01', 'R04']) == ['R04']
    hits = candidates(retriever, 'เมนูที่สองทำอย่างไร', set(), set(), ['R01', 'R04'])
    assert [h['recipe']['recipe_id'] for h in hits] == ['R04']
    assert candidates(retriever, 'เมนูที่สามทำอย่างไร', {'ไข่ไก่'}, set(), ['R01']) == []

def test_constraints_and_abstention(retriever):
    assert candidates(retriever, 'ข้าวผัดไข่ทำอย่างไร', set(), {'ไมโครเวฟ'}) == []
    assert candidates(retriever, 'ข้าวผัดไข่กี่แคลอรี', {'ไข่ไก่'}, set()) == []
    assert candidates(retriever, 'มีแซลมอน อะโวคาโด', set(), set()) == []
    assert candidates(retriever, 'สูตรพิซซ่าไข่', {'ไข่ไก่'}, set()) == []

def fake_client(obj):
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
        create=lambda **kwargs: SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(obj)))]))))

def test_llm_citation_validation_and_exact_evidence(retriever):
    hits = candidates(retriever, 'ข้าวผัดไข่ทำอย่างไร', set(), set())
    with pytest.raises(ValueError):
        select_with_llm(fake_client({'recipe_ids': ['FAKE'], 'citations': ['FAKE']}), 'mock', 'q', hits)
    with pytest.raises(ValueError):
        select_with_llm(fake_client({'recipe_ids': ['R01'], 'citations': ['R02']}), 'mock', 'q', hits)
    chosen = select_with_llm(fake_client({'recipe_ids': ['R01'], 'citations': ['R01']}), 'mock', 'q', hits)
    answer = render_answer(chosen)
    assert 'recipes.md' in answer and '1 ถ้วย' in answer and '[R01]' in answer
    assert all(s in answer for s in chosen[0]['recipe']['steps'])

def test_no_key_ui():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=20)
    at.secrets['GROQ_API_KEY'] = ''
    at.run()
    assert not at.exception
    assert any('ยังไม่ได้ตั้งค่า' in i.value for i in at.info)
    at.chat_input[0].set_value('มีไข่ ข้าวสวย').run()
    assert not at.exception
    assert 'ยังไม่ได้เรียก LLM' in at.session_state['messages'][-1]['content']
    at.button(key='reset_header').click().run()
    assert at.session_state['messages'] == []

@pytest.mark.parametrize('failure', ['authentication', 'timeout', 'rate_limit', 'connection', 'success'])
def test_groq_ui_with_simulated_responses(monkeypatch, model, failure):
    """No live API call: verify sanitized SDK errors and extractive UI behavior."""
    import groq
    import httpx
    import sentence_transformers
    from streamlit.testing.v1 import AppTest
    monkeypatch.setattr(sentence_transformers, 'SentenceTransformer', lambda *a, **kw: model)
    request = httpx.Request('POST', 'https://api.groq.com/openai/v1/chat/completions')
    if failure == 'authentication':
        error = groq.AuthenticationError('private diagnostic', response=httpx.Response(401, request=request), body=None)
        expected = 'Key ไม่ถูกต้อง'
    elif failure == 'timeout':
        error = groq.APITimeoutError(request=request); expected = 'นานเกินกำหนด'
    elif failure == 'rate_limit':
        error = groq.RateLimitError('private diagnostic', response=httpx.Response(429, request=request), body=None)
        expected = 'ขีดจำกัด'
    elif failure == 'connection':
        error = groq.APIConnectionError(request=request); expected = 'เชื่อมต่อ Groq ไม่สำเร็จ'
    else:
        error = None; expected = 'recipes.md'
    def create(**kwargs):
        if error:
            raise error
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"recipe_ids":["R01"],"citations":["R01"]}'))])
    monkeypatch.setattr(groq, 'Groq', lambda **kw: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
    at.secrets['GROQ_API_KEY'] = 'SIMULATED_PLACEHOLDER_NOT_A_KEY'
    at.run()
    at.chat_input[0].set_value('ข้าวผัดไข่ทำอย่างไร มีไข่ ข้าวสวย ต้นหอม').run()
    assert not at.exception
    answer = at.session_state['messages'][-1]['content']
    assert expected in answer
    assert 'private diagnostic' not in answer and 'SIMULATED_PLACEHOLDER' not in answer
    if failure == 'success':
        assert 'ยังขาดวัตถุดิบ: น้ำมันพืช, ซีอิ๊วขาว' in answer
        assert at.session_state['previous'] == ['R01']
