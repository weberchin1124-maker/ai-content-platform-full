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
        // 🚨 關鍵修正：在嘗試抓取專案之前，檢查 Token。如果沒有，則不執行 API 呼叫
        const token = localStorage.getItem('token');
        if (!token) {
            console.warn("Token missing. Aborting project fetch to prevent 401 error.");
            return;
        }

        try {
            const data = await api.getProjects();
            const formatted = data.map(p => ({ id: p.project_id, name: p.name }));
            setProjects(formatted);
            // 如果還沒選專案，預設選第一個
            if (!activeProjectId && formatted.length > 0) setActiveProjectId(formatted[0].id);
        } catch (e) {
            // 由於我們在前面已檢查 token，這裡主要處理連線或後端 401
            if (e.message?.includes('401')) {
                alert("會話過期，請重新登入。");
                api.logout();
            }
        }
    };

    // 專門用來抓取「特定專案內容」的函式
    const fetchProjectContents = async (projectId) => {
        setLoading(true);
        setContents([]); // 切換前先清空畫面
        try {
            // 呼叫精準抓取 API
            const data = await api.getContentsByProject(projectId);
            
            if (Array.isArray(data)) {
                const results = data.map(item => ({
                    id: String(item.id),
                    
                    // 關鍵修改：讀取後端回傳的 version，如果是 0 或 undefined 預設顯示 v1.0
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
        // 🚨 關鍵修正：強制延遲 100ms，確保 LocalStorage 完成 Token 寫入
        const timer = setTimeout(() => {
            fetchProjects(); 
        }, 100); 

        return () => clearTimeout(timer); // 清除計時器
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
        
        // 樂觀更新 ID
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
                model: currentModel // 傳遞選中的模型
            });

            // 接收 API 回覆後更新狀態
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

    // 刪除專案
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

    // 刪除內容
    // ContentCard 已經做了 window.confirm，這裡只執行刪除邏輯
    const handleDeleteContent = async (contentId) => {
        console.log("Dashboard 執行刪除筆記:", contentId);
        
        // 樂觀更新
        const originalContents = [...contents];
        setContents(contents.filter(c => c.id !== contentId));

        try {
            await api.deleteContent(contentId);
        } catch (e) {
            alert("刪除失敗");
            setContents(originalContents); // 失敗復原
        }
    };

    // 編輯內容
    const handleUpdateContent = async (contentId, newPrompt) => {
        // 1. 先做樂觀更新
        const originalContents = [...contents];
        setContents(contents.map(item => item.id === contentId ? { ...item, prompt: newPrompt } : item));
        try {
            await api.updateContent(contentId, newPrompt);
            if (activeProjectId) fetchProjectContents(activeProjectId);
        } catch (e) { alert("修改失敗"); setContents(originalContents); }
    };

    // AI 美化內容
    const handleRefineContent = async (contentId) => {
        const originalContents = [...contents];
        // 顯示 Loading 狀態
        setContents(contents.map(item => item.id === contentId ? { ...item, prompt: "✨ AI 正在美化您的筆記中..." } : item));

        try {
            const token = localStorage.getItem('token');
            // 注意：這裡直接呼叫了 localhost:5000/api/contents/.../refine，沒有使用 api.js 的 proxy
            const response = await fetch(`http://127.0.0.1:5000/api/contents/${contentId}/refine`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ model: currentModel }) // 傳遞選中的模型
            });
            const data = await response.json();
            
            if (response.ok) {
                // 成功後重新抓取整個列表 (更新版本號和內容)
                if (activeProjectId) fetchProjectContents(activeProjectId);
            } else {
                throw new Error(data.error || "Refine failed");
            }
            
        } catch (e) {
            alert("美化失敗: " + e.message);
            setContents(originalContents); // 失敗復原
        }
    };

    // 生成週報
    const handleGenerateSummary = async () => {
        if (!activeProjectId) return;
        setSummaryLoading(true);
        try {
            const token = localStorage.getItem('token');
            // 注意：這裡直接呼叫了 localhost:5000/api/projects/.../summary，沒有使用 api.js 的 proxy
            const response = await fetch(`http://127.00.1:5000/api/projects/${activeProjectId}/summary`, {
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