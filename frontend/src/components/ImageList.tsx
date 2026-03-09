import React from 'react';
import { Image as ImageIcon } from 'lucide-react';
import { ImageCard } from './ImageCard';

interface ImageItem {
  id: number;
  prompt: string;
  image_url: string;
  aspect_ratio: string;
  created_at: string;
  is_favorite: boolean;
}

interface ImageListProps {
  images: ImageItem[];
  emptyText: string;
  onToggleFavorite: (id: number) => void;
  onDelete: (id: number) => void;
}

export function ImageList({ images, emptyText, onToggleFavorite, onDelete }: ImageListProps) {
  if (images.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        <div className="flex flex-col items-center gap-4">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center">
            <ImageIcon size={40} className="text-gray-300" />
          </div>
          <p className="text-gray-400">{emptyText}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {images.map((image) => (
          <ImageCard
            key={image.id}
            image={image}
            onToggleFavorite={onToggleFavorite}
            onDelete={onDelete}
          />
        ))}
      </div>
    </div>
  );
}
