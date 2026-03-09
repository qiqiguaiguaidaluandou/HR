import React from 'react';
import { Type, Info } from 'lucide-react';

interface DescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function DescriptionInput({ value, onChange }: DescriptionInputProps) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-800 flex items-center gap-2">图片描述</h2>
        {/* <button className="text-xs text-gray-400 hover:text-gray-600 transition-colors flex items-center gap-1">
          使用说明 <Info size={12} />
        </button> */}
      </div>
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value.slice(0, 800))}
          placeholder="请描述你想生成的图片"
          className="w-full h-32 bg-white border border-gray-200 rounded-xl p-4 text-sm text-gray-700 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500/50 transition-all resize-none"
        />
        <button className="absolute bottom-3 left-4"><Type size={16} className="text-gray-400" /></button>
        <div className="absolute bottom-3 right-4 text-[10px] text-gray-400 font-mono">{value.length}/800</div>
      </div>
    </div>
  );
}
