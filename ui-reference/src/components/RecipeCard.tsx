import React, { useState } from 'react';
import { Recipe, Source } from '../data/scenariosData';
import { ChevronDown, ChevronUp, Check, AlertTriangle, FileText, ExternalLink, MessageSquare, Utensils } from 'lucide-react';

interface RecipeCardProps {
  recipe: Recipe;
  sources: Source[];
  onSelectRecipe: (recipeId: string, recipeName: string) => void;
  isSelected?: boolean;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({
  recipe,
  sources,
  onSelectRecipe,
  isSelected,
}) => {
  const [showSteps, setShowSteps] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);

  // Filter sources belonging to this recipe
  const matchingSources = sources.filter((s) => s.recipe_id === recipe.recipe_id);
  const displaySources = matchingSources.length > 0 ? matchingSources : sources;

  // Badge mapping
  const renderBadge = () => {
    if (recipe.ingredient_match === 'complete') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
          <Check className="w-3 h-3 stroke-[3]" />
          <span>วัตถุดิบครบตามสูตร</span>
        </span>
      );
    }
    if (recipe.ingredient_match === 'missing') {
      const count = recipe.missing_ingredients.length;
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300">
          <AlertTriangle className="w-3 h-3" />
          <span>ยังขาด {count} รายการ</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-stone-100 text-stone-700 border border-stone-300">
        <span>ℹ️ ข้อมูลยังไม่พอ</span>
      </span>
    );
  };

  // Equipment match mapping
  const renderEquipmentStatus = () => {
    const eqList = recipe.equipment.length > 0 ? recipe.equipment.join(', ') : 'ไม่ระบุ';
    if (recipe.equipment_match === 'compatible') {
      return (
        <span className="text-emerald-700 font-medium">
          ✅ อุปกรณ์ตรงกับสูตร ({eqList})
        </span>
      );
    }
    if (recipe.equipment_match === 'incompatible') {
      return (
        <span className="text-red-700 font-medium">
          ❌ อุปกรณ์ไม่ตรงกับสูตร (สูตรกำหนดใช้: {eqList})
        </span>
      );
    }
    if (recipe.equipment_match === 'unrestricted') {
      return (
        <span className="text-stone-600">
          🍳 อุปกรณ์ที่สูตรใช้: {eqList}
        </span>
      );
    }
    return <span className="text-stone-500">❓ ไม่ทราบข้อมูลอุปกรณ์</span>;
  };

  return (
    <div
      className={`bg-white border rounded-2xl p-4 md:p-5 mb-4 transition-all shadow-xs ${
        isSelected
          ? 'border-[#A8421B] ring-2 ring-[#A8421B]/15 bg-[#FFFDFB]'
          : 'border-[#E6DDD2] hover:border-[#D6C7B8]'
      }`}
    >
      {/* Title & Badge */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2.5 mb-2.5">
        <h3 className="text-base md:text-lg font-bold text-[#292524] leading-snug">
          {recipe.name}
        </h3>
        <div className="shrink-0">{renderBadge()}</div>
      </div>

      {/* Meta info: Servings & Equipment */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs md:text-sm text-[#57534E] mb-3.5 pb-2.5 border-b border-[#F0EAE1]">
        <div>
          🍽️ <strong>จำนวนเสิร์ฟ:</strong>{' '}
          {recipe.servings ? recipe.servings : 'สูตรไม่ได้ระบุจำนวนเสิร์ฟ'}
        </div>
        <div className="flex items-center gap-1">{renderEquipmentStatus()}</div>
      </div>

      {/* Matched vs Missing ingredients breakdown */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-3">
        {/* Matched */}
        <div className="p-3 bg-emerald-50/70 border border-emerald-200/80 rounded-xl">
          <p className="text-xs font-bold text-emerald-800 mb-1 flex items-center gap-1">
            <Check className="w-3.5 h-3.5 stroke-[2.5]" />
            <span>วัตถุดิบที่คุณมี:</span>
          </p>
          <p className="text-xs text-emerald-950 font-medium">
            {recipe.matched_ingredients.length > 0
              ? recipe.matched_ingredients.join(', ')
              : 'ไม่มีระบุ'}
          </p>
        </div>

        {/* Missing */}
        <div className="p-3 bg-rose-50/70 border border-rose-200/80 rounded-xl">
          <p className="text-xs font-bold text-rose-800 mb-1 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>วัตถุดิบ/เครื่องปรุงที่ยังขาด:</span>
          </p>
          {recipe.missing_ingredients.length > 0 ? (
            <p className="text-xs text-rose-950 font-medium">
              {recipe.missing_ingredients.join(', ')}
            </p>
          ) : (
            <p className="text-xs text-stone-500 italic">
              🎉 ไม่มีวัตถุดิบที่ขาดตามสูตร
            </p>
          )}
        </div>
      </div>

      {/* Quantity Disclaimer if unknown */}
      {recipe.quantity_check === 'unknown' && (
        <div className="px-3 py-2 bg-[#FAF5F0] border-l-3 border-[#D97706] rounded-r-lg text-xs text-[#78350F] mb-3.5 leading-relaxed">
          ⚠️ <strong>หมายเหตุ:</strong> ตรวจสอบเฉพาะรายชื่อวัตถุดิบ ยังไม่ได้ตรวจว่าปริมาณที่คุณมีเพียงพอตามสูตรหรือไม่
        </div>
      )}

      {/* Inline Expander: Steps & Ingredients */}
      <div className="border border-[#E6DDD2] rounded-xl overflow-hidden mb-2.5">
        <button
          type="button"
          onClick={() => setShowSteps(!showSteps)}
          className="w-full px-3.5 py-2.5 bg-[#FAF5F0] hover:bg-[#F3E8DE] flex items-center justify-between text-left text-xs md:text-sm font-semibold text-[#292524] transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <span>📖</span>
            <span>ดูวิธีทำและส่วนผสมทั้งหมด</span>
          </span>
          <span className="text-[#78716C]">
            {showSteps ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </span>
        </button>

        {showSteps && (
          <div className="p-3.5 bg-white text-xs md:text-sm space-y-3">
            <div>
              <p className="font-bold text-[#292524] mb-1.5">ส่วนผสมตามสูตรต้นฉบับ:</p>
              <ul className="list-disc list-inside space-y-1 text-[#44403C]">
                {recipe.ingredients.map((ing, i) => (
                  <li key={i}>
                    <span className="font-medium">{ing.name}</span>: {ing.amount}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <p className="font-bold text-[#292524] mb-1.5">ขั้นตอนการทำ:</p>
              <ol className="list-decimal list-inside space-y-1.5 text-[#44403C]">
                {recipe.steps.map((st, i) => (
                  <li key={i} className="leading-relaxed">
                    <span>{st}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        )}
      </div>

      {/* Inline Expander: Evidence & Citations */}
      <div className="border border-[#E6DDD2] rounded-xl overflow-hidden mb-3.5">
        <button
          type="button"
          onClick={() => setShowEvidence(!showEvidence)}
          className="w-full px-3.5 py-2 bg-[#FAF5F0] hover:bg-[#F3E8DE] flex items-center justify-between text-left text-xs font-semibold text-[#57534E] transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-[#A8421B]" />
            <span>ดูหลักฐานจากสูตร (Evidence & Citations)</span>
          </span>
          <span className="text-[#78716C]">
            {showEvidence ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </span>
        </button>

        {showEvidence && (
          <div className="p-3 bg-white space-y-2 text-xs">
            {displaySources.length > 0 ? (
              displaySources.map((src, i) => (
                <div key={i} className="bg-[#FAF5F0] border border-[#E6DDD2] p-2.5 rounded-lg space-y-1.5">
                  <div className="font-bold text-[#292524]">
                    📄 {src.document_name} &bull; หัวข้อ: {src.section}
                    {src.page !== null && ` | หน้า: ${src.page}`}
                  </div>
                  <div className="bg-white border-l-2 border-[#A8421B] p-2 text-[#44403C] italic whitespace-pre-wrap break-words">
                    "{src.excerpt}"
                  </div>
                  {src.source_url ? (
                    <a
                      href={src.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-[#A8421B] hover:underline flex items-center gap-1 font-medium mt-1"
                    >
                      <ExternalLink className="w-3 h-3" />
                      <span>แหล่งที่มาต้นฉบับ</span>
                    </a>
                  ) : (
                    <p className="text-[11px] text-[#78716C]">
                      🔒 ข้อมูลออฟไลน์ในคลังตัวอย่าง (ไม่มี URL ภายนอก)
                    </p>
                  )}
                </div>
              ))
            ) : (
              <p className="text-stone-500 italic">ไม่มีหลักฐานประกอบผลลัพธ์นี้</p>
            )}
          </div>
        )}
      </div>

      {/* Action Row: Follow-up button */}
      <div className="flex items-center justify-between pt-1">
        <button
          type="button"
          onClick={() => onSelectRecipe(recipe.recipe_id, recipe.name)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            isSelected
              ? 'bg-[#A8421B] text-white'
              : 'bg-[#FAF5F0] hover:bg-[#F3E8DE] border border-[#E6DDD2] text-[#A8421B]'
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>{isSelected ? '✓ เลือกเมนูนี้อยู่' : 'ถามต่อเกี่ยวกับเมนูนี้'}</span>
        </button>

        <span className="text-[11px] text-[#A8A29E]">ID: {recipe.recipe_id}</span>
      </div>
    </div>
  );
};
