---
sidebar_position: 4
---

# nonpm（純 Nolang Node.js 包管理器）

notools 倉庫內含一個**純 Nolang 實現的 Node.js 包管理器**（`nonpm/` 目錄），兼容 [pnpm](https://github.com/pnpm/pnpm) 接口，採用虛擬存儲與符號鏈接實現磁碟高效的依賴管理。

## 特性

- **Virtual Store** — 基於內容尋址的磁碟存儲，每個包版本僅存儲一次
- **Isolated `node_modules`** — 基於符號鏈接的結構，無幽靈依賴
- **Semantic Versioning** — 完整 SemVer 2.0.0 範圍匹配（`^`、`~`、`>=`、`<=`、`>`、`<`、`*`）
- **Workspace Support** — 通過 `pnpm-workspace.yaml` 管理 Monorepo
- **Lockfile** — 通過 `pnpm-lock.yaml` 實現確定性安裝
- **Script Runner** — 通過 `nonpm run` 執行 `package.json` 中的腳本
- **Package Publishing** — 打包並發布到 npm registry
- **Binary Links** — 自動為 CLI 工具創建 `.bin` 符號鏈接
- **Peer Dependencies** — 自動安裝 peer 依賴
- **Hoisting** — 可選的 shamefully-hoist 模式用於兼容性

## 主要命令

| 命令 | 說明 |
|------|------|
| `install` | 安裝 package.json 中的所有依賴 |
| `add <pkg>` | 添加依賴（`-D` 開發依賴、`@version` 指定版本） |
| `remove <pkg>` | 移除依賴 |
| `run [script]` | 列出或運行 package.json 中的腳本 |
| `update [pkg]` | 更新依賴 |
| `list` | 列出已安裝的包 |
| `outdated` | 檢查過時的包 |
| `why <pkg>` | 查看包為何被安裝 |
| `init [path]` | 初始化新項目 |
| `pack` | 創建 tarball |
| `publish` | 發布到 registry |
| `exec <cmd>` | 在 node_modules/.bin 環境中運行命令 |
| `dlx <pkg>` | 在臨時環境中運行包 |
| `link <path>` | 鏈接本地包 |
| `cache clean` | 清理緩存 |

## 構建與運行

```bash
cd nonpm
no build
# 產物位於 nonpm/dist/nonpm

# 示例：安裝依賴
cd my-project
nonpm install

# 示例：添加依賴
nonpm add express

# 示例：運行腳本
nonpm run build
```

詳細的命令列表、配置選項、模組架構等信息請參見 [`nonpm/README.md`](https://github.com/lizongying/notools/blob/main/nonpm/README.md)。
