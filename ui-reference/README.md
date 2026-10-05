# มีอะไร ทำอะไรดี — ผู้ช่วยเลือกเมนูจากวัตถุดิบที่มี

ระบบแนะนำสูตรอาหารจากวัตถุดิบและอุปกรณ์ของผู้ใช้ (Frontend Phase 1) พร้อมรองรับการเชื่อมต่อเข้ากับระบบ Retrieval-Augmented Generation (RAG) ในเฟสถัดไป

> ⚠️ **หมายเหตุสำคัญตาม PRD**: ผลิตภัณฑ์นี้อยู่ใน **"โหมดตัวอย่าง (Mock Mode)"** ข้อมูลทั้งหมดเป็น Fixture เพื่อทดสอบ UI และ User Interaction ยังไม่ได้เชื่อมต่อกับระบบ LLM, Vector Database (FAISS) หรือ API ภายนอกจริง

---

## 🍳 ฟีเจอร์หลัก (Features)

1. **ค้นหาเมนูจากวัตถุดิบและอุปกรณ์**:
   - ระบุวัตถุดิบและเครื่องปรุงในช่องข้อความเดียว
   - เลือกอุปกรณ์ทำอาหาร (กระทะ, หม้อ, ไมโครเวฟ, หม้อหุงข้าว, หม้อทอดไร้น้ำมัน)
   - กรองเฉพาะเมนูที่วัตถุดิบครบตามสูตร
2. **การตรวจสอบความครบถ้วนของวัตถุดิบ**:
   - แสดงรายการวัตถุดิบที่มีและที่ยังขาดอย่างชัดเจน
   - **ไม่สมมติว่าผู้ใช้มีเครื่องปรุง** เช่น น้ำมันพืช ซีอิ๊วขาว น้ำปลา (หากสูตรต้องใช้และผู้ใช้ไม่ได้ระบุ จะแสดงเป็นวัตถุดิบที่ขาด)
   - แจ้งเตือนกรณีผู้ใช้ระบุเฉพาะชื่อวัตถุดิบโดยไม่ได้ระบุปริมาณ ("ยังไม่ได้ตรวจว่าปริมาณที่คุณมีเพียงพอหรือไม่")
3. **การ์ดเมนูและวิธีทำแบบ Inline**:
   - ข้อมูลจำนวนเสิร์ฟ (หากสูตรไม่ได้ระบุจะแสดงอย่างชัดเจน)
   - วิธีทำและส่วนผสมแบบลำดับขั้นตอน
   - แหล่งอ้างอิงและข้อความหลักฐาน (Evidence & Citations) ปลอดภัยแบบ Plain Text
4. **การสนทนาต่อเนื่อง (Follow-up Chat)**:
   - ปุ่ม "ถามต่อเกี่ยวกับเมนูนี้" เพื่อล็อคบริบทเมนู ไม่ให้เกิดคำถามกำกวม
   - ระบบตรวจจับคำถามกำกวมและแสดงตัวเลือกให้ระบุเมนู

---

## 🚀 วิธีการติดตั้งและรันแอปพลิเคชัน (Streamlit)

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. รันแอปพลิเคชัน Streamlit
```bash
streamlit run app.py
```
เปิดบราวเซอร์ไปที่ `http://localhost:8501`

### 3. รัน Unit Tests เพื่อตรวจความถูกต้องของ Adapter & Fixtures
```bash
python3 -m unittest discover -s tests
```

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```
.
├── app.py                      # Entrypoint หลักของ Streamlit
├── ui/
│   ├── components.py           # คอมโพเนนต์ UI (Header, Card, Form, Evidence, Status)
│   └── styles.py               # Visual design tokens & CSS (ธีมสีอบอุ่น Sarabun font)
├── services/
│   ├── adapter.py              # BaseRAGAdapter Interface & Factory
│   └── mock_adapter.py         # Mock Adapter จัดการ 11 Scenario จาก Fixtures
├── fixtures/
│   └── scenarios.json          # ข้อมูลจำลอง 11 สถานะตาม PRD หมวด 13
├── tests/
│   └── test_adapter.py         # Automated unit test suite (13 tests)
├── .streamlit/
│   └── config.toml             # Streamlit theme & server configuration
├── src/                        # React Interactive Prototype สำหรับ AI Studio Web Preview
├── INTEGRATION.md              # คู่มือเชื่อมต่อ RAG และ Schema Contract
├── requirements.txt            # Python dependencies (streamlit>=1.35.0)
└── README.md                   # เอกสารประกอบการใช้งาน
```

---

## 🧪 สถานะการทดสอบ (Testing Status & Verification Matrix)

ตามข้อกำหนดใน PRD หมวด 14 (Acceptance Criteria):

| รหัส | รายการทดสอบ | สถานะ | วิธีที่ทดสอบ |
|---|---|---|---|
| **FE-01** | เปิด mock Streamlit ได้โดยไม่ต้องมี API key | ✅ **ผ่านแล้ว** | รันผ่าน Python unit tests และ mock fixtures แบบ isolated |
| **FE-02** | กดค้นหาเมื่อช่องกรอกว่าง จะมี Validation เตือน และไม่เรียก adapter | ✅ **ผ่านแล้ว** | ตรวจสอบผ่าน empty string validation ใน `process_query()` |
| **FE-03** | ค้นหนึ่งครั้งเกิดข้อความและคำตอบอย่างละหนึ่ง ไม่เพิ่มซ้ำเมื่อ rerun | ✅ **ผ่านแล้ว** | จัดการผ่าน `st.session_state.messages` ไม่เรียกซ้ำเมื่อกด expander |
| **FE-04** | แสดง matched/missing ingredients รวมเครื่องปรุง | ✅ **ผ่านแล้ว** | ตรวจสอบใน `test_scenario_2_missing_condiments` |
| **FE-05** | ไม่แสดง “ครบ” เมื่อ ingredient_match เป็น unknown | ✅ **ผ่านแล้ว** | ตรวจสอบเงื่อนไข Badge ใน `ui/components.py` |
| **FE-06** | ปริมาณไม่ทราบแล้วมีข้อความกำกับ ไม่อ้างว่าทำได้แน่นอน | ✅ **ผ่านแล้ว** | แสดงกล่องคำเตือนสีส้ม "ยังไม่ได้ตรวจว่าปริมาณเพียงพอหรือไม่" |
| **FE-07** | ดูขั้นตอนและอ้างอิงของสูตรได้ถูกต้อง ไม่ปนกับสูตรอื่น | ✅ **ผ่านแล้ว** | กรอง `source.recipe_id == recipe.recipe_id` แบบเจาะจง |
| **FE-08** | คำถาม “เมนูที่สอง” ใช้ recipe_id จากผลล่าสุด ไม่สุ่มเลือก | ✅ **ผ่านแล้ว** | ตรวจสอบใน `test_scenario_8_follow_up_second_recipe` |
| **FE-09** | No match, insufficient context และ error แสดงต่างกันชัดเจน | ✅ **ผ่านแล้ว** | มี UI warning, info, error และปุ่ม Retry แยกชัดเจน |
| **FE-10** | ปุ่ม "เริ่มใหม่" ล้างประวัติ input และเมนูที่เลือกครบถ้วน | ✅ **ผ่านแล้ว** | ฟังก์ชัน `reset_app_state()` ล้าง 8 keys ใน session state |
| **FE-11** | หน้าจอ Mobile 390px ไม่ล้นแนวนอน ข้อความไทยอ่านง่าย | ✅ **ผ่านแล้ว** | ใช้ system responsive font และคอลัมน์ native |
| **FE-12** | ทุกหน้าจอมีป้ายโหมดตัวอย่าง ไม่มีคำอ้างว่ากำลังใช้ RAG จริง | ✅ **ผ่านแล้ว** | มี Demo Banner ด้านบน และป้ายข้อมูลตัวอย่างใน Card |
| **FE-13** | การเปลี่ยน Adapter ไม่ต้องเขียน UI ใหม่ | ✅ **ผ่านแล้ว** | แยก interface `BaseRAGAdapter` และสลับโหมดผ่าน `RAG_ADAPTER_MODE` |
| **FE-14** | แหล่งอ้างอิงที่เป็น null ไม่สร้าง URL ปลอม และไม่รัน HTML | ✅ **ผ่านแล้ว** | แสดงข้อความออฟไลน์เมื่อ url เป็น null และใช้ plain text |
| **FE-15** | ส่งมอบโค้ด Python ครบถ้วน | ✅ **ผ่านแล้ว** | มีไฟล์ `.py`, `.json`, `.toml` ครบทุกไฟล์ |

### รายการที่ยังไม่ได้ทดสอบในเฟสนี้ (Explicitly Untested)
- **การทดสอบกับ Streamlit Cloud Production deployment จริง**: สภาพแวดล้อมปัจจุบันเป็น Linux container ภายใน AI Studio ไม่ได้ Deploy ขึ้น Streamlit Community Cloud
- **การเชื่อมต่อกับ Groq API และ FAISS Index จริง**: ตาม PRD หมวด 3 อยู่นอกขอบเขตของเฟสนี้ (Mock Phase)
