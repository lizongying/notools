---
sidebar_position: 3
---

# nouv（純 Nolang Python 包管理器）

notools 倉庫內含一個**純 Nolang 實現的 Python 包和項目管理器**（`nouv/` 目錄），兼容 [uv](https://github.com/astral-sh/uv) 和 pip 接口，管理完整的 Python 項目生命週期。

## 特性

- pip 兼容接口（install / uninstall / freeze / list / show / compile / sync）
- 完整的 pyproject.toml 項目生命週期管理（init → add → sync → lock → build → publish）
- 虛擬環境管理（venv 創建、激活提示、依賴升級）
- Python 版本管理（從 python-build-standalone 下載安裝）
- 工具管理（uvx/pipx 風格的 ephemeral 環境運行 CLI 工具）
- 依賴解析器（PEP 508 解析、環境標記求值、版本約束、回溯解析）
- Lockfile 生成與管理（uv.lock 格式，支持哈希、源信息）
- Wheel 安裝與構建（ZIP 解壓安裝、entry point 腳本、sdist/wheel 打包）
- 多源依賴（registry / git / url / path / editable）
- 全局緩存（wheel/sdist/url/git 去重緩存，prune 清理）
- Workspace 支持（多包工作區）
- 全局配置（環境變量、配置文件、pyproject.toml `[tool.uv]` 層級優先級）

## 主要命令

| 命令 | 說明 |
|------|------|
| `init [path]` | 創建新的 Python 項目 |
| `add <pkg>` | 添加依賴（`--dev`、`--editable`、`--group=`） |
| `remove <pkg>` | 移除依賴 |
| `sync` | 同步環境與依賴 |
| `lock` | 生成 uv.lock 鎖文件 |
| `run <cmd>` | 在項目環境中運行命令 |
| `build` | 構建項目分發 |
| `pip install <pkg>` | pip 兼容安裝接口 |
| `venv [path]` | 創建虛擬環境 |
| `python install <ver>` | 安裝 Python 版本 |
| `tool run <cmd>` | 在臨時環境中運行工具 |
| `uvx <pkg>` | 運行工具的快捷方式 |
| `cache clean` | 清空緩存 |

## 構建與運行

```bash
cd nouv
no build
# 產物位於 nouv/dist/nouv

# 示例：創建新項目
nouv init my-project
cd my-project
nouv add requests
nouv sync
nouv run python main.py
```

## 環境變量

nouv 兼容 uv 的環境變量命名（`UV_*`），同時支持 pip 的 `PIP_*` 變量。

| 變量 | 說明 |
|------|------|
| `UV_INDEX_URL` | 主索引 URL |
| `UV_EXTRA_INDEX_URL` | 額外索引 URL |
| `UV_CACHE_DIR` | 緩存目錄 |
| `UV_PYTHON` | Python 版本或路徑 |
| `UV_NO_SYNC` | 跳過同步 |
| `UV_FROZEN` | 凍結模式 |
| `UV_LOCKED` | 鎖定模式 |
| `UV_NO_CACHE` | 禁用緩存 |
| `UV_LINK_MODE` | 鏈接模式（clone / copy / symlink / hardlink） |
| `UV_TOKEN` | Bearer token 認證 |
| `UV_PUBLISH_TOKEN` | 發布 token |
| `UV_PUBLISH_URL` | 發布 URL |
| `UV_TOOL_DIR` | 工具安裝目錄 |
| `UV_CONFIG_FILE` | 配置文件路徑 |

## 模組架構

| 模組 | 職責 |
|------|------|
| `main.no` | CLI 入口與命令分發 |
| `src/config.no` | pyproject.toml 配置讀寫 |
| `src/dependency.no` | 依賴解析與版本約束 |
| `src/resolver.no` | 回溯依賴解析器（PEP 508 + 環境標記） |
| `src/registry.no` | PyPI 註冊表 HTTP 客戶端（Simple API / JSON API） |
| `src/installer.no` | 包安裝與卸載（wheel / sdist） |
| `src/venv.no` | 虛擬環境管理 |
| `src/python.no` | Python 版本發現與安裝 |
| `src/tool.no` | 工具管理（uvx / pipx） |
| `src/lockfile.no` | uv.lock 鎖文件生成與解析 |
| `src/wheel.no` | Wheel 格式處理（解析 / 安裝 / entry point） |
| `src/sdist.no` | 源碼分發包處理（PEP 517 構建後端） |
| `src/cache.no` | 全局緩存管理 |
| `src/pep508.no` | PEP 508 依賴規範解析器 |
| `src/markers.no` | PEP 508 環境標記求值 |
| `src/sources.no` | 多源依賴（registry / git / url / path / editable） |
| `src/toml.no` | TOML 解析器 |
| `src/utils.no` | 通用工具函數 |

## 已知限制

- 註冊表的 JSON API 接口為 stub 實現（待 Nolang JSON 對象迭代 API 完善後補全）
- `nouv self update` 尚未實現
- sdist 構建安裝（`install-from-source`）為簡化實現
- 環境標記中 `python_version` 通過 `python3 -c` 獲取，依賴系統 Python
- Wheel 安裝的 entry point 腳本為簡化實現

完整的項目結構等信息請參見 [`nouv/README.md`](https://github.com/lizongying/notools/blob/main/nouv/README.md)。
