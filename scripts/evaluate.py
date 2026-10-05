"""Run real retrieval scenarios; optional Groq selection, with deterministic checks."""
import csv
import json
import sys
import tomllib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rag import MODEL, DEFAULT_GROQ_MODEL, Retriever, candidates, load_recipes, select_with_llm, render_answer

def main():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL, device='cpu', cache_folder=str(ROOT / '.cache/models'), local_files_only=True)
    retriever = Retriever(load_recipes(ROOT / 'data'), model)
    live = '--llm' in sys.argv
    client = None
    if live:
        from groq import Groq
        config = tomllib.loads((ROOT / '.streamlit/secrets.toml').read_text(encoding='utf-8'))
        client = Groq(api_key=config['GROQ_API_KEY'], timeout=30, max_retries=0)
    results = []
    with (ROOT / 'test_questions.csv').open(encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            hits = candidates(retriever, row['question'], set(filter(None, row['pantry'].split('|'))),
                              set(filter(None, row['equipment'].split('|'))), list(filter(None, row['previous_recipe_ids'].split('|'))))
            if live and hits:
                hits = select_with_llm(client, config.get('GROQ_MODEL', DEFAULT_GROQ_MODEL), row['question'], hits)
            ids = [h['recipe']['recipe_id'] for h in hits]
            expected = list(filter(None, row['expected_recipe_ids'].split('|')))
            passed = set(expected).issubset(ids) if row['answerable'] == 'yes' else not ids
            # Exact ingredient omissions and original steps/citation checked without LLM-as-Judge.
            if row['expected_missing'] and hits:
                passed &= set(row['expected_missing'].split('|')).issubset(hits[0]['missing'])
            if live and hits:
                answer = render_answer(hits)
                passed &= all(h['recipe']['document'] in answer and all(s in answer for s in h['recipe']['steps']) for h in hits)
            results.append(dict(id=row['id'], actual_recipe_ids=ids, passed=bool(passed)))
    report = dict(mode='live_groq' if live else 'real_semantic_retrieval_no_llm',
                  passed=sum(r['passed'] for r in results), total=len(results), cases=results)
    target = ROOT / ('test-results.local.json' if live else 'retrieval_results.json')
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not all(r['passed'] for r in results):
        sys.exit(1)

if __name__ == '__main__':
    main()
