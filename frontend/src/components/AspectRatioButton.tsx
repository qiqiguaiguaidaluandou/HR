import React from 'react';

interface AspectRatioButtonProps {
  ratio: string;
  active: boolean;
  onClick: () => void;
}

export function AspectRatioButton({ ratio, active, onClick }: AspectRatioButtonProps) {
  const getIcon = () => {
    switch (ratio) {
      case '1:1': return <div className="w-4 h-4 border-2 border-current rounded-sm" />;
      case '4:3': return <div className="w-5 h-4 border-2 border-current rounded-sm" />;
      case '3:4': return <div className="w-4 h-5 border-2 border-current rounded-sm" />;
      case '3:2': return <div className="w-5 h-3.5 border-2 border-current rounded-sm" />;
      case '16:9': return <div className="w-6 h-3.5 border-2 border-current rounded-sm" />;
      case '9:16': return <div className="w-3.5 h-6 border-2 border-current rounded-sm" />;
      default: return <div className="w-4 h-4 border-2 border-current rounded-sm" />;
    }
  };

  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-center justify-center gap-2 p-3 rounded-xl border transition-all duration-200 flex-1 min-w-[70px] ${
        active
          ? "bg-indigo-50 border-indigo-500 text-indigo-600"
          : "bg-white border-gray-200 text-gray-500 hover:border-gray-300 hover:text-gray-600"
      }`}
    >
      {getIcon()}
      <span className="text-xs font-medium">{ratio}</span>
    </button>
  );
}
