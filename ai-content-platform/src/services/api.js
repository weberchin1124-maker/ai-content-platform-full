// src/services/api.js

const API_URL = '/api'; // 配合 Vite Proxy 設定

// 小幫手：取得 Token 並放入 Header
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token 
    ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } 
    : { 'Content-Type': 'application/json' };
};

export const api = {
  // ==========================================
  // 1. 會員系統 (Auth)
  // ==========================================
  
  // 登入
  login: async (email, password) => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    
    // 如果登入成功，把 Token 存起來！
    if (res.ok) {
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    return { status: res.status, data };
  },

  // 註冊
  register: async (username, email, password) => {
    const res = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });
    const data = await res.json();

    // 🚨 關鍵修正：如果註冊成功，直接模擬登入，儲存 Token
    if (res.ok && data.access_token) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
    }
    return data;
  },

  // 更新使用者資料
  updateUser: async (data) => {
    const res = await fetch(`${API_URL}/auth/update`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // 登出
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login'; // 強制跳回登入頁
  },

  // ==========================================
  // 2. 專案系統 (Projects)
  // ==========================================
  
  // 取得專案列表
  getProjects: async () => {
    const res = await fetch(`${API_URL}/projects`, { headers: getAuthHeaders() });
    return res.json();
  },

  // 建立新專案
  createProject: async (name) => {
    const res = await fetch(`${API_URL}/projects`, {
      method: 'POST',
      headers: getAuthHeaders(), // ✅ Headers 正確
      body: JSON.stringify({ name }),
    });
    return res.json();
  },

  // 刪除專案
  deleteProject: async (projectId) => {
    const res = await fetch(`${API_URL}/projects/${projectId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return res.json();
  },

  // ==========================================
  // 3. 內容與搜尋 (Content & Search)
  // ==========================================

  // 取得單一專案的所有內容 (精準抓取)
  getContentsByProject: async (projectId) => {
    const res = await fetch(`${API_URL}/contents/project/${projectId}`, { 
      headers: getAuthHeaders() 
    });
    return res.json();
  },

  // 新增內容
  createContent: async (projectId, payload) => {
    const res = await fetch(`${API_URL}/contents/project/${projectId}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return res.json();
  },

  // 更新內容 (編輯)
  updateContent: async (contentId, newPrompt) => {
    const res = await fetch(`${API_URL}/contents/${contentId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({ prompt: newPrompt }),
    });
    return res.json();
  },

  // 刪除內容
  deleteContent: async (contentId) => {
    const res = await fetch(`${API_URL}/contents/${contentId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return res.json();
  },

  // 搜尋功能
  search: async (query) => {
    const res = await fetch(`${API_URL}/search?q=${query}`, { headers: getAuthHeaders() });
    return res.json();
  }
};