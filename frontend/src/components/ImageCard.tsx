import React from 'react';
import { Bookmark, Trash2, Download } from 'lucide-react';

interface ImageItem {
  id: number;
  prompt: string;
  imageUrl: string;
  aspectRatio: string;
  createdAt: string;
  isFavorite: boolean;
}

interface ImageCardProps {
  image: ImageItem;
  onToggleFavorite: (id: number) => void;
  onDelete: (id: number) => void;
}

export function ImageCard({ image, onToggleFavorite, onDelete }: ImageCardProps) {
  return (
    <div className="group relative bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-all">
      {/* 图片 */}
      <div className="aspect-square bg-gray-100 relative overflow-hidden">
        <img
          src={image.imageUrl}
          alt={image.prompt}
          className="w-full h-full object-cover"
        />
        {/* 悬浮操作栏 */}
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button
            onClick={() => onToggleFavorite(image.id)}
            className="p-2 bg-white/90 rounded-lg hover:bg-white transition-colors"
            title={image.isFavorite ? "取消收藏" : "收藏"}
          >
            <Bookmark size={18} className={image.isFavorite ? "fill-indigo-600 text-indigo-600" : "text-gray-700"} />
          </button>
          <button
            className="p-2 bg-white/90 rounded-lg hover:bg-white transition-colors"
            title="下载"
          >
            <Download size={18} className="text-gray-700" />
          </button>
          <button
            onClick={() => onDelete(image.id)}
            className="p-2 bg-white/90 rounded-lg hover:bg-white transition-colors"
            title="删除"
          >
            <Trash2 size={18} className="text-red-500" />
          </button>
        </div>
      </div>
      {/* 信息 */}
      <div className="p-3">
        <p className="text-sm text-gray-600 truncate">{image.prompt}</p>
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-gray-400">{image.aspectRatio}</span>
          <span className="text-xs text-gray-400">{image.createdAt}</span>
        </div>
      </div>
    </div>
  );
}
