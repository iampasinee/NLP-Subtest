import React from 'react';
import { RotateCcw, AlertTriangle, Code, PlayCircle, Eye } from 'lucide-react';

interface HeaderProps {
  onReset: () => void;
  activeTab: 'app' | 'scenarios' | 'deliverables';
  setActiveTab: (tab: 'app' | 'scenarios' | 'deliverables') => void;
}

export const Header: React.FC<HeaderProps> = ({ onReset, activeTab, setActiveTab }) => {
  return (
    <header className="mb-4">
      {/* Top Banner */}
      <div className="bg-[#FEF3C7] border border-[#FCD34D] text-[#92400E] px-3.5 py-2 rounded-lg text-xs md:text-sm font-medium mb-3 flex items-center justify-between gap-2 shadow-xs">
        <div className="flex items-center gap-2">
          <span className="text-base">ℹ️</span>
          <span>
            <strong>โหมดตัวอย่าง (Mock Mode)</strong> — ยังไม่ได้เชื่อมระบบค้นเอกสารจริง (ข้อมูลทั้งหมดเป็น Fixture เพื่อทดสอบ UI)
          </span>
        </div>
        <span className="text-[11px] bg-[#FDE68A] text-[#78350F] px-2 py-0.5 rounded-full font-semibold shrink-0">
          PRD v1.0
        </span>
      </div>

      {/* Main Title Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E6DDD2] pb-3.5">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="text-3xl">🍳</span>
            <h1 className="text-2xl md:text-3xl font-bold text-[#292524] tracking-tight">
              มีอะไร ทำอะไรดี
            </h1>
          </div>
          <p className="text-sm md:text-base text-[#655C54] mt-0.5">
            ค้นเมนูจากวัตถุดิบที่มี พร้อมสูตรและแหล่งอ้างอิง
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-[#E6DDD2] hover:border-[#A8421B] hover:text-[#A8421B] text-[#44403C] text-sm font-medium rounded-lg transition-all shadow-xs"
            title="ล้างประวัติการค้นหาและเริ่มต้นใหม่"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>เริ่มใหม่</span>
          </button>
        </div>
      </div>

      {/* View Switcher Tabs */}
      <div className="flex items-center gap-1 mt-3 bg-[#FBF4EB] p-1 rounded-xl border border-[#E6DDD2]">
        <button
          onClick={() => setActiveTab('app')}
          className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-xs md:text-sm font-semibold transition-all ${
            activeTab === 'app'
              ? 'bg-[#A8421B] text-white shadow-xs'
              : 'text-[#655C54] hover:text-[#292524] hover:bg-white/60'
          }`}
        >
          <Eye className="w-3.5 h-3.5" />
          <span>หน้าจอแอปหลัก (Streamlit Preview)</span>
        </button>

        <button
          onClick={() => setActiveTab('scenarios')}
          className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-xs md:text-sm font-semibold transition-all ${
            activeTab === 'scenarios'
              ? 'bg-[#A8421B] text-white shadow-xs'
              : 'text-[#655C54] hover:text-[#292524] hover:bg-white/60'
          }`}
        >
          <PlayCircle className="w-3.5 h-3.5" />
          <span>ทดสอบ 11 Scenarios</span>
        </button>

        <button
          onClick={() => setActiveTab('deliverables')}
          className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-xs md:text-sm font-semibold transition-all ${
            activeTab === 'deliverables'
              ? 'bg-[#A8421B] text-white shadow-xs'
              : 'text-[#655C54] hover:text-[#292524] hover:bg-white/60'
          }`}
        >
          <Code className="w-3.5 h-3.5" />
          <span>ไฟล์ส่งมอบ Python</span>
        </button>
      </div>
    </header>
  );
};
