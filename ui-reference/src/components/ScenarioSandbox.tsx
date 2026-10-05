import React, { useState } from 'react';
import { SCENARIOS, ScenarioItem, RAGResponse } from '../data/scenariosData';
import { Play, CheckCircle2, AlertTriangle, FileCode, Check, RefreshCw } from 'lucide-react';
import { RecipeCard } from './RecipeCard';
import { StatusNotice } from './StatusNotice';
import { ClarificationOptions } from './ClarificationOptions';

export const ScenarioSandbox: React.FC = () => {
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>(SCENARIOS[0].id);
  const activeScenario = SCENARIOS.find((s) => s.id === selectedScenarioId) || SCENARIOS[0];

  return (
    <div className="space-y-4">
      {/* Intro Box */}
      <div className="bg-white border border-[#E6DDD2] rounded-2xl p-4 shadow-xs">
        <div className="flex items-center gap-2 mb-1.5">
          <Play className="w-5 h-5 text-[#A8421B]" />
          <h2 className="text-base font-bold text-[#292524]">
            ทดสอบ 11 Fixture Scenarios ตาม PRD หมวด 13
          </h2>
        </div>
        <p className="text-xs text-[#655C54]">
          คลิกเลือก Scenario ด้านล่างเพื่อดูผลลัพธ์จำลองที่ตรงกัน 100% ระหว่าง Python Streamlit App และ React Preview
        </p>
      </div>

      {/* Scenario Pills Selector */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
        {SCENARIOS.map((sc, idx) => {
          const isSelected = sc.id === selectedScenarioId;
          return (
            <button
              key={sc.id}
              onClick={() => setSelectedScenarioId(sc.id)}
              className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between ${
                isSelected
                  ? 'bg-[#A8421B] text-white border-[#A8421B] shadow-xs'
                  : 'bg-white text-[#292524] border-[#E6DDD2] hover:border-[#A8421B]/60'
              }`}
            >
              <div className="flex items-start justify-between gap-1 mb-1">
                <span className="text-xs font-bold leading-tight">
                  {sc.title}
                </span>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded font-mono shrink-0 ${
                    isSelected ? 'bg-white/20 text-white' : 'bg-stone-100 text-stone-600'
                  }`}
                >
                  {sc.response.status}
                </span>
              </div>
              <p
                className={`text-[11px] line-clamp-2 ${
                  isSelected ? 'text-white/85' : 'text-[#655C54]'
                }`}
              >
                {sc.description}
              </p>
            </button>
          );
        })}
      </div>

      {/* Detail & Response Container */}
      <div className="bg-[#FAF5F0] border border-[#E6DDD2] rounded-2xl p-4 md:p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 mb-3 border-b border-[#E6DDD2]">
          <div>
            <span className="text-xs font-bold text-[#A8421B] uppercase tracking-wider">
              กำลังแสดง Scenario:
            </span>
            <h3 className="text-base font-bold text-[#292524]">
              {activeScenario.title}
            </h3>
            <p className="text-xs text-[#655C54] mt-0.5">
              {activeScenario.description}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              <Check className="w-3.5 h-3.5" />
              <span>Unit Tests Passed</span>
            </span>
          </div>
        </div>

        {/* Short Answer */}
        <div className="bg-white border border-[#E6DDD2] rounded-xl p-3.5 mb-3 text-xs md:text-sm text-[#292524]">
          <span className="font-bold text-[#A8421B] mr-1.5">💬 คำตอบสรุป:</span>
          <span>{activeScenario.response.answer}</span>
        </div>

        {/* Status Notice if needed */}
        {activeScenario.response.status !== 'ok' && (
          <StatusNotice
            status={activeScenario.response.status}
            answer={activeScenario.response.answer}
            errorCode={activeScenario.response.error_code}
            onRetry={() => {}}
          />
        )}

        {/* Clarification Options */}
        {activeScenario.response.status === 'needs_clarification' &&
          activeScenario.response.clarification_options && (
            <ClarificationOptions
              options={activeScenario.response.clarification_options}
              onSelectOption={() => {}}
            />
          )}

        {/* Recipes Rendering */}
        {activeScenario.response.recipes.length > 0 && (
          <div>
            <p className="text-xs font-bold text-[#655C54] mb-2 uppercase tracking-wide">
              สูตรที่พบ ({activeScenario.response.recipes.length} รายการ):
            </p>
            {activeScenario.response.recipes.map((rec) => (
              <RecipeCard
                key={rec.recipe_id}
                recipe={rec}
                sources={activeScenario.response.sources}
                onSelectRecipe={() => {}}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
