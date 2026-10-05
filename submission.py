"""One-shot submission queue shared by chat, welcome, sidebar, and follow-ups."""
from uuid import uuid4

def enqueue(state, question):
    if not question or state.get('request_processing', False) or state.get('pending_submission'):
        return False
    state['pending_submission'] = dict(id=uuid4().hex, question=question)
    state['request_processing'] = True
    return True

def take(state):
    return state.pop('pending_submission', None)

def finish(state):
    state['request_processing'] = False
