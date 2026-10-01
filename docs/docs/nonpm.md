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

## 配置

配置讀取優先級：

1. **全局**：`~/.nonpm/config`
2. **項目**：項目根目錄的 `.npmrc`
3. **環境**：`NONPM_*` 環境變量

```ini
# .npmrc 示例
registry=https://registry.npmjs.org/
shamefully-hoist=true
auto-install-peers=true
network-concurrency=16
node-linker=isolated
```

| 環境變量 | 說明 |
|----------|------|
| `NONPM_REGISTRY` | 覆蓋 registry URL |
| `NONPM_STORE_DIR` | 覆蓋 store 目錄 |
| `NONPM_CACHE_DIR` | 覆蓋緩存目錄 |
| `NPM_TOKEN` | 發布用認證 token |
| `NONPM_TOKEN` | 備用認證 token |

## 架構

### 虛擬存儲結構

```
node_modules/
  .nonpm/                          ← 虛擬存儲
    express@4.17.1/
      package/                      ← 解壓後的包
      node_modules/                 ← 包自身的依賴（符號鏈接）
    lodash@4.17.21/
      package/
      node_modules/
  express → .nonpm/express@4.17.1/package    ← 符號鏈接
  lodash  → .nonpm/lodash@4.17.21/package     ← 符號鏈接
  .bin/                             ← 二進制鏈接
    express
```

### 模組結構

| 模組 | 說明 |
|------|------|
| `main.no` | CLI 入口與命令分發 |
| `src/utils.no` | 工具函數（字符串、文件、路徑、進程） |
| `src/json.no` | JSON 解析與生成輔助 |
| `src/semver.no` | SemVer 2.0.0 解析、比較、範圍匹配 |
| `src/config.no` | `.npmrc` 配置管理 |
| `src/registry.no` | npm registry HTTP 交互 |
| `src/resolver.no` | 依賴解析與衝突解決 |
| `src/installer.no` | 包安裝與 `node_modules` 管理 |
| `src/linker.no` | 符號鏈接管理（pnpm isolated 結構） |
| `src/lockfile.no` | `pnpm-lock.yaml` 生成與讀取 |
| `src/tarball.no` | Tarball 下載與解壓 |
| `src/workspace.no` | Workspace 多包管理 |
| `src/run.no` | 腳本執行器 |
| `src/publish.no` | 包發布 |

## 測試

```bash
# 運行所有測試
no test

# 運行指定測試
no test tests/test-semver.no
```

完整的命令列表等信息請參見 [`nonpm/README.md`](https://github.com/lizongying/notools/blob/main/nonpm/README.md)。
