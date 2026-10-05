import csv
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

CASES = [
('ครบสูตร', 'มีข้าวสวย ไข่ ต้นหอม น้ำมันพืช ซีอิ๊วขาว ทำอะไรได้บ้าง', 'ข้าวสวย|ไข่ไก่|ต้นหอม|น้ำมันพืช|ซีอิ๊วขาว', '', '', 'ข้าวผัดไข่ วัตถุดิบครบตามสูตร', 'R01', 'yes', ''),
('ขาดเครื่องปรุง', 'ข้าวผัดไข่ทำอย่างไร มีไข่ ข้าวสวย ต้นหอม', 'ไข่ไก่|ข้าวสวย|ต้นหอม', '', '', 'แสดงสูตรและแจ้งขาดน้ำมันพืชกับซีอิ๊วขาว', 'R01', 'yes', 'น้ำมันพืช|ซีอิ๊วขาว'),
('ขาดบางส่วน', 'ไข่เจียวต้นหอมทำอย่างไร', 'ไข่ไก่|น้ำปลา|น้ำมันพืช', '', '', 'แจ้งยังขาดต้นหอม', 'R02', 'yes', 'ต้นหอม'),
('ไมโครเวฟพร้อมเครื่องมือ', 'ไข่ตุ๋นไมโครเวฟทำอย่างไร', 'ไข่ไก่|น้ำ|ซีอิ๊วขาว|ต้นหอม', 'ไมโครเวฟ|ถ้วยทนไมโครเวฟ|ช้อน|มีด', '', 'แสดงไข่ตุ๋นและขั้นตอนจากเอกสาร', 'R04', 'yes', ''),
('อุปกรณ์ไม่พอ', 'ข้าวผัดไข่ทำอย่างไร มีเฉพาะไมโครเวฟ', 'ไข่ไก่|ข้าวสวย', 'ไมโครเวฟ', '', 'ไม่พบข้อมูลที่ตรงเงื่อนไขในเอกสาร', '', 'no', ''),
('ปริมาณ', 'ไข่ตุ๋นไมโครเวฟใช้ไข่กี่ฟอง', '', '', '', 'ไข่ไก่ 1 ฟอง น้ำ 100 มิลลิลิตร หนึ่งเสิร์ฟ', 'R04', 'yes', ''),
('ขั้นตอน', 'ยำทูน่าทำอย่างไร', '', '', '', 'แสดง 4 ขั้นตอนยำทูน่าพร้อมรายการวัตถุดิบ', 'R09', 'yes', ''),
('ถามต่อ', 'เมนูที่สองทำอย่างไร', 'ไข่ไก่|ข้าวสวย', '', 'R01|R04', 'อธิบายไข่ตุ๋นไมโครเวฟซึ่งเป็นเมนูที่สองก่อนหน้า', 'R04', 'yes', ''),
('ถามต่อไม่มีประวัติ', 'เมนูที่สองทำอย่างไร', '', '', '', 'ไม่พบข้อมูลที่ตรงเงื่อนไขในเอกสาร', '', 'no', ''),
('ไม่มีวัตถุดิบในคลัง', 'มีแซลมอน อะโวคาโด ทำอะไรได้บ้าง', '', '', '', 'ไม่พบข้อมูลที่ตรงเงื่อนไขในเอกสาร', '', 'no', ''),
('เมนูไม่อยู่ในคลัง', 'ขอสูตรพิซซ่าไข่', 'ไข่ไก่', '', '', 'ไม่พบข้อมูลที่ตรงเงื่อนไขในเอกสาร', '', 'no', ''),
('โภชนาการ', 'ข้าวผัดไข่มีแคลอรีเท่าไร', 'ไข่ไก่|ข้าวสวย', '', '', 'ไม่พบข้อมูลที่ตรงเงื่อนไขในเอกสาร', '', 'no', ''),
('นอกหัวข้อ', 'ช่วยเขียนโค้ดเกมให้หน่อย', '', '', '', 'ไม่พบข้อมูลที่ตรงเงื่อนไขในเอกสาร', '', 'no', ''),
('alias', 'ข้าวผัดไข่ใช้ซีอิ้วขาวเท่าไร', '', '', '', 'ซีอิ๊วขาว 1 ช้อนชา', 'R01', 'yes', ''),
('ไม่อนุมานเวลา', 'ไข่ตุ๋นไมโครเวฟใช้กี่นาที', '', '', '', 'ไม่พบข้อมูลที่ตรงเงื่อนไขในเอกสาร', '', 'no', ''),
('ไม่มีความร้อน', 'กล้วยนมสดทำอย่างไร', 'กล้วย|นมจืด', 'ถ้วย|ช้อน|มีด', '', 'กล้วย 1 ลูก นมจืด 150 มิลลิลิตร วัตถุดิบครบ', 'R20', 'yes', ''),
('ไม่แทนส่วนผสม', 'ผัดเห็ดกระเทียมใช้เห็ดชนิดอื่นแทนวัตถุดิบได้ไหม', '', '', '', 'ไม่พบข้อมูลที่ตรงเงื่อนไขในเอกสาร', '', 'no', ''),
('จำนวนเสิร์ฟ', 'ซุปมันฝรั่งทำได้กี่เสิร์ฟ', '', '', '', 'จำนวนเสิร์ฟ 1', 'R15', 'yes', ''),
('อุปกรณ์ตามสูตร', 'มักกะโรนีซอสมะเขือเทศต้องใช้อุปกรณ์อะไร', '', '', '', 'เตา หม้อ กระทะ ตะหลิว กระชอน มีด', 'R18', 'yes', ''),
('ถามต่อสาม', 'เมนูที่สามทำอย่างไร', '', '', 'R01|R04|R20', 'แสดงกล้วยนมสด', 'R20', 'yes', ''),
]

def md(text):
    return dict(cell_type='markdown', metadata={}, source=text.splitlines(keepends=True))

def code(text):
    return dict(cell_type='code', metadata={}, source=text.splitlines(keepends=True), execution_count=None, outputs=[])

def main():
    with (ROOT / 'test_questions.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'category', 'question', 'pantry', 'equipment', 'previous_recipe_ids', 'expected_answer', 'expected_recipe_ids', 'answerable', 'expected_missing'])
        for n, row in enumerate(CASES, 1):
            writer.writerow([f'T{n:02}', *row])
    cells = [md('# ผู้ช่วยเลือกเมนูจากวัตถุดิบที่มีด้วย RAG\n\nชื่อผู้จัดทำ: [กรอกชื่อ]  รหัสนักศึกษา: [กรอก]  รายวิชา: [กรอก]\n\nStreamlit URL: [ยังไม่ได้ Deploy — กรอกหลังใช้งานจริง]\n\nGitHub URL: [ยังไม่ได้ Push — กรอกหลังสร้าง repository]'),
             md('## แนวคิดและระบบ\nอ่าน data/recipes.md → แยกสูตรตาม ## และหัวข้อย่อยตาม ### → Cleaning → Structure-based Chunking พร้อมตรวจ token budget → multilingual Sentence Embedding บน CPU → normalized FAISS IndexFlatIP → รวมสูตรเต็มที่เกี่ยวข้อง → ตรวจวัตถุดิบและอุปกรณ์ → context-grounded prompt → Groq API → ตรวจ recipe_id/citations → แสดงรายละเอียดต้นฉบับ\n\nLLM เลือกสูตรจาก Context เป็น JSON แอปแสดงข้อความจากเอกสารโดยตรงเพื่อจำกัด hallucination สูตรตัวอย่าง 20 เมนูสร้างโดย AI สำหรับงานนี้ ต้องตรวจทานก่อนใช้จริง'),
             md('## การติดตั้งบน Colab เพื่อทดสอบ Retrieval\nกรอก GitHub URL ของคุณก่อนรัน ไม่ต้องใส่ API Key เพื่อทดสอบ Retrieval Colab ใช้สำหรับอธิบายและทดสอบโมดูล ไม่ใช่โฮสต์เว็บ Streamlit ถาวร'),
             code('REPOSITORY_URL = "YOUR_GITHUB_REPOSITORY_URL"\nassert REPOSITORY_URL != "YOUR_GITHUB_REPOSITORY_URL", "กรอก URL GitHub ที่สร้างจริงก่อน"\nimport subprocess\nsubprocess.run(["git", "clone", REPOSITORY_URL, "menu-rag"], check=True)\n'),
             code('%cd /content/menu-rag\n%pip install -r requirements-dev.txt\n'),
             code('from sentence_transformers import SentenceTransformer\nfrom rag import MODEL\nSentenceTransformer(MODEL, device="cpu", cache_folder=".cache/models")\n'),
             code('!python scripts/validate_data.py\n!python -m pytest -q\n!python scripts/evaluate.py\n'),
             md('## การทดสอบ LLM (ทางเลือก)\nไม่บันทึก API Key ลง Notebook ใช้ Colab Secrets ชื่อ GROQ_API_KEY แล้วเรียก Groq โดยตรงตามตัวอย่างนี้ ยังไม่มีผลทดสอบ LLM จริงใน Notebook นี้'),
             code('from google.colab import userdata\nfrom groq import Groq\nfrom rag import Retriever, load_recipes, candidates, select_with_llm, render_answer\nmodel = SentenceTransformer(MODEL, device="cpu", cache_folder=".cache/models")\nretriever = Retriever(load_recipes("data"), model)\nhits = candidates(retriever, "ข้าวผัดไข่ทำอย่างไร", {"ไข่ไก่", "ข้าวสวย", "ต้นหอม"}, set())\nclient = Groq(api_key=userdata.get("GROQ_API_KEY"), timeout=30, max_retries=0)\nselected = select_with_llm(client, "llama-3.3-70b-versatile", "ข้าวผัดไข่ทำอย่างไร", hits)\nprint(render_answer(selected))\n'),
             md('## ผลทดสอบและข้อจำกัด\nดู TEST_REPORT.md และ retrieval_results.json สำหรับผลที่รันจริง ตรวจผล LLM กับ expected_answer ใน test_questions.csv โดยมนุษย์ด้วย ไม่ใช้ LLM-as-Judge เพียงอย่างเดียว\n\nการตรวจของที่มีใช้ชื่อและ alias ที่กำหนด ไม่รับประกันปริมาณเพียงพอ การอ่านภาษาไทยแบบอิสระยังมีข้อจำกัด ไม่มีข้อมูลโภชนาการ/เวลาเป็นตัวเลข จึงปฏิเสธคำถามดังกล่าว ไม่มี Key จะเปิดเว็บได้แต่ไม่สร้างคำตอบปลอม'),
             md('## ภาพหน้าจอหลังเว็บใช้งานจริง\n1. หน้าแรกและข้อมูลคลังสูตร\n2. คำตอบเมื่อวัตถุดิบครบ\n3. คำตอบที่ขาดเครื่องปรุง\n4. เงื่อนไขไมโครเวฟ\n5. ถามต่อเมนูที่สอง\n6. หลักฐานอ้างอิง\n7. ปฏิเสธคำถามโภชนาการ\n8. หน้าตั้งค่า Secrets โดยปิดบังคีย์ทั้งหมด\n\n[เพิ่มภาพ Capture จริงภายหลัง — ไม่มีภาพจำลอง]')]
    notebook = dict(cells=cells, metadata=dict(kernelspec=dict(display_name='Python 3', language='python', name='python3'), language_info=dict(name='python'), colab=dict(provenance=[])), nbformat=4, nbformat_minor=5)
    for n, cell in enumerate(cells):
        cell['id'] = f'cell-{n:02}'
    (ROOT / 'submission.ipynb').write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
