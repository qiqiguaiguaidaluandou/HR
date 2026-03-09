'use client';

import React, { useState } from 'react';
import { Image as ImageIcon, Settings, History, Bookmark, Sparkles } from 'lucide-react';
import { SidebarItem } from '@/components/SidebarItem';
import { AspectRatioButton } from '@/components/AspectRatioButton';
import { DescriptionInput } from '@/components/DescriptionInput';
import { ReferenceUploader } from '@/components/ReferenceUploader';
import { ImageCountSelector } from '@/components/ImageCountSelector';
import { GenerateButton } from '@/components/GenerateButton';
import { GalleryHeader } from '@/components/GalleryHeader';
import { EmptyState } from '@/components/EmptyState';
import { ImageList } from '@/components/ImageList';

// 模拟数据
interface ImageItem {
  id: number;
  prompt: string;
  imageUrl: string;
  aspectRatio: string;
  createdAt: string;
  isFavorite: boolean;
}

const mockImages: ImageItem[] = [
  { id: 1, prompt: "一只可爱的橘猫在阳光下玩耍", imageUrl: "https://picsum.photos/400/400?random=1", aspectRatio: "1:1", createdAt: "2024-01-15 10:30", isFavorite: true },
  { id: 2, prompt: " sunset over the ocean", imageUrl: "https://picsum.photos/400/400?random=2", aspectRatio: "16:9", createdAt: "2024-01-14 15:20", isFavorite: false },
  { id: 3, prompt: "未来城市科技感", imageUrl: "https://picsum.photos/400/400?random=3", aspectRatio: "9:16", createdAt: "2024-01-13 09:45", isFavorite: true },
  { id: 4, prompt: "山水画风景", imageUrl: "https://picsum.photos/400/400?random=4", aspectRatio: "3:2", createdAt: "2024-01-12 14:00", isFavorite: false },
  { id: 5, prompt: "抽象艺术风格", imageUrl: "https://picsum.photos/400/400?random=5", aspectRatio: "1:1", createdAt: "2024-01-11 18:30", isFavorite: true },
  { id: 6, prompt: "可爱的小狗", imageUrl: "https://picsum.photos/400/400?random=6", aspectRatio: "4:3", createdAt: "2024-01-10 11:15", isFavorite: false },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState('generate');
  const [description, setDescription] = useState('');
  const [aspectRatio, setAspectRatio] = useState('1:1');
  const [imageCount, setImageCount] = useState(1);
  const [images, setImages] = useState<ImageItem[]>(mockImages);
  const aspectRatios = ['1:1', '4:3', '3:4', '3:2', '16:9', '9:16'];

  // 切换收藏状态
  const handleToggleFavorite = (id: number) => {
    setImages(prev => prev.map(img =>
      img.id === id ? { ...img, isFavorite: !img.isFavorite } : img
    ));
  };

  // 删除图片
  const handleDelete = (id: number) => {
    setImages(prev => prev.filter(img => img.id !== id));
  };

  // 获取收藏的图片
  const favoriteImages = images.filter(img => img.isFavorite);

  // 渲染右侧内容
  const renderContent = () => {
    if (activeTab === 'generate') {
      return (
        <>
          <GalleryHeader isFavoriteOnly={false} onFavoriteChange={() => {}} />
          <EmptyState />
        </>
      );
    } else if (activeTab === 'history') {
      return (
        <>
          <div className="h-16 border-b border-gray-200 px-8 flex items-center bg-white">
            <h2 className="text-lg font-semibold text-gray-800">生成历史</h2>
            <span className="ml-2 text-sm text-gray-400">({images.length}张)</span>
          </div>
          <ImageList
            images={images}
            emptyText="暂无生成记录"
            onToggleFavorite={handleToggleFavorite}
            onDelete={handleDelete}
          />
        </>
      );
    } else if (activeTab === 'bookmarks') {
      return (
        <>
          <div className="h-16 border-b border-gray-200 px-8 flex items-center bg-white">
            <h2 className="text-lg font-semibold text-gray-800">我的收藏</h2>
            <span className="ml-2 text-sm text-gray-400">({favoriteImages.length}张)</span>
          </div>
          <ImageList
            images={favoriteImages}
            emptyText="暂无收藏图片"
            onToggleFavorite={handleToggleFavorite}
            onDelete={handleDelete}
          />
        </>
      );
    }
    return null;
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-800 font-sans overflow-hidden">
      <aside className="w-20 flex flex-col items-center py-6 gap-6 border-r border-gray-200 bg-gray-100">
        <div className="flex flex-col gap-4 flex-1">
          <SidebarItem icon={<ImageIcon size={22} />} label="图片生成" active={activeTab === 'generate'} onClick={() => setActiveTab('generate')} />
          <SidebarItem icon={<History size={22} />} label="生成历史" active={activeTab === 'history'} onClick={() => setActiveTab('history')} />
          <SidebarItem icon={<Bookmark size={22} />} label="我的收藏" active={activeTab === 'bookmarks'} onClick={() => setActiveTab('bookmarks')} />
        </div>
        {/* <div className="flex flex-col gap-4">
          <SidebarItem icon={<Settings size={22} />} label="系统设置" />
        </div> */}
      </aside>
      <main className="flex-1 flex overflow-hidden">
        {activeTab === 'generate' && (
          <section className="w-[360px] border-r border-gray-200 bg-white flex flex-col overflow-y-auto custom-scrollbar">
            <div className="p-6 flex flex-col gap-8">
              <DescriptionInput value={description} onChange={setDescription} />
              <ReferenceUploader />
              <div className="flex flex-col gap-4">
                <h2 className="text-sm font-semibold text-gray-800">比例</h2>
                <div className="grid grid-cols-3 gap-2">
                  {aspectRatios.map((ratio) => <AspectRatioButton key={ratio} ratio={ratio} active={aspectRatio === ratio} onClick={() => setAspectRatio(ratio)} />)}
                </div>
              </div>
              <ImageCountSelector value={imageCount} onChange={setImageCount} />
              <GenerateButton />
            </div>
          </section>
        )}
        <section className="flex-1 bg-gray-50 flex flex-col overflow-hidden">
          {renderContent()}
        </section>
      </main>
    </div>
  );
}
