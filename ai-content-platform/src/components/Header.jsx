// src/components/Header.jsx

function Header({ searchTerm, onSearch }) {
  return (
    <header style={{
      backgroundColor: '#1f2428',
      padding: '15px 20px',
      borderBottom: '1px solid #30363d',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      position: 'sticky', // 讓標題列固定在上方
      top: 0,
      zIndex: 10
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <h2 style={{ margin: 0, fontSize: '1.2rem', color: '#e6edf3' }}>🚀 AI 內容管理平台</h2>
        <span style={{ fontSize: '0.9rem', color: '#8b949e' }}>| 第九組期末報告</span>
      </div>

      {/* 新增：搜尋框 */}
      <input 
        type="text" 
        placeholder="🔍 搜尋 Prompt 或內容..." 
        value={searchTerm} // 綁定搜尋文字
        onChange={(e) => onSearch(e.target.value)} // 打字時通知 App
        style={{
          padding: '8px 12px',
          borderRadius: '6px',
          border: '1px solid #30363d',
          backgroundColor: '#0d1117',
          color: 'white',
          outline: 'none',
          width: '250px'
        }}
      />
    </header>
  )
}

export default Header