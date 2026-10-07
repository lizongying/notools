# nouv

纯 [Nolang](https://github.com/lizongying/nolang) 实现的 [uv](https://github.com/astral-sh/uv)（Python 包和项目管理器）。

## 特性

- 纯 Nolang 实现，不依赖 Python 自身的 pip/venv/virtualenv
- 完整的 pyproject.toml 项目生命周期管理（init → add → sync → lock → build → publish）
- pip 兼容接口（install / uninstall / freeze / list / show / compile / sync）
- 虚拟环境管理（venv 创建、激活提示、依赖升级）
- Python 版本管理（从 [python-build-standalone](https://github.com/astral-sh/python-build-standalone) 下载安装）
- 工具管理（uvx/pipx 风格的 ephemeral 环境运行 CLI 工具）
- 依赖解析器（PEP 508 解析、环境标记求值、版本约束、回溯解析）
- Lockfile 生成与管理（uv.lock 格式，支持哈希、源信息）
- Wheel 安装与构建（ZIP 解压安装、entry point 脚本、sdist/wheel 打包）
- 多源依赖（registry / git / url / path / editable）
- 全局缓存（wheel/sdist/url/git 去重缓存，prune 清理）
- Workspace 支持（多包工作区）
- 全局配置（环境变量、配置文件、pyproject.toml `[tool.uv]` 层级优先级）

## 安装

### 方式一：从 Releases 下载预编译二进制

```bash
# Linux amd64 示例
curl -fsSL -o nouv https://github.com/lizongying/notools/releases/latest/download/nouv-linux-amd64
chmod +x nouv && sudo mv nouv /usr/local/bin/
```

### 方式二：从源码构建

```bash
cd nouv
no build
# 产物位于 nouv/dist/nouv
```

### 方式三：直接运行

```bash
no run /path/to/nouv <command> [args...]
```

## 命令列表

### 项目管理

| 命令 | 说明 | 示例 |
|------|------|------|
| `init [path]` | 创建新的 Python 项目 | `nouv init my-project` |
| `add <pkg> [pkg...]` | 添加依赖（`--dev`、`--editable`、`--group=`） | `nouv add requests` |
| `remove <pkg> [pkg...]` | 移除依赖 | `nouv remove requests` |
| `sync` | 同步环境与依赖（`--frozen`、`--locked`） | `nouv sync` |
| `lock` | 生成 uv.lock 锁文件 | `nouv lock` |
| `run <cmd>` | 在项目环境中运行命令 | `nouv run python main.py` |
| `build` | 构建项目分发（`--sdist`、`--wheel`） | `nouv build` |
| `publish` | 发布项目到 PyPI | `nouv publish` |
| `export` | 导出锁文件为 requirements 格式 | `nouv export --format=requirements` |
| `tree [pkg]` | 显示依赖树 | `nouv tree` |

### pip 兼容接口

| 命令 | 说明 | 示例 |
|------|------|------|
| `pip install <pkg>` | 安装包（`--reinstall`、`--upgrade`、`--no-deps`、`-e`） | `nouv pip install requests` |
| `pip uninstall <pkg>` | 卸载包 | `nouv pip uninstall requests` |
| `pip freeze` | 列出已安装包（freeze 格式） | `nouv pip freeze` |
| `pip list` | 列出已安装包 | `nouv pip list` |
| `pip show <pkg>` | 显示包详情 | `nouv pip show requests` |
| `pip compile <file>` | 编译 requirements 到锁文件 | `nouv pip compile requirements.txt` |
| `pip sync <file>` | 用 requirements 文件同步环境 | `nouv pip sync requirements.txt` |

### 虚拟环境

| 命令 | 说明 | 示例 |
|------|------|------|
| `venv [path]` | 创建虚拟环境（`--seed`、`--clear`、`--upgrade`、`--python=`） | `nouv venv .venv` |

### Python 版本管理

| 命令 | 说明 | 示例 |
|------|------|------|
| `python install <ver>` | 安装 Python 版本 | `nouv python install 3.12.7` |
| `python uninstall <ver>` | 卸载 Python 版本 | `nouv python uninstall 3.12.7` |
| `python list` | 列出已安装的 Python 版本 | `nouv python list` |
| `python dir` | 显示 Python 安装目录 | `nouv python dir` |
| `python find <ver>` | 查找可用的 Python 版本 | `nouv python find 3.12` |
| `python pin <ver>` | 固定项目 Python 版本 | `nouv python pin 3.12` |

### 工具管理

| 命令 | 说明 | 示例 |
|------|------|------|
| `tool run <cmd>` | 在临时环境中运行工具（`--from=`、`--with=`） | `nouv tool run ruff check` |
| `tool install <pkg>` | 安装工具 | `nouv tool install ruff` |
| `tool list` | 列出已安装工具 | `nouv tool list` |
| `tool upgrade [pkg]` | 升级工具（`--all`） | `nouv tool upgrade --all` |
| `tool uninstall <pkg>` | 卸载工具 | `nouv tool uninstall ruff` |
| `tool dir` | 显示工具安装目录 | `nouv tool dir` |
| `tool clear` | 移除所有工具 | `nouv tool clear` |
| `uvx <pkg> [args...]` | 运行工具的快捷方式（等同 `tool run`） | `nouv uvx ruff check` |

### 缓存管理

| 命令 | 说明 | 示例 |
|------|------|------|
| `cache clean` | 清空缓存 | `nouv cache clean` |
| `cache dir` | 显示缓存目录 | `nouv cache dir` |
| `cache prune` | 清理过期缓存 | `nouv cache prune` |

### 其他

| 命令 | 说明 | 示例 |
|------|------|------|
| `self version` | 显示版本 | `nouv self version` |
| `version` | 显示版本 | `nouv version` |
| `help` | 显示帮助 | `nouv help` |

### 全局选项

| 选项 | 说明 |
|------|------|
| `-V, --version` | 显示版本 |
| `-h, --help` | 显示帮助 |
| `-q, --quiet` | 安静输出 |
| `-v, --verbose` | 详细输出 |
| `--no-cache` | 禁用缓存 |
| `--no-sync` | 修改后不同步 |
| `--frozen` | 不更新锁文件 |
| `--locked` | 要求锁文件最新 |
| `--index-url URL` | 主索引 URL |
| `--extra-index-url URL` | 额外索引 URL |
| `--python VER` | Python 版本 |
| `--no-color` | 禁用彩色输出 |
| `--native-tls` | 使用系统 TLS |
| `--preview` | 启用预览功能 |

## 快速开始

```bash
# 创建新项目
nouv init my-project
cd my-project

# 添加依赖
nouv add requests flask
nouv add --dev pytest

# 同步环境
nouv sync

# 运行命令
nouv run python -m pytest

# 生成锁文件
nouv lock

# 构建
nouv build

# 导出 requirements
nouv export -o requirements.txt
```

## 环境变量

nouv 兼容 uv 的环境变量命名（`UV_*`），同时支持 pip 的 `PIP_*` 变量。

| 变量 | 说明 |
|------|------|
| `UV_INDEX_URL` | 主索引 URL |
| `UV_EXTRA_INDEX_URL` | 额外索引 URL |
| `UV_CACHE_DIR` | 缓存目录 |
| `UV_PYTHON` | Python 版本或路径 |
| `UV_NO_SYNC` | 跳过同步 |
| `UV_FROZEN` | 冻结模式 |
| `UV_LOCKED` | 锁定模式 |
| `UV_NO_CACHE` | 禁用缓存 |
| `UV_LINK_MODE` | 链接模式（clone/copy/symlink/hardlink） |
| `UV_TOKEN` | Bearer token 认证 |
| `UV_PUBLISH_TOKEN` | 发布 token |
| `UV_PUBLISH_URL` | 发布 URL |
| `UV_TOOL_DIR` | 工具安装目录 |
| `UV_CONFIG_FILE` | 配置文件路径 |

## 模块架构

| 模块 | 职责 |
|------|------|
| `main.no` | CLI 入口与命令分发 |
| `src/config.no` | pyproject.toml 配置读写 |
| `src/dependency.no` | 依赖解析与版本约束 |
| `src/resolver.no` | 回溯依赖解析器（PEP 508 + 环境标记） |
| `src/registry.no` | PyPI 注册表 HTTP 客户端（Simple API / JSON API） |
| `src/httpclient.no` | 纯 Nolang HTTPS/1.1 GET 客户端（基于 std tls，带超时预算） |
| `src/jsonx.no` | 轻量 JSON 解析器（绕过 std json 运行时缺陷，供注册表 JSON API 使用） |
| `src/installer.no` | 包安装与卸载（wheel/sdist） |
| `src/venv.no` | 虚拟环境管理 |
| `src/python.no` | Python 版本发现与安装 |
| `src/tool.no` | 工具管理（uvx/pipx） |
| `src/lockfile.no` | uv.lock 锁文件生成与解析 |
| `src/wheel.no` | Wheel 格式处理（解析/安装/entry point） |
| `src/sdist.no` | 源码分发包处理（PEP 517 构建后端） |
| `src/build.no` | 项目构建与发布 |
| `src/cache.no` | 全局缓存管理 |
| `src/pep508.no` | PEP 508 依赖规范解析器 |
| `src/markers.no` | PEP 508 环境标记求值 |
| `src/sources.no` | 多源依赖管理（registry/git/url/path/editable） |
| `src/runner.no` | 命令执行与 PEP 723 内联脚本 |
| `src/settings.no` | 全局设置与环境变量 |
| `src/requirements.no` | requirements.txt 解析与生成 |
| `src/workspace.no` | 工作区管理 |
| `src/ptoml.no` | 最小 TOML 解析/序列化器（读写 pyproject.toml，支持 `[[数组表]]`） |
| `src/version.no` | 版本号解析与比较 |
| `src/utils.no` | 通用工具函数 |

## 项目结构

```
nouv/
├── main.no              ; CLI 入口与命令分发
├── package.jsonc        ; 项目配置
├── src/
│   ├── build.no         ; 项目构建与发布
│   ├── cache.no         ; 全局缓存管理
│   ├── config.no        ; pyproject.toml 配置
│   ├── dependency.no    ; 依赖解析
│   ├── httpclient.no    ; 纯 Nolang HTTPS 客户端
│   ├── installer.no     ; 包安装/卸载
│   ├── jsonx.no         ; 轻量 JSON 解析器
│   ├── lockfile.no      ; uv.lock 锁文件
│   ├── markers.no       ; 环境标记求值
│   ├── pep508.no        ; PEP 508 解析器
│   ├── ptoml.no         ; TOML 解析/序列化
│   ├── python.no        ; Python 版本管理
│   ├── registry.no      ; PyPI 注册表客户端
│   ├── requirements.no  ; requirements.txt 处理
│   ├── resolver.no      ; 回溯依赖解析器
│   ├── runner.no        ; 命令执行
│   ├── sdist.no         ; 源码分发包
│   ├── settings.no      ; 全局设置
│   ├── sources.no       ; 多源依赖
│   ├── tool.no          ; 工具管理
│   ├── utils.no         ; 通用工具
│   ├── venv.no          ; 虚拟环境
│   ├── version.no       ; 版本号工具
│   ├── wheel.no         ; Wheel 格式处理
│   └── workspace.no     ; 工作区管理
├── tests/
│   ├── run-all.no            ; 统一测试运行器（串行执行下列套件）
│   ├── test-version.no       ; 版本比较测试
│   ├── test-pep508.no        ; PEP 508 解析测试
│   ├── test-wheel.no         ; Wheel 测试
│   ├── test-toml.no          ; TOML 解析测试（含 [[数组表]]）
│   ├── test-markers.no       ; 环境标记测试
│   ├── test-cache.no         ; 缓存测试
│   ├── test-venv.no          ; 虚拟环境测试
│   ├── test-python.no        ; Python 管理测试
│   ├── test-installer.no     ; 安装器测试
│   ├── test-registry.no      ; 注册表测试
│   ├── test-registry-json.no ; 注册表 JSON API 测试
│   ├── test-sdist.no         ; sdist 测试
│   ├── test-lockfile.no      ; 锁文件测试
│   └── test-httpclient.no    ; HTTP 超时测试
└── dist/                ; 构建产物
```

## 测试

```bash
# 定位 no 编译器：优先 $NO_BIN，其次 PATH 上的 `no`
NO_BIN=/absolute/path/to/no no run tests/run-all.no
```

`run-all.no` 会串行执行 `tests/` 下所有离线套件（当前 14 个）。单个套件也可直接 `no run tests/<file>.no`。

## 已知限制

- `nouv self update` 尚未实现
- sdist 构建（`python -m build`）与从源码安装（`install-from-source`）为简化实现，仍需系统 `python3`/`pip`
- 环境标记中 `python_version` 通过 `python3 -c` 获取，依赖系统 Python
- Wheel 安装的 entry point 脚本为简化实现
- 网络相关命令（`add`/`sync`/`lock`/`publish`、`python install`、`tool run`、sdist 下载）需要联网，回归仅在离线单元层面验证；HTTP 客户端带可配置超时预算（`NOUV_HTTP_TIMEOUT`，默认 30s）
- 归档读写、目录遍历、文件查找等已改为纯 Nolang 实现（std `archive/tar`、`archive/zip`、`fs`），不再依赖外部 `tar`/`unzip`/`find`/`ls`/`uname`；仅 `tool.no` 的部分软链/路径操作仍调用系统 `ln`/`ls`

## 许可证

MIT
