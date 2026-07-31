# notools

Unix 常用命令行工具集，使用 [Nolang](https://github.com/lizongying/nolang) 语言实现。

## 特性

- 纯 Nolang 实现
- 单一可执行文件，子命令分发
- 支持 stdin 管道与文件输入
- 友好的错误处理

## 安装

```bash
# 克隆项目
git clone git@github.com:lizongying/notools.git notools
cd notools

# 构建（需先安装 Nolang）
no build

# 产物位于 dist/main，可重命名为 notools
cp dist/notools /usr/local/bin/notools
```

## 工具列表

### 文件与目录

| 命令 | 说明 | 示例 |
|------|------|------|
| `ls` | 列出目录内容 | `notools ls -l /tmp` |
| `tree` | 显示目录树 | `notools tree -L 2` |
| `cat` | 输出文件内容 | `notools cat file.txt` |
| `touch` | 创建空文件或更新时间戳 | `notools touch new.txt` |
| `mv` | 移动或重命名 | `notools mv a.txt b.txt` |
| `rm` | 删除文件或目录 | `notools rm -r dir/` |
| `chmod` | 修改文件权限 | `notools chmod 755 script.sh` |
| `find` | 递归查找文件 | `notools find . -name "*.no"` |
| `cp` | 复制文件（单源复制 / 复制到目录） | `notools cp src.txt dst.txt` |
| `ln` | 创建硬链接 / 符号链接（-s） | `notools ln -s src.txt link.txt` |
| `du` | 估算文件 / 目录磁盘占用 | `notools du dir/` |
| `df` | 显示文件系统磁盘空间 | `notools df` |

### 文本处理

| 命令 | 说明 | 示例 |
|------|------|------|
| `echo` | 输出参数 | `notools echo -n hello` |
| `grep` | 搜索文本模式 | `notools grep -n pattern file.txt` |
| `wc` | 统计行/词/字节 | `notools wc -l file.txt` |
| `sort` | 排序行 | `notools sort -r file.txt` |
| `uniq` | 去除连续重复行 | `notools uniq -c file.txt` |
| `sed` | 流编辑器（替换） | `notools sed 's/old/new/g' file.txt` |
| `awk` | 字段提取 | `notools awk '{print $1}' file.txt` |
| `tr` | 字符转换 / 删除 | `echo "abc" \| notools tr a X` |
| `cut` | 按字段（-d/-f）或字符（-c）截取 | `echo "a,b" \| notools cut -d, -f 1` |
| `tee` | 输出到 stdout 并同时写入文件 | `echo hi \| notools tee out.txt` |
| `head` | 输出文件开头 N 行（-n N） | `notools head -n 10 file.txt` |
| `tail` | 输出文件末尾 N 行（-n N） | `notools tail -n 5 file.txt` |

### 归档

| 命令 | 说明 | 示例 |
|------|------|------|
| `tar` | 创建/解压/列出 tar 归档 | `notools tar -cf out.tar file` |
| `zip` | 创建 zip 归档 | `notools zip out.zip file1 file2` |
| `unzip` | 解压/列出 zip 归档 | `notools unzip -l out.zip` |

### 系统

| 命令 | 说明 | 示例 |
|------|------|------|
| `ps` | 列出进程 | `notools ps -ef` |
| `top` | 显示系统资源与进程 | `notools top -n 20` |
| `date` | 显示系统日期与时间 | `notools date` |
| `pwd` | 打印当前工作目录 | `notools pwd` |
| `whoami` | 打印当前用户名 | `notools whoami` |
| `sleep` | 暂停指定时长（支持 s/m/h） | `notools sleep 1` |

### 网络

| 命令 | 说明 | 示例 |
|------|------|------|
| `curl` | 纯 Nolang HTTP/1.1 客户端（`net` TCP 实现，仅 `http://`） | `notools curl http://127.0.0.1:8080/file` |
| `ping` | 纯 Nolang ICMP 回显请求（内置 `net.ping`，默认 `-c 4`） | `notools ping -c 4 127.0.0.1` |

### 哈希与编码

| 命令 | 说明 | 示例 |
|------|------|------|
| `md5` | MD5 摘要（128 位，纯 Nolang 实现） | `notools md5 file.txt`、`echo -n abc \| notools md5` |
| `sha1` | SHA-1 摘要（160 位） | `notools sha1 file.txt` |
| `sha224` | SHA-224 摘要（224 位） | `notools sha224 file.txt` |
| `sha256` | SHA-256 摘要（256 位） | `notools sha256 file.txt` |
| `sha384` | SHA-384 摘要（384 位，64 位字运算） | `notools sha384 file.txt` |
| `sha512` | SHA-512 摘要（512 位，64 位字运算） | `notools sha512 file.txt` |
| `base64` | Base64 编码/解码（RFC 4648，`-d` 解码） | `notools base64 file.bin`、`echo -n YWJj \| notools base64 -d` |
| `hmac` | HMAC 密钥摘要（`-a md5\|sha1\|sha256\|sha512`，`-k` 指定密钥，默认 sha256） | `notools hmac -a sha256 -k key message` |

> 哈希/HMAC 输出与 GNU coreutils / Python hashlib 逐字节一致（已用 abc / 空输入 / 长输入 / 二进制随机输入对照验证）。所有算法均为纯 Nolang 实现：MD5/SHA-224/SHA-256/SHA-1/SHA-384/SHA-512 完整实现于 `src/*x.no`；HMAC 的 sha1/sha256/sha512 复用标准库 `hmac`，md5 按 RFC 2104 手工实现（含长 key 先哈希）。实现过程中规避了当前编译器的两个 codegen 缺陷：str 返回值静默丢失（改用 void 函数直接 `print`）与旋转表达式 `@llvm.fshl` 子表达式损坏（拆分为独立移位局部变量），详见 [NOLANG_STDLIB_ISSUES.md](./NOLANG_STDLIB_ISSUES.md)。

> ⚠️ 网络命令现状：`curl` 与 `ping` 现已改为**纯 Nolang 实现**，不再委托系统命令（`process.process-system`）。`curl` 基于标准库 `net` 的 TCP 原语自行实现 HTTP/1.1 客户端（仅支持 `http://`，暂不支持 TLS/HTTPS）；`ping` 使用内置的 `net.ping` / `net.ping-count`（ICMP Echo 在纯 Nolang 中构造）。两者受标准库当前限制：**DNS 解析（`dns.dns-resolve`）在当前编译器（v5b4f734）下会令程序编译失败**（GEP 空指针，`opt` 阶段报错），因此 `curl` / `ping` 仅接受 **IP 字面量**主机（如 `127.0.0.1`），不支持域名；`curl` 亦不支持 `https://`（标准库已有纯 Nolang `tls.no`，但 `tls-conn.connect` 同样依赖 `net-dial` 无法解析域名，且 `tls` 接收路径的 `it` 绑定存在 codegen 崩溃 B12，尚不可用）。`ln` 是目前唯一仍委托系统命令 `ln` 的命令 —— 因为标准库 `fs` 暂无 `symlink` / `link` 内置。标准库的已知问题与待实现项见 [NOLANG_STDLIB_ISSUES.md](./NOLANG_STDLIB_ISSUES.md)。

## 用法

```bash
# 通用格式
notools <command> [args]

# 管道示例
echo "hello world" | notools grep hello
notools cat file.txt | notools sort | notools uniq -c

# 查看帮助
notools
```

## 已知限制

- `cp` 多源复制（一次复制多个源文件）因当前编译器优化器会错误编译「循环内拼接目标路径中的 basename」而暂不支持（详见 [NOLANG_STDLIB_ISSUES.md](./NOLANG_STDLIB_ISSUES.md) B11）。「每进程只能写一次文件」的限制已由编译器修复，单源复制本身工作正常。`cp` 仅支持**单源复制**（含「复制到目录」，自动以源文件名命名）；多源复制会明确报错退出，不会静默丢文件。
- 其余命令（echo / cat / ls / rm / tree / mv / touch / find / grep / wc / sort / uniq / sed / awk / chmod / tar / zip / unzip / ps / top / mkdir / stat / chown / cp / head / tail / date / pwd / du / df / ln / cut / tr / tee / sleep / whoami / curl / ping）均已在 macOS (arm64) 上验证可用。
- 哈希/编码命令（md5 / sha1 / sha224 / sha256 / sha384 / sha512 / base64 / hmac）已逐一验证正确，且 `main.no` 已接入分发；但**当前开发中的编译器 HEAD（2026-07-27 晚间构建）对内建 `printf` 存在回归**（最小 3 行 `printf('%s', 'hi')` 程序即报 `use of undefined value '@printf'`），导致所有使用 `printf` 的旧命令（echo 等）乃至完整 `main.no` 暂时无法编译——这与哈希代码无关（哈希命令不用 `printf`，单独入口可正常编译运行）。待编译器修复后 `no build notools/main.no` 即可直接产出完整二进制。

## 项目结构

```
notools/
├── main.no          # 入口，子命令分发
├── src/
│   ├── echo.no      # 各工具实现
│   ├── cat.no
│   ├── ls.no
│   ├── ...
│   └── top.no
└── mod.jsonc        # 项目配置
```

## 开发

```bash
# 构建
no build ./notools/main.no

# 运行
no run ./notools/main.no <command> [args]
```

## 许可证

MIT
