// src/components/PromptInput.jsx
import { useState } from 'react';

export default function PromptInput({ onNewPrompt }) {
  const [text, setText] = useState("");
  const [selectedTags, setSelectedTags] = useState(["一般"]); 
  const [customTag, setCustomTag] = useState(""); // ✨ 新增：自訂標籤輸入狀態
  const [isSending, setIsSending] = useState(false);
  const availableTags = ["React", "SQL", "Python", "筆記", "除錯", "翻譯"];

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setIsSending(true);
    await onNewPrompt(text, selectedTags);
    setText("");
    setIsSending(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const toggleTag = (tag) => {
    if (selectedTags.includes(tag)) setSelectedTags(selectedTags.filter(t => t !== tag));
    else setSelectedTags([...selectedTags, tag]);
  };

  // ✨ 新增：加入自訂標籤的功能
  const addCustomTag = () => {
    if (customTag.trim() && !selectedTags.includes(customTag.trim())) {
      setSelectedTags([...selectedTags, customTag.trim()]);
      setCustomTag("");
    }
  };

  return (
    <div style={{ position: 'fixed', bottom: 0, left: '260px', right: 0, padding: '20px', backgroundColor: '#0d1117', borderTop: '1px solid #30363d', display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
        
        {/* 標籤區 */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '8px', overflowX: 'auto', alignItems: 'center' }}>
          {/* 既有標籤 */}
          {availableTags.map(tag => (
            <span key={tag} onClick={() => toggleTag(tag)} style={{ fontSize: '0.8rem', padding: '4px 10px', borderRadius: '15px', cursor: 'pointer', border: '1px solid #30363d', backgroundColor: selectedTags.includes(tag) ? '#1f6feb' : '#21262d', color: selectedTags.includes(tag) ? 'white' : '#8b949e', transition: '0.2s' }}>
              {tag}
            </span>
          ))}
          
          {/* ✨ 自訂標籤輸入區 */}
          <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #30363d', borderRadius: '15px', padding: '0 5px', backgroundColor: '#161b22' }}>
             <input 
               type="text" 
               placeholder="+ 自訂" 
               value={customTag}
               onChange={(e) => setCustomTag(e.target.value)}
               onKeyDown={(e) => e.key === 'Enter' && addCustomTag()}
               style={{ background: 'transparent', border: 'none', color: 'white', fontSize: '0.8rem', width: '60px', outline: 'none', padding: '4px' }}
             />
             <button onClick={addCustomTag} style={{ background: 'none', border: 'none', color: '#58a6ff', cursor: 'pointer', fontSize: '1rem' }}>+</button>
          </div>
          
          {/* 顯示已選的自訂標籤 (不在預設清單內的) */}
          {selectedTags.filter(t => !availableTags.includes(t)).map(tag => (
             <span key={tag} onClick={() => toggleTag(tag)} style={{ fontSize: '0.8rem', padding: '4px 10px', borderRadius: '15px', cursor: 'pointer', border: '1px solid #1f6feb', backgroundColor: '#1f6feb', color: 'white' }}>
              {tag} ✕
            </span>
          ))}
        </div>

        {/* 輸入框與按鈕 (保持不變) */}
        <div style={{ position: 'relative', display: 'flex', alignItems: 'flex-end', gap: '10px' }}>
          <textarea value={text} onChange={(e) => setText(e.target.value)} onKeyDown={handleKeyDown} placeholder="輸入內容..." rows={1} style={{ width: '100%', padding: '12px', paddingRight: '80px', backgroundColor: '#161b22', border: '1px solid #30363d', borderRadius: '8px', color: 'white', resize: 'none', outline: 'none', minHeight: '45px' }} />
          <button onClick={handleSubmit} disabled={isSending || !text.trim()} style={{ position: 'absolute', right: '10px', bottom: '8px', backgroundColor: '#238636', color: 'white', border: 'none', borderRadius: '6px', padding: '6px 12px', cursor: 'pointer', opacity: text.trim() ? 1 : 0.5 }}>
            {isSending ? '...' : '儲存'}
          </button>
        </div>
      </div>
    </div>
  );
}