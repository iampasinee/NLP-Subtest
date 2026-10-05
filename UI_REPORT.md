# ผลปรับ UI — 5 ตุลาคม 2569

ปรับหน้า Streamlit เดิมเป็น “มีอะไร ทำอะไรดี” หลังอ่าน app.py/rag.py เดิม และ app.py, ui/styles.py, ui/components.py, services/adapter.py, INTEGRATION.md ของ ui-reference ไม่คัดลอก app.py ตัวอย่างทับระบบเดิม ตัวอย่างใช้ MockAdapter และตีความการไม่เลือกอุปกรณ์แบบ unrestricted จึงสร้าง LiveRecipeAdapter สำหรับระบบจริงแทน

## ไฟล์ที่แก้

- app.py: ส่วนหัว/เริ่มใหม่, expander ข้อมูลในครัว, ตัวอย่างสามใบ, ประวัติแชต/สถานะกำลังค้นหา, selected_recipe_id และการถามกลับ เก็บ cache index, fingerprint, logs, Secrets และ error branches เดิม
- presentation.py: mapping คำถามและผลจริงเป็น recommendation/method/fact, หลักฐานหัวข้อจริง, การถามต่อ/ถามกลับ, แยก no_match/insufficient_context และไม่จับ API/parsing error เป็นการไม่พบข้อมูล คำถามปริมาณไม่ทำให้แอปสมมติว่าผู้ใช้มีวัตถุดิบนั้น
- ui/styles.py, ui/components.py, ui/__init__.py: สีครีม/ขาว/ส้มอิฐ Sarabun + fallback, native Streamlit containers และ CSS สำหรับการ์ด/มือถือ, ไม่เกินสามเมนู, ปริมาณและขั้นตอนจริง, expander หลักฐาน/หมายเหตุ/แหล่งที่มา
- .streamlit/config.toml: สี theme โดยรักษา fileWatcherType="none" และไม่มีหัวข้อ TOML ซ้ำ
- tests/test_presentation.py, tests/test_rag.py: การกดตัวอย่าง การ์ด/อ้างอิง คำตอบสั้น การถามต่อและถามกลับ เริ่มใหม่ และคง regression เดิม (เปลี่ยนตัวทดสอบ reset ไปเรียกปุ่มในส่วนหัวด้วย key)
- pytest.ini: จำกัด discovery เฉพาะ tests ของระบบจริง ไม่รวม tests ของ reference mock app
- README.md, UI_REPORT.md: วิธีใช้/ทดสอบและข้อจำกัด
- .gitignore: ไฟล์ผลเรียกจริง/diagnostic logs เฉพาะเครื่อง

ไม่ได้แก้ rag.py, configuration.py, diagnostics.py, groq_support.py, data/recipes.md หรือ requirements.txt ไม่เปลี่ยน threshold/สูตร/cache algorithm ไม่เรียก fixtures หรือ MockAdapter ใน production ไม่ commit/push/deploy

## ผลทดสอบ

1. `python -m pytest -q`: **57 passed (25.78s)** รวม regression เดิม 47 ข้อและส่วน UI/mapping 10 ข้อ ชุด UI ใช้ API จำลองเพื่อทดสอบ interaction/errors อย่างคงที่ ไม่ใช่หลักฐาน end-to-end จริง
2. `python scripts/evaluate.py`: **semantic retrieval จริง 20/20 ผ่าน** ใช้ SentenceTransformer และ FAISS จริง คลังเดิม 20 สูตร/160 chunks ไม่มี LLM ในชุดนี้ ผล retrieval_results.json เหมือนเดิม
3. **เรียก Groq จริง** ด้วย local Streamlit Secrets โมเดล openai/gpt-oss-120b: smoke non-streaming มีข้อความตอบกลับ; AppTest หน้าแอปจริงกดตัวอย่างเลือกเมนูได้ R01/R05/R02, ตัวอย่างปริมาณได้ R04 และ “ไข่ไก่ 1 ฟอง” ตามเอกสาร; ถามต่อ “เมนูนี้ทำอย่างไร” ได้ขั้นตอน R04 ทุกคำตอบ status=ok และไม่มี AppTest exception หลักฐานรายละเอียดเก็บใน ui_live_results.local.json ที่ ignored ไม่มีคีย์ในผล/Logs
4. ทดสอบเพิ่มยืนยันคำถามปริมาณ “ใช้ไข่กี่ฟอง” รักษารายการในครัวเดิม และการถามต่อที่มีหลายเมนูต้องถามกลับก่อน เมื่อเลือกเมนูจึงประมวลผลคำถามเดิมต่อ
5. **ยังไม่ได้ตรวจภาพจริงบน desktop/mobile**: เครื่องมือ Browser ปฏิเสธ localhost เพราะ saved user permission ที่บล็อกไว้ ไม่พยายามเลี่ยงข้อจำกัด ตรวจเฉพาะโครงสร้าง/interaction ด้วย AppTest และ CSS/การ wrap ของ native columns จึงยังยืนยัน pixel layout หรือการโหลดฟอนต์จากเบราว์เซอร์จริงไม่ได้ ไม่มีภาพจำลองอ้างว่าเป็นภาพจริง

## รันและตรวจบนเครื่อง/Cloud

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/evaluate.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

เปิด URL ที่ terminal แสดง ตรวจ desktop และ viewport มือถือ: การ์ดตัวอย่าง/ชื่อไทย/ปุ่มไม่ล้น, เลือกตัวอย่างทั้งสาม, อุปกรณ์ว่างต้องแสดงว่ายังไม่ได้ระบุ, การ์ดเสนอไม่เกินสามเมนู, ปริมาณไม่แสดงสูตรเต็ม, แหล่งอ้างอิงและหลักฐานเปิดได้, เลือกเมนูแล้วถามต่อ, ถามกลับเมื่อกำกวม, เริ่มใหม่ล้างข้อมูลทั้งหมด

เมื่อผู้ใช้พร้อมนำขึ้น Cloud ให้อัปเดต branch ที่ Cloud ตั้งค่าไว้ให้มี app.py, presentation.py และ ui/ ใหม่ครบ คง requirements.txt เดิม ตั้ง GROQ_API_KEY และ GROQ_MODEL ใน Cloud Secrets เท่านั้น แล้ว reboot หากยังแสดงโค้ดเก่า ตรวจชื่อหน้าใหม่และ sidebar “สำหรับนักพัฒนา” เทียบ model/index กับ startup logs ทดสอบ Groq ตรงก่อนทดสอบสามตัวอย่างและการถามต่อ ตรวจ Cloud logs แยก API/parse/validation/retrieval และตรวจ viewport มือถือจริง งานรอบนี้ยังไม่ได้ทำขั้นตอนเผยแพร่
