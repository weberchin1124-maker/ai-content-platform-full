// src/pages/Dashboard.jsx
import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

import Header from '../components/Header';
import ContentCard from '../components/ContentCard';
import PromptInput from '../components/PromptInput';
import Sidebar from '../components/Sidebar';
import CreateProjectModal from '../components/CreateProjectModal';

const mockUser = { id: 'user_001', name: 'Admin', avatar: '👨‍💻', role: 'owner' };

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [activeProjectId, setActiveProjectId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [contents, setContents] = useState([]); 
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();

  // ==========================================
  // 1. 定義抓取函式 (必須放在 useEffect 之前！)
  // ==========================================
  
  const fetchProjects = async () => {
    try {
      const data = await api.getProjects();
      const formatted = data.map(p => ({ id: p.project_id, name: p.name }));
      setProjects(formatted);
      // 如果還沒選專案，預設選第一個
      if (!activeProjectId && formatted.length > 0) setActiveProjectId(formatted[0].id);
    } catch (e) {
      if (e.message?.includes('401')) api.logout();
    }
  };

  // 📌 專門用來抓取「特定專案內容」的函式
  const fetchProjectContents = async (projectId) => {
    setLoading(true);
    setContents([]); // 切換前先清空畫面
    try {
      // 呼叫精準抓取 API
      const data = await api.getContentsByProject(projectId);
      
      if (Array.isArray(data)) {
        const results = data.map(item => ({
          id: String(item.id),
          
          // 🚨 關鍵修改：讀取後端回傳的 version，如果是 0 或 undefined 預設顯示 v1.0
          version: item.version ? `v${item.version}.0` : "v1.0",
          
          date: item.date ? item.date.slice(0, 10) : '剛剛',
          tags: item.tags || [],
          prompt: item.prompt,
          response: item.response
        }));
        setContents(results);
      }
    } catch (e) {
      console.error("載入內容失敗:", e);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // 2. useEffect 監聽區
  // ==========================================

  // 初始化：抓取專案列表
  useEffect(() => { 
    fetchProjects(); 
  }, []);

  // 監聽 activeProjectId 改變
  useEffect(() => {
    if (activeProjectId) {
      fetchProjectContents(activeProjectId);
    }
  }, [activeProjectId]);


  // ==========================================
  // 3. 其他操作函式
  // ==========================================

  // 搜尋功能
  const handleSearch = async (text) => {
    setSearchTerm(text);
    if (!text) {
      if (activeProjectId) fetchProjectContents(activeProjectId);
      return;
    }
    setLoading(true);
    try {
      const res = await api.search(text); 
      const results = res.results.map(item => ({
        id: item.mongo_id || item.id,
        version: "v1.0", // 搜尋結果暫時沒帶版本號，這裡可以優化
        date: item.created_at ? item.created_at.slice(0, 10) : '剛剛',
        tags: item.tags || [],
        prompt: item.prompt || item.original_prompt,
        response: item.response || item.generated_content
      }));
      setContents(results);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  // 新增內容
  const handleNewPrompt = async (prompt, tags) => {
    if (!activeProjectId) return alert("請先建立或選擇一個專案！");
    
    // 樂觀更新 (預設 v1.0)
    const tempId = Date.now();
    const newItem = { id: tempId, version: "v1.0", date: new Date().toISOString().slice(0, 10), tags: tags.length > 0 ? tags : ["未分類"], prompt: prompt, response: "" };
    setContents([newItem, ...contents]);

    try {
      await api.createContent(activeProjectId, {
        title: prompt.slice(0, 10), prompt: prompt, response: "", source_tool: "Manual Note", tags: tags
      });
      // 建議：可以在這裡也呼叫 fetchProjectContents 確保 ID 正確，但為了效能先不加
    } catch (e) {
      alert("新增失敗");
      setContents(prev => prev.filter(item => item.id !== tempId));
    }
  };

  // 刪除專案
  const handleDeleteProject = async (projectId) => {
     try {
       await api.deleteProject(projectId);
       const newProjects = projects.filter(p => p.id !== projectId);
       setProjects(newProjects);
       if(activeProjectId === projectId) {
          setActiveProjectId(newProjects.length > 0 ? newProjects[0].id : null);
          setContents([]);
       }
     } catch(e) { alert("刪除失敗: " + e.message); }
  };

  // 刪除內容
  const handleDeleteContent = async (contentId) => {
    if(!window.confirm("確定要刪除這筆筆記嗎？")) return;
    const originalContents = [...contents];
    setContents(contents.filter(c => c.id !== contentId));

    try {
      await api.deleteContent(contentId);
    } catch (e) {
      alert("刪除失敗");
      setContents(originalContents);
    }
  };

  // 編輯內容
  const handleUpdateContent = async (contentId, newPrompt) => {
    // 1. 先做樂觀更新 (只更新文字，版本號暫時不變，等抓取)
    const originalContents = [...contents];
    setContents(contents.map(item => item.id === contentId ? { ...item, prompt: newPrompt } : item));

    try {
      // 2. 呼叫後端更新 (這會產生新版本)
      const res = await api.updateContent(contentId, newPrompt);
      
      // 3. 🚨 關鍵修改：成功後，重新抓取整個列表
      // 這樣才能讓畫面上的版本號從 v1.0 跳到 v2.0
      if (activeProjectId) {
         fetchProjectContents(activeProjectId);
      }
      
    } catch (e) {
      alert("修改失敗");
      setContents(originalContents); // 失敗復原
    }
  };

  const currentProject = projects.find(p => p.id === activeProjectId) || { name: "..." };

  return (
    <div className="app-container">
      <Sidebar 
        projects={projects} 
        activeProjectId={activeProjectId} 
        onSelect={setActiveProjectId} 
        user={mockUser} 
        onLogout={api.logout} 
        onNewProject={() => setIsModalOpen(true)}
        onDeleteProject={handleDeleteProject}
      />
      <CreateProjectModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onProjectCreated={fetchProjects} />
      
      <div style={{ marginLeft: '260px' }}>
        <Header searchTerm={searchTerm} onSearch={handleSearch} />
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', paddingBottom: '100px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
             <h2>🗂️ {currentProject.name}</h2>
             <span style={{ color: '#8b949e', fontSize: '0.9rem' }}>{loading ? "讀取中..." : `筆數: ${contents.length}`}</span>
          </div>
          {contents.length > 0 ? (
            contents.map((item) => (
              <ContentCard 
                key={item.id} {...item} 
                onDelete={handleDeleteContent}
                onUpdate={handleUpdateContent}
              />
            ))
          ) : (
            <div style={{ textAlign: 'center', color: '#8b949e', marginTop: '50px' }}>
                <p>{loading ? "正在載入內容..." : "此專案尚無內容，請在下方輸入。"}</p>
            </div>
          )}
        </div>
        <PromptInput onNewPrompt={handleNewPrompt} />
      </div>
    </div>
  );
}