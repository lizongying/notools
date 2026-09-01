---
sidebar_position: 1
---

# nogit（純 Nolang Git 實現）

notools 倉庫內含一個**純 Nolang 實現的 Git**（`nogit/` 目錄），不依賴系統 `git` 二進制，從底層數據結構到 CLI 命令全部使用 Nolang 編寫。

## 特性

- **純 Nolang 實現**：不調用系統 `git`，從 SHA-1 哈希到 zlib 壓縮均為原生代碼
- **Loose 對象存儲**：blob / tree / commit / tag 以 zlib 壓縮的 loose 對象形式存儲在 `.git/objects/`
- **Packfile v2 讀取**：支持讀取 Git packfile 格式，包括 ofs-delta 和 ref-delta 增量對象
- **Git index v2**：完整支持暫存區（staging area）讀寫
- **Reflog**：記錄 HEAD 和分支引用的變更歷史
- **倉庫發現**：從當前目錄向上搜索 `.git` 目錄
- **配置管理**：支持 `user.name` / `user.email` 等 config 讀寫

## 支持的命令

| 命令 | 說明 | 示例 |
|------|------|------|
| `init [path]` | 初始化新倉庫（冪等，可重複執行） | `nogit init myrepo` |
| `add <path>` | 將文件或目錄寫入 blob 並加入暫存區（支持遞迴添加目錄） | `nogit add file.txt`、`nogit add .` |
| `commit -m <msg>` | 從暫存區創建 tree 和 commit 對象 | `nogit commit -m 'initial'` |
| `log [count]` | 遍歷提交歷史 | `nogit log -n 10` |
| `status` | 顯示當前分支、已暫存與未暫存的變更 | `nogit status` |
| `branch [name] [-d <name>]` | 列出、創建或刪除分支 | `nogit branch dev`、`nogit branch -d dev` |
| `checkout <name>` | 切換分支並還原工作樹 | `nogit checkout dev` |
| `tag <name> [-a <name> -m <msg>] [-d <name>]` | 創建輕量/標註標籤或刪除標籤 | `nogit tag v1.0`、`nogit tag -a v1.0 -m 'msg'` |
| `show <ref>` | 顯示對象類型與內容 | `nogit show HEAD` |
| `cat-file <opt> <ref>` | 按類型/引用查看對象（`-t`/`-s`/`-p`） | `nogit cat-file -p HEAD` |
| `hash-object [-w] <file>` | 計算文件 SHA-1（`-w` 寫入對象庫） | `nogit hash-object -w file` |
| `ls-tree <ref>` | 列出 tree 內容 | `nogit ls-tree HEAD` |
| `ls-files` | 列出暫存區文件 | `nogit ls-files` |
| `rev-parse <ref>` | 將引用解析為 OID | `nogit rev-parse HEAD` |
| `write-tree` | 從暫存區寫入 tree 對象 | `nogit write-tree` |
| `rm <path> [--cached]` | 從暫存區和工作樹中刪除文件 | `nogit rm file.txt` |
| `reset [ref]` | 重置 HEAD 和索引到指定引用 | `nogit reset HEAD` |
| `update-ref <ref> <oid>` | 更新引用 | `nogit update-ref refs/heads/x <oid>` |
| `config <key> [val]` | 讀取或設置配置項 | `nogit config user.name 'Alice'` |
| `reflog` | 顯示 HEAD reflog | `nogit reflog` |

## 底層模組

| 模組 | 職責 |
|------|------|
| `util` | 通用工具函數（hex 編解碼、字節查找、整數轉字串等） |
| `oid` | SHA-1 對象標識符、對象頭構造、hash-object |
| `object` | Blob / Tree / Commit / Tag 對象的寫入與讀取（loose 格式） |
| `refs` | 引用管理：分支、標籤、HEAD、symbolic-ref、reflog |
| `config` | Git config 文件解析與讀寫 |
| `index` | 暫存區（Git index v2）讀寫 |
| `repository` | 倉庫初始化、`.git` 目錄發現、路徑輔助函數 |
| `revwalk` | 提交遍歷、引用解析、祖先檢測 |
| `zlib` | zlib 壓縮 / 解壓（deflate / inflate、Adler-32） |
| `pack` | Packfile v2 讀取（變數長頭、ofs-delta、ref-delta） |

## 構建與運行

```bash
cd nogit
no build
; 產物位於 nogit/dist/git

; 示例工作流
cd my-project
no run /path/to/nogit/dist/git init
no run /path/to/nogit/dist/git config user.name 'Alice'
no run /path/to/nogit/dist/git config user.email 'alice@example.com'
no run /path/to/nogit/dist/git add file.txt
no run /path/to/nogit/dist/git commit -m 'initial commit'
no run /path/to/nogit/dist/git log
```

## 項目結構

```
nogit/
├── main.no              ; CLI 入口與命令分發
├── src/
│   ├── util.no          ; 通用工具
│   ├── oid.no           ; SHA-1 對象標識
│   ├── object.no        ; 對象讀寫（blob/tree/commit/tag）
│   ├── refs.no          ; 引用與 reflog
│   ├── config.no        ; 配置文件
│   ├── index.no         ; 暫存區（index v2）
│   ├── repository.no    ; 倉庫初始化（冪等）與發現
│   ├── revwalk.no       ; 提交遍歷與引用解析
│   ├── zlib.no          ; zlib 壓縮/解壓（archive/gzip）
│   └── pack.no          ; Packfile v2 讀取（delta 解析）
├── tests/
│   ├── test.no               ; 統一測試運行器
│   ├── test-e2e-init.no       ; 初始化集成測試
│   ├── test-e2e-commit.no     ; 提交流水線集成測試
│   ├── test-e2e-comprehensive.no ; 全流程集成測試
│   └── ...                   ; 其餘單元測試
└── package.jsonc        ; 項目配置
```
