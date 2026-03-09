import React from 'react';
import { Upload } from 'lucide-react';

export function ReferenceUploader() {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold text-gray-800">上传参考图<span className="text-gray-400 font-normal ml-1">(非必选)</span></h2>
      <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center gap-3 hover:border-gray-300 hover:bg-gray-50 transition-all cursor-pointer group">
        <div className="p-3 bg-gray-100 rounded-full group-hover:scale-110 transition-transform">
          <Upload size={24} className="text-gray-400 group-hover:text-gray-500" />
        </div>
        <p className="text-xs text-gray-400 group-hover:text-gray-500">点击或拖拽上传参考图</p>
      </div>
    </div>
  );
}
