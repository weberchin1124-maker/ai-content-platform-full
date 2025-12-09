// src/components/CreateProjectModal.jsx
import { useState } from 'react';
import { api } from '../services/api';

export default function CreateProjectModal({ isOpen, onClose, onProjectCreated }) {
  const [projectName, setProjectName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const presets = ["編程助手", "學習筆記", "旅遊規劃", "健康紀錄", "創意寫作"];

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (!projectName.trim()) return alert("請輸入專案名稱");

    setIsLoading(true);
    try {
      const res = await api.createProject(projectName);

      // ✨ 修正重點：同時檢查 message, msg 和 project_id
      // 後端成功時回傳: { message: "Project created", project_id: 1, ... }
      // 後端Token過期回傳: { msg: "Token has expired" }
      
      const successMsg = res.message || res.msg;
      const isSuccess = 
        successMsg === "Project created" || 
        successMsg === "專案建立成功" || 
        res.project_id; // 只要有回傳 ID 也算成功

      if (isSuccess) {
        onProjectCreated(); 
        setProjectName('');
        onClose();
        // 成功就不跳視窗了，直接關閉體驗比較好
      } else {
        // 處理失敗狀況
        const errorMsg = res.message || res.msg || res.error || "未知錯誤";
        
        if (errorMsg.includes("expired") || errorMsg.includes("過期")) {
           alert("登入時效已過，請重新登入！");
           api.logout(); // 自動登出
        } else {
           alert("建立失敗: " + errorMsg);
        }
      }
    } catch (error) {
      console.error(error);
      alert("連線錯誤或伺服器無回應");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <div style={styles.header}>
          <h3>✨ 建立新專案</h3>
          <button onClick={onClose} style={styles.closeBtn}>×</button>
        </div>
        <input 
          type="text" 
          placeholder="專案名稱" 
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          style={styles.input}
          autoFocus
        />
        <div style={styles.tagContainer}>
          <p style={{ fontSize: '0.85rem', color: '#8b949e', marginBottom: '8px' }}>快速選擇類型：</p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {presets.map(tag => (
              <button key={tag} onClick={() => setProjectName(tag)} style={styles.tagBtn}>{tag}</button>
            ))}
          </div>
        </div>
        <button 
          onClick={handleSubmit} 
          disabled={isLoading}
          style={{...styles.createBtn, backgroundColor: isLoading ? '#6e7681' : '#1f6feb'}}
        >
          {isLoading ? '建立中...' : '建立專案'}
        </button>
      </div>
    </div>
  );
}

const styles = {
  overlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
  modal: { backgroundColor: '#161b22', padding: '24px', borderRadius: '12px', width: '400px', border: '1px solid #30363d', color: 'white' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
  closeBtn: { background: 'none', border: 'none', color: '#8b949e', fontSize: '1.5rem', cursor: 'pointer' },
  input: { width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #30363d', backgroundColor: '#0d1117', color: 'white', marginBottom: '15px', boxSizing: 'border-box' },
  tagContainer: { marginBottom: '20px' },
  tagBtn: { padding: '6px 12px', borderRadius: '20px', border: '1px solid #30363d', backgroundColor: '#21262d', color: '#c9d1d9', cursor: 'pointer', fontSize: '0.85rem', transition: '0.2s' },
  createBtn: { width: '100%', padding: '12px', borderRadius: '6px', border: 'none', color: 'white', fontSize: '1rem', fontWeight: 'bold', cursor: 'pointer' }
};