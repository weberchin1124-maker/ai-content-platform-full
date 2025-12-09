// src/pages/RegisterPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleRegister = async () => {
    if (!username || !email || !password) {
      alert("請填寫所有欄位");
      return;
    }

    try {
      // 1. 先註冊
      const res = await api.register(username, email, password);
      
      if (res.message === "User created" || res.message === "註冊成功") {
        
        // 2. ✨ 自動登入 (不用使用者再打一次密碼)
        const loginRes = await api.login(email, password);
        
        if (loginRes.status === 200) {
          alert("🎉 註冊成功！正在進入系統...");
          navigate('/dashboard'); // 直接進儀表板！
        } else {
          alert("註冊成功，但自動登入失敗，請手動登入");
          navigate('/login');
        }

      } else {
        alert("註冊失敗: " + (res.message || res.error || "未知錯誤"));
      }
    } catch (err) {
      console.error(err);
      alert("連線錯誤");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={{ marginBottom: '20px' }}>📝 註冊帳號</h1>
        
        <input type="text" placeholder="使用者名稱" value={username} onChange={(e) => setUsername(e.target.value)} style={styles.input} />
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} style={styles.input} />
        <input type="password" placeholder="設定密碼" value={password} onChange={(e) => setPassword(e.target.value)} style={styles.input} />

        <button onClick={handleRegister} style={styles.button}>註冊並自動登入</button>
        
        <p style={{ marginTop: '20px', fontSize: '0.9rem', color: '#8b949e' }}>
          已經有帳號了？ <span onClick={() => navigate('/login')} style={styles.link}>返回登入</span>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: { height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0d1117', color: 'white' },
  card: { backgroundColor: '#161b22', padding: '40px', borderRadius: '12px', border: '1px solid #30363d', textAlign: 'center', width: '320px' },
  input: { width: '100%', padding: '12px', marginBottom: '15px', borderRadius: '6px', border: '1px solid #30363d', backgroundColor: '#0d1117', color: 'white', fontSize: '1rem' },
  button: { width: '100%', padding: '12px', fontSize: '1rem', cursor: 'pointer', backgroundColor: '#1f6feb', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold', marginTop: '10px' },
  link: { color: '#58a6ff', cursor: 'pointer', textDecoration: 'underline', marginLeft: '5px' }
};