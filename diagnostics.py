"""Allowlisted operational logs: never serialize secrets, requests or API error bodies."""
import json
import logging
import re

logger = logging.getLogger('krua')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
logger.propagate = False

FIELDS = {'stage', 'reason', 'pipeline_version', 'doc_hash', 'recipes', 'chunks', 'model',
          'error_type', 'http_status', 'candidate_ids', 'recipe_id', 'score', 'kept',
          'selected_ids', 'finish_reason', 'content_characters', 'retry_after', 'intent'}

def log_event(stage, **fields):
    record = {'stage': stage}
    for key, value in fields.items():
        if key not in FIELDS:
            continue
        if key == 'model' and (not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9./_-]{1,80}', value) or value.startswith('gsk_')):
            value = 'invalid_model_configuration'
        record[key] = value
    logger.info(json.dumps(record, ensure_ascii=False))

def log_failure(stage, error, model=None):
    response = getattr(error, 'response', None)
    headers = getattr(response, 'headers', {})
    retry_after = headers.get('retry-after', '')
    retry_after = retry_after if re.fullmatch(r'\d+(?:\.\d+)?', retry_after) else None
    log_event(stage, error_type=type(error).__name__, http_status=getattr(error, 'status_code', None), model=model, retry_after=retry_after)
