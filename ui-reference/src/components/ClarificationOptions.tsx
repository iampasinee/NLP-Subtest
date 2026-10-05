import React from 'react';
import { ClarificationOption } from '../data/scenariosData';
import { HelpCircle, ArrowRight } from 'lucide-react';

interface ClarificationOptionsProps {
  options: ClarificationOption[];
  onSelectOption: (recipeId: string, recipeName: string) => void;
}

export const ClarificationOptions: React.FC<ClarificationOptionsProps> = ({
  options,
  onSelectOption,
}) => {
  return (
    <div className="p-4 bg-amber-50/90 border border-amber-300 rounded-2xl mb-4 space-y-2.5 shadow-xs">
      <div className="flex items-center gap-2 text-amber-900 font-semibold text-xs md:text-sm">
        <HelpCircle className="w-4 h-4 text-amber-700" />
        <span>คำถามของคุณอาจหมายถึงหลายเมนู กรุณาเลือกเมนูที่ต้องการ:</span>
      </div>

      <div className="flex flex-wrap gap-2 pt-1">
        {options.map((opt) => (
          <button
            key={opt.recipe_id}
            type="button"
            onClick={() => onSelectOption(opt.recipe_id, opt.name)}
            className="flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-[#FFF9F2] border border-amber-300 hover:border-[#A8421B] rounded-xl text-xs md:text-sm font-bold text-[#292524] transition-all shadow-xs group"
          >
            <span>👉 {opt.name}</span>
            <ArrowRight className="w-3.5 h-3.5 text-[#A8421B] group-hover:translate-x-0.5 transition-transform" />
          </button>
        ))}
      </div>
    </div>
  );
};
