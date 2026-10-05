# รายงานแก้สถานะและ Top-K — 5 ตุลาคม 2569

## สาเหตุและหลักฐานก่อนแก้

ทำซ้ำด้วยโค้ดเดิม: update_pantry ของคำถาม “มีไข่ ข้าวสวย และต้นหอม ทำอะไรได้บ้าง” ได้ `{ไข่ไก่, ข้าวสวย, ต้นหอม}` แล้ว update_pantry ของ “มาม่า ทำอะไรได้บ้าง” ยังคงได้ชุดเดิม เพราะเป็นการ union กับของเก่าและ parser ไม่รู้จักมาม่า หน้า app.py ยังนำค่าที่อ่านจากแชตไปเขียนทับ form_ingredients/form_seasonings ทำให้ของเก่าติดอยู่ในช่องกรอกด้วย

ตรวจทั้งรายการวัตถุดิบและเนื้อหาคลัง: ไม่มี “มาม่า”, “บะหมี่” หรือ “บะหมี่กึ่งสำเร็จรูป” จึงไม่มีสูตรรองรับวัตถุดิบนี้ ไม่เพิ่ม alias หรือสูตรเพื่อให้ผ่าน ข้อมูลเก่าไหลจาก form/session ไปถึง query embeddings และ overlap filter → prompt มีสูตรจากวัตถุดิบเก่า → Groq เลือก ID ที่ valid แต่ไม่ตรงวัตถุดิบใหม่ → renderer แสดง matched จากชุดเก่า การตรวจ IDs เพียงอย่างเดียวไม่แก้ปัญหาความหมายนี้

ไม่พบ cache คำตอบในแอป: มีเฉพาะ embedding/index cache ซึ่ง fingerprint ตามเอกสาร/โมเดล/implementation ไม่ใช่สาเหตุคำตอบเก่า selected_recipe_id ไม่ได้ใช้เลือกเมนูในคำถามมาม่าที่เป็น recommendation แต่ต้องล้างเมื่อเริ่มค้นใหม่เพื่อป้องกันการถามต่ออ้างเมนูเก่า

ก่อนแก้ Retriever.search ค้น 60 chunks แล้ว deduplicate เป็น recipe hits และส่งสามสูตร ยังไม่มี Top-K ของ context chunks ที่ผู้ใช้ควบคุมได้

## ความหมายของสถานะปัจจุบัน

- ช่องกรอกเป็นของที่บันทึกไว้ จนผู้ใช้แก้/ลบ/เริ่มใหม่ แชตไม่เขียนทับช่องกรอก
- รายการวัตถุดิบในคำถามใหม่เป็นชุดค้นใหม่ เช่น “ไข่ไก่, ต้นหอม” ไม่รวมข้าวจากช่องกรอกโดยเงียบ ๆ พร้อมล้าง selected_recipe_id/previous เมื่อเปลี่ยนการค้น
- “มีไข่เพิ่ม” รวมกับของในช่องกรอก ถ้าช่องกรอกว่างจะรวมกับบริบทวัตถุดิบล่าสุด ปุ่มค้นจากของที่มีใช้เฉพาะช่องกรอก
- ถามต่อ “เมนูนี้ใช้ไข่กี่ฟอง” รักษาเมนูและบริบทล่าสุด ไม่ตีความคำว่าไข่ว่าผู้ใช้มีไข่เพิ่ม หากแก้ช่องกรอกแล้วถามต่อให้ใช้รายการที่แก้ หากมีหลายเมนูและยังไม่เลือก ระบบถามกลับ
- วัตถุดิบที่อ่านไม่ได้/ไม่มีสูตร เช่นมาม่า (รวมเมื่อกรอกในช่องวัตถุดิบแล้วกดค้น) แจ้งไม่มีสูตรรองรับและไม่ใช้ของเดิมแทน ไม่แสดงทางเลือกที่ไม่เกี่ยวข้องเป็น matches
- แต่ละคำตอบแสดงวัตถุดิบและอุปกรณ์ที่ใช้จริง matched/missing คำนวณจากชุดนั้นและ canonical ingredients รวมเครื่องปรุง ไม่ให้ LLM แต่งรายการ ไม่เลือกอุปกรณ์ = ไม่ทราบ/ไม่กรอง ความครบตามชื่อไม่เท่ากับปริมาณเพียงพอ
- เริ่มใหม่ล้างประวัติ ของในครัว เมนู และผลเดิม แต่คง Top-K

## Top-K และ Prompt จริง

1. FAISS ค้นกลุ่มกว้าง 60 chunks เพื่อไม่ลดคุณภาพจากการตัด K ก่อนตรวจเงื่อนไข
2. กรองตาม recipe reference, threshold เดิม 0.28, ingredient overlap และอุปกรณ์ จัดอันดับสูตรตามสิ่งที่ขาด/score เช่นเดิม
3. เลือก chunks แบบกระจายสูตร: chunk ที่ score ดีที่สุดของแต่ละสูตรตามอันดับก่อน แล้วเติม chunks ที่เหลือ ค่า K 1–10 default 3 จึงควบคุม context seeds จริง ไม่ใช่ตัดเฉพาะ evidence บนหน้าจอ หาก eligible chunks ไม่พอ จำนวนจริงต่ำกว่า K
4. ชุด chunks เหล่านั้นถูกส่งใน retrieved_chunks ของ build_rag_messages ที่ select_with_llm เรียกจริง เมนูที่แสดงไม่เกินสามเมนูและมาจาก recipe IDs ที่ seeds รองรับ K สูงอาจมี seeds ของสูตรอื่นเพิ่มด้วย ไม่เพิ่มจำนวนการ์ดเกินสาม
5. Context ยังเติมสูตรเต็มของเมนูที่เกี่ยวข้องเพื่อให้ได้ปริมาณ/ขั้นตอนครบ แสดงหัวข้อเติมบริบทแยกจาก K ไม่อ้างว่าบริบททั้งหมดมีเพียง K chunks
6. ประวัติเก็บ trace ของแต่ละคำตอบ: K, count, chunk_id, recipe_id, name, section, score และ text พร้อมหัวข้อเพิ่มเติม เปลี่ยน K ไม่แก้ trace เดิม ไม่มี response cache จึงใช้ K ใหม่ทันที Index ไม่ขึ้นกับ K; fingerprint มี implementation และเพิ่ม pipeline version เป็น v3-topk ให้ rebuild เมื่อเปลี่ยน retrieval/chunk metadata

Prompt มีคำถามจริง วัตถุดิบจริง chunks จริง และ Context จากสูตรต้นฉบับ กฎห้ามแต่งปริมาณ เวลา ราคา โภชนาการ วัตถุดิบ อุปกรณ์/ทดแทน ถือ recipe text เป็นข้อมูล และ validate recipe_ids/citations ต่อไป ใช้ Groq openai/gpt-oss-120b จริง ไม่ใช้ fixtures/MockAdapter ตัวคำตอบสั้นและส่วนประกอบสูตรอ่านจากเอกสารตามระบบเดิม ไม่สร้างตัวเลขใหม่

คำถาม unsupported facts อาจค้นพบข้อความเกี่ยวข้องแต่เอกสารไม่มีฟิลด์นั้น จึงแสดง insufficient_context ส่วนสูตร/วัตถุดิบที่ไม่รองรับเป็น no_match API, parsing, validation และ empty selection errors ยังเป็น error แยกกัน พร้อมหลักฐานการค้นที่เกิดก่อน error โดยไม่ log key/header/secrets

## ตัวอย่างและข้อมูลรองรับ

| คำถาม | ผลที่คาดหวัง | หลักฐาน |
| --- | --- | --- |
| มีไข่ ข้าวสวย และต้นหอม ทำอะไรได้บ้าง | เมนูตรง เช่น R01/R05/R02 พร้อมส่วนที่ยังขาด | วัตถุดิบ/เครื่องปรุงของสูตรจริง |
| ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง | ไข่ไก่ 1 ฟอง สำหรับ 1 เสิร์ฟ | R04 วัตถุดิบ/จำนวนเสิร์ฟ |
| ข้าวผัดไข่ทำอย่างไร | ส่วนผสมพร้อมปริมาณและขั้นตอน | R01 วัตถุดิบ/เครื่องปรุง/ขั้นตอน |
| ไข่ตุ๋นไมโครเวฟใช้อุปกรณ์อะไร | ไมโครเวฟ ถ้วยทนไมโครเวฟ ช้อน มีด | R04 อุปกรณ์ |
| ข้าวผัดไข่มีกี่แคลอรี | ปฏิเสธข้อเท็จจริง | ทั้งคลังไม่มีข้อมูลแคลอรี่ |
| ไข่ตุ๋นไมโครเวฟราคาเท่าไร | ปฏิเสธข้อเท็จจริง | ทั้งคลังไม่มีราคา/ต้นทุน |
| ขอสูตรพิซซ่าไข่ | ไม่มีสูตรรองรับ | ทั้งคลังไม่มีพิซซ่า |
| มาม่า ทำอะไรได้บ้าง | ไม่มีสูตรที่ใช้วัตถุดิบนี้ ไม่ย้อนใช้ของเดิม | ไม่มีมาม่าหรือบะหมี่กึ่งสำเร็จรูป |

เพิ่ม S01–S08 ใน test_questions.csv พร้อม expected IDs/answer/refusal และ supporting_sections โดยรักษา T01–T20 เดิม ตัวอย่างใน UI แยกสอง tabs (ตอบได้ 4 / ไม่ได้ 3) และกดเข้าระบบจริง หลังมีบทสนทนาเปิดจาก expander ได้

## ผลตรวจจริงและข้อจำกัด

- pytest: **67 passed (33.83s)** รวม regression เดิม error sanitization และ tests สถานะ/Top-K 1,3,5/context payload/evidence ข้ามรอบ/reset/sample corpus ข้อ UI ใช้ AppTest และ API จำลองเพื่อทดสอบ interaction/errors จึงไม่ถือเป็น live end-to-end
- scripts/evaluate.py: **semantic retrieval จริง 28/28 ผ่าน** ใช้ embeddings/FAISS จริงและ Top-K 3 รวม 20 ข้อเดิม+8 ข้อใหม่ ดู retrieval_results.json ไม่มี LLM ในชุดนี้
- Live Groq แบบ bounded ใช้ Secrets จริง max_retries=0: smoke ตอบข้อความไม่ว่าง; คำถามวัตถุดิบ K=3 ค้นคืน 3 chunks/เลือก R01,R05,R02; ปริมาณ R04 K=1 ค้นคืน 1 chunk/ตอบไข่ไก่ 1 ฟอง ทั้งสอง status=ok ไม่มี 429 รอบนี้ กรณีมาม่าได้ no_match/0 สูตรก่อน API ผลละเอียด state_topk_live.local.json และ logs เฉพาะเครื่องเป็น ignored ไม่บันทึกคีย์
- recipes.md และ requirements.txt ไม่เปลี่ยน ยังคง 20 สูตร/160 chunks พร้อม chunk_id Corpus digest regression ผ่าน
- Notebook เพิ่ม “ขั้นตอน 4: เขียน RAG Prompt Template” ใช้ build_rag_messages ของแอป ตรวจ JSON และ Python syntax ของ cell ใหม่แล้ว ไม่ execute Notebook ทั้งเล่มเพราะต้องตั้ง repository/Colab Secrets ไม่มี output ที่แต่งขึ้น
- ยังไม่ได้ตรวจภาพ desktop/mobile จริง: saved browser permission บล็อก localhost จึงไม่ใช้ทางเลี่ยง ตรวจ AppTest และโค้ด CSS เท่านั้น ปรับ header padding, bottom clearance, button wrapping และการ์ดสองคอลัมน์ responsive แต่ยังยืนยัน pixel layout/ฟอนต์จากเบราว์เซอร์ไม่ได้
- Parser เป็นกฎภาษาไทย มีข้อจำกัดกับคำสะกด/ถ้อยคำซับซ้อน ควรแยกรายการวัตถุดิบชัดเจน ไม่มีการอ้างว่าครอบคลุมภาษาไทยทั่วไปหรือสูตรนอกคลัง

## ไฟล์ที่เปลี่ยนและตรวจ Cloud

app.py, request_state.py, presentation.py, rag.py, diagnostics.py, ui/components.py, ui/styles.py, tests/test_state_topk.py, tests/test_presentation.py, tests/test_groq_regressions.py, scripts/evaluate.py, test_questions.csv, retrieval_results.json, submission.ipynb, README.md, TEST_REPORT.md, UI_REPORT.md, STATE_TOPK_REPORT.md และ .gitignore

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/evaluate.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

ยังไม่ได้ commit/push/deploy เมื่อผู้ใช้พร้อมอัปเดต Cloud ให้ส่งไฟล์ทั้งหมดที่เกี่ยวข้องไป branch ที่ Cloud ตั้งค่าไว้ ตรวจ entrypoint app.py และ Secrets (GROQ_MODEL=openai/gpt-oss-120b) โดยไม่ส่ง secrets.toml ขึ้น Git รีบูตเมื่อจำเป็น ตรวจหน้า “ตั้งค่าการค้นหา”, tabs ตัวอย่าง และ developer version v3-topk/index hash ให้ตรง logs จากโค้ดล่าสุด

ทดสอบ Cloud ตามลำดับ: smoke โดยตรง → ไข่/ข้าว/ต้นหอม → มาม่า (ต้องไม่แสดงสูตรเก่า) → “มีไข่เพิ่ม” → เลือกเมนู/ถามปริมาณ → K=1/3/5 และเปิด evidence ตรวจ count/text/context เพิ่มเติม → เปลี่ยน K ตรวจหลักฐานเก่าไม่เปลี่ยน → เริ่มใหม่ตรวจล้างของและคง K → ตัวอย่างปฏิเสธทั้งสาม → desktop/mobile ตรวจหัว/ปุ่ม/แชตไม่ทับเนื้อหา ถ้า HTTP429 ให้หยุดและรอตาม quota ไม่รีบูตหรือกดซ้ำเป็น retry storm
