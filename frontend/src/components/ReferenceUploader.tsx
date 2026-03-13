import React, { useRef, useState } from 'react';
import { Upload, X, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

interface ReferenceUploaderProps {
  value?: string;
  onChange?: (url: string) => void;
}

export function ReferenceUploader({ value, onChange }: ReferenceUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string>(value || '');
  const [error, setError] = useState<string>('');

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('请上传图片文件');
      return;
    }

    // Validate file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      setError('图片大小不能超过 2MB');
      return;
    }

    setError('');
    setIsUploading(true);

    try {
      const result = await api.uploadImage(file);
      const imageUrl = result.url;

      // Create preview URL
      const preview = URL.createObjectURL(file);
      setPreviewUrl(preview);

      if (onChange) {
        onChange(imageUrl);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败');
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemove = () => {
    setPreviewUrl('');
    if (onChange) {
      onChange('');
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold text-gray-800">上传参考图<span className="text-gray-400 font-normal ml-1">(非必选)</span></h2>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />

      {previewUrl ? (
        <div className="relative rounded-xl overflow-hidden border border-gray-200">
          <img
            src={previewUrl}
            alt="参考图预览"
            className="w-full h-40 object-cover"
          />
          <button
            type="button"
            onClick={handleRemove}
            className="absolute top-2 right-2 p-1.5 bg-black/50 rounded-full hover:bg-black/70 transition-colors"
          >
            <X size={16} className="text-white" />
          </button>
        </div>
      ) : (
        <div
          onClick={handleClick}
          className="border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center gap-3 hover:border-gray-300 hover:bg-gray-50 transition-all cursor-pointer group"
        >
          {isUploading ? (
            <>
              <Loader2 size={24} className="text-gray-400 animate-spin" />
              <p className="text-xs text-gray-400">上传中...</p>
            </>
          ) : (
            <>
              <div className="p-3 bg-gray-100 rounded-full group-hover:scale-110 transition-transform">
                <Upload size={24} className="text-gray-400 group-hover:text-gray-500" />
              </div>
              <p className="text-xs text-gray-400 group-hover:text-gray-500">点击或拖拽上传参考图</p>
            </>
          )}
        </div>
      )}

      {error && (
        <p className="text-xs text-red-500">{error}</p>
      )}
    </div>
  );
}
