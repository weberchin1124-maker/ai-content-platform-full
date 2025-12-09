// src/mockData.js

export const initialProjects = [
  {
    id: 1,
    name: "資料庫期末報告",
    data: [
      { 
        id: 1, 
        version: "v1.0", 
        date: "2023-11-16", 
        tags: ["React", "UI設計"], // 新增標籤
        prompt: "請幫我寫一段 React 的介紹。", 
        response: "React 是一個用於構建使用者介面的 JavaScript 函式庫..." 
      },
      { 
        id: 2, 
        version: "v1.1", 
        date: "2023-11-17", 
        tags: ["資安", "SQL"], // 新增標籤
        prompt: "什麼是 SQL Injection？", 
        response: "SQL Injection 是一種資料庫安全漏洞..." 
      }
    ]
  },
  {
    id: 2,
    name: "React 學習筆記",
    data: [
      { 
        id: 101, 
        version: "v1.0", 
        date: "2023-11-20", 
        tags: ["基礎", "教學"], // 新增標籤
        prompt: "如何建立 React Component？", 
        response: "你可以建立一個 function 並回傳 JSX..." 
      },
      { 
        id: 102, 
        version: "v2.0", 
        date: "2023-11-21", 
        tags: ["進階", "Hooks"], // 新增標籤
        prompt: "解釋 useState 的用法", 
        response: "useState 是 React 的 Hook，用來管理狀態..." 
      }
    ]
  }
];