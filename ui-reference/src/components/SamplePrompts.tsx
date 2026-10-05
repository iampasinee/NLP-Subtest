import React from 'react';
import { Sparkles, Utensils, Zap, BookOpen } from 'lucide-react';

interface SamplePromptsProps {
  onSelectPrompt: (text: string, equipment: string[], requireAll: boolean) => void;
}

export const SamplePrompts: React.FC<SamplePromptsProps> = ({ onSelectPrompt }) => {
  return (
    <div className="bg-white border border-[#E6DDD2] rounded-2xl p-5 mb-4 shadow-xs">
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="w-5 h-5 text-[#A8421B]" />
        <h2 className="text-base font-bold text-[#292524]">
          วันนี้มีอะไรอยู่ในครัวบ้าง?
        </h2>
      </div>
      <p className="text-xs md:text-sm text-[#655C54] mb-3.5">
        คลิกตัวอย่างคำถามเพื่อทดสอบการตอบกลับตามเงื่อนไขและคลังสูตรตัวอย่าง:
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        <button
          onClick={() => onSelectPrompt('มีไข่ ข้าวสวย และต้นหอม', [], false)}
          className="p-3 bg-[#FAF5F0] hover:bg-[#F3E8DE] border border-[#E6DDD2] hover:border-[#A8421B] rounded-xl text-left transition-all group flex flex-col justify-between"
        >
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-lg">🥚</span>
            <span className="text-xs font-bold text-[#292524] group-hover:text-[#A8421B]">
              มีไข่ ข้าวสวย และต้นหอม
            </span>
          </div>
          <span className="text-[11px] text-[#78716C] leading-snug">
            มีวัตถุดิบหลักแต่ขาดเครื่องปรุง (น้ำมัน, ซีอิ๊ว)
          </span>
        </button>

        <button
          onClick={() => onSelectPrompt('เต้าหู้ เห็ด ซีอิ๊วขาว', ['ไมโครเวฟ'], false)}
          className="p-3 bg-[#FAF5F0] hover:bg-[#F3E8DE] border border-[#E6DDD2] hover:border-[#A8421B] rounded-xl text-left transition-all group flex flex-col justify-between"
        >
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-lg">🍲</span>
            <span className="text-xs font-bold text-[#292524] group-hover:text-[#A8421B]">
              มีเต้าหู้กับเห็ด ใช้ได้แค่ไมโครเวฟ
            </span>
          </div>
          <span className="text-[11px] text-[#78716C] leading-snug">
            ทดสอบการจับคู่อุปกรณ์ที่ตรงกับสูตร
          </span>
        </button>

        <button
          onClick={() => onSelectPrompt('ขอดูขั้นตอนของเมนูตัวอย่าง', [], false)}
          className="p-3 bg-[#FAF5F0] hover:bg-[#F3E8DE] border border-[#E6DDD2] hover:border-[#A8421B] rounded-xl text-left transition-all group flex flex-col justify-between"
        >
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-lg">📖</span>
            <span className="text-xs font-bold text-[#292524] group-hover:text-[#A8421B]">
              ขอดูขั้นตอนของเมนูตัวอย่าง
            </span>
          </div>
          <span className="text-[11px] text-[#78716C] leading-snug">
            ทดสอบการแสดงวิธีทำ ข้อความยาว และฟิลด์ว่าง
          </span>
        </button>
      </div>
    </div>
  );
};
