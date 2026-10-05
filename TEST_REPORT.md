# ผลทดสอบจริง — 5 ตุลาคม 2569

สภาพแวดล้อม: Windows, Python 3.12, Streamlit 1.65.0, sentence-transformers 6.1.0, FAISS CPU 1.15.1, Groq SDK 1.7.0, NumPy 2.5.3 ใช้โมเดล multilingual MiniLM จริงบน CPU ไม่มี Groq API Key สำหรับการทดสอบจริง

| รายการ | ผลที่รันจริง |
|---|---|
| ตรวจคลัง JSON/schema | ผ่าน: 20 ไฟล์ 20 สูตร 19,506 ตัวอักษรเนื้อหา |
| Embedding model | 384 dimensions, max_seq_length 128 tokens |
| Structure-based chunks | 100 chunks, ยาวที่สุด 113 tokens รวม prefix/special tokens |
| pytest | 19 tests ผ่าน รวม AppTest และ Groq client จำลอง |
| คำถามใน CSV / Semantic Retrieval จริง | 20/20 ผ่าน ดู `retrieval_results.json` |
| Dependencies | `pip check`: No broken requirements found |
| เว็บ Streamlit ในเครื่อง | รันได้ที่ localhost:8501, health check HTTP 200 / ok |
| Groq จริง | **ยังไม่ได้ทดสอบ — ไม่มี API Key** |
| Hosting บน Community Cloud | **ยังไม่ได้ Deploy** |
| ภาพหน้าเว็บ desktop/mobile | **ยังไม่ได้ตรวจด้วย browser จริง** เครื่องมือ Browser Use ปฏิเสธสิทธิ์เปิด localhost |

pytest ครอบคลุมการโหลดข้อมูลผิดโครงสร้าง/recipe_id ซ้ำ, fingerprint เปลี่ยนเมื่อเนื้อหาเปลี่ยน, token budget และการแบ่งข้อความยาวโดยไม่สูญหาย, FAISS เวกเตอร์ normalized, semantic paraphrase, top_k เกินจำนวน chunks, คลังว่าง, alias/การปฏิเสธวัตถุดิบ, แยกการถามสูตรออกจากการแจ้งของที่มี, เครื่องปรุงที่ขาด, อุปกรณ์และข้อมูลอุปกรณ์ไม่เพียงพอ, การถามต่อ, สูตรนอกคลัง, อ้างอิงผิด ID, คำตอบที่แสดงขั้นตอนต้นฉบับ และหน้าเว็บไม่มี Key/เริ่มบทสนทนาใหม่

AppTest ของ Groq ใช้ client จำลองสำหรับ Key ไม่ถูกต้อง, timeout, rate limit, connection error และคำตอบสำเร็จ ตรวจว่าไม่แสดงข้อความ exception ดิบ/placeholder คีย์ ไม่ใช่ผลทดสอบ API หรือคุณภาพคำตอบของโมเดลจริง

การประเมิน 20 ข้อวัด expected_recipe_ids, สถานะตอบได้/ไม่ได้ และวัตถุดิบที่คาดว่าขาด โดยไม่เรียก LLM ไม่มีการอ้างว่า 20/20 คือความแม่นยำของ Groq ในข้อมูลทั่วไป ชุดคำถามนี้เป็นชุดตัวอย่างขนาดเล็กสำหรับคลังเอกสารที่เตรียมไว้

ระหว่างพัฒนาพบคำถาม “เมนูที่สาม” ค้นสูตรที่สามไม่เจอใน top chunks เมื่อใช้ข้อความถามต่ออย่างเดียว แก้ด้วยการเติมชื่อสูตรจาก recipe_id ในประวัติเข้า semantic query แล้วรันทดสอบชุด CSV ใหม่ ได้ 20/20 สถานะปัจจุบัน

การทดสอบ pytest ครั้งแรกติดสิทธิ์ Temp ของ sandbox (9 ผ่าน 3 setup errors) หลังรันด้วยสิทธิ์ที่อนุญาตแล้วผ่านทั้งหมด ไม่ถือ setup errors เดิมเป็นผลผ่าน คลังข้อมูลและไฟล์ Notebook ตัวอย่างเดิมยังอยู่ ไม่ได้ Push/Deploy

ก่อนส่งงาน: ใส่ Key ของตนเอง รัน `python scripts/evaluate.py --llm` และตรวจคำตอบบนเว็บเทียบเฉลยด้วยตนเอง ตรวจสูตรตัวอย่างก่อนใช้จริง ทดสอบมือถือและ Capture ภาพจริง จากนั้น Deploy แล้วกรอก URL จริงใน README/Notebook
