import React from 'react';
import { Sparkles, Loader2 } from 'lucide-react';

interface GenerateButtonProps {
  onClick?: () => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function GenerateButton({ onClick, isLoading, disabled }: GenerateButtonProps) {
  return (
    <div className="mt-auto pt-4">
      <button
        onClick={onClick}
        disabled={disabled || isLoading}
        className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-300 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <Loader2 size={18} className="animate-spin" />
        ) : (
          <Sparkles size={18} />
        )}
        {isLoading ? '生成中...' : '立即生成'}
      </button>
    </div>
  );
}
