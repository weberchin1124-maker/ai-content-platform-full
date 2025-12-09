// src/components/ContentCard.jsx
import { useState } from 'react'

function ContentCard({ id, version, date, prompt, response, tags, onDelete, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editPrompt, setEditPrompt] = useState(prompt);
  // 如果原本沒有 response，編輯時預設為空字串
  const [editResponse, setEditResponse] = useState(response || "");

  return (
    <div style={{
      backgroundColor: '#2b3137',
      border: '1px solid #30363d',
      borderRadius: '6px',
      padding: '20px',
      marginBottom: '20px',
      color: '#e6edf3',
      position: 'relative',
      display: 'flex',
      flexDirection: 'column'
    }}>

      {/* 刪除按鈕 (固定在右上角) */}
      <button 
        onClick={() => onDelete(id)}
        style={{
          position: 'absolute',
          top: '15px',
          right: '15px',
          backgroundColor: 'transparent',
          border: 'none',
          cursor: 'pointer',
          fontSize: '1.2rem',
          padding: '5px',
          opacity: 0.6,
          transition: 'opacity 0.2s',
          zIndex: 10
        }}
        title="刪除此筆記"
        onMouseOver={(e) => e.target.style.opacity = 1}
        onMouseOut={(e) => e.target.style.opacity = 0.6}
      >
        🗑️
      </button>

      {/* 頂部資訊 (日期與標籤) */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', paddingRight: '40px' }}>
        
        {/* 左邊：標籤 */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
           {tags && tags.length > 0 ? (
             tags.map((tag, index) => (
               <span key={index} style={{
                 backgroundColor: '#1f6feb',
                 color: 'white',
                 fontSize: '0.75rem',
                 padding: '2px 8px',
                 borderRadius: '12px',
                 fontWeight: 'bold'
               }}>
                 #{tag}
               </span>
             ))
           ) : (
             <span style={{ color: '#8b949e', fontSize: '0.8rem' }}>#未分類</span>
           )}
        </div>

        {/* 右邊：版本與日期 (✨ 這裡加回去了！) */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {/* 版本號徽章 */}
            <span style={{ 
                fontSize: '0.75rem', 
                color: '#c9d1d9', 
                backgroundColor: '#30363d', 
                padding: '2px 6px', 
                borderRadius: '4px',
                border: '1px solid #30363d'
            }}>
                {version || "v1.0"}
            </span>
            
            {/* 日期 */}
            <span style={{ fontSize: '0.85rem', color: '#8b949e' }}>{date}</span>
        </div>
      </div>

      {/* 內容區：合併顯示，不再分 User/AI，視為一體筆記 */}
      <div style={{ marginBottom: '15px' }}>
        {isEditing ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
             <label style={{ fontSize: '0.85rem', color: '#8b949e' }}>筆記內容</label>
             <textarea 
               style={{ width: '100%', padding: '10px', borderRadius: '6px', backgroundColor: '#0d1117', color: 'white', border: '1px solid #30363d', minHeight: '100px', resize: 'vertical' }}
               value={editPrompt} 
               onChange={(e) => setEditPrompt(e.target.value)}
             />
             
             {/* 只有當原本就有 response 時，才顯示編輯 response 的框 (保留彈性) */}
             {response && (
               <>
                 <label style={{ fontSize: '0.85rem', color: '#8b949e' }}>AI 回覆 (唯讀或備註)</label>
                 <textarea
                   style={{ width: '100%', padding: '10px', borderRadius: '6px', backgroundColor: '#161b22', color: '#8b949e', border: '1px solid #30363d', minHeight: '60px' }}
                   value={editResponse}
                   onChange={(e) => setEditResponse(e.target.value)}
                 />
               </>
             )}
          </div>
        ) : (
          <div>
            {/* 主要筆記內容 (Prompt) */}
            <p style={{ 
              margin: '0', 
              padding: '0',
              fontSize: '1rem',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap', // 保留換行
              color: '#e6edf3'
            }}>
              {prompt}
            </p>

            {/* 如果有 response (AI 回應)，則以引用區塊顯示在下方 */}
            {response && (
              <div style={{ 
                marginTop: '15px', 
                padding: '10px 15px', 
                backgroundColor: '#21262d', 
                borderLeft: '4px solid #3fb950', 
                borderRadius: '4px',
                color: '#8b949e',
                fontSize: '0.9rem'
              }}>
                <strong style={{ display: 'block', marginBottom: '5px', color: '#3fb950' }}>🤖 AI 補充:</strong>
                {response}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 底部編輯按鈕區 */}
      {isEditing ? (
        <div style={{ paddingTop: '15px', borderTop: '1px solid #30363d', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button 
            style={{ padding: '8px 16px', backgroundColor: '#d73a49', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => {
              setIsEditing(false);
              setEditPrompt(prompt);
              setEditResponse(response || "");
            }}
          >
            取消
          </button>
          <button 
            style={{ padding: '8px 16px', backgroundColor: '#238636', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => {
              // 呼叫上層更新函式
              onUpdate(id, editPrompt); 
              setIsEditing(false);
            }}
          >
            儲存變更
          </button>
        </div>
      ) : (
        // 滑鼠移上去才顯示編輯按鈕 (優化視覺)
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'auto' }}>
           <button 
            style={{ 
              background: 'none', 
              border: 'none', 
              color: '#58a6ff', 
              cursor: 'pointer', 
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}
            onClick={() => setIsEditing(true)}
          >
            ✏️ 編輯
          </button>
        </div>
      )}

    </div>
  )
}

export default ContentCard