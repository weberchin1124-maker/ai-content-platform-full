// src/pages/ProfilePage.jsx
import { useState, useEffect } from 'react';
import { api } from '../services/api';
import Sidebar from '../components/Sidebar';

export default function ProfilePage() {
  const [user, setUser] = useState({ name: '', email: '' });
  const [username, setUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [projects, setProjects] = useState([]); // 為了顯示 Sidebar

  // 初始化：抓取使用者資料 (從 localStorage 或 API)
  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    if (storedUser) {
      setUser({ name: storedUser.username, email: storedUser.email });
      setUsername(storedUser.username);
    }
    // 為了讓 Sidebar 正常顯示，還是要抓一下專案
    api.getProjects().then(data => {
        const formatted = data.map(p => ({ id: p.project_id, name: p.name, data: [] }));
        setProjects(formatted);
    });
  }, []);

  const handleUpdate = async () => {
    const payload = {};
    if (username !== user.name) payload.username = username;
    if (newPassword) payload.new_password = newPassword;

    if (Object.keys(payload).length === 0) return alert("沒有任何修改");

    try {
      const res = await api.updateUser(payload);
      if (res.message === "更新成功") {
        alert("🎉 資料更新成功！");
        // 更新 localStorage 裡的資料
        const newUser = { ...JSON.parse(localStorage.getItem('user')), username: res.user.username };
        localStorage.setItem('user', JSON.stringify(newUser));
        setUser({ ...user, name: res.user.username });
        setNewPassword(''); // 清空密碼欄
      } else {
        alert("更新失敗: " + res.message);
      }
    } catch (e) {
      alert("連線錯誤");
    }
  };

  return (
    <div className="app-container">
      {/* 這裡重複使用 Sidebar，讓介面看起來像在同一個系統內 */}
      <Sidebar 
        projects={projects} 
        activeProjectId={null} 
        onSelect={() => {}}
        user={{ ...user, avatar: '👨‍💻', role: 'owner' }} // 組合一下顯示用的資料
        onLogout={api.logout}
      />
      
      <div style={{ marginLeft: '260px', padding: '40px', color: 'white' }}>
        <h2 style={{ borderBottom: '1px solid #30363d', paddingBottom: '20px', marginBottom: '30px' }}>
          👤 個人檔案設定
        </h2>

        <div style={{ maxWidth: '500px' }}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px', color: '#8b949e' }}>Email (無法修改)</label>
            <input type="text" value={user.email} disabled style={{ ...styles.input, opacity: 0.5, cursor: 'not-allowed' }} />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px' }}>使用者名稱</label>
            <input 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              style={styles.input} 
            />
          </div>

          <div style={{ marginBottom: '30px' }}>
            <label style={{ display: 'block', marginBottom: '10px' }}>設定新密碼 (若不修改請留空)</label>
            <input 
              type="password" 
              placeholder="輸入新密碼..."
              value={newPassword} 
              onChange={(e) => setNewPassword(e.target.value)} 
              style={styles.input} 
            />
          </div>

          <button onClick={handleUpdate} style={styles.button}>
            儲存變更
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  input: {
    width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #30363d', backgroundColor: '#0d1117', color: 'white', fontSize: '1rem'
  },
  button: {
    padding: '12px 24px', fontSize: '1rem', cursor: 'pointer', backgroundColor: '#1f6feb', color: 'white', border: 'none', borderRadius: '6px'
  }
};