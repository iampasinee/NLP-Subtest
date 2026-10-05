from html import escape
import streamlit as st
from presentation import EXAMPLES, UNANSWERABLE_EXAMPLES

def samples():
    selected = None
    groups = st.tabs(['ลองถามจากข้อมูลในคลังสูตร', 'ลองถามสิ่งที่เอกสารไม่ได้ระบุ'])
    for group, examples, prefix in zip(groups, [EXAMPLES, UNANSWERABLE_EXAMPLES], ['sample', 'unsupported']):
        with group:
            columns = st.columns(2, gap='small')
            for n, (icon, title, query) in enumerate(examples):
                with columns[n % 2]:
                    with st.container(key=f'sample_card_{prefix}_{n}'):
                        st.caption(f'{icon} {title}')
                        if st.button(query, key=f'{prefix}_{n}', width='stretch', wrap=True):
                            selected = query
    return selected

def retrieval_evidence(response):
    trace = response.get('retrieval')
    if trace is None:
        return
    with st.expander('ดูหลักฐานการค้นคืน'):
        chunks = trace['retrieved_chunks']
        st.caption(f"Top-K ที่ใช้: {trace['top_k']} • chunks ที่คัดเลือกจริง: {len(chunks)}")
        st.caption('คะแนนเป็นความคล้าย ไม่ใช่เปอร์เซ็นต์ความมั่นใจ')
        for item in chunks:
            c = item['chunk']
            st.caption(f"{c['chunk_id']} • {c['recipe_id']} • {c['name']} • {c['section']} • {item['score']:.3f}")
            st.text(c['text'])
        with st.expander('หัวข้อสูตรเพิ่มเติมเพื่อเติมบริบท (ไม่นับใน Top-K)'):
            for part in trace['additional_sections']:
                st.caption(f"{part['recipe_id']} • {part['name']} • {part['section']}")
                st.text(part['text'])

def notes(view):
    r = view['recipe']
    with st.expander('หมายเหตุและแหล่งที่มา'):
        st.write(r['notes'])
        st.write(r['source'])

def evidence(view):
    with st.expander(f"ดูหลักฐาน • {view['name']}"):
        st.caption(view['citation'])
        for part in view['evidence']:
            st.markdown(f"**{part['section']}**")
            st.text(part['text'])
        with st.expander('ข้อความที่ค้นพบและคะแนนความคล้าย'):
            st.text(view['retrieval_evidence'])
            st.caption(f"คะแนนความคล้าย {view['score']:.3f} ไม่ใช่เปอร์เซ็นต์ความมั่นใจ")

def full_recipe(view):
    r = view['recipe']
    st.caption(f"สูตรสำหรับ {r['servings']} เสิร์ฟ • อุปกรณ์: {', '.join(r['equipment']) or 'ไม่ระบุ'}")
    st.markdown('**วัตถุดิบและเครื่องปรุงตามสูตร**')
    for i in r['ingredients']:
        st.markdown(f"- **{i['name']}**: {i['quantity']}")
    st.markdown('**ขั้นตอน**')
    for n, step in enumerate(r['steps'], 1):
        st.markdown(f'{n}. {step}')

def recipe_card(view, message_id, number, kind, on_select):
    r = view['recipe']
    with st.container(key=f"recipe_card_{message_id}_{r['recipe_id']}"):
        st.html(f'<p class="card-title">{number}. {escape(r["name"])}</p>')
        label = f'ยังขาด {len(view["missing"])} รายการ' if view['missing'] else 'วัตถุดิบครบตามรายชื่อในสูตร'
        css = '' if view['missing'] else ' complete'
        st.html(f'<span class="badge{css}">{label}</span>')
        st.caption(view['citation'])
        if kind == 'recommendation':
            a, b = st.columns(2, gap='small')
            for col, cls, label, values in [(a, 'matched', 'วัตถุดิบที่ตรง', view['matched']),
                                          (b, 'missing', 'ยังขาด รวมเครื่องปรุง', view['missing'])]:
                with col:
                    text = ', '.join(values) if values else ('ยังไม่ได้ระบุ' if cls == 'matched' else 'ไม่ขาดตามรายชื่อ')
                    st.html(f'<div class="ingredient-panel {cls}"><p><strong>{label}</strong></p><p>{escape(text)}</p></div>')
            st.markdown('**อุปกรณ์ที่ต้องใช้:** ' + (', '.join(view['equipment']) or 'สูตรไม่ได้ระบุ'))
            st.caption(view['equipment_status'])
        else:
            if view['missing']:
                st.caption('ยังขาดวัตถุดิบ: ' + ', '.join(view['missing']))
            st.caption(view['equipment_status'])
        st.html('<div class="quantity-note">ตรวจเฉพาะชื่อวัตถุดิบ ยังไม่ยืนยันว่าปริมาณที่มีเพียงพอ</div>')
        if kind == 'method':
            full_recipe(view)
        else:
            with st.expander('ดูสูตรเต็ม'):
                full_recipe(view)
        if st.button('ถามต่อเกี่ยวกับเมนูนี้', key=f"select_{message_id}_{r['recipe_id']}", icon=':material/chat:', width='stretch'):
            on_select(r['recipe_id'])
            st.rerun()
        evidence(view)
        notes(view)

def answer_message(message, on_select, on_clarify):
    response = message.get('response')
    if not response:
        st.markdown(message['content'])
        return
    effective = response.get('effective', message.get('request', {}))
    if effective:
        st.caption('วัตถุดิบที่ใช้ค้น: ' + (', '.join(effective.get('ingredients', [])) or 'ยังไม่ได้ระบุ') + ' • อุปกรณ์: ' + (', '.join(effective.get('equipment', [])) or 'ยังไม่ได้ระบุ / ไม่กรอง'))
    retrieval_evidence(response)
    status = response['status']
    if status == 'error':
        st.error(response['answer'])
    elif status == 'no_match':
        st.warning(response['answer'])
    elif status == 'insufficient_context':
        st.info(response['answer'])
        st.caption('เอกสารไม่มีข้อมูลรองรับข้อที่ถาม หรือข้อมูลคำถามยังไม่ชัดเจน')
    else:
        st.markdown(response['answer'])
    if status == 'needs_clarification':
        for option in response.get('options', []):
            if st.button(option['name'], key=f"clarify_{message['id']}_{option['recipe_id']}"):
                on_clarify(option['recipe_id'], message['query'])
                st.rerun()
    elif status == 'insufficient_context':
        for view in response.get('recipes', []):
            st.caption(view['citation'])
            evidence(view)
            notes(view)
    elif status == 'ok':
        views = response.get('recipes', [])
        if response['kind'] == 'fact':
            for view in views:
                st.caption(view['citation'])
                if 'อุปกรณ์' in message['query']:
                    st.caption('อุปกรณ์ข้างต้นเป็นข้อกำหนดของสูตร ไม่ใช่การยืนยันว่าผู้ใช้มีครบ')
                evidence(view)
                notes(view)
        else:
            for n, view in enumerate(views[:3], 1):
                recipe_card(view, message['id'], n, response['kind'], on_select)
