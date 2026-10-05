"""Reproduce the UI pipeline; --live tests Groq smoke first, then retrieved Context.
Only allowlisted IDs/counts/scores/statuses are saved. Credentials stay in Secrets.
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rag import (MODEL, PIPELINE_VERSION, Retriever, load_recipes, update_pantry,
                 candidates, fingerprint, select_with_llm, completion_text)
from configuration import read_configuration
from diagnostics import log_failure
from groq_support import smoke_test

QUERIES = ['ไข่', 'ไข่ไก่', 'มีไข่ ข้าวสวย และต้นหอม ทำอะไรได้บ้าง',
           'ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง', 'ขอสูตรพิซซ่าไข่', 'ข้าวผัดไข่มีกี่แคลอรี']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--stream-smoke', action='store_true')
    parser.add_argument('--smoke-only', action='store_true')
    args = parser.parse_args()
    client = None
    report = dict(pipeline_version=PIPELINE_VERSION, index_key=fingerprint(ROOT / 'data')[:12], live=args.live, cases=[])
    if args.live:
        from groq import Groq
        path = ROOT / '.streamlit/secrets.toml'
        if not path.exists():
            print('ยังไม่ได้ทดสอบ Groq จริง: ไม่มี local Streamlit Secrets'); return
        key, model_name = read_configuration(tomllib.loads(path.read_text(encoding='utf-8-sig')))
        report['model'] = model_name
        if not key:
            print('ยังไม่ได้ทดสอบ Groq จริง: ไม่มี GROQ_API_KEY'); return
        client = Groq(api_key=key, timeout=45, max_retries=0)
        try:
            report['smoke'] = dict(nonempty=bool(smoke_test(client, model_name, stream=args.stream_smoke)), stream=args.stream_smoke)
        except Exception as error:
            log_failure('smoke', error, model_name)
            report['smoke'] = dict(error_type=type(error).__name__, http_status=getattr(error, 'status_code', None))
        if args.smoke_only:
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return
    from sentence_transformers import SentenceTransformer
    rs = load_recipes(ROOT / 'data')
    rt = Retriever(rs, SentenceTransformer(MODEL, device='cpu', cache_folder=str(ROOT / '.cache/models'), local_files_only=True))
    report.update(recipes=len(rs), chunks=len(rt.chunks))
    names = {i['name'] for r in rs for i in r['ingredients']}
    for q in QUERIES:
        pantry = update_pantry(q, set(), names, rs)
        hits = candidates(rt, q, pantry, set())
        row = dict(question=q, normalized_ingredients=sorted(pantry),
                   candidates=[dict(recipe_id=h['recipe']['recipe_id'], score=round(h['score'], 5), missing=h['missing']) for h in hits],
                   retrieval_answerable=bool(hits))
        if client and hits:
            try:
                selected = select_with_llm(client, model_name, q, hits)
                row['selected_ids'] = [h['recipe']['recipe_id'] for h in selected]
                row['stage'] = 'validated_llm_response'
            except Exception as error:
                log_failure('live_diagnostic', error, model_name)
                row.update(stage='groq_error', error_type=type(error).__name__, http_status=getattr(error, 'status_code', None))
        else:
            row['stage'] = 'context_ready_no_api_call' if hits else 'retrieval_rejected'
        report['cases'].append(row)
    filename = 'groq_diagnostics.local.json' if args.live else 'bugfix_results.json'
    (ROOT / filename).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
