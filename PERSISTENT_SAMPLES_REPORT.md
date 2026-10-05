# แชตชิด avatar และตัวอย่างคำถามถาวร — 5 ตุลาคม 2569

## สาเหตุและสิ่งที่แก้

โค้ดแชตเดิมกลับทิศ flex ของผู้ใช้ แต่ยังใช้ st.chat_message และ st.html แบบ width="stretch" จึงย่อเพียงฟองด้านในโดยไม่ย่อกลุ่ม avatar + ตัวครอบข้อความทั้งหมด ทำให้เหลือพื้นที่ระหว่างฟองและ avatar แก้ให้ native container จัดกลุ่ม user ชิดขวา ใช้ chat_message/html width="content" และ content flex ไม่ขยาย เติม max-width responsive ให้ทั้งกลุ่ม Gap 10px desktop / 8px mobile และ align-items:flex-start ไม่ใช้คอลัมน์กว้างแยก avatar หรือ space-between

ผู้ช่วยยังเป็นกลุ่ม avatar/เนื้อหาชิดซ้าย ย้าย effective constraints ไปใต้ฟองคำตอบพร้อม citations/evidence/cards ในกลุ่มเดียวกัน ลด padding แนวตั้งและใช้ wrapper gap=None ภาษาไทยในฟองชิดซ้าย มี overflow-wrap และ user text ผ่าน html.escape CSS จำกัดการจัด role ใน keyed chat containers ของ main

ตัวอย่างเดิมเรียก samples เฉพาะเมื่อ messages ว่าง จึงหายหลังคำถามแรก รักษาการ์ด welcome แบบเดิม แล้วเพิ่ม sidebar expander “คำถามตัวอย่าง” ที่สร้างทุก rerun ทั้งก่อน/หลังสนทนา แบ่ง “คำถามที่เอกสารตอบได้” และ “คำถามที่เอกสารไม่ได้ระบุ” ใช้ EXAMPLES/UNANSWERABLE_EXAMPLES เดิม ไม่สร้างสูตร/คำตอบใหม่

ปุ่ม/คำใบ้ “คำถามตัวอย่าง” ใกล้หัว main เปิด native expander ได้ หาก sidebar ถูกยุบ ต้องใช้ลูกศรมุมซ้ายบน มีคำแนะนำไทยชัดเจน ไม่มี DOM scripts หรือ frontend ใหม่ และไม่มี grid ซ้ำใต้คำตอบ

## การส่งคำถาม

submission.py เป็นคิวรับครั้งเดียว ใช้ UUID ต่อเหตุการณ์ ไม่ deduplicate ด้วยข้อความ callback ของ welcome, sidebar, chat input, ปุ่มค้นของที่มี และ clarification ใช้ enqueue เดียวกัน take จะ pop ก่อนเรียก pipeline จึงไม่ replay เมื่อ rerun ตั้ง request_processing ก่อน render รอบที่ทำงานเพื่อ disable ปุ่มตัวอย่าง/ช่องแชต/ปุ่มค้น/clarification ระหว่างทำงาน ปลด guard ใน finally ทั้งสำเร็จและ error หลังเสร็จกดข้อความเดิมได้อีกครั้ง

ทุกคำถามผ่าน plan_request → Retriever/FAISS → LiveRecipeAdapter/Groq/validation เดิม ใช้ Top-K ของรอบนั้น แล้ว append user/assistant ใหม่ ไม่มี production mock การปฏิเสธ unsupported facts ยังอาจไม่เรียก Groq ตามกฎเอกสารเดิม แต่เป็น turn ใหม่ผ่าน adapter จริง ไม่แสดงคำตอบ fixture

รักษาของในช่องกรอกและ evidence snapshots วัตถุดิบในตัวอย่างใหม่ไม่ union กับของเก่าโดยเงียบ ๆ คำว่าเพิ่ม/ถามต่อยังใช้กฎเดิม เปิด evidence ไม่ enqueue คำถามหรือค้นใหม่ ไม่แก้ recipes.md, rag.py, presentation.py, request_state.py, requirements, cache, citations หรือ error branches

## ผลตรวจจริง

- ชุดรวม pytest: **75 passed** (72 เดิม + 3 focused tests ใหม่) ทดสอบ sidebar ก่อน/หลังสนทนา, welcome grid เฉพาะเริ่มต้น, คลิกซ้ำข้อความเดิมได้สอง turn, exactly one API request ต่อคลิก, rerun ไม่ replay, K 3→5, ไม่ใช้ของเก่าปะปน, snapshot เดิมคงที่, เปิดหลักฐานไม่เพิ่ม semantic search/API calls และ submission widgets disabled ระหว่าง create / enabled หลังเสร็จ
- Tests ใช้ sentence embeddings จริงและ API จำลองเฉพาะเพื่อทดสอบ interaction/counters/errors อย่างแน่นอน ไม่อ้างว่าเป็น end-to-end จริง
- เรียก Groq จริงผ่าน AppTest และ Secrets แบบ bounded: sidebar ตัวอย่างเดียวกัน “ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง” สองครั้ง K=3 และ K=5 ได้ R04/status=ok ทั้งสองรอบ count chunks 3/5, messages 2→4, network API ใหม่ **1 ครั้งต่อคลิก** ไม่มี exceptions/API errors รอบนี้ เปิด evidence เก่าเพิ่ม API **0 ครั้ง** และ K snapshot แรกยังเป็น 3 ผล ui_live_results.local.json / logs เป็น ignored ไม่เผยคีย์
- Tests render ข้อความไทยสั้น/ยาวของ user/assistant และตรวจ escaping เดิมผ่าน ยังไม่ยืนยัน pixel layout จาก AppTest
- **Visual verification desktop/mobile ยัง pending** เพราะ saved browser permission บล็อก localhost ไม่เลี่ยงสิทธิ์และไม่อ้างว่าภาพผ่าน ยังต้องตรวจว่าฟองและ avatar ชิดกันจริง การ wrap/overflow และ input ไม่ทับ action ใน browser

## ไฟล์และตรวจ Cloud

แก้ app.py, ui/components.py, ui/styles.py, README.md เพิ่ม submission.py, tests/test_persistent_samples.py และรายงานนี้ ยังไม่ commit/push/deploy

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

หลังอัปเดต branch ที่ Cloud ใช้ ให้ตรวจ:

1. welcome cards ยังอยู่ก่อนแชต; sidebar “คำถามตัวอย่าง” ยังอยู่หลังตอบ และปุ่มใกล้หัวเปิดส่วนนี้ได้ เปิด sidebar ด้วยลูกศรถ้าปิดอยู่
2. กดตัวอย่างเดิมซ้ำเมื่อคำตอบจบ ตรวจประวัติเพิ่มสองข้อความต่อคลิกและ Groq request เพียงครั้งเดียวต่อคลิก เปลี่ยน K แล้วกดอีกครั้ง ตรวจหลักฐานใหม่และเก่า
3. เปิดหลักฐานเก่า ตรวจ logs ไม่มี retrieval/API เพิ่ม และตรวจของในช่องกรอกไม่ถูกเขียนทับ ตัวอย่างใหม่ไม่ค้นจากวัตถุดิบเก่าที่ไม่เกี่ยวข้อง
4. ตรวจไทยสั้น/ยาวบน desktop และมือถือ 360–390px: user bubble + avatar เป็นกลุ่มชิดขวา gap 8–10px, assistant ซ้าย avatar ตรงบนฟอง ข้อความชิดซ้าย ไม่มี horizontal overflow และไม่มี grid แทรกหลังคำตอบ
