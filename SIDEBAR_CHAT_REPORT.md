# ผลปรับ sidebar และการจัดแชต — 5 ตุลาคม 2569

หน้า main เน้นบทสนทนาเดียวเรียงตามเวลาและการ์ดสูตร ย้ายช่องวัตถุดิบ/เครื่องปรุง/อุปกรณ์, Top-K และรายละเอียดหลักฐานไป native st.sidebar แบ่งสามแท็บ “ของที่มี”, “ตั้งค่า Top-K”, “หลักฐานและแหล่งที่มา” ส่วน developer diagnostics ยังคงเป็น expander ปิดอยู่ ตัวอย่างตอบได้/ไม่ได้อยู่เฉพาะหน้าเริ่มต้น ไม่แทรกระหว่างบทสนทนา

ข้อความผู้ใช้เป็นฟอง charcoal #292524 ตัวอักษรขาว ข้อความและ avatar อยู่ขวา ผู้ช่วยเป็นฟองขาว ตัวอักษรเข้ม ขอบบาง พร้อม avatar ซ้าย ทุกฟองจัดข้อความไทยชิดซ้ายและห่อคำยาว มี max-width/min-width และ mobile padding การ์ด/อ้างอิง/ปุ่มหลักฐานอยู่ใต้คำตอบผู้ช่วยในฝั่งเดียวกัน ใช้ st.chat_message และ keyed role containers ของ Streamlit 1.65.0 CSS เฉพาะ role ถูกจำกัดใน main ไม่เปลี่ยน controls ของ sidebar ข้อความผู้ใช้ผ่าน html.escape ก่อน st.html ไม่ใช้ unsafe HTML ของผู้ใช้

## หลักฐานและสถานะ

- “ดูหลักฐาน” เลือกคำตอบนั้น “ดูหลักฐานของสูตรนี้” เลือกคำตอบและกรอง recipe_id ใน sidebar โดยไม่เปลี่ยน selected_recipe_id ที่ใช้ถามต่อ
- เลือกคำตอบก่อนหน้าได้จาก dropdown ใน panel และเลือกเฉพาะสูตรได้ แสดง K/count/chunk_id/recipe_id/ชื่อ/หัวข้อ/score/ข้อความจริง พร้อม context ที่เติมแยกจาก chunks และ source notes จาก snapshot ไม่มี URL/page number ที่แต่งขึ้น
- หลักฐานยังเป็น snapshot ของคำตอบเดิม เมื่อเปลี่ยน K หรือถามใหม่ไม่แก้ข้อมูลย้อนหลัง ค่า K ของคำตอบทั้งหมดแสดงแยกจากจำนวน chunks หลังกรองเฉพาะสูตร
- ID ของ turn ใหม่เป็น UUID; session เก่าที่ไม่มี ID ได้ ID ครั้งเดียวเพื่อให้ widget keys คงที่และไม่ซ้ำ
- ปุ่ม evidence เป็น callback ที่เปลี่ยนเฉพาะ selection + native tab state ไม่มี query/retrieval/API call ประวัติ ของในครัว และการเลือกเมนูยังอยู่ เริ่มใหม่ล้างสิ่งเหล่านี้และ evidence selection แต่คง K
- รุ่นติดตั้งรองรับการเลือก native tab ผ่าน key/on_change จึงสลับแท็บหลักฐานได้ แต่ไม่มี public API เปิด sidebar ที่ถูกยุบโดยอัตโนมัติ หากแผงปิดอยู่ ผู้ใช้เปิดด้วยลูกศรมุมซ้ายบน มีข้อความบอกวิธีเปิด ไม่ใช้ DOM scripts
- chat input ใช้ key เดิมคงที่ `chat_query` และ native pinned input ไม่อ่านหรือเขียน draft ที่ยังไม่ submit ต้องตรวจ draft/cursor จริงบน browser เพราะ AppTest จำลองข้อความที่ยังไม่ submit ไม่ได้

## ผลตรวจ

- Regression tests: **72 passed** รวม tests เดิม 67 ข้อ และตรวจ HTML escaping, ไทยสั้น/ยาวทั้งสอง role ใน stream ตามเวลา, widget อยู่ sidebar, การเลือกหลักฐานข้ามรอบ/เฉพาะสูตร, K snapshots, ไม่มี API เพิ่มจาก evidence clicks และ reset ที่คง K ผ่าน Streamlit AppTest ชุด API จำลองใช้เฉพาะ tests
- เรียก Groq จริงจาก local Secrets ผ่าน AppTest หน้าใหม่หนึ่งคำถาม (ตัวอย่างปริมาณไข่ตุ๋น): status=ok, R04, ไม่มี exception/error จำนวน API calls ก่อนและหลังคลิก “ดูหลักฐาน” เท่ากับ **1 → 1** เลือก turn และสลับ native evidence tab ถูกต้อง ไม่ใช่คำตอบ mock ผลเฉพาะเครื่อง ui_live_results.local.json / ui_live_logs.local.txt เป็น ignored
- ไม่มีการเปลี่ยน recipes.md, requirements.txt, rag.py, presentation.py, request_state.py, threshold, prompt, cache หรือ logs ของ pipeline ในรอบนี้ ยังใช้ Sentence Embedding/FAISS/Groq จริง และ tests วัตถุดิบใหม่/เพิ่ม/มาม่า/follow-up/API/parse เดิมผ่าน
- **ยังไม่ได้ตรวจภาพ desktop/mobile จริง**: browser saved permission บล็อก localhost จึงไม่ใช้วิธีเลี่ยงข้อจำกัด การ render ด้วย AppTest ยืนยันโครงสร้างและพฤติกรรม แต่ไม่ยืนยัน pixel alignment, overflow, sidebar animation, สีที่ render หรือ draft ของช่องแชต ไม่มีภาพจำลองอ้างเป็นภาพจริง
- ไม่มี screenshot ที่เปิดตรวจได้ในไฟล์แนบคำขอรอบนี้ ใช้ข้อกำหนดซ้าย/ขวาและ reference source ที่มีอยู่ ไม่อ้างว่าเปรียบเทียบภาพแบบ pixel ต่อ pixel

## ไฟล์และวิธีตรวจ

แก้ app.py, ui/components.py, ui/styles.py, tests/test_presentation.py, README.md และเพิ่ม tests/test_sidebar_chat.py กับรายงานนี้ ไม่ commit/push/deploy

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

ตรวจ Cloud หลังอัปเดตโค้ดของ branch/entrypoint เดิมและรักษา Secrets:

1. เปิด/ปิด sidebar ด้วยลูกศร ตรวจแท็บทั้งสามและ developer expander พิมพ์ของใน sidebar แล้วค้น และถามวัตถุดิบใหม่ในแชตเพื่อยืนยัน state ไม่ปะปน
2. ทดสอบข้อความไทยสั้นและยาวทั้งสองฝั่ง ตรวจ user/avatar ขวา assistant/avatar ซ้าย ตัวอักษรในฟองชิดซ้าย การ์ดใต้คำตอบ ไม่มีขอบหรือปุ่มล้น ทั้ง desktop และมือถือ 360–390px
3. สร้างคำตอบ K=3 แล้ว K=5 คลิก evidence ของทั้งสองคำตอบ ตรวจ K ของแต่ละรอบไม่เปลี่ยน กรองสูตรและตรวจข้อความ/แหล่งที่มา เฝ้า logs ให้ไม่มี retrieval/Groq request เพิ่มจากการดูหลักฐาน
4. พิมพ์ draft ที่ยังไม่ส่งแล้วคลิก evidence ตรวจ draft/cursor ตาม native widget behavior ตรวจการเลื่อนถึงข้อความสุดท้ายไม่ถูก chat input ทับ แล้วเริ่มใหม่ตรวจล้าง pantry/history/selected recipe/evidence แต่ K คงเดิม
