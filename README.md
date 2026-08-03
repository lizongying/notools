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

> 以下为已实现并接入分发的全部命令（160+ 个）。`md5`/`sha*` 为 BSD 风格命名，`md5sum`/`sha*sum` 为 GNU 风格命名，两者输出相同。

### 文件与目录

| 命令 | 说明 | 示例 |
|------|------|------|
| `ls` | 列出目录内容 | `notools ls -l /tmp` |
| `dir` | 类似 `ls`，默认不彩色、按列输出 | `notools dir` |
| `vdir` | 等同 `ls -l` | `notools vdir` |
| `tree` | 显示目录树 | `notools tree -L 2` |
| `cat` | 输出文件内容 | `notools cat file.txt` |
| `cp` | 复制文件 / 目录（支持多源、`-r` 递归） | `notools cp a.txt b.txt dir/` |
| `mv` | 移动或重命名 | `notools mv a.txt b.txt` |
| `rm` | 删除文件或目录 | `notools rm -r dir/` |
| `ln` | 创建硬链接 / 符号链接（-s） | `notools ln -s src.txt link.txt` |
| `link` | 创建硬链接 | `notools link a b` |
| `unlink` | 删除单个文件 | `notools unlink a.txt` |
| `touch` | 创建空文件或更新时间戳 | `notools touch new.txt` |
| `mkdir` | 创建目录 | `notools mkdir -p a/b/c` |
| `rmdir` | 删除空目录 | `notools rmdir empty/` |
| `mkfifo` | 创建命名管道 | `notools mkfifo /tmp/pipe` |
| `mknod` | 创建特殊文件 | `notools mknod /tmp/f p` |
| `mktemp` | 安全创建临时文件 / 目录 | `notools mktemp -d` |
| `tempfile` | 创建临时文件 | `notools tempfile` |
| `install` | 复制文件并设置属性 | `notools install -m 755 a b` |
| `chmod` | 修改文件权限 | `notools chmod 755 script.sh` |
| `chown` | 修改文件属主 | `notools chown user:group file` |
| `chgrp` | 修改文件属组 | `notools chgrp staff file` |
| `find` | 递归查找文件 | `notools find . -name "*.no"` |
| `du` | 估算文件 / 目录磁盘占用 | `notools du dir/` |
| `df` | 显示文件系统磁盘空间 | `notools df` |
| `stat` | 显示文件状态信息 | `notools stat file.txt` |
| `file` | 判断文件类型 | `notools file data.bin` |
| `rename` | 批量重命名文件 | `notools rename 's/\.old/.new/' *.old` |
| `dd` | 按块复制 / 转换文件 | `notools dd if=in of=out bs=512` |
| `basename` | 取路径末尾文件名 | `notools basename /a/b/c.txt` |
| `dirname` | 取路径目录部分 | `notools dirname /a/b/c.txt` |
| `pwd` | 打印当前工作目录 | `notools pwd` |
| `readlink` | 读取符号链接目标 | `notools readlink link` |
| `realpath` | 输出规范绝对路径 | `notools realpath ../a/b` |
| `namei` | 逐段解析路径 | `notools namei /a/b/c` |
| `pathchk` | 检查路径可移植性 | `notools pathchk path` |
| `dircolors` | 输出 ls 配色设置 | `notools dircolors` |
| `shred` | 安全擦除文件内容 | `notools shred secret.txt` |
| `truncate` | 缩减 / 扩展文件到指定大小 | `notools truncate -s 0 log` |
| `sync` | 刷新文件系统缓冲 | `notools sync` |

### 文本查看与处理

| 命令 | 说明 | 示例 |
|------|------|------|
| `echo` | 输出参数 | `notools echo -n hello` |
| `printf` | 格式化输出 | `notools printf '%d\n' 42` |
| `head` | 输出文件开头 N 行（-n N） | `notools head -n 10 file.txt` |
| `tail` | 输出文件末尾 N 行（-n N） | `notools tail -n 5 file.txt` |
| `more` | 分页查看文件 | `notools more file.txt` |
| `less` | 增强版分页器（前后翻页、搜索） | `notools less file.txt` |
| `tac` | 逆序输出行 | `notools tac file.txt` |
| `nl` | 添加行号 | `notools nl file.txt` |
| `pr` | 分页排版打印 | `notools pr file.txt` |
| `fold` | 折断过长行 | `notools fold -w 80 file` |
| `fmt` | 段落重排 | `notools fmt -w 72 file` |
| `expand` | 制表符转空格 | `notools expand file` |
| `unexpand` | 空格转制表符 | `notools unexpand -a file` |
| `column` | 列对齐排版 | `notools column -t data` |
| `cut` | 按字段（-d/-f）或字符（-c）截取 | `echo "a,b" \| notools cut -d, -f 1` |
| `paste` | 合并文件列 | `notools paste a b` |
| `join` | 按公共字段连接 | `notools join a b` |
| `comm` | 比较两个有序文件 | `notools comm a b` |
| `csplit` | 按模式切分文件 | `notools csplit file /pattern/` |
| `split` | 按大小 / 行数切分文件 | `notools split -l 100 file` |
| `tr` | 字符转换 / 删除 | `echo "abc" \| notools tr a X` |
| `rev` | 反转每行字符 | `echo "abc" \| notools rev` |
| `grep` | 搜索文本模式 | `notools grep -n pattern file.txt` |
| `egrep` | 等同 `grep -E`（扩展正则） | `notools egrep 'a\|b' file` |
| `fgrep` | 等同 `grep -F`（固定串） | `notools fgrep literal file` |
| `sed` | 流编辑器（替换） | `notools sed 's/old/new/g' file.txt` |
| `awk` | 字段提取 | `notools awk '{print $1}' file.txt` |
| `sort` | 排序行 | `notools sort -r file.txt` |
| `uniq` | 去除连续重复行 | `notools uniq -c file.txt` |
| `shuf` | 随机打乱行 | `notools shuf file.txt` |
| `tsort` | 拓扑排序 | `notools tsort deps` |
| `wc` | 统计行/词/字节 | `notools wc -l file.txt` |
| `tee` | 输出到 stdout 并同时写入文件 | `echo hi \| notools tee out.txt` |
| `strings` | 提取可打印字符串 | `notools strings bin` |
| `od` | 八进制 / 多进制转储 | `notools od -Ax -tx1 file` |
| `hexdump` | 十六进制转储 | `notools hexdump -C file` |
| `xxd` | 十六进制转储 / 还原 | `notools xxd file` |
| `envsubst` | 替换环境变量 | `echo '$HOME' \| notools envsubst` |
| `dos2unix` | CRLF → LF | `notools dos2unix file` |
| `unix2dos` | LF → CRLF | `notools unix2dos file` |
| `mac2unix` | CR → LF | `notools mac2unix file` |
| `unix2mac` | LF → CR | `notools unix2mac file` |
| `cmp` | 逐字节比较两文件 | `notools cmp a b` |
| `diff` | 逐行差异比较 | `notools diff a b` |
| `diff3` | 三路差异比较 | `notools diff3 a b c` |
| `sdiff` | 并排差异比较 | `notools sdiff a b` |
| `patch` | 应用 diff 补丁 | `notools patch < fix.diff` |
| `test` | 条件求值 | `notools test -f file` |
| `[` | `test` 的同义形式 | `notools [ -f file ]` |

### 归档与压缩

| 命令 | 说明 | 示例 |
|------|------|------|
| `tar` | 创建/解压/列出 tar 归档 | `notools tar -cf out.tar file` |
| `zip` | 创建 zip 归档 | `notools zip out.zip file1 file2` |
| `unzip` | 解压/列出 zip 归档 | `notools unzip -l out.zip` |
| `gzip` | gzip 压缩 | `notools gzip file` |
| `gunzip` | gzip 解压 | `notools gunzip file.gz` |
| `zcat` | 解压并输出到 stdout | `notools zcat file.gz` |
| `compress` | LZW `.Z` 压缩（纯 Nolang） | `notools compress file` |
| `uncompress` | LZW `.Z` 解压（纯 Nolang） | `notools uncompress file.Z` |

### 系统信息与管理

| 命令 | 说明 | 示例 |
|------|------|------|
| `ps` | 列出进程 | `notools ps -ef` |
| `top` | 显示系统资源与进程 | `notools top -n 20` |
| `free` | 显示内存使用 | `notools free` |
| `lscpu` | 显示 CPU 架构信息 | `notools lscpu` |
| `uname` | 打印系统信息 | `notools uname -a` |
| `arch` | 打印机器架构 | `notools arch` |
| `uptime` | 系统运行时间与负载 | `notools uptime` |
| `hostname` | 打印 / 设置主机名 | `notools hostname` |
| `domainname` | 打印 NIS 域名 | `notools domainname` |
| `hostid` | 打印主机标识 | `notools hostid` |
| `dmesg` | 打印内核日志 | `notools dmesg` |
| `date` | 显示系统日期与时间 | `notools date` |
| `cal` | 显示日历 | `notools cal` |
| `nproc` | 打印可用 CPU 数 | `notools nproc` |
| `whoami` | 打印当前用户名 | `notools whoami` |
| `id` | 打印用户 / 组 ID | `notools id` |
| `groups` | 打印用户所属组 | `notools groups` |
| `logname` | 打印登录用户名 | `notools logname` |
| `who` | 列出登录会话（简化版） | `notools who` |
| `users` | 列出当前登录用户名 | `notools users` |
| `pinky` | 轻量级 who（用户信息） | `notools pinky` |
| `tty` | 打印终端名 | `notools tty` |
| `getconf` | 查询系统配置值 | `notools getconf PATH_MAX` |
| `locale` | 打印区域设置 | `notools locale` |
| `logger` | 写入系统日志 | `notools logger 'msg'` |
| `env` | 显示 / 设置环境变量运行命令 | `notools env` |
| `printenv` | 打印环境变量 | `notools printenv PATH` |
| `watch` | 周期执行命令 | `notools watch -n 1 date` |
| `clear` | 清屏 | `notools clear` |
| `reset` | 重置终端 | `notools reset` |
| `sleep` | 暂停指定时长（支持 s/m/h） | `notools sleep 1` |
| `which` | 定位可执行文件路径 | `notools which ls` |
| `whereis` | 定位二进制 / 源码 / 手册 | `notools whereis ls` |
| `locate` | 基于预建数据库的快速文件查找 | `notools locate pattern` |
| `updatedb` | 更新 `locate` 数据库 | `notools updatedb -U /` |
| `ptx` | 生成置换索引 | `notools ptx file.txt` |

### 进程与作业控制

| 命令 | 说明 | 示例 |
|------|------|------|
| `kill` | 发送信号给进程 | `notools kill -9 1234` |
| `killall` | 按名称杀进程 | `notools killall myapp` |
| `pgrep` | 按名称查进程号 | `notools pgrep myapp` |
| `pkill` | 按名称发信号 | `notools pkill myapp` |
| `pidof` | 查找运行中程序的 PID | `notools pidof myapp` |
| `nice` | 以调整后的优先级运行命令 | `notools nice -n 5 cmd` |
| `renice` | 调整运行中进程优先级 | `notools renice 5 -p 1234` |
| `nohup` | 忽略 SIGHUP 运行命令 | `notools nohup cmd &` |
| `timeout` | 限时运行命令 | `notools timeout 5 cmd` |
| `time` | 统计命令耗时 | `notools time cmd` |
| `setsid` | 在新会话中运行命令 | `notools setsid cmd` |
| `flock` | 文件锁 | `notools flock /tmp/lock cmd` |

### 网络

| 命令 | 说明 | 示例 |
|------|------|------|
| `curl` | 纯 Nolang HTTP/1.1 客户端（`net` TCP 实现，支持 `http://` 和 `https://`） | `notools curl https://127.0.0.1:8443/file` |
| `ping` | 纯 Nolang ICMP 回显请求（内置 `net.ping`，默认 `-c 4`，支持 IP 和域名） | `notools ping -c 4 example.com` |

### 哈希与编码

| 命令 | 说明 | 示例 |
|------|------|------|
| `md5` | MD5 摘要（128 位，纯 Nolang 实现） | `notools md5 file.txt`、`echo -n abc \| notools md5` |
| `md5sum` | MD5 摘要（GNU 风格） | `notools md5sum file.txt` |
| `sha1` | SHA-1 摘要（160 位） | `notools sha1 file.txt` |
| `sha1sum` | SHA-1 摘要（GNU 风格） | `notools sha1sum file.txt` |
| `sha224` | SHA-224 摘要（224 位） | `notools sha224 file.txt` |
| `sha224sum` | SHA-224 摘要（GNU 风格） | `notools sha224sum file.txt` |
| `sha256` | SHA-256 摘要（256 位） | `notools sha256 file.txt` |
| `sha256sum` | SHA-256 摘要（GNU 风格） | `notools sha256sum file.txt` |
| `sha384` | SHA-384 摘要（384 位，64 位字运算） | `notools sha384 file.txt` |
| `sha384sum` | SHA-384 摘要（GNU 风格） | `notools sha384sum file.txt` |
| `sha512` | SHA-512 摘要（512 位，64 位字运算） | `notools sha512 file.txt` |
| `sha512sum` | SHA-512 摘要（GNU 风格） | `notools sha512sum file.txt` |
| `cksum` | CRC 校验和 | `notools cksum file` |
| `sum` | BSD / SYSV 校验和 | `notools sum file` |
| `base32` | Base32 编码 / 解码（`-d`） | `notools base32 file` |
| `base64` | Base64 编码/解码（RFC 4648，`-d` 解码） | `notools base64 file.bin`、`echo -n YWJj \| notools base64 -d` |
| `hmac` | HMAC 密钥摘要（`-a md5\|sha1\|sha256\|sha512`，`-k` 指定密钥，默认 sha256） | `notools hmac -a sha256 -k key message` |
| `uuencode` | UU 编码 | `notools uuencode file` |
| `uudecode` | UU 解码 | `notools uudecode file.uu` |
| `uuidgen` | 生成 UUID | `notools uuidgen` |
| `uuidparse` | 解析 UUID | `notools uuidparse <uuid>` |
| `mcookie` | 生成随机 cookie | `notools mcookie` |
| `b2sum` | BLAKE2b 摘要（GNU coreutils，`-c` 校验模式） | `notools b2sum file.txt` |

### 数学与杂项

| 命令 | 说明 | 示例 |
|------|------|------|
| `expr` | 整数算术 / 字符串求值 | `notools expr 1 + 2` |
| `factor` | 质因数分解 | `notools factor 60` |
| `numfmt` | 数字格式化（K/M/G 等） | `notools numfmt --to=iec 1024` |
| `seq` | 输出数字序列 | `notools seq 1 2 10` |
| `true` | 退出码恒为 0 | `notools true` |
| `false` | 退出码恒为 1 | `notools false` |
| `yes` | 重复输出字符串 | `notools yes y` |
| `getopt` | 解析命令行选项 | `notools getopt -o ab: -- -a -b x` |
| `xargs` | 从 stdin 构建并执行命令 | `find . -name '*.txt' \| notools xargs rm` |

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

## 待实现（对照 Git for Windows / MSYS2 自带 Linux 工具）

下列命令在 Git for Windows 内置的 MSYS2 环境中常见，但 notools 尚未实现，便于后续按优先级补全。

### 压缩 / 解压

| 命令 | 说明 | 状态 |
|------|------|------|
| `bzip2` / `bunzip2` / `bzcat` | bzip2 压缩 / 解压 / 解压到 stdout | 需 `archive/bzip2` 模块（BWT + Huffman） |
| `xz` / `unxz` / `xzcat` | XZ 压缩 / 解压 / 解压到 stdout | 需 `archive/xz` 模块（LZMA2） |
| `lzma` / `unlzma` / `lzcat` | LZMA 压缩 / 解压 / 解压到 stdout | 需 `archive/xz` 模块（LZMA2） |
| `zstd` / `unzstd` / `zstdcat` | Zstandard 压缩 / 解压 / 解压到 stdout | 需 `archive/zstd` 模块（FSE + Huffman） |

### coreutils 其余

| 命令 | 说明 | 状态 |
|------|------|------|
| `chroot` | 切换根目录运行命令（需 root） | 需 `os.chroot()` 系统调用 |
| `stdbuf` | 调整命令的 stdio 缓冲模式 | 需 `setvbuf` 式 stdio 缓冲控制 |

### 平台相关 / 不适用

| 命令 | 说明 | 状态 |
|------|------|------|
| `chcon` | 修改 SELinux 安全上下文 | 不适用（macOS / Windows 无 SELinux） |
| `runcon` | 以指定 SELinux 上下文运行命令 | 不适用（同上） |

## 已知限制

- 全部已实现命令均已在 macOS (arm64) 上构建并验证可用。
- `who` / `users` / `pinky` 为简化实现，仅显示当前用户会话（通过 `os.get-login()` + `os.ttyname(0)`），不遍历 utmpx 列出全部登录会话。
- `compress` / `uncompress` 为纯 Nolang LZW 实现，与系统 `compress` 命令的 `.Z` 格式兼容。
- `less` 使用行输入（`fs.get-line()`），不支持字符级即时响应（需终端 raw 模式）。
- `bzip2` / `xz` / `lzma` / `zstd` 系列命令当前通过 `process.process-system()` 委托系统命令执行，纯 Nolang 实现需以下标准库模块：

### 需要标准库支持的命令

| 命令 | 需要的标准库模块 | 算法/功能说明 |
|------|-----------------|--------------|
| `chroot` | `os.chroot()` | 切换根目录的系统调用 |
| `stdbuf` | `setvbuf` 式 stdio 控制 | 设置子进程 stdio 缓冲模式 |
| `bzip2` / `bunzip2` / `bzcat` | `archive/bzip2` | Burrows-Wheeler Transform + Huffman |
| `xz` / `unxz` / `xzcat` | `archive/xz` | LZMA2 压缩算法 |
| `lzma` / `unlzma` / `lzcat` | `archive/xz` | LZMA2（传统 `.lzma` 格式） |
| `zstd` / `unzstd` / `zstdcat` | `archive/zstd` | FSE + Huffman（Zstandard） |

## 项目结构

```
notools/
├── main.no              # 入口，子命令分发
├── src/
│   ├── echo.no          # 各工具实现
│   ├── cat.no
│   ├── ls.no
│   ├── sha256x.no       # SHA-256 纯 Nolang 实现（返回 hex str）
│   ├── sha224x.no       # SHA-224（同算法不同 IV，56 字符输出）
│   ├── sha1x.no         # SHA-1
│   ├── sha512x.no       # SHA-512（64 位字运算）
│   ├── sha384x.no       # SHA-384（同算法不同 IV，96 字符输出）
│   ├── md5x.no          # MD5
│   ├── hashutil.no      # 哈希命令共享逻辑（do-hash / hash-cmd）
│   ├── sha224sum.no     # GNU 风格 SHA-224 校验和（直接调用 sha224x）
│   ├── sha384sum.no     # GNU 风格 SHA-384 校验和（直接调用 sha384x）
│   ├── who.no           # 登录会话（简化版）
│   ├── users.no         # 当前登录用户名
│   ├── pinky.no         # 轻量级 who
│   └── ...
└── package.jsonc        # 项目配置
```

## 开发

### 构建

```bash
no build ./notools/main.no
# 产物位于 dist/main
```

### 测试

```bash
# 哈希算法验证（对照系统 shasum）
echo -n abc | ./dist/main md5       # 900150983cd24fb0d6963f7d28e17f72
echo -n abc | ./dist/main sha224    # 23097d223405d8228642a477bda255b32aadbce4bda0b3f7e36c9da7
echo -n abc | ./dist/main sha256    # ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
echo -n abc | ./dist/main sha384    # cb00753f45a35e8bb5a03d699ac65007272c32ab0eded1631a8b605a43ff5bed...
echo -n abc | ./dist/main sha512    # ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a...
echo -n abc | ./dist/main sha1      # a9993e364706816aba3e25717850c26c9cd0d89d

# HMAC
echo -n abc | ./dist/main hmac -a sha256 -k key
# 9c196e32dc0175f86f4b1cb89289d6619de6bee699e4c378e68309ed97a1a6ab

# GNU 风格校验和（含 -c 校验模式）
echo -n abc > /tmp/test.txt
./dist/main sha224sum /tmp/test.txt     # 23097d22...  /tmp/test.txt
./dist/main sha384sum /tmp/test.txt     # cb00753f...  /tmp/test.txt
./dist/main sha224sum /tmp/test.txt > /tmp/check.txt
./dist/main sha224sum -c /tmp/check.txt  # /tmp/test.txt: OK

# 大输入（多块处理）
python3 -c "print('a'*1000, end='')" > /tmp/large.txt
./dist/main sha256 /tmp/large.txt
./dist/main sha384 /tmp/large.txt

# 用户信息
./dist/main users     # 当前登录用户名
./dist/main who       # 当前用户 + 终端
./dist/main pinky     # 轻量级用户信息
```

## 许可证

MIT
