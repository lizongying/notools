---
sidebar_position: 3
---

# 项目结构

```
notools/
├── main.no              # 入口，子命令分发
├── src/
│   ├── echo.no          # 各工具实现
│   ├── cat.no
│   ├── ls.no
│   ├── chroot.no        # 原生 os.chroot() 系统调用
│   ├── stdbuf.no        # 管道代理模式缓冲控制
│   ├── bzip2.no         # bzip2 压缩/解压（archive/bzip2）
│   ├── xz.no            # xz/lzma 压缩/解压（archive/xz）
│   ├── zstd.no          # zstd 压缩/解压（archive/zstd）
│   ├── curl.no          # 纯 Nolang HTTP 客户端（net TCP）
│   ├── ping.no          # 纯 Nolang ICMP 回显（net.ping）
│   ├── hmac.no          # HMAC 密钥摘要
│   ├── hashutil.no      # 哈希命令共享逻辑
│   ├── sha256x.no       # SHA-256 纯 Nolang 实现
│   ├── sha512x.no       # SHA-512（64 位字运算）
│   ├── md5x.no          # MD5
│   └── ...              # 其余 190+ 个工具
├── nogit/               # 纯 Nolang Git 实现（独立子项目）
│   ├── main.no          # nogit CLI 入口与命令分发
│   └── src/             # 底层模块（object/refs/index/pack/...）
├── noimg/               # 纯 Nolang 图像处理工具库（独立子项目）
│   ├── main.no          # noimg CLI 入口与命令分发
│   ├── lib.no           # 库导出声明
│   └── src/             # 格式编解码与图像操作模块
├── nouv/                # 纯 Nolang Python 包管理器（独立子项目）
│   ├── main.no          # nouv CLI 入口与命令分发
│   └── src/             # 依赖解析/安装/锁文件/工具管理等模块
├── nonpm/               # 纯 Nolang Node.js 包管理器（独立子项目）
│   ├── main.no          # nonpm CLI 入口与命令分发
│   └── src/             # 依赖解析/安装/锁文件/发布等模块
└── package.jsonc        # 项目配置
```

## 已知限制

- 全部已实现命令均已在 macOS (arm64) 上构建并验证可用。
- `who` / `users` / `pinky` 为简化实现，仅显示当前用户会话（通过 `os.get-login()` + `os.ttyname(0)`），不遍历 utmpx 列出全部登录会话。
- `compress` / `uncompress` 为纯 Nolang LZW 实现，与系统 `compress` 命令的 `.Z` 格式兼容。
- `less` 使用行输入（`fs.get-line()`），不支持字符级即时响应（需终端 raw 模式）。
- `bzip2` / `xz` / `lzma` / `zstd` 系列命令的**解压缩**使用纯 Nolang 标准库模块实现，不委托系统命令；**压缩**侧为简化实现，尚未实现完整 BWT / LZMA2 / FSE 压缩算法。
- `chroot` 使用原生 `os.chroot()` 系统调用，需要 root 权限。
- `stdbuf` 使用纯 Nolang 管道代理模式实现，支持 `-o0`/`-oL`/`-oB`/`-e0`/`-eL`/`-eB` 缓冲模式。

## 许可证

MIT
