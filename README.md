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
| `curl` | 纯 Nolang HTTP/1.1 客户端（`net` TCP 实现，支持 `http://` 和 `https://`） | `notools curl https://127.0.0.1:8443/file` |
| `ping` | 纯 Nolang ICMP 回显请求（内置 `net.ping`，默认 `-c 4`，支持 IP 和域名） | `notools ping -c 4 example.com` |

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

> `curl` 基于标准库 `net` 的 TCP 原语自行实现 HTTP/1.1 客户端（支持 `http://` 和 `https://`）；`ping` 使用内置的 `net.ping` / `net.ping-count`（ICMP Echo 在纯 Nolang 中构造）。两者均支持 **IP 字面量**和**域名**主机（`net-dial` 内部通过 `getaddrinfo` 解析域名）。`curl` 的 `https://` 路径使用标准库纯 Nolang `tls.no`（TLS 1.2/1.3 客户端）。此前限制 DNS 解析与 HTTPS 的编译器 codegen 缺陷已修复：`it` 绑定的 primitive option 类型处理（stmt.go）、结构体字段赋值的深拷贝（expr.go）及结构体/字符串零初始化（stmt.go llvm.memset）。

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
