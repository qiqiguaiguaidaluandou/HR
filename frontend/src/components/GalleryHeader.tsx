import React from 'react';
import { ChevronDown, Search, Grid, List } from 'lucide-react';

interface GalleryHeaderProps {
  isFavoriteOnly: boolean;
  onFavoriteChange: (value: boolean) => void;
}

export function GalleryHeader({ isFavoriteOnly, onFavoriteChange }: GalleryHeaderProps) {
  return (
    <header className="h-16 border-b border-gray-200 px-8 flex items-center justify-between bg-white">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2 cursor-pointer group">
          <span className="text-sm font-medium text-gray-500 group-hover:text-gray-700 transition-colors">类型: 全部</span>
          <ChevronDown size={14} className="text-gray-400 group-hover:text-gray-500" />
        </div>
        <label className="flex items-center gap-2 cursor-pointer group">
          <input
            type="checkbox"
            checked={isFavoriteOnly}
            onChange={(e) => onFavoriteChange(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 bg-white text-indigo-600 focus:ring-indigo-500"
          />
          <span className="text-sm font-medium text-gray-500 group-hover:text-gray-700 transition-colors">我的收藏</span>
        </label>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input type="text" placeholder="搜索生成记录..." className="bg-white border border-gray-200 rounded-lg py-1.5 pl-9 pr-4 text-xs text-gray-600 focus:outline-none focus:border-gray-300 w-48" />
        </div>
        <div className="flex items-center bg-white border border-gray-200 rounded-lg p-1">
          <button className="p-1.5 text-indigo-600 bg-indigo-50 rounded-md"><Grid size={14} /></button>
          <button className="p-1.5 text-gray-400 hover:text-gray-600"><List size={14} /></button>
        </div>
      </div>
    </header>
  );
}
