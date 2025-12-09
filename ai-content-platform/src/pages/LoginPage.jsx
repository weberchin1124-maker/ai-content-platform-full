// src/pages/LoginPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    setErrorMsg('');
    setIsLoading(true);

    try {
      const result = await api.login(email, password);
      if (result.status === 200) {
        navigate('/dashboard'); 
      } else {
        setErrorMsg(result.data.message || '登入失敗');
      }
    } catch (err) {
      setErrorMsg("🔌 無法連線到伺服器");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={{ marginBottom: '20px' }}>🔐 請先登入</h1>
        
        {errorMsg && <div style={styles.errorBox}>{errorMsg}</div>}
        
        <input 
          type="email" 
          placeholder="Email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={styles.input}
        />
        <input 
          type="password" 
          placeholder="密碼" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
        />
        
        <button 
          onClick={handleLogin} 
          disabled={isLoading}
          style={styles.button}
        >
          {isLoading ? '⏳ 登入中...' : '登入系統'}
        </button>

        <p style={{ marginTop: '20px', fontSize: '0.9rem', color: '#8b949e' }}>
          還沒有帳號？ 
          <span onClick={() => navigate('/register')} style={styles.link}>馬上註冊</span>
        </p>
      </div>
    </div>
  );
}

// 👇👇👇 關鍵：一定要有這一段，不然會白屏！ 👇👇👇
const styles = {
  container: { height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0d1117', color: 'white' },
  card: { backgroundColor: '#161b22', padding: '40px', borderRadius: '12px', border: '1px solid #30363d', textAlign: 'center', width: '320px' },
  errorBox: { backgroundColor: 'rgba(248, 81, 73, 0.1)', color: '#ff7b72', padding: '10px', borderRadius: '6px', marginBottom: '15px', fontSize: '0.9rem' },
  input: { width: '100%', padding: '12px', marginBottom: '15px', borderRadius: '6px', border: '1px solid #30363d', backgroundColor: '#0d1117', color: 'white', fontSize: '1rem' },
  button: { width: '100%', padding: '12px', fontSize: '1rem', cursor: 'pointer', backgroundColor: '#238636', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold' },
  link: { color: '#58a6ff', cursor: 'pointer', textDecoration: 'underline', marginLeft: '5px' }
};