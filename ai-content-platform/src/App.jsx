// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import ProfilePage from './pages/ProfilePage'; // ✅ 已引入
import './App.css'; 

// 🛡️ 保護路由元件：檢查有沒有登入
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  
  // 如果沒有 Token，就踢回登入頁
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  // 有 Token，放行！顯示原本要去的頁面
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 公開頁面：任何人都能看 */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* 保護頁面：只有登入後才能看 */}
        
        {/* 1. 儀表板 */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />

        {/* 2. ✨ 新增這段：個人檔案頁面 (也要受保護) */}
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } 
        />

        {/* 預設路徑：一進來就嘗試去 Dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;