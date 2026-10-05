from rag import completion_text

def smoke_test(client, model_name, stream=False):
    """Nonempty request without RAG; supports either documented response pathway."""
    kwargs = dict(model=model_name, messages=[{'role': 'user', 'content': 'Reply with the single word OK.'}],
                  max_completion_tokens=2048, stream=stream)
    if model_name in ['openai/gpt-oss-120b', 'openai/gpt-oss-20b']:
        kwargs.update(reasoning_effort='low', include_reasoning=False)
    return completion_text(client.chat.completions.create(**kwargs), stream=stream)
