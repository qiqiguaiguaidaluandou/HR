'use client';

import React, { useState, useEffect } from 'react';
import { Image as ImageIcon, History, Bookmark, Loader2 } from 'lucide-react';
import { SidebarItem } from '@/components/SidebarItem';
import { AspectRatioButton } from '@/components/AspectRatioButton';
import { DescriptionInput } from '@/components/DescriptionInput';
import { ReferenceUploader } from '@/components/ReferenceUploader';
import { ImageCountSelector } from '@/components/ImageCountSelector';
import { GenerateButton } from '@/components/GenerateButton';
import { GalleryHeader } from '@/components/GalleryHeader';
import { EmptyState } from '@/components/EmptyState';
import { ImageList } from '@/components/ImageList';
import { api } from '@/lib/api';

interface ImageItem {
  id: number;
  prompt: string;
  image_url: string;
  aspect_ratio: string;
  created_at: string;
  is_favorite: boolean;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState('generate');
  const [description, setDescription] = useState('');
  const [aspectRatio, setAspectRatio] = useState('1:1');
  const [imageCount, setImageCount] = useState(1);
  const [images, setImages] = useState<ImageItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const aspectRatios = ['1:1', '4:3', '3:4', '3:2', '16:9', '9:16'];

  // Load images from API
  const loadImages = async (favoriteOnly: boolean = false) => {
    setIsLoading(true);
    try {
      const response = await api.getImages(favoriteOnly);
      setImages(response.images || []);
    } catch (error) {
      console.error('Failed to load images:', error);
      setImages([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Load images when tab changes
  useEffect(() => {
    if (activeTab === 'history' || activeTab === 'bookmarks') {
      loadImages(activeTab === 'bookmarks');
    }
  }, [activeTab]);

  // Generate images
  const handleGenerate = async () => {
    if (!description.trim()) return;

    setIsGenerating(true);
    try {
      const response = await api.generateImages(description, aspectRatio, imageCount);
      if (response.images && response.images.length > 0) {
        setImages(prev => [...response.images, ...prev]);
        setActiveTab('history');
        setDescription('');
      }
    } catch (error) {
      console.error('Failed to generate images:', error);
      alert('图片生成失败，请稍后重试');
    } finally {
      setIsGenerating(false);
    }
  };

  // Toggle favorite
  const handleToggleFavorite = async (id: number) => {
    try {
      await api.toggleFavorite(id);
      setImages(prev => prev.map(img =>
        img.id === id ? { ...img, is_favorite: !img.is_favorite } : img
      ));
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  // Delete image
  const handleDelete = async (id: number) => {
    try {
      await api.deleteImage(id);
      setImages(prev => prev.filter(img => img.id !== id));
    } catch (error) {
      console.error('Failed to delete image:', error);
    }
  };

  // Get favorite images
  const favoriteImages = images.filter(img => img.is_favorite);

  // Render content
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
          {isLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
            </div>
          ) : (
            <ImageList
              images={images}
              emptyText="暂无生成记录"
              onToggleFavorite={handleToggleFavorite}
              onDelete={handleDelete}
            />
          )}
        </>
      );
    } else if (activeTab === 'bookmarks') {
      return (
        <>
          <div className="h-16 border-b border-gray-200 px-8 flex items-center bg-white">
            <h2 className="text-lg font-semibold text-gray-800">我的收藏</h2>
            <span className="ml-2 text-sm text-gray-400">({favoriteImages.length}张)</span>
          </div>
          {isLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
            </div>
          ) : (
            <ImageList
              images={favoriteImages}
              emptyText="暂无收藏图片"
              onToggleFavorite={handleToggleFavorite}
              onDelete={handleDelete}
            />
          )}
        </>
      );
    }
    return null;
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-800 font-sans overflow-hidden">
      <aside className="w-20 flex flex-col items-center py-6 gap-6 border-r border-gray-200 bg-white">
        <div className="flex flex-col gap-4 flex-1">
          <SidebarItem icon={<ImageIcon size={22} />} label="图片生成" active={activeTab === 'generate'} onClick={() => setActiveTab('generate')} />
          <SidebarItem icon={<History size={22} />} label="生成历史" active={activeTab === 'history'} onClick={() => setActiveTab('history')} />
          <SidebarItem icon={<Bookmark size={22} />} label="我的收藏" active={activeTab === 'bookmarks'} onClick={() => setActiveTab('bookmarks')} />
        </div>
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
              <GenerateButton onClick={handleGenerate} isLoading={isGenerating} disabled={!description.trim() || isGenerating} />
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
