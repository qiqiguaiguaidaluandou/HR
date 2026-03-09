import React from 'react';
import { Sparkles } from 'lucide-react';

export function GenerateButton() {
  return (
    <div className="mt-auto pt-4">
      {/* <div className="mb-3 text-[10px] text-gray-400 flex items-center gap-1">(消耗 0 算力)</div> */}
      <button className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2">
        <Sparkles size={18} />立即生成
      </button>
    </div>
  );
}
