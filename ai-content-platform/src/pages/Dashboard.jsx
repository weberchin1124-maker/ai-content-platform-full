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
  
  // ✨ 1. AI 模型狀態
  const [currentModel, setCurrentModel] = useState("gemini-1.5-flash");

  const [summaryLoading, setSummaryLoading] = useState(false);
  const navigate = useNavigate();

  // ==========================================
  // 1. 定義抓取函式
  // ==========================================
  
  const fetchProjects = async () => {
    try {
      const data = await api.getProjects();
      const formatted = data.map(p => ({ id: p.project_id, name: p.name }));
      setProjects(formatted);
      if (!activeProjectId && formatted.length > 0) setActiveProjectId(formatted[0].id);
    } catch (e) {
      if (e.message?.includes('401')) api.logout();
    }
  };

  const fetchProjectContents = async (projectId) => {
    setLoading(true);
    setContents([]); 
    try {
      const data = await api.getContentsByProject(projectId);
      if (Array.isArray(data)) {
        const results = data.map(item => ({
          id: String(item.id),
          version: item.version ? `v${item.version}.0` : "v1.0",
          date: item.date ? item.date.slice(0, 10) : '剛剛',
          tags: item.tags || [],
          prompt: item.prompt,
          response: item.response
        }));
        setContents(results);
      }
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { fetchProjects(); }, []);
  useEffect(() => { if (activeProjectId) fetchProjectContents(activeProjectId); }, [activeProjectId]);

  // ==========================================
  // 3. 其他操作函式
  // ==========================================

  const handleSearch = async (text) => {
    setSearchTerm(text);
    if (!text) { if (activeProjectId) fetchProjectContents(activeProjectId); return; }
    setLoading(true);
    try {
      const res = await api.search(text); 
      const results = res.results.map(item => ({
        id: item.mongo_id || item.id,
        version: "v1.0", 
        date: item.created_at ? item.created_at.slice(0, 10) : '剛剛',
        tags: item.tags || [],
        prompt: item.prompt || item.original_prompt,
        response: item.response || item.generated_content
      }));
      setContents(results);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  const handleNewPrompt = async (prompt, tags) => {
    if (!activeProjectId) return alert("請先建立或選擇一個專案！");
    
    const tempId = "temp_" + Date.now();
    
    const optimisticItem = { 
      id: tempId, 
      version: "v1.0", 
      date: "處理中...", 
      tags: tags.length > 0 ? tags : ["🤖 AI 分析中..."], 
      prompt: prompt, 
      response: "",
      isOptimistic: true 
    };
    
    setContents([optimisticItem, ...contents]);

    try {
      const res = await api.createContent(activeProjectId, {
        title: prompt.slice(0, 10), 
        prompt: prompt, 
        response: "", 
        source_tool: "Manual Note", 
        tags: tags,
        model: currentModel
      });

      setContents(currentContents => currentContents.map(item => {
        if (item.id === tempId) {
          return {
            ...item,
            id: String(res.id),
            version: "v1.0",
            date: new Date().toISOString().slice(0, 10),
            tags: res.tags || [],
            response: res.response,
            isOptimistic: false
          };
        }
        return item;
      }));

    } catch (e) {
      console.error(e);
      alert("新增失敗");
      setContents(prev => prev.filter(item => item.id !== tempId));
    }
  };

  // ✅ 專案刪除：Sidebar 已經做了 window.confirm，這裡直接刪
  const handleDeleteProject = async (projectId) => {
     console.log("Dashboard 執行刪除專案:", projectId); 
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

  // ✅ 內容刪除：ContentCard 已經做了 window.confirm，這裡直接刪
  const handleDeleteContent = async (contentId) => {
    console.log("Dashboard 執行刪除筆記:", contentId);
    
    // 移除這裡的 window.confirm，避免跳兩次視窗
    const originalContents = [...contents];
    setContents(contents.filter(c => c.id !== contentId));

    try {
      await api.deleteContent(contentId);
    } catch (e) {
      alert("刪除失敗");
      setContents(originalContents); // 失敗復原
    }
  };

  const handleUpdateContent = async (contentId, newPrompt) => {
    const originalContents = [...contents];
    setContents(contents.map(item => item.id === contentId ? { ...item, prompt: newPrompt } : item));
    try {
      await api.updateContent(contentId, newPrompt);
      if (activeProjectId) fetchProjectContents(activeProjectId);
    } catch (e) { alert("修改失敗"); setContents(originalContents); }
  };

  const handleRefineContent = async (contentId) => {
    const originalContents = [...contents];
    setContents(contents.map(item => item.id === contentId ? { ...item, prompt: "✨ AI 正在美化您的筆記中..." } : item));

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:5000/api/contents/${contentId}/refine`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ model: currentModel }) 
      });
      const data = await response.json();
      
      if (response.ok) {
          if (activeProjectId) fetchProjectContents(activeProjectId);
      } else {
          throw new Error(data.error || "Refine failed");
      }
    } catch (e) {
      alert("美化失敗: " + e.message);
      setContents(originalContents);
    }
  };

  const handleGenerateSummary = async () => {
    if (!activeProjectId) return;
    setSummaryLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:5000/api/projects/${activeProjectId}/summary`, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if(data.summary) {
          alert("📊 專案週報生成結果：\n\n" + data.summary);
      } else {
          alert("生成失敗或內容為空");
      }
    } catch (e) {
      alert("生成失敗: " + e.message);
    } finally {
      setSummaryLoading(false);
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
        
        currentModel={currentModel}
        onModelChange={setCurrentModel}
        onDeleteProject={handleDeleteProject}
      />
      <CreateProjectModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onProjectCreated={fetchProjects} />
      
      <div style={{ marginLeft: '260px' }}>
        <Header searchTerm={searchTerm} onSearch={handleSearch} />
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', paddingBottom: '100px' }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
             <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <h2>🗂️ {currentProject.name}</h2>
                {activeProjectId && (
                    <button 
                        onClick={handleGenerateSummary}
                        disabled={summaryLoading}
                        style={{
                            backgroundColor: '#238636',
                            color: 'white',
                            border: 'none',
                            padding: '5px 12px',
                            borderRadius: '6px',
                            cursor: summaryLoading ? 'wait' : 'pointer',
                            fontSize: '0.85rem'
                        }}
                    >
                        {summaryLoading ? "生成中..." : "📊 生成週報"}
                    </button>
                )}
             </div>
             <span style={{ color: '#8b949e', fontSize: '0.9rem' }}>{loading ? "讀取中..." : `筆數: ${contents.length}`}</span>
          </div>

          {contents.length > 0 ? (
            contents.map((item) => (
              <ContentCard 
                key={item.id} {...item} 
                onDelete={handleDeleteContent}
                onUpdate={handleUpdateContent}
                onRefine={handleRefineContent}
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