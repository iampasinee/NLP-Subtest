# คู่มือการเชื่อมต่อระบบ RAG (INTEGRATION.md)

เอกสารนี้ระบุสัญญาข้อมูล (Contract), Schema, ความหมายของข้อมูล (Field Semantics) และขั้นตอนการเปลี่ยนจาก `MockAdapter` ไปเป็นระบบค้นเอกสารจริง (Live RAG System เช่น SentenceTransformer, FAISS และ Groq) โดย **ไม่ต้องแก้ไขโค้ด UI ใน `app.py` หรือ `ui/components.py`** ตามข้อกำหนด PRD หมวด 9 และ 12

---

## 1. สถาปัตยกรรมและการแยกชั้น (Architectural Decoupling)

```
┌────────────────────────────────────────────────────────┐
│               Streamlit UI Layer (`app.py`)             │
│   (Form, Chat containers, Recipe cards, Evidence)      │
└───────────────────────────┬────────────────────────────┘
                            │ Calls answer_request(request)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Service Layer (`services/adapter.py`)       │
│        BaseRAGAdapter Interface & Factory Pattern      │
└─────────────┬────────────────────────────┬─────────────┘
              │ Mode: "mock" (default)     │ Mode: "live"
              ▼                            ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│      MockAdapter          │ │     LiveRAGAdapter       │
│ (`services/mock_adapter`) │ │ (`services/live_adapter`)│
│  Loads fixture scenarios  │ │  SentenceTransformer +   │
│   (scenarios.json)        │ │  FAISS Index + Groq LLM  │
└───────────────────────────┘ └──────────────────────────┘
```

---

## 2. Request Schema (ข้อมูลขาเข้า)

ฟังก์ชัน `answer_request(request: dict) -> dict` จะได้รับ Dictionary ตามโครงสร้างต่อไปนี้:

```json
{
  "request_id": "req-8f4b1a2c",
  "query": "มีไข่กับข้าวสวย ทำอะไรได้บ้าง",
  "available_ingredients": ["ไข่", "ข้าวสวย"],
  "available_ingredients_text": "ไข่ ข้าวสวย",
  "equipment": ["กระทะ"],
  "require_all_ingredients": false,
  "selected_recipe_id": null,
  "history": [
    {
      "role": "user",
      "content": "มีไข่กับข้าวสวย"
    },
    {
      "role": "assistant",
      "content": "พบ 2 เมนูในข้อมูลตัวอย่าง"
    }
  ]
}
```

### คำอธิบายฟิลด์ Request
| Field | Type | คำอธิบาย |
|---|---|---|
| `request_id` | `str` | รหัสอ้างอิงคำขอ สำหรับ tracking หรือ error logs |
| `query` | `str` | ข้อความค้นหาหลัก หรือคำถามต่อเนื่องของผู้ใช้ |
| `available_ingredients` | `List[str]` | รายการวัตถุดิบและเครื่องปรุงที่แยกเป็นคำๆ (tokenized) |
| `available_ingredients_text` | `str` | ข้อความวัตถุดิบต้นฉบับที่ผู้ใช้พิมพ์ใน text area |
| `equipment` | `List[str]` | รายการอุปกรณ์ที่เลือก (เช่น `["กระทะ", "ไมโครเวฟ"]`). หากเป็นรายการว่าง `[]` หมายถึง **ไม่จำกัดอุปกรณ์** |
| `require_all_ingredients` | `bool` | หากเป็น `true` หมายถึงต้องกรองเฉพาะเมนูที่วัตถุดิบครบตามสูตร |
| `selected_recipe_id` | `Optional[str]` | รหัสสูตรที่กำลังโฟกัสอยู่ (เมื่อผู้ใช้กด "ถามต่อเกี่ยวกับเมนูนี้") เพื่อป้องกันคำถามกำกวม |
| `history` | `List[dict]` | ประวัติการสนทนาย้อนหลัง 4 ข้อความล่าสุด |

---

## 3. Response Schema (ข้อมูลขาออก)

Live Adapter หรือ Mock Adapter ต้องส่งคืน Dictionary ตามโครงสร้างนี้:

```json
{
  "status": "ok",
  "answer": "พบ 1 เมนูที่มีวัตถุดิบครบตามสูตรที่คุณระบุไว้",
  "recipes": [
    {
      "recipe_id": "demo-001",
      "name": "ข้าวผัดไข่สูตรหอพัก",
      "ingredient_match": "complete",
      "matched_ingredients": ["ข้าวสวย", "ไข่ไก่", "น้ำมันพืช", "ซีอิ๊วขาว", "ต้นหอม"],
      "missing_ingredients": [],
      "quantity_check": "unknown",
      "equipment": ["กระทะ"],
      "equipment_match": "compatible",
      "servings": "1 จาน",
      "ingredients": [
        {"name": "ข้าวสวย", "amount": "1 ถ้วย"},
        {"name": "ไข่ไก่", "amount": "1 ฟอง"},
        {"name": "น้ำมันพืช", "amount": "1 ช้อนโต๊ะ"},
        {"name": "ซีอิ๊วขาว", "amount": "1 ช้อนชา"},
        {"name": "ต้นหอมซอย", "amount": "1 ต้น"}
      ],
      "steps": [
        "ตั้งกระทะใส่น้ำมันพืชให้ร้อนด้วยไฟกลาง",
        "ตอกไข่ไก่ลงไป ใช้ตะหลิวยีพอให้ไข่ขาวและไข่แดงเริ่มสุก",
        "ใส่ข้าวสวยลงผัดคลุกเคล้าให้เข้ากัน ปรุงรสด้วยซีอิ๊วขาว",
        "โรยต้นหอมซอย ผัดเร็วๆ อีก 30 วินาที แล้วปิดเตา จัดเสิร์ฟ"
      ],
      "source_ids": ["demo-source-001"]
    }
  ],
  "sources": [
    {
      "source_id": "demo-source-001",
      "document_name": "สูตรตัวอย่างสำหรับทดสอบหน้าจอ",
      "recipe_id": "demo-001",
      "section": "ข้าวผัดไข่สูตรหอพัก",
      "page": 1,
      "source_url": null,
      "excerpt": "ข้าวผัดไข่สูตรประหยัดสำหรับเด็กหอ ใช้วัตถุดิบพื้นฐาน 5 รายการ ผัดด้วยกระทะใบเดียวเสร็จใน 5 นาที"
    }
  ],
  "is_mock": false,
  "error_code": null,
  "clarification_options": []
}
```

---

## 4. Field Semantics & Enum Definitions

### 4.1 `status` (สถานะการตอบ)
- `ok`: ค้นพบสูตรหรือตอบคำถามได้ตามปกติ
- `no_match`: ค้นหาในคลังเอกสารแล้วไม่พบสูตรที่ตรงกับเงื่อนไข
- `insufficient_context`: เอกสารไม่มีข้อมูลตอบคำถามนี้ (เช่น ถามแคลอรี่ แต่คลังเอกสารไม่มีระบุ)
- `needs_clarification`: คำถามกำกวม จำเป็นต้องให้ผู้ใช้เลือกเมนูจาก `clarification_options`
- `error`: เกิดข้อผิดพลาดของระบบหรือ API ขัดข้อง

### 4.2 `ingredient_match` (ความครบของวัตถุดิบ)
- `complete`: ผู้ใช้ระบุวัตถุดิบครบทุกตัวที่สูตรต้องการ (รวมถึงเครื่องปรุง)
- `missing`: ยังขาดวัตถุดิบหรือเครื่องปรุงบางรายการ (ดูรายการใน `missing_ingredients`)
- `unknown`: ข้อมูลไม่เพียงพอที่จะตรวจสอบความครบ

### 4.3 `equipment_match` (ความเข้ากันได้ของอุปกรณ์)
- `compatible`: อุปกรณ์ที่ผู้ใช้มีตรงกับอุปกรณ์ที่สูตรกำหนด
- `incompatible`: อุปกรณ์ที่ผู้ใช้มีไม่ตรงกับอุปกรณ์ที่สูตรกำหนด
- `unrestricted`: ผู้ใช้ไม่ได้เลือกอุปกรณ์ใดๆ (ทำได้ทุกประเภท)
- `unknown`: สูตรไม่ได้ระบุอุปกรณ์

### 4.4 `quantity_check` (การตรวจสอบปริมาณ)
- `sufficient`: ปริมาณที่ผู้ใช้มีเพียงพอตามสูตร
- `insufficient`: ปริมาณที่ผู้ใช้มีไม่เพียงพอ
- `unknown`: ผู้ใช้ระบุเฉพาะชื่อวัตถุดิบโดยไม่ได้ระบุปริมาณ (UI จะแสดงคำเตือนกำกับ)

---

## 5. กฎ UX & ป้องกันการหลอน (Guardrails)

1. **ห้ามสมมติว่าผู้ใช้มีเครื่องปรุง**: หากสูตรระบุว่าต้องใช้น้ำมัน ซีอิ๊ว หรือน้ำปลา และผู้ใช้ไม่ได้พิมพ์คำเหล่านี้มา ต้องส่งคืนใน `missing_ingredients` เสมอ
2. **ไม่สร้าง URL ปลอม**: ฟิลด์ `source_url` หากไม่มี URL ต้นฉบับจริงให้ใส่ `null`
3. **ความปลอดภัยของหลักฐาน**: ฟิลด์ `excerpt` จะถูกเรนเดอร์เป็น Plain text เสมอ ห้ามแทรก HTML/JS code
4. **ลำดับการแสดงผล**: UI จะแสดงผลการ์ดตามลำดับที่ Adapter ส่งมาโดยตรง ไม่จัดอันดับเอง

---

## 6. ขั้นตอนการติดตั้ง Live RAG Adapter (SentenceTransformer + FAISS + Groq)

### ขั้นตอนที่ 1: สร้างไฟล์ `services/live_adapter.py`
สร้างคลาส `LiveRAGAdapter` ที่สืบทอดจาก `BaseRAGAdapter`:

```python
# services/live_adapter.py
from typing import Any, Dict
from services.adapter import BaseRAGAdapter
from sentence_transformers import SentenceTransformer
import faiss
import groq

class LiveRAGAdapter(BaseRAGAdapter):
    def __init__(self):
        # 1. โหลด Embedding Model เช่น wangchanberta หรือ bge-m3
        self.embedder = SentenceTransformer("BAAI/bge-m3")
        # 2. โหลด FAISS Index
        self.index = faiss.read_index("data/recipe_index.faiss")
        # 3. เตรียม Groq Client
        self.groq_client = groq.Groq()

    def answer_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        query = request.get("query", "")
        ingredients = request.get("available_ingredients", [])

        # ทำ Dense Retrieval ผ่าน FAISS
        # ทำ Filtering ตาม equipment และ require_all_ingredients
        # สังเคราะห์คำตอบและจัดรูปแบบตาม Response Schema

        return {
            "status": "ok",
            "answer": "ผลการค้นหาจากระบบ RAG จริง",
            "recipes": [...],
            "sources": [...],
            "is_mock": False,
            "error_code": None,
            "clarification_options": []
        }
```

### ขั้นตอนที่ 2: ตั้งค่า Environment Variable
รัน Streamlit โดยเปิดโหมด Live:
```bash
export RAG_ADAPTER_MODE=live
export GROQ_API_KEY="gsk_..."
streamlit run app.py
```

เมื่อตั้งค่าตัวแปร `RAG_ADAPTER_MODE=live` แล้ว `services/adapter.py` จะเรียกใช้ `LiveRAGAdapter` อัตโนมัติทันที
