"""Request-local ingredients; saved form values are never mutated by chat."""
import re
from rag import extract_names, ALIASES, update_pantry

def plan_request(query, saved, current, recipes):
    names = {i['name'] for r in recipes for i in r['ingredients']}
    explicit_recipe = any(r['name'] in query for r in recipes)
    reference = any(w in query for w in ['เมนูนี้', 'สูตรนี้', 'เมนูเดิม', 'อันนี้']) or re.search(r'(?:เมนู|สูตร)(?:ที่)?\s*(หนึ่ง|สอง|สาม|[123])', query)
    from presentation import question_kind
    if not explicit_recipe and not reference and question_kind(query) == 'method':
        subject = query
        for word in ['ทำอย่างไร', 'ทำยังไง', 'วิธีทำ', 'ขั้นตอน', 'ขอ', 'ครับ', 'ค่ะ']:
            subject = subject.replace(word, '')
        if subject.strip() and not extract_names(subject, names):
            return dict(intent='new_search', pantry=set(), unknown=[subject.strip()])
    if explicit_recipe and question_kind(query) != 'fact' and re.search(r'\sมี\s*', query):
        return dict(intent='recipe_with_inventory', pantry=update_pantry(query, saved, names, recipes), unknown=[])
    if explicit_recipe or reference or question_kind(query) in ['method', 'fact']:
        return dict(intent='followup', pantry=set(saved or current), unknown=[])
    addition = 'เพิ่ม' in query or 'รวมกับของเดิม' in query
    generic = query.strip() in ['ทำอะไรได้บ้าง', 'มีอะไรทำอะไรดี', 'ค้นเมนูจากของที่มี']
    if generic:
        return dict(intent='saved_search', pantry=set(saved), unknown=[])
    requested = extract_names(query, names)
    # Only strip conversational wrappers, never silently discard unknown food names.
    text = query
    for w in ['ทำอะไรได้บ้าง', 'ทำอะไรดี', 'มีอะไรทำได้บ้าง', 'เพิ่ม', 'รวมกับของเดิม', 'ฉันมี', 'มี', 'และ', 'กับ', 'ช่วยเลือกเมนู', 'จาก']:
        text = text.replace(w, ' ')
    unknown = []
    for part in re.split(r'[,;\n\s]+', text):
        if not part or part in ['ครับ', 'ค่ะ', 'บ้าง']:
            continue
        remainder = part
        aliases = [a for n in names for a in ALIASES.get(n, [n])]
        for alias in sorted(aliases, key=len, reverse=True):
            remainder = remainder.replace(alias, '')
        remainder = re.sub(r'[0-9./]+|ฟอง|ถ้วย|ต้น|ช้อนโต๊ะ|ช้อนชา|กรัม|ไม่', '', remainder)
        if remainder:
            unknown.append(remainder)
    return dict(intent='addition' if addition else 'new_search',
                pantry=(set(saved or current) | requested) if addition else requested, unknown=unknown)
