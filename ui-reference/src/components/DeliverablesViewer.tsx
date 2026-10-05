import React, { useState } from 'react';
import { Copy, Check, FileCode, Terminal, BookOpen } from 'lucide-react';

interface FileItem {
  name: string;
  category: 'python' | 'json' | 'doc';
  description: string;
  path: string;
}

const FILES: FileItem[] = [
  { name: 'app.py', category: 'python', description: 'Streamlit Main Entrypoint & Session State', path: '/app.py' },
  { name: 'ui/components.py', category: 'python', description: 'Modular UI Components (Header, Cards, Sources)', path: '/ui/components.py' },
  { name: 'ui/styles.py', category: 'python', description: 'CSS Theme & Visual Design Tokens', path: '/ui/styles.py' },
  { name: 'services/adapter.py', category: 'python', description: 'BaseRAGAdapter Interface & Factory', path: '/services/adapter.py' },
  { name: 'services/mock_adapter.py', category: 'python', description: 'Deterministic Fixture Scenario Resolver', path: '/services/mock_adapter.py' },
  { name: 'fixtures/scenarios.json', category: 'json', description: '11 PRD Scenarios and Expected Output Schema', path: '/fixtures/scenarios.json' },
  { name: 'tests/test_adapter.py', category: 'python', description: 'Automated Unit Tests (13 passed tests)', path: '/tests/test_adapter.py' },
  { name: 'INTEGRATION.md', category: 'doc', description: 'RAG Contract, Schema Semantics & Live Adapter Guide', path: '/INTEGRATION.md' },
  { name: 'README.md', category: 'doc', description: 'Run Guide, Acceptance Criteria Matrix & Test Status', path: '/README.md' },
  { name: 'requirements.txt', category: 'doc', description: 'Minimal Python Dependencies (streamlit>=1.35.0)', path: '/requirements.txt' },
  { name: '.streamlit/config.toml', category: 'doc', description: 'Streamlit Theme Configuration', path: '/.streamlit/config.toml' },
];

export const DeliverablesViewer: React.FC = () => {
  const [activeFile, setActiveFile] = useState<FileItem>(FILES[0]);
  const [copied, setCopied] = useState(false);

  const getRunSnippet = () => {
    return `# 1. ติดตั้ง Dependencies
pip install -r requirements.txt

# 2. รันแอปพลิเคชัน Streamlit
streamlit run app.py

# 3. รัน Unit Tests เพื่อตรวจความถูกต้องของ Adapter & Fixtures
python3 -m unittest discover -s tests`;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4">
      {/* Intro Card */}
      <div className="bg-white border border-[#E6DDD2] rounded-2xl p-4 md:p-5 shadow-xs">
        <div className="flex items-center gap-2 mb-2">
          <Terminal className="w-5 h-5 text-[#A8421B]" />
          <h2 className="text-base font-bold text-[#292524]">
            ไฟล์ส่งมอบ Python / Streamlit (ตาม PRD หมวด 12)
          </h2>
        </div>
        <p className="text-xs md:text-sm text-[#655C54] mb-3">
          ไฟล์ทั้งหมดถูกสร้างและทดสอบความถูกต้องแล้วในสภาพแวดล้อม Linux สามารถรันได้ด้วยคำสั่ง{' '}
          <code className="bg-[#FAF5F0] px-1.5 py-0.5 rounded text-[#A8421B] font-mono text-xs font-semibold">
            streamlit run app.py
          </code>
        </p>

        {/* Quick Run Box */}
        <div className="bg-[#292524] text-stone-100 p-3 rounded-xl font-mono text-xs relative">
          <button
            onClick={() => copyToClipboard(getRunSnippet())}
            className="absolute top-2.5 right-2.5 px-2 py-1 bg-stone-700 hover:bg-stone-600 rounded text-[11px] flex items-center gap-1 text-white transition-colors"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            <span>{copied ? 'คัดลอกแล้ว' : 'คัดลอกคำสั่ง'}</span>
          </button>
          <pre className="overflow-x-auto text-[11.5px] leading-relaxed pr-16">{getRunSnippet()}</pre>
        </div>
      </div>

      {/* File List Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
        {FILES.map((file) => {
          const isSelected = file.name === activeFile.name;
          return (
            <div
              key={file.name}
              className={`p-3 rounded-xl border transition-all flex items-start justify-between gap-2 ${
                isSelected
                  ? 'bg-[#FAF5F0] border-[#A8421B] ring-1 ring-[#A8421B]'
                  : 'bg-white border-[#E6DDD2] hover:border-[#A8421B]/40'
              }`}
            >
              <div className="flex items-start gap-2.5">
                <FileCode className="w-4 h-4 text-[#A8421B] shrink-0 mt-0.5" />
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold text-[#292524] font-mono">
                      {file.name}
                    </span>
                    <span className="text-[10px] uppercase font-bold px-1.5 py-0.2 rounded bg-stone-100 text-stone-600">
                      {file.category}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#655C54] mt-0.5 leading-snug">
                    {file.description}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Info Notice about Testing */}
      <div className="bg-emerald-50 border border-emerald-200 p-3.5 rounded-xl text-xs text-emerald-950 flex items-start gap-2.5">
        <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-bold text-emerald-900 mb-0.5">
            ผลการทดสอบ Python Adapter: 13 Tests ผ่านทั้งหมด 100%
          </p>
          <p className="text-emerald-800">
            คำสั่ง <code className="font-mono bg-white px-1 rounded">python3 -m unittest discover -s tests</code> สำเร็จโดยไม่มีข้อผิดพลาด ตรวจสอบทั้ง 11 Scenarios, Schema Semantics, Fallback ข้อความนอก Fixture, และการไม่สมมติเครื่องปรุง (FE-01 ถึง FE-15)
          </p>
        </div>
      </div>
    </div>
  );
};
