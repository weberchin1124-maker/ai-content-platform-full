// src/components/ContentCard.jsx
import { useState } from 'react'

function ContentCard({ id, version, date, prompt, response, tags, onDelete, onUpdate, onRefine }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editPrompt, setEditPrompt] = useState(prompt);
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

      {/* ✨ 修復版刪除按鈕 (右側內容) */}
      <button 
        onClick={(e) => {
            e.stopPropagation(); // 防止誤觸其他卡片事件
            if(window.confirm("確定要刪除這筆筆記嗎？")) {
                onDelete(id);
            }
        }}
        style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          backgroundColor: '#2b3137', // 給一個背景色，防止被下層文字干擾
          border: '1px solid #30363d',
          borderRadius: '50%', // 圓形按鈕
          width: '32px', 
          height: '32px',
          cursor: 'pointer',
          fontSize: '1rem',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#ff7b72',
          zIndex: 100, // ✨ 強制拉到最上層，確保不被蓋住
          boxShadow: '0 2px 4px rgba(0,0,0,0.3)', // 加一點陰影讓它浮起來
          transition: 'all 0.2s'
        }}
        title="刪除此筆記"
        onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#ff7b72';
            e.currentTarget.style.color = 'white';
        }}
        onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#2b3137';
            e.currentTarget.style.color = '#ff7b72';
        }}
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

        {/* 右邊：版本與日期 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ 
                fontSize: '0.75rem', color: '#c9d1d9', backgroundColor: '#30363d', 
                padding: '2px 6px', borderRadius: '4px', border: '1px solid #30363d'
            }}>
                {version || "v1.0"}
            </span>
            <span style={{ fontSize: '0.85rem', color: '#8b949e' }}>{date}</span>
        </div>
      </div>

      {/* 內容區 */}
      <div style={{ marginBottom: '15px', flexGrow: 1 }}>
        {isEditing ? (
          // === 編輯模式 ===
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
             <label style={{ fontSize: '0.85rem', color: '#8b949e' }}>筆記內容 (User)</label>
             <textarea 
               style={{ width: '100%', padding: '10px', borderRadius: '6px', backgroundColor: '#0d1117', color: 'white', border: '1px solid #30363d', minHeight: '100px', resize: 'vertical', fontFamily: 'inherit' }}
               value={editPrompt} 
               onChange={(e) => setEditPrompt(e.target.value)}
             />
             {response && (
               <>
                 <label style={{ fontSize: '0.85rem', color: '#8b949e', marginTop: '10px' }}>AI 內容 (Assistant)</label>
                 <textarea
                   style={{ width: '100%', padding: '10px', borderRadius: '6px', backgroundColor: '#161b22', color: '#c9d1d9', border: '1px solid #30363d', minHeight: '80px', resize: 'vertical', fontFamily: 'inherit' }}
                   value={editResponse}
                   onChange={(e) => setEditResponse(e.target.value)}
                 />
               </>
             )}
          </div>
        ) : (
          // === 瀏覽模式 ===
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div style={{ fontSize: '1rem', lineHeight: '1.7', whiteSpace: 'pre-wrap', color: '#e6edf3' }}>
              {prompt}
            </div>
            {response && (
              <>
                <hr style={{ border: 'none', borderTop: '1px solid #30363d', margin: '0' }} />
                <div style={{ fontSize: '0.95rem', lineHeight: '1.7', whiteSpace: 'pre-wrap', color: '#c9d1d9' }}>
                  <span style={{ marginRight: '8px' }}>🤖</span>
                  {response}
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* 底部按鈕區 */}
      {isEditing ? (
        <div style={{ paddingTop: '15px', borderTop: '1px solid #30363d', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button 
            style={{ padding: '8px 16px', backgroundColor: '#d73a49', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => { setIsEditing(false); setEditPrompt(prompt); setEditResponse(response || ""); }}
          >
            取消
          </button>
          <button 
            style={{ padding: '8px 16px', backgroundColor: '#238636', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => { onUpdate(id, editPrompt); setIsEditing(false); }}
          >
            儲存變更
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'auto', gap: '15px', alignItems: 'center' }}>
           {onRefine && (
             <button 
              style={{ background: 'none', border: 'none', color: '#a371f7', cursor: 'pointer', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px', padding: '5px 10px', borderRadius: '6px', transition: 'background-color 0.2s' }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(163, 113, 247, 0.1)'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              onClick={() => onRefine(id)}
            >
              ✨ AI 美化
            </button>
           )}
           <button 
            style={{ background: 'none', border: 'none', color: '#58a6ff', cursor: 'pointer', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px', padding: '5px 10px', borderRadius: '6px', transition: 'background-color 0.2s' }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(88, 166, 255, 0.1)'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
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