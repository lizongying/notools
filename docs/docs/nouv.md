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

詳細的命令列表、環境變量、模組架構等信息請參見 [`nouv/README.md`](https://github.com/lizongying/notools/blob/main/nouv/README.md)。
