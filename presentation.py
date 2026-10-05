"""Live RAG → presentation mapping. No fixtures, mock adapter, or generated recipe text."""
import re
from rag import (NO_DATA, candidates, extract_names, select_with_llm)
from diagnostics import log_event

EXAMPLES = [
    ('🥚', 'เริ่มจากของที่มี', 'มีไข่ ข้าวสวย และต้นหอม ทำอะไรได้บ้าง'),
    ('🍲', 'ถามปริมาณตามสูตร', 'ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง'),
    ('📖', 'เปิดขั้นตอนทำอาหาร', 'ข้าวผัดไข่ทำอย่างไร'),
]

def question_kind(query):
    if any(s in query for s in ['ทำอย่างไร', 'วิธีทำ', 'ขั้นตอน', 'ทำยังไง']):
        return 'method'
    if any(s in query for s in ['กี่', 'เท่าไร', 'เท่าไหร่', 'ปริมาณ', 'อุปกรณ์', 'เครื่องมือ']):
        return 'fact'
    return 'recommendation'

def unsupported_information(query):
    return any(s in query for s in ['โภชนาการ', 'แคลอรี', 'แคลอรี่', 'โปรตีนกี่', 'แทนวัตถุดิบ',
               'ใช้แทน', 'ลดน้ำหนัก', 'กี่นาที', 'กี่วัตต์', 'อุณหภูมิ', 'กี่องศา', 'เก็บได้กี่'])

def resolve_request(query, recipes, previous, selected_recipe_id=None):
    """Resolve references before retrieval; never silently pick among multiple dishes."""
    lookup = {r['recipe_id']: r for r in recipes}
    explicit = [r['recipe_id'] for r in recipes if r['name'] in query]
    ordinal = re.search(r'(?:เมนู|สูตร)(?:ที่)?\s*(?:หนึ่ง|สอง|สาม|[123])', query)
    if explicit or ordinal:
        return dict(query=query, previous=list(previous), target=explicit[0] if len(explicit) == 1 else None)
    reference = any(s in query for s in ['เมนูนี้', 'สูตรนี้', 'เมนูเดิม', 'อันนี้'])
    followup = reference or question_kind(query) in ['method', 'fact']
    if not followup:
        return dict(query=query, previous=list(previous), target=None)
    target = selected_recipe_id if selected_recipe_id in lookup else (previous[0] if len(previous) == 1 else None)
    if target in lookup:
        # Replace pronouns, otherwise rag.resolve_followup would prefer the first item.
        resolved = query
        for word in ['เมนูนี้', 'สูตรนี้', 'เมนูเดิม', 'อันนี้']:
            resolved = resolved.replace(word, lookup[target]['name'])
        if lookup[target]['name'] not in resolved:
            resolved = lookup[target]['name'] + ' ' + resolved
        return dict(query=resolved, previous=[target], target=target)
    options = [dict(recipe_id=i, name=lookup[i]['name']) for i in previous if i in lookup]
    return dict(status='needs_clarification', answer='ต้องการถามเกี่ยวกับเมนูไหนครับ? เลือกเมนูด้านล่างหรือพิมพ์ชื่อเมนู',
                options=options, query=query)

def recipe_view(hit, pantry, equipment, kind):
    r = hit['recipe']
    present = set(hit.get('available_ingredients', pantry))
    return dict(recipe_id=r['recipe_id'], name=r['name'], recipe=r,
                matched=[i['name'] for i in r['ingredients'] if i['name'] in present],
                missing=list(hit['missing']), quantity_check='unknown',
                equipment=list(r['equipment']), equipment_status=hit['equipment_status'],
                equipment_match='not_specified' if not equipment else ('compatible' if r['equipment'] and set(r['equipment']).issubset(equipment) else 'unknown'),
                citation=f"{r['document']} • {r['name']} [{r['recipe_id']}]",
                # Facts need relevant source text, not an unrelated FAISS hit excerpt.
                evidence=[dict(section=k, text=v) for k, v in r['_sections'].items()
                          if k in (['วัตถุดิบ', 'เครื่องปรุง', 'จำนวนเสิร์ฟ', 'อุปกรณ์'] if kind == 'fact' else ['วัตถุดิบ', 'เครื่องปรุง', 'อุปกรณ์', 'ขั้นตอน'])],
                retrieval_evidence=hit['hit']['text'], score=hit['score'])

def fact_answer(query, recipe):
    if any(s in query for s in ['เสิร์ฟ', 'กี่คน', 'กี่จาน']):
        return f"{recipe['name']} ตามสูตรสำหรับ **{recipe['servings']} เสิร์ฟ**"
    if any(s in query for s in ['อุปกรณ์', 'เครื่องมือ']):
        return 'อุปกรณ์ที่สูตรระบุ: ' + (', '.join(recipe['equipment']) if recipe['equipment'] else 'สูตรไม่ได้ระบุอุปกรณ์')
    statement = query.replace(recipe['name'], '')
    names = {i['name'] for i in recipe['ingredients']}
    requested = extract_names(statement, names)
    if requested:
        return '\n\n'.join(f"**{i['name']} {i['quantity']}** ตามสูตร{recipe['name']} ({recipe['servings']} เสิร์ฟ)"
                            for i in recipe['ingredients'] if i['name'] in requested)
    return None

def map_answer(query, selected, pantry, equipment):
    kind = question_kind(query)
    views = [recipe_view(h, pantry, equipment, kind) for h in selected[:3]]
    if kind == 'fact':
        if len(views) != 1:
            return dict(status='needs_clarification', answer='ต้องการทราบข้อมูลของเมนูไหนครับ?',
                        options=[dict(recipe_id=v['recipe_id'], name=v['name']) for v in views], recipes=[])
        answer = fact_answer(query, views[0]['recipe'])
        if answer is None:
            return dict(status='insufficient_context', answer='ยังระบุข้อเท็จจริงที่ต้องการไม่ได้ กรุณาบอกชื่อวัตถุดิบหรือข้อมูลที่ต้องการทราบ', recipes=views, kind='fact')
    elif kind == 'method':
        answer = 'วิธีทำจากสูตรที่เกี่ยวข้อง พร้อมส่วนผสมและปริมาณตามเอกสาร'
    else:
        answer = f'พบ {len(views)} เมนูจากวัตถุดิบที่ระบุ เลือกดูสูตรหรือถามต่อได้เลย'
    # Store a textual equivalent for history/tests/accessibility, without full recipes.
    content = answer
    for v in views:
        content += '\n\n' + v['citation']
        if kind != 'fact' and v['missing']:
            content += '\nยังขาดวัตถุดิบ: ' + ', '.join(v['missing'])
    return dict(status='ok', kind=kind, answer=answer, content=content, recipes=views,
                selected_recipe_id=views[0]['recipe_id'] if len(views) == 1 else None)

class LiveRecipeAdapter:
    def __init__(self, retriever, client, model_name):
        self.retriever = retriever
        self.client = client
        self.model_name = model_name

    def answer_request(self, query, pantry, equipment, previous=(), selected_recipe_id=None):
        recipes = list(self.retriever.recipes.values())
        if unsupported_information(query):
            log_event('retrieval_rejected', reason='unsupported_information')
            return dict(status='insufficient_context', answer=NO_DATA, recipes=[], kind=question_kind(query))
        resolution = resolve_request(query, recipes, previous, selected_recipe_id)
        if resolution.get('status'):
            return resolution
        resolved = resolution['query']
        hits = candidates(self.retriever, resolved, set(pantry), set(equipment), resolution['previous'])
        if not hits:
            return dict(status='insufficient_context' if unsupported_information(query) else 'no_match',
                        answer=NO_DATA, recipes=[], kind=question_kind(query))
        selected = select_with_llm(self.client, self.model_name, resolved, hits)
        # No exceptions are swallowed or converted to NO_DATA here.
        return map_answer(resolved, selected, pantry, equipment)
