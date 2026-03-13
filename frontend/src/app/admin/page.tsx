'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, Trash2, Plus, Users, Shield } from 'lucide-react';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export default function AdminPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, loading: authLoading } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    isAdmin: false
  });

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  // Load users
  const loadUsers = async () => {
    try {
      const data = await api.getAllUsers();
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadUsers();
    }
  }, [isAuthenticated, isAdmin]);

  // Create user
  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createUser(
        newUser.username,
        newUser.email,
        newUser.password,
        newUser.isAdmin
      );
      setShowModal(false);
      setNewUser({ username: '', email: '', password: '', isAdmin: false });
      loadUsers();
    } catch (error) {
      alert('创建用户失败');
    }
  };

  // Delete user
  const handleDeleteUser = async (userId: number) => {
    if (!confirm('确定要删除这个用户吗？')) return;
    try {
      await api.deleteUser(userId);
      loadUsers();
    } catch (error) {
      alert('删除用户失败');
    }
  };

  if (authLoading || loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (!isAuthenticated || !isAdmin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-800">用户管理</h1>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500"
          >
            <Plus size={18} />
            创建用户
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户名</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">邮箱</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">角色</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-500">{user.id}</td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-800">{user.username}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{user.email}</td>
                  <td className="px-6 py-4">
                    {user.is_admin ? (
                      <span className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded-full">管理员</span>
                    ) : (
                      <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full">用户</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {user.is_active ? '活跃' : '禁用'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create User Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">创建用户</h2>
            <form onSubmit={handleCreateUser}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
                  <input
                    type="text"
                    required
                    value={newUser.username}
                    onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
                  <input
                    type="email"
                    required
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
                  <input
                    type="password"
                    required
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="isAdmin"
                    checked={newUser.isAdmin}
                    onChange={(e) => setNewUser({ ...newUser, isAdmin: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <label htmlFor="isAdmin" className="text-sm text-gray-700">设为管理员</label>
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500"
                >
                  创建
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
