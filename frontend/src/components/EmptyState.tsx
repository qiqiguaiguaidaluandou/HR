import React from 'react';
import { Image as ImageIcon, Sparkles } from 'lucide-react';

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="flex flex-col items-center gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div className="relative">
          <div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center border border-gray-200">
            <div className="w-20 h-20 bg-gray-200 rounded-2xl flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-transparent" />
              <ImageIcon size={40} className="text-gray-400" />
            </div>
          </div>
          <Sparkles size={16} className="absolute -top-2 -right-2 text-indigo-400/40 animate-pulse" />
          <Sparkles size={12} className="absolute top-4 -left-4 text-gray-400 animate-pulse delay-75" />
        </div>
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-600 mb-2">当前数据为空，快去生成吧!</h3>
          <p className="text-sm text-gray-400 max-w-[280px]">在左侧输入描述词并调整参数，开启你的 AI 创作之旅</p>
        </div>
        <button className="px-6 py-2.5 bg-white hover:bg-gray-50 border border-gray-200 text-gray-500 hover:text-gray-700 rounded-xl text-sm font-medium transition-all">
          查看示例作品
        </button>
      </div>
    </div>
  );
}
