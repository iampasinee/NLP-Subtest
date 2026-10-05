# รายงานแก้บั๊กครัวคิดให้ — 5 ตุลาคม 2569

แก้เสร็จในเครื่อง ยังไม่ได้ commit/push/deploy ไม่เปลี่ยนข้อมูลหรือโครงสร้าง `data/recipes.md` ไม่มีคีย์ในรายงานหรือ logs

## หลักฐานก่อนแก้และขอบเขตข้อสรุป

- Markdown loader โหลดครบ **20 สูตร / 160 chunks** ทุกสูตรมีเจ็ดหัวข้อและส่วนผสมรวมเครื่องปรุง อ่าน R04 ได้ไข่ไก่ **1 ฟอง**, น้ำ 100 มิลลิลิตร, ซีอิ๊วขาว 1 ช้อนชา, ต้นหอม 1 ต้น
- ทั้งสี่คำถามผ่าน retrieval/ranking ในโค้ดก่อนแก้ ไม่ถูกปฏิเสธเพราะวัตถุดิบไม่ครบหรือไม่มี pantry คำถามเจาะจง R04 ทำงานผ่าน explicit recipe selection
- คำถามสั้น normalize เป็นไข่ไก่จริง ตัวอย่างคะแนน raw FAISS ก่อนแก้: `ไข่` R03=0.7271, `ไข่ไก่` R02=0.6893, คำถามข้าว/ไข่/ต้นหอม R01=0.6791, คำถามปริมาณ R04=0.7406 เหนือ threshold 0.28 ไม่ลด threshold
- พบคีย์ที่ตั้งไว้ใน local `.streamlit/secrets.toml` จึงเรียก API จริงโดยไม่แสดงค่า: smoke ก่อน RAG สำเร็จ จากนั้นโค้ดเดิมตอบ “ไข่” และ “ไข่ไก่” ได้ IDs จริง อีกสองคำถามได้ **RateLimitError HTTP 429** ไม่มีหลักฐานว่า GPT-OSS ใช้ไม่ได้หรือว่า JSON parsing เป็นสาเหตุของสองคำถามแรก
- **อาการทุกคำถามไม่พบข้อมูลบน Cloud ทำซ้ำไม่ได้ในเครื่อง** จึงยังชี้สาเหตุเดียวบน Cloud ไม่ได้โดยไม่มี logs/เวอร์ชันของ deployment เดิม การอ้างว่าเป็น threshold หรือ loader เสียจะขัดกับผลที่วัดได้
- ไม่พบไฟล์ตัวอย่างเรียก API เพิ่มเติมใน attachments ของรอบนี้ จึงเทียบส่วน `messages`, `max_completion_tokens`, `reasoning_effort`, `stream` และการรับผลตามรายละเอียดที่ผู้ใช้ให้ กับเอกสารทางการและ API จริง

## จุดบกพร่องที่แก้และความเสี่ยงที่พบ

1. `render_answer([])` ถูกใช้ทั้งเมื่อ retrieval ไม่มี Context และเมื่อ LLM ตอบ IDs ว่าง ทำให้ UI แสดงข้อความ “ไม่พบข้อมูลที่ตรงเงื่อนไขในเอกสาร” แม้ค้นสูตรเจอแล้ว แก้ให้ LLM ว่างเป็น `LLMNoSelectionError` และ UI แจ้งว่าพบสูตรแต่ Groq ยังไม่เลือก ไม่มี fallback คำตอบจำลอง
2. Prompt เดิม “ข้อมูลไม่พอให้เลือก []” ไม่แยกสูตรที่ขาดเครื่องปรุงจากสูตรที่ไม่มีข้อมูลรองรับ เพิ่ม intent ชัดเจน: ingredient recommendation ให้เสนอเมนูแม้วัตถุดิบไม่ครบ พร้อมข้อมูล missing; recipe question ไม่ต้องให้ผู้ใช้ยืนยัน pantry นี่เป็นความกำกวมของ prompt ที่ตรวจพบ ไม่ใช่หลักฐานว่าโมเดลเลือกว่างใน API run ก่อนแก้
3. Context เดิมส่ง fields เต็มและ `_sections` ที่มีข้อมูลเดียวกันซ้ำ ลดให้เหลือ fields สูตรครบหนึ่งชุด ไม่ซ้ำ `_sections` เพื่อลดภาระ API และโอกาสแตะโควตา ยังมี ingredients/quantities/steps/equipment/source/notes/document ครบ ผล 429 ที่พบจริงเป็น rate limit; การลด Context ไม่รับประกันว่าจะหมดปัญหาโควตา
4. ค่าเริ่มต้นเดิมยังเป็น Llama แม้บัญชีใช้ GPT-OSS เปลี่ยน defaults/config example/Notebook/CLI ให้เป็น `openai/gpt-oss-120b` แต่ยังอ่าน `GROQ_MODEL` จาก Secrets จริง ก่อนแก้ local override อ่าน GPT-OSS ได้อยู่แล้ว จึงไม่อ้างว่า default mismatch ทำให้ local API fail
5. คำสั่ง API เดิมใช้ `max_tokens=512` และไม่ได้ระบุ stream/reasoning ชัดเจน เปลี่ยน GPT-OSS เป็น strict JSON schema, `max_completion_tokens=2048`, low reasoning, include_reasoning false, stream false และอ่านข้อความ non-stream โดยตรง แยก content ว่าง/finish_reason length/JSON อ่านไม่ได้ออกจาก schema/IDs ไม่ถูกต้อง สำหรับ streaming helper รวมทุก `delta.content` ก่อน parse
6. Validation เดิมบังคับ citations เรียงเหมือน recipe_ids แม้อ้าง IDs ถูกทั้งหมด แก้ตรวจ set ของ citations พร้อมตรวจ IDs ไม่เกิน Context/ไม่ซ้ำ และรักษาลำดับ recipe_ids ที่โมเดลเลือก
7. Cache เดิมผูกกับเอกสารเท่านั้น Helper parse/chunk เปลี่ยนแต่ Streamlit cached wrapper ไม่เปลี่ยนอาจใช้ index เดิม แก้ fingerprint รวม implementation, embedding model และ pipeline revision ด้วย พร้อมแสดง version/index key ใน sidebar
8. เพิ่ม allowlisted logs สำหรับจำนวนสูตร/chunks, candidate IDs, score, filter reason, model, error class, HTTP status และ numeric retry-after ไม่บันทึกคำถาม ข้อความตอบดิบ exception body คีย์ header หรือ Secrets แยก stage `retrieval_rejected`, `groq_api`, `groq_parse`, `groq_validation`, `groq_selection` ปิด watcher ใน `[server]` เดิมด้วย `fileWatcherType='none'`

อ้างอิงพารามิเตอร์: [Groq Structured Outputs](https://console.groq.com/docs/structured-outputs), [GPT-OSS Reasoning](https://console.groq.com/docs/reasoning), [Chat Completions](https://console.groq.com/docs/text-chat) ตรวจวันที่ 5 ตุลาคม 2569 GPT-OSS รองรับ strict schema และ low reasoning; ไม่ส่ง reasoning_format

## ผลหลังแก้ที่รันจริง

| คำถาม | candidates และคะแนนหลัง ranking | จุดที่จบ |
|---|---|---|
| ไข่ | R03 0.68214, R02 0.66795, R13 0.62495 | Groq จริงเลือกทั้งสาม; validation ผ่าน |
| ไข่ไก่ | R03 0.63191, R02 0.62860, R13 0.61037 | Groq จริงเลือกทั้งสาม; validation ผ่าน |
| มีไข่ ข้าวสวย และต้นหอม ทำอะไรได้บ้าง | R01 0.69969, R05 0.61965, R02 0.61941 | Groq จริงเลือกทั้งสาม; แจ้งเครื่องปรุงที่ขาด |
| ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง | R04 0.71873 | Groq จริงเลือก R04; ปริมาณจากเอกสารคือ 1 ฟอง |
| ขอสูตรพิซซ่าไข่ | ไม่มี candidate | ปฏิเสธที่ requested_recipe_not_in_corpus; ไม่เรียก API |
| ข้าวผัดไข่มีกี่แคลอรี | ไม่มี candidate | ปฏิเสธที่ unsupported_information; ไม่เรียก API |

- pytest **47 ผ่าน**: แยก retrieval regressions, Secrets override/default, parser/chunker cache invalidation ทั้ง revision/implementation และ hash ที่คงเดิมเมื่อเปลี่ยน CRLF/LF, normalization ที่ไม่รวมไข่เป็ด/ไข่ปลา, API parameters, stream fragment assembly, content truncation, IDs/citations, logs ไม่รั่ว secrets และ UI ไม่เปลี่ยน API/parse/validation/selection error เป็น NO_DATA
- Semantic Retrieval เดิม **20/20 ผ่าน** และชุดวินิจฉัยใหม่สี่คำถาม+สองคำถามปฏิเสธผ่านจากโมเดลจริง ดู `retrieval_results.json` และ `bugfix_results.json`
- Groq smoke จริง **non-streaming ผ่าน** ก่อน RAG และ **streaming ผ่าน** โดยรวม delta ก่อนอ่าน content
- Groq RAG จริงทั้ง **4/4 คำถามผ่าน** ในรอบหลังแก้ รายละเอียดใน `groq_diagnostics.local.json` ซึ่ง ignore จาก Git
- AppTest **เรียก Groq จริง** สำหรับคำถาม R04: UI มี `recipes.md`, `1 ฟอง`, previous IDs=`['R04']` ไม่ใช่ mock ผลนี้ยืนยัน pipeline ผ่าน UI ในเครื่อง ไม่ใช่การรับรอง deployment Cloud หรือ browser/mobile rendering
- สูตรเดิมไม่เปลี่ยน ตรวจ digest ที่บันทึกจาก JSON ก่อนย้ายผ่านอีกครั้ง

## วิธีตรวจแยกสองขั้น

```powershell
.\.venv\Scripts\python.exe scripts/diagnose_pipeline.py
.\.venv\Scripts\python.exe scripts/diagnose_pipeline.py --live --smoke-only
.\.venv\Scripts\python.exe scripts/diagnose_pipeline.py --live
# ทดสอบ streaming เฉพาะ smoke โดยไม่ยิง RAG ซ้ำ:
.\.venv\Scripts\python.exe scripts/diagnose_pipeline.py --live --stream-smoke --smoke-only
```

โหมดปกติไม่มี API call โหมด live อ่าน local Streamlit Secrets โดยไม่พิมพ์คีย์ ถ้าคีย์ไม่มีจะแจ้งตรง ๆ ไม่มีการจำลองคำตอบแทน API ทุกการทดสอบจริงใช้โควตาบัญชี หาก HTTP 429 ให้รอรีเซ็ตแล้วลองทีละคำถาม ไม่ตีความว่าเอกสารไม่มีสูตร

## นำโค้ดล่าสุดขึ้น Cloud (ผู้ใช้ทำภายหลัง)

1. รัน tests ตรวจ diff แล้ว commit/push เอง เฉพาะไฟล์โค้ด/เอกสาร/ผล retrieval ที่ปลอดภัย ห้ามเพิ่ม `.streamlit/secrets.toml`, `.env`, cache หรือไฟล์ `*.local.json` ตรวจ `.gitignore` ได้กันคีย์และผล local แล้ว
2. ใน Streamlit Cloud ตรวจ repository/branch และ entrypoint `app.py` ว่าชี้ชุดที่ push จริง ตั้ง Secrets เป็น GROQ_API_KEY ของบัญชี และ `GROQ_MODEL = "openai/gpt-oss-120b"` ห้ามใส่คีย์ใน URL/README/log
3. หลังอัปเดต Reboot app เพื่อโหลด process/โมดูลใหม่ เปิด session ใหม่หรือกดเริ่มบทสนทนาใหม่ หลีกเลี่ยงข้อจำกัดอุปกรณ์ที่เลือกค้าง การปิด watcher ไม่ได้แทนการ reboot เมื่อทดสอบโค้ดใน process เดิม
4. ดู sidebar ต้องเป็นเวอร์ชัน `markdown-rag-2026-10-05-v2` และ index key ตรงกับ `python scripts/diagnose_pipeline.py` ของ checkout ที่ส่งขึ้น (normalize CRLF/LF ใน fingerprint แล้ว จึงเทียบ Windows กับ Cloud ได้) ดู startup/index_build logs ประกอบ: model GPT-OSS, recipes=20, chunks=160 ถ้าไม่ตรงให้ตรวจ commit/branch/reboot แทนการเดา threshold
5. กด **ตรวจการเชื่อมต่อ Groq → ทดสอบ Groq โดยตรง** ก่อนค้นสูตร จากนั้นลองทั้งสี่คำถามทีละข้อ เปิดหลักฐานตรวจ `recipes.md`, recipe_id และปริมาณ
6. หากไม่พบคำตอบ ดู Cloud logs: context IDs ว่าง=filter reason ช่วยอธิบาย; context IDs ไม่ว่างแต่ API error=class/status; response ว่าง/length=groq_parse; IDs ผิด=groq_validation; IDs ว่าง=groq_selection ผลเหล่านี้ไม่ควรถูกรวมเป็นข้อความเอกสารไม่พบ

ยังไม่เข้าถึง deployment/logs บน Cloud ของผู้ใช้ จึงยังยืนยันไม่ได้ว่า Cloud ปัจจุบันใช้โค้ดล่าสุดหรือมีสาเหตุอื่นใด
