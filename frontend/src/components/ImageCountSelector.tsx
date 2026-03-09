import React from 'react';

interface ImageCountSelectorProps {
  value: number;
  onChange: (value: number) => void;
}

export function ImageCountSelector({ value, onChange }: ImageCountSelectorProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-800">输出张数</h2>
        {/* <span className="text-xs font-mono text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">{value} 张</span> */}
      </div>
      <div className="flex gap-2">
        {[1, 2, 3, 4].map((num) => (
          <button
            key={num}
            onClick={() => onChange(num)}
            className={`flex-1 py-2.5 rounded-xl border text-sm font-medium transition-all duration-200 ${
              value === num
                ? "bg-indigo-50 border-indigo-500 text-indigo-600"
                : "bg-white border-gray-200 text-gray-500 hover:border-gray-300 hover:text-gray-600"
            }`}
          >
            {num}
          </button>
        ))}
      </div>
    </div>
  );
}
