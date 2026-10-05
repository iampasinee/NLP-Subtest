import React from 'react';
import { AlertTriangle, Info, AlertOctagon, RotateCw } from 'lucide-react';

interface StatusNoticeProps {
  status: 'ok' | 'no_match' | 'insufficient_context' | 'needs_clarification' | 'error';
  answer: string;
  errorCode?: string | null;
  onRetry?: () => void;
}

export const StatusNotice: React.FC<StatusNoticeProps> = ({
  status,
  answer,
  errorCode,
  onRetry,
}) => {
  if (status === 'no_match') {
    return (
      <div className="p-3.5 bg-amber-50/80 border border-amber-200 rounded-xl mb-4 text-xs md:text-sm text-amber-900 flex items-start gap-2.5 shadow-xs">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold mb-0.5">ไม่พบสูตรที่ตรงเงื่อนไข</p>
          <p className="text-amber-800 leading-relaxed">{answer}</p>
        </div>
      </div>
    );
  }

  if (status === 'insufficient_context') {
    return (
      <div className="p-3.5 bg-sky-50/80 border border-sky-200 rounded-xl mb-4 text-xs md:text-sm text-sky-950 flex items-start gap-2.5 shadow-xs">
        <Info className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold mb-0.5">ข้อมูลในเอกสารยังไม่เพียงพอ</p>
          <p className="text-sky-900 leading-relaxed">{answer}</p>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl mb-4 text-xs md:text-sm text-rose-950 space-y-2 shadow-xs">
        <div className="flex items-start gap-2.5">
          <AlertOctagon className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold text-rose-900">เกิดข้อผิดพลาดในการประมวลผล</p>
            <p className="text-rose-800 leading-relaxed">{answer}</p>
            {errorCode && (
              <p className="font-mono text-[11px] text-rose-600 mt-1">
                Error Code: {errorCode}
              </p>
            )}
          </div>
        </div>

        {onRetry && (
          <div className="pt-1">
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold transition-all shadow-xs"
            >
              <RotateCw className="w-3.5 h-3.5" />
              <span>ลองใหม่อีกครั้ง (Retry)</span>
            </button>
          </div>
        )}
      </div>
    );
  }

  return null;
};
