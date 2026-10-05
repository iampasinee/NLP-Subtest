/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Header } from './components/Header';
import { InputSection } from './components/InputSection';
import { SamplePrompts } from './components/SamplePrompts';
import { RecipeCard } from './components/RecipeCard';
import { StatusNotice } from './components/StatusNotice';
import { ClarificationOptions } from './components/ClarificationOptions';
import { ScenarioSandbox } from './components/ScenarioSandbox';
import { DeliverablesViewer } from './components/DeliverablesViewer';
import { RAGResponse, resolveMockQuery } from './data/scenariosData';
import { Send, X, RefreshCw } from 'lucide-react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: RAGResponse;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'app' | 'scenarios' | 'deliverables'>('app');

  // Input states
  const [ingredients, setIngredients] = useState<string>('');
  const [equipment, setEquipment] = useState<string[]>([]);
  const [requireAll, setRequireAll] = useState<boolean>(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Selected recipe context for follow-up questions
  const [selectedRecipeId, setSelectedRecipeId] = useState<string | null>(null);
  const [selectedRecipeName, setSelectedRecipeName] = useState<string | null>(null);

  // Chat message history
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatPrompt, setChatPrompt] = useState<string>('');

  // Reset application state (FE-10)
  const handleReset = () => {
    setMessages([]);
    setIngredients('');
    setEquipment([]);
    setRequireAll(false);
    setSelectedRecipeId(null);
    setSelectedRecipeName(null);
    setValidationError(null);
    setChatPrompt('');
  };

  // Unified Query Processor
  const executeQuery = (
    queryText: string,
    ingText: string = ingredients,
    eqList: string[] = equipment,
    reqAll: boolean = requireAll,
    targetRecipeId: string | null = selectedRecipeId
  ) => {
    const cleanQuery = queryText.trim();
    const cleanIng = ingText.trim();

    if (!cleanQuery && !cleanIng) {
      setValidationError('กรุณาระบุวัตถุดิบหรือคำถามก่อนค้น');
      return;
    }

    setValidationError(null);

    // Format user display text
    let userDisplayText = cleanQuery || `ค้นวัตถุดิบ: ${cleanIng}`;
    if (eqList.length > 0 && !cleanQuery) {
      userDisplayText += ` (อุปกรณ์: ${eqList.join(', ')})`;
    }
    if (reqAll && !cleanQuery) {
      userDisplayText += ' [ตัวกรอง: วัตถุดิบครบตามสูตร]';
    }

    const userMsgId = `user_${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      role: 'user',
      content: userDisplayText,
    };

    // Call Mock Resolver with identical logic as Python MockAdapter
    const resp = resolveMockQuery(cleanQuery, cleanIng, eqList, reqAll, targetRecipeId);

    const asstMsgId = `asst_${Date.now() + 1}`;
    const asstMsg: ChatMessage = {
      id: asstMsgId,
      role: 'assistant',
      content: resp.answer,
      response: resp,
    };

    setMessages((prev) => [...prev, userMsg, asstMsg]);
    setChatPrompt('');
  };

  // Handle sample prompt click
  const handleSelectSample = (text: string, eq: string[], reqAll: boolean) => {
    setIngredients(text);
    setEquipment(eq);
    setRequireAll(reqAll);
    executeQuery(text, text, eq, reqAll, null);
  };

  // Handle recipe card selection for follow-up
  const handleSelectRecipe = (rId: string, rName: string) => {
    setSelectedRecipeId(rId);
    setSelectedRecipeName(rName);
  };

  // Handle clarification selection
  const handleClarifyOption = (rId: string, rName: string) => {
    setSelectedRecipeId(rId);
    setSelectedRecipeName(rName);
    executeQuery(`ขอดูวิธีทำของ ${rName}`, ingredients, equipment, requireAll, rId);
  };

  // Handle retry
  const handleRetry = () => {
    const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUserMsg) {
      executeQuery(lastUserMsg.content, ingredients, equipment, requireAll, selectedRecipeId);
    }
  };

  return (
    <div className="min-h-screen bg-[#FFF9F2] text-[#292524] py-6 px-3 sm:px-4 md:px-6">
      <main className="max-w-3xl mx-auto">
        {/* Header & Tabs */}
        <Header
          onReset={handleReset}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        {/* Tab 1: Interactive App Preview */}
        {activeTab === 'app' && (
          <div>
            {/* Input Form Section (ข้อมูลที่ฉันมี) */}
            <InputSection
              ingredients={ingredients}
              setIngredients={setIngredients}
              equipment={equipment}
              setEquipment={setEquipment}
              requireAll={requireAll}
              setRequireAll={setRequireAll}
              onSearch={() => executeQuery('', ingredients, equipment, requireAll, selectedRecipeId)}
              validationError={validationError}
            />

            {/* Active Selected Recipe Context Banner */}
            {selectedRecipeName && (
              <div className="bg-[#FAF5F0] border border-[#A8421B]/40 rounded-xl px-3.5 py-2 mb-4 flex items-center justify-between gap-2 text-xs md:text-sm shadow-xs">
                <div className="flex items-center gap-1.5 text-[#292524]">
                  <span className="text-base">📌</span>
                  <span>
                    กำลังเจาะจงถามเกี่ยวกับเมนู: <strong>{selectedRecipeName}</strong>
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setSelectedRecipeId(null);
                    setSelectedRecipeName(null);
                  }}
                  className="flex items-center gap-1 text-xs text-[#78716C] hover:text-red-700 font-medium"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>ปลดเลือก</span>
                </button>
              </div>
            )}

            {/* Initial State Prompts if no conversation yet */}
            {messages.length === 0 && (
              <SamplePrompts onSelectPrompt={handleSelectSample} />
            )}

            {/* Chat Containers / Results */}
            {messages.length > 0 && (
              <div className="space-y-4 mb-5">
                {messages.map((msg) => {
                  const isUser = msg.role === 'user';
                  const resp = msg.response;

                  return (
                    <div
                      key={msg.id}
                      className={`flex gap-3 items-start ${
                        isUser ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {!isUser && (
                        <div className="w-8 h-8 rounded-full bg-[#A8421B] text-white flex items-center justify-center text-sm font-bold shrink-0 shadow-xs">
                          🍳
                        </div>
                      )}

                      <div className={`max-w-2xl ${isUser ? 'w-auto' : 'w-full'}`}>
                        {/* Message Bubble */}
                        <div
                          className={`rounded-2xl p-3.5 text-xs md:text-sm leading-relaxed shadow-xs ${
                            isUser
                              ? 'bg-[#292524] text-white rounded-tr-xs'
                              : 'bg-white border border-[#E6DDD2] text-[#292524] rounded-tl-xs'
                          }`}
                        >
                          <p>{msg.content}</p>
                        </div>

                        {/* If Assistant response with structured data */}
                        {!isUser && resp && (
                          <div className="mt-3 space-y-3">
                            {/* Status Notices (No match, Insufficient context, Error) */}
                            {resp.status !== 'ok' && (
                              <StatusNotice
                                status={resp.status}
                                answer={resp.answer}
                                errorCode={resp.error_code}
                                onRetry={handleRetry}
                              />
                            )}

                            {/* Clarification Options */}
                            {resp.status === 'needs_clarification' &&
                              resp.clarification_options && (
                                <ClarificationOptions
                                  options={resp.clarification_options}
                                  onSelectOption={handleClarifyOption}
                                />
                              )}

                            {/* Recipe Cards (up to 3 per response) */}
                            {resp.recipes && resp.recipes.length > 0 && (
                              <div className="space-y-3">
                                {resp.recipes.slice(0, 3).map((rec) => (
                                  <RecipeCard
                                    key={rec.recipe_id}
                                    recipe={rec}
                                    sources={resp.sources || []}
                                    onSelectRecipe={handleSelectRecipe}
                                    isSelected={selectedRecipeId === rec.recipe_id}
                                  />
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {isUser && (
                        <div className="w-8 h-8 rounded-full bg-[#FAF5F0] border border-[#E6DDD2] text-[#292524] flex items-center justify-center text-sm shrink-0 shadow-xs">
                          🧑‍🍳
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Bottom Chat Input */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (chatPrompt.trim()) {
                  executeQuery(chatPrompt);
                }
              }}
              className="sticky bottom-3 bg-white/95 backdrop-blur-xs border border-[#E6DDD2] p-2 rounded-2xl shadow-md flex items-center gap-2 mt-4"
            >
              <input
                type="text"
                value={chatPrompt}
                onChange={(e) => setChatPrompt(e.target.value)}
                placeholder="ถามต่อเกี่ยวกับเมนู หรือบอกวัตถุดิบเพิ่มเติม..."
                className="flex-1 px-3 py-2 text-xs md:text-sm bg-transparent outline-none text-[#292524] placeholder:text-[#A8A29E]"
              />
              <button
                type="submit"
                disabled={!chatPrompt.trim()}
                className="p-2 bg-[#A8421B] hover:bg-[#8D3716] disabled:bg-[#D6C7B8] text-white rounded-xl transition-all shadow-xs cursor-pointer"
                title="ส่งข้อความ"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        )}

        {/* Tab 2: Scenario Sandbox */}
        {activeTab === 'scenarios' && <ScenarioSandbox />}

        {/* Tab 3: Python Deliverables Inspector */}
        {activeTab === 'deliverables' && <DeliverablesViewer />}
      </main>
    </div>
  );
}
