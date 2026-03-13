'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, Lock, Eye, EyeOff, Settings, CheckCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export default function SettingsPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Redirect if not authenticated
  if (!authLoading && !isAuthenticated) {
    router.push('/login');
    return null;
  }

  if (authLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (newPassword !== confirmPassword) {
      setError('新密码和确认密码不一致');
      return;
    }

    if (newPassword.length < 6) {
      setError('密码长度至少6位');
      return;
    }

    setLoading(true);
    try {
      await api.changePassword(oldPassword, newPassword);
      setMessage('密码修改成功');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError(err instanceof Error ? err.message : '修改密码失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-md mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <Settings className="w-8 h-8 text-indigo-600" />
          <h1 className="text-2xl font-bold text-gray-800">账户设置</h1>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="mb-6 pb-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">账户信息</h2>
            <div className="space-y-2 text-sm text-gray-600">
              <p><span className="font-medium">用户名：</span>{user?.username}</p>
              <p><span className="font-medium">邮箱：</span>{user?.email}</p>
            </div>
          </div>

          <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Lock size={18} />
            修改密码
          </h2>

          {message && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm flex items-center gap-2">
              <CheckCircle size={16} />
              {message}
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">当前密码</label>
              <div className="relative">
                <input
                  type={showOldPassword ? 'text' : 'password'}
                  required
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  className="w-full px-4 py-2 pr-10 border border-gray-200 rounded-lg"
                  placeholder="请输入当前密码"
                />
                <button
                  type="button"
                  onClick={() => setShowOldPassword(!showOldPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                >
                  {showOldPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">新密码</label>
              <div className="relative">
                <input
                  type={showNewPassword ? 'text' : 'password'}
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-2 pr-10 border border-gray-200 rounded-lg"
                  placeholder="请输入新密码（至少6位）"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                >
                  {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">确认新密码</label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-200 rounded-lg"
                placeholder="请再次输入新密码"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {loading ? <><Loader2 size={18} className="animate-spin" />保存中...</> : '保存'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
