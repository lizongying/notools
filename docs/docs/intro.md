---
sidebar_position: 1
---

# notools 簡介

notools 是一個使用 [Nolang](https://github.com/lizongying/nolang) 語言實現的 Unix 常用命令行工具集，涵蓋 cat、ls、grep、wc、head、tail 等經典工具，展示了 Nolang 在系統編程領域的實際應用能力。

## 核心特性

- **純 Nolang 實現**：不依賴外部系統命令，所有工具均使用 Nolang 語言編寫
- **單一可執行文件**：子命令分發，共 193 個命令
- **支持 stdin 管道與文件輸入**：與傳統 Unix 工具無縫銜接
- **友好的錯誤處理**：清晰的錯誤提示與退出碼
- **多子項目**：內含 nogit、noimg、nouv、nonpm 四個獨立子項目

## 子項目一覽

| 項目 | 說明 |
|------|------|
| [notools](/docs/tools) | Unix 常用命令行工具集（193 個命令） |
| [nogit](/docs/nogit) | 純 Nolang Git 實現（不依賴系統 `git`） |
| [noimg](/docs/noimg) | 純 Nolang 圖像處理工具庫（9 種格式、55+ 種操作） |
| [nouv](/docs/nouv) | 純 Nolang Python 包管理器（兼容 uv/pip） |
| [nonpm](/docs/nonpm) | 純 Nolang Node.js 包管理器（兼容 pnpm） |

## 快速開始

```bash
# 從 Releases 下載預編譯二進制
curl -fsSL -o notools https://github.com/lizongying/notools/releases/latest/download/notools-linux-amd64
chmod +x notools && sudo mv notools /usr/local/bin/

# 使用
notools cat file.txt
echo "hello world" | notools grep hello
notools ls -l /tmp
```

## 應用場景

- **系統管理**：日常文件操作、文本處理、系統信息查看
- **開發工具鏈**：替代傳統 Unix 工具，驗證 Nolang 語言能力
- **Git 版本管理**：使用 nogit 進行版本控制，無需安裝系統 git
- **圖像處理**：使用 noimg 進行批量圖像轉換與處理
- **Python 項目管理**：使用 nouv 管理 Python 項目依賴
- **Node.js 項目管理**：使用 nonpm 管理 Node.js 項目依賴
