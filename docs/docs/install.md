---
sidebar_position: 2
---

# 安裝與使用

## 安裝

### 方式一：從 Releases 下載預編譯二進制（推薦）

直接從 [GitHub Releases](https://github.com/lizongying/notools/releases) 下載對應平台的已編譯好二進制文件，無需安裝編譯器。

五個獨立工具各自構建，可按需下載：

| 工具 | 說明 |
|------|------|
| `notools` | Unix 常用命令行工具集（193 個命令） |
| `nogit` | 純 Nolang Git 實現（不依賴系統 `git`） |
| `noimg` | 純 Nolang 圖像處理工具庫（9 種格式、55+ 種操作） |
| `nouv` | 純 Nolang Python 包管理器（兼容 uv/pip） |
| `nonpm` | 純 Nolang Node.js 包管理器（兼容 pnpm） |

支持的平台：

| 平台 | notools | nogit | noimg | nouv | nonpm |
|------|---------|-------|-------|------|-------|
| Linux amd64 | `notools-linux-amd64` | `nogit-linux-amd64` | `noimg-linux-amd64` | `nouv-linux-amd64` | `nonpm-linux-amd64` |
| Linux arm64 | `notools-linux-arm64` | `nogit-linux-arm64` | `noimg-linux-arm64` | `nouv-linux-arm64` | `nonpm-linux-arm64` |
| macOS amd64 | `notools-darwin-amd64` | `nogit-darwin-amd64` | `noimg-darwin-amd64` | `nouv-darwin-amd64` | `nonpm-darwin-amd64` |
| macOS arm64 | `notools-darwin-arm64` | `nogit-darwin-arm64` | `noimg-darwin-arm64` | `nouv-darwin-arm64` | `nonpm-darwin-arm64` |
| Windows amd64 | `notools-windows-amd64.exe` | `nogit-windows-amd64.exe` | `noimg-windows-amd64.exe` | `nouv-windows-amd64.exe` | `nonpm-windows-amd64.exe` |
| Windows arm64 | `notools-windows-arm64.exe` | `nogit-windows-arm64.exe` | `noimg-windows-arm64.exe` | `nouv-windows-arm64.exe` | `nonpm-windows-arm64.exe` |

```bash
# Linux amd64 示例 — 按需安裝
# notools
curl -fsSL -o notools https://github.com/lizongying/notools/releases/latest/download/notools-linux-amd64
chmod +x notools && sudo mv notools /usr/local/bin/

# nogit
curl -fsSL -o nogit https://github.com/lizongying/notools/releases/latest/download/nogit-linux-amd64
chmod +x nogit && sudo mv nogit /usr/local/bin/

# noimg
curl -fsSL -o noimg https://github.com/lizongying/notools/releases/latest/download/noimg-linux-amd64
chmod +x noimg && sudo mv noimg /usr/local/bin/

# nouv
curl -fsSL -o nouv https://github.com/lizongying/notools/releases/latest/download/nouv-linux-amd64
chmod +x nouv && sudo mv nouv /usr/local/bin/

# nonpm
curl -fsSL -o nonpm https://github.com/lizongying/notools/releases/latest/download/nonpm-linux-amd64
chmod +x nonpm && sudo mv nonpm /usr/local/bin/
```

下載後可使用同目錄下的 `checksums-sha256.txt` 進行校驗。

### 方式二：從源碼構建

五個子項目各自獨立構建：

```bash
# 克隆項目
git clone git@github.com:lizongying/notools.git notools
cd notools

# 構建 notools（需先安裝 Nolang）
cd notools && no build && cd ..
cp notools/dist/notools /usr/local/bin/notools

# 構建 nogit
cd nogit && no build && cd ..
cp nogit/dist/nogit /usr/local/bin/nogit

# 構建 noimg
cd noimg && no build && cd ..
cp noimg/dist/noimg /usr/local/bin/noimg

# 構建 nouv
cd nouv && no build && cd ..
cp nouv/dist/nouv /usr/local/bin/nouv

# 構建 nonpm
cd nonpm && no build && cd ..
cp nonpm/dist/nonpm /usr/local/bin/nonpm
```

## 使用方式

### 通用格式

```bash
notools <command> [args]
```

### 管道示例

```bash
echo "hello world" | notools grep hello
notools cat file.txt | notools sort | notools uniq -c
```

### 查看幫助

```bash
notools
```

## 環境要求

- **Nolang 編譯器**（僅從源碼構建時需要）：從 [Nolang Releases](https://github.com/lizongying/nolang/releases/latest) 下載安裝
- **操作系統**：Linux、macOS、Windows
- **架構**：amd64、arm64
