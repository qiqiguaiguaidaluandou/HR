import React from 'react';

interface SidebarItemProps {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
}

export function SidebarItem({ icon, label, active, onClick }: SidebarItemProps) {
  return (
    <div className="relative group flex items-center justify-center">
      <button
        onClick={onClick}
        className={`p-3 rounded-xl transition-all duration-200 cursor-pointer ${
          active
            ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20"
            : "text-gray-500 hover:bg-gray-100 hover:text-gray-700"
        }`}
      >
        {icon}
      </button>
      <div className="absolute left-16 px-3 py-1.5 bg-gray-800 text-white text-xs rounded-md whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 shadow-lg">
        {label}
        <div className="absolute top-1/2 -left-1 -translate-y-1/2 w-2 h-2 bg-gray-800 rotate-45" />
      </div>
    </div>
  );
}
