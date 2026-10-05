import React, { useState } from 'react';
import { Search, ChevronDown, ChevronUp, Check, AlertCircle } from 'lucide-react';

interface InputSectionProps {
  ingredients: string;
  setIngredients: (val: string) => void;
  equipment: string[];
  setEquipment: (val: string[]) => void;
  requireAll: boolean;
  setRequireAll: (val: boolean) => void;
  onSearch: () => void;
  validationError: string | null;
}

const EQUIPMENT_OPTIONS = ['กระทะ', 'หม้อ', 'ไมโครเวฟ', 'หม้อหุงข้าว', 'หม้อทอดไร้น้ำมัน'];

export const InputSection: React.FC<InputSectionProps> = ({
  ingredients,
  setIngredients,
  equipment,
  setEquipment,
  requireAll,
  setRequireAll,
  onSearch,
  validationError,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  const toggleEquipment = (item: string) => {
    if (equipment.includes(item)) {
      setEquipment(equipment.filter((e) => e !== item));
    } else {
      setEquipment([...equipment, item]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch();
  };

  return (
    <div className="bg-white border border-[#E6DDD2] rounded-2xl shadow-xs overflow-hidden mb-4 transition-all">
      {/* Expander Header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-[#FAF5F0] border-b border-[#E6DDD2] flex items-center justify-between text-left text-sm font-semibold text-[#292524] hover:bg-[#F5ECE3] transition-colors"
      >
        <span className="flex items-center gap-2">
          <span>📝</span>
          <span>ระบุวัตถุดิบและอุปกรณ์ของคุณ (ข้อมูลที่ฉันมี)</span>
        </span>
        <span className="text-[#655C54] flex items-center gap-1 text-xs">
          {isOpen ? 'ย่อหน้าต่าง' : 'แก้ไขข้อมูล'}
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </span>
      </button>

      {isOpen && (
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Ingredients Text Area */}
          <div>
            <label className="block text-sm font-bold text-[#292524] mb-1.5">
              มีวัตถุดิบอะไรบ้าง?
            </label>
            <textarea
              value={ingredients}
              onChange={(e) => setIngredients(e.target.value)}
              placeholder="เช่น ไข่ ข้าวสวย ต้นหอม น้ำมัน น้ำปลา"
              rows={3}
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#E6DDD2] focus:border-[#A8421B] focus:ring-2 focus:ring-[#A8421B]/20 outline-none text-[#292524] text-sm placeholder:text-[#A8A29E] bg-[#FFFCF9] transition-all resize-none"
            />
            <p className="mt-1 text-xs text-[#655C54] flex items-center gap-1">
              <span>💡</span>
              <span>
                <strong>ระบุเครื่องปรุงที่มีด้วย</strong> เพื่อให้รายการวัตถุดิบที่ขาดถูกต้อง (ระบบไม่สมมติว่าคุณมีน้ำมันหรือน้ำปลา)
              </span>
            </p>
          </div>

          {/* Equipment Pills Multiselect */}
          <div>
            <label className="block text-xs font-bold text-[#292524] mb-1.5 uppercase tracking-wide">
              อุปกรณ์ทำอาหารที่มี:
            </label>
            <div className="flex flex-wrap gap-2">
              {EQUIPMENT_OPTIONS.map((item) => {
                const isSelected = equipment.includes(item);
                return (
                  <button
                    key={item}
                    type="button"
                    onClick={() => toggleEquipment(item)}
                    className={`text-xs px-3 py-1.5 rounded-lg border font-medium flex items-center gap-1.5 transition-all ${
                      isSelected
                        ? 'bg-[#A8421B] text-white border-[#A8421B] shadow-xs'
                        : 'bg-white text-[#44403C] border-[#E6DDD2] hover:border-[#A8421B]/50'
                    }`}
                  >
                    {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                    <span>{item}</span>
                  </button>
                );
              })}
            </div>
            <p className="mt-1 text-[11px] text-[#78716C]">
              * หากไม่เลือก หมายถึงไม่จำกัดอุปกรณ์ (ทำได้ทุกประเภท ไม่ใช่ไม่มีอุปกรณ์)
            </p>
          </div>

          {/* Checkbox: Require all ingredients */}
          <div className="pt-1">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={requireAll}
                onChange={(e) => setRequireAll(e.target.checked)}
                className="w-4 h-4 rounded text-[#A8421B] focus:ring-[#A8421B] border-[#D6C7B8] accent-[#A8421B]"
              />
              <span className="text-xs sm:text-sm font-medium text-[#292524]">
                แสดงเฉพาะเมนูที่วัตถุดิบครบตามสูตร
              </span>
            </label>
          </div>

          {/* Validation Notice if Empty */}
          {validationError && (
            <div className="p-2.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
              <span>{validationError}</span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full py-2.5 px-4 bg-[#A8421B] hover:bg-[#8D3716] active:bg-[#732B10] text-white font-semibold rounded-xl text-sm transition-all flex items-center justify-center gap-2 shadow-xs cursor-pointer"
          >
            <Search className="w-4 h-4" />
            <span>ค้นเมนู</span>
          </button>
        </form>
      )}
    </div>
  );
};
