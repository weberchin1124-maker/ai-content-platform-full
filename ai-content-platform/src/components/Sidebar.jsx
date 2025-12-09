// src/components/Sidebar.jsx
import { useNavigate } from 'react-router-dom';

function Sidebar({ projects, activeProjectId, onSelect, user, onLogout, onNewProject, onDeleteProject }) {
  const navigate = useNavigate();

  return (
    <aside style={{
      width: '260px', height: '100vh', backgroundColor: '#0d1117', color: 'white',
      display: 'flex', flexDirection: 'column', padding: '10px', boxSizing: 'border-box',
      position: 'fixed', left: 0, top: 0, borderRight: '1px solid #30363d'
    }}>
      {/* 標題 */}
      <h2 
        onClick={() => navigate('/dashboard')}
        style={{ padding: '0 10px', fontSize: '1.2rem', marginBottom: '15px', cursor: 'pointer' }}
      >
        🤖 AI Content Pro
      </h2>
      
      {/* 建立按鈕 */}
      <button 
        onClick={onNewProject}
        style={{
          display: 'flex', alignItems: 'center', gap: '10px', width: '100%',
          padding: '10px 15px', marginBottom: '20px', backgroundColor: '#238636',
          border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', color: 'white',
          cursor: 'pointer', fontSize: '0.95rem', fontWeight: 'bold', boxSizing: 'border-box'
        }}
      >
        <span style={{ fontSize: '1.2rem', lineHeight: 1 }}>+</span> 建立新專案
      </button>

      {/* 專案列表區 */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <p style={{ padding: '0 10px', fontSize: '0.8rem', color: '#8b949e', marginBottom: '5px' }}>我的專案</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          {projects.map(project => (
            <div 
              key={project.id}
              onClick={() => onSelect(project.id)}
              style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center', // ✨ 關鍵：左右排開
                padding: '10px', borderRadius: '6px', cursor: 'pointer',
                backgroundColor: activeProjectId === project.id ? '#1f6feb' : 'transparent',
                color: activeProjectId === project.id ? 'white' : '#c9d1d9',
                transition: '0.2s', fontSize: '0.9rem'
              }}
              className="project-item" // 可以配合 CSS 做 hover 效果
            >
              <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', flex: 1 }}>
                # {project.name}
              </div>
              
              {/* ✨ 刪除按鈕：點擊時要阻止冒泡 (stopPropagation)，不然會觸發切換專案 */}
              <button 
                onClick={(e) => { 
                  e.stopPropagation(); 
                  if(window.confirm(`確定要刪除專案「${project.name}」嗎？\n裡面的筆記也會一起消失喔！`)) {
                    onDeleteProject(project.id);
                  }
                }}
                style={{
                  background: 'none', border: 'none', color: '#ff7b72', 
                  cursor: 'pointer', fontSize: '1rem', padding: '0 5px',
                  opacity: 0.7, transition: 'opacity 0.2s'
                }}
                title="刪除專案"
                onMouseOver={(e) => e.target.style.opacity = 1}
                onMouseOut={(e) => e.target.style.opacity = 0.7}
              >
                🗑️
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 使用者資訊 */}
      {user && (
        <div style={{ marginTop: 'auto', borderTop: '1px solid #30363d', paddingTop: '15px' }}>
          <div onClick={() => navigate('/profile')} style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px', padding: '8px 5px', borderRadius: '6px', cursor: 'pointer' }}>
            <span style={{ fontSize: '1.5rem' }}>{user.avatar || '👤'}</span>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{user.name}</span>
              <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>{user.role || 'user'}</span>
            </div>
          </div>
          <button onClick={onLogout} style={{ width: '100%', padding: '8px', backgroundColor: '#21262d', border: '1px solid #30363d', color: '#c9d1d9', borderRadius: '6px', cursor: 'pointer' }}>🚪 登出系統</button>
        </div>
      )}
    </aside>
  )
}

export default Sidebar