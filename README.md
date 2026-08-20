# notools

Unix 常用命令行工具集，使用 [Nolang](https://github.com/lizongying/nolang) 语言实现。

## 特性

- 纯 Nolang 实现，不依赖外部系统命令
- 单一可执行文件，子命令分发（193 个命令）
- 支持 stdin 管道与文件输入
- 友好的错误处理
- 内含纯 Nolang Git 实现（`nogit/` 子项目），不依赖系统 `git` 二进制
- 内含纯 Nolang 图像处理工具库（`noimg/` 子项目），支持 9 种格式读写与 55+ 种图像操作

## 安装

### 方式一：从 Releases 下载预编译二进制（推荐）

直接从 [GitHub Releases](https://github.com/lizongying/notools/releases) 下载对应平台的已编译好二进制文件，无需安装编译器。

三个独立工具各自构建，可按需下载：

| 工具 | 说明 |
|------|------|
| `notools` | Unix 常用命令行工具集（193 个命令） |
| `nogit` | 纯 Nolang Git 实现（不依赖系统 `git`） |
| `noimg` | 纯 Nolang 图像处理工具库（9 种格式、55+ 种操作） |

支持的平台：

| 平台 | notools | nogit | noimg |
|------|---------|-------|-------|
| Linux amd64 | `notools-linux-amd64` | `nogit-linux-amd64` | `noimg-linux-amd64` |
| Linux arm64 | `notools-linux-arm64` | `nogit-linux-arm64` | `noimg-linux-arm64` |
| macOS amd64 | `notools-darwin-amd64` | `nogit-darwin-amd64` | `noimg-darwin-amd64` |
| macOS arm64 | `notools-darwin-arm64` | `nogit-darwin-arm64` | `noimg-darwin-arm64` |
| Windows amd64 | `notools-windows-amd64.exe` | `nogit-windows-amd64.exe` | `noimg-windows-amd64.exe` |
| Windows arm64 | `notools-windows-arm64.exe` | `nogit-windows-arm64.exe` | `noimg-windows-arm64.exe` |

```bash
# Linux amd64 示例 — 按需安装
# notools
curl -fsSL -o notools https://github.com/lizongying/notools/releases/latest/download/notools-linux-amd64
chmod +x notools && sudo mv notools /usr/local/bin/

# nogit
curl -fsSL -o nogit https://github.com/lizongying/notools/releases/latest/download/nogit-linux-amd64
chmod +x nogit && sudo mv nogit /usr/local/bin/

# noimg
curl -fsSL -o noimg https://github.com/lizongying/notools/releases/latest/download/noimg-linux-amd64
chmod +x noimg && sudo mv noimg /usr/local/bin/
```

下载后可使用同目录下的 `checksums-sha256.txt` 进行校验。

### 方式二：从源码构建

三个子项目各自独立构建：

```bash
# 克隆项目
git clone git@github.com:lizongying/notools.git notools
cd notools

# 构建 notools（需先安装 Nolang）
cd notools && no build && cd ..
cp notools/dist/notools /usr/local/bin/notools

# 构建 nogit
cd nogit && no build && cd ..
cp nogit/dist/nogit /usr/local/bin/nogit

# 构建 noimg
cd noimg && no build && cd ..
cp noimg/dist/noimg /usr/local/bin/noimg
```

## 工具列表

> 以下为已实现并接入分发的全部命令（193 个）。`md5`/`sha*` 为 BSD 风格命名，`md5sum`/`sha*sum` 为 GNU 风格命名，两者输出相同。

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
| `bzip2` | bzip2 压缩（纯 Nolang，BWT + Huffman） | `notools bzip2 file` |
| `bunzip2` | bzip2 解压 | `notools bunzip2 file.bz2` |
| `bzcat` | 解压 .bz2 到 stdout | `notools bzcat file.bz2` |
| `xz` | XZ 压缩（纯 Nolang，LZMA2） | `notools xz file` |
| `unxz` | XZ 解压 | `notools unxz file.xz` |
| `xzcat` | 解压 .xz 到 stdout | `notools xzcat file.xz` |
| `lzma` | LZMA 压缩（传统 `.lzma` 格式） | `notools lzma file` |
| `unlzma` | LZMA 解压 | `notools unlzma file.lzma` |
| `lzcat` | 解压 .lzma 到 stdout | `notools lzcat file.lzma` |
| `zstd` | Zstandard 压缩（纯 Nolang，FSE + Huffman） | `notools zstd file` |
| `unzstd` | Zstandard 解压 | `notools unzstd file.zst` |
| `zstdcat` | 解压 .zst 到 stdout | `notools zstdcat file.zst` |
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
| `chroot` | 切换根目录运行命令（需 root，原生 `os.chroot()`） | `notools chroot /newroot /bin/sh` |
| `stdbuf` | 调整命令的 stdio 缓冲模式（纯 Nolang 管道代理） | `notools stdbuf -oL cat file` |
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

## nogit（纯 Nolang Git 实现）

notools 仓库内含一个**纯 Nolang 实现的 Git**（`nogit/` 目录），不依赖系统 `git` 二进制，从底层数据结构到 CLI 命令全部使用 Nolang 编写。

### 支持的命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `init [path]` | 初始化新仓库（幂等，可重复执行） | `nogit init myrepo` |
| `add <path>` | 将文件或目录写入 blob 并加入暂存区（支持递归添加目录） | `nogit add file.txt`、`nogit add .` |
| `commit -m <msg>` | 从暂存区创建 tree 和 commit 对象 | `nogit commit -m 'initial'` |
| `log [count]` | 遍历提交历史 | `nogit log -n 10` |
| `status` | 显示当前分支、已暂存与未暂存的变更 | `nogit status` |
| `branch [name] [-d <name>]` | 列出、创建或删除分支 | `nogit branch dev`、`nogit branch -d dev` |
| `checkout <name>` | 切换分支并还原工作树 | `nogit checkout dev` |
| `tag <name> [-a <name> -m <msg>] [-d <name>]` | 创建轻量/标注标签或删除标签 | `nogit tag v1.0`、`nogit tag -a v1.0 -m 'msg'` |
| `show <ref>` | 显示对象类型与内容 | `nogit show HEAD` |
| `cat-file <opt> <ref>` | 按类型/引用查看对象（`-t`/`-s`/`-p`） | `nogit cat-file -p HEAD` |
| `hash-object [-w] <file>` | 计算文件 SHA-1（`-w` 写入对象库） | `nogit hash-object -w file` |
| `ls-tree <ref>` | 列出 tree 内容 | `nogit ls-tree HEAD` |
| `ls-files` | 列出暂存区文件 | `nogit ls-files` |
| `rev-parse <ref>` | 将引用解析为 OID | `nogit rev-parse HEAD` |
| `write-tree` | 从暂存区写入 tree 对象 | `nogit write-tree` |
| `rm <path> [--cached]` | 从暂存区和工作树中删除文件 | `nogit rm file.txt` |
| `reset [ref]` | 重置 HEAD 和索引到指定引用 | `nogit reset HEAD` |
| `update-ref <ref> <oid>` | 更新引用 | `nogit update-ref refs/heads/x <oid>` |
| `config <key> [val]` | 读取或设置配置项 | `nogit config user.name 'Alice'` |
| `reflog` | 显示 HEAD reflog | `nogit reflog` |

### 底层模块

| 模块 | 职责 |
|------|------|
| `util` | 通用工具函数（hex 编解码、字节查找、整数转字符串等） |
| `oid` | SHA-1 对象标识符、对象头构造、hash-object |
| `object` | Blob / Tree / Commit / Tag 对象的写入与读取（loose 格式） |
| `refs` | 引用管理：分支、标签、HEAD、symbolic-ref、reflog |
| `config` | Git config 文件解析与读写 |
| `index` | 暂存区（Git index v2）读写 |
| `repository` | 仓库初始化、`.git` 目录发现、路径辅助函数 |
| `revwalk` | 提交遍历、引用解析、祖先检测 |
| `zlib` | zlib 压缩 / 解压（deflate / inflate、Adler-32） |
| `pack` | Packfile v2 读取（变量长头、ofs-delta、ref-delta） |

### 技术特性

- **纯 Nolang 实现**：不调用系统 `git`，从 SHA-1 哈希到 zlib 压缩均为原生代码
- **Loose 对象存储**：blob / tree / commit / tag 以 zlib 压缩的 loose 对象形式存储在 `.git/objects/`
- **Packfile v2 读取**：支持读取 Git packfile 格式，包括 ofs-delta 和 ref-delta 增量对象
- **Git index v2**：完整支持暂存区（staging area）读写
- **Reflog**：记录 HEAD 和分支引用的变更历史
- **仓库发现**：从当前目录向上搜索 `.git` 目录
- **配置管理**：支持 `user.name` / `user.email` 等 config 读写

### 构建与运行

```bash
cd nogit
no build
; 产物位于 nogit/dist/git

; 示例工作流
cd my-project
no run /path/to/nogit/dist/git init
no run /path/to/nogit/dist/git config user.name 'Alice'
no run /path/to/nogit/dist/git config user.email 'alice@example.com'
no run /path/to/nogit/dist/git add file.txt
no run /path/to/nogit/dist/git commit -m 'initial commit'
no run /path/to/nogit/dist/git log
```

### 项目结构

```
nogit/
├── main.no              ; CLI 入口与命令分发
├── src/
│   ├── util.no          ; 通用工具
│   ├── oid.no           ; SHA-1 对象标识
│   ├── object.no        ; 对象读写（blob/tree/commit/tag）
│   ├── refs.no          ; 引用与 reflog
│   ├── config.no        ; 配置文件
│   ├── index.no         ; 暂存区（index v2）
│   ├── repository.no    ; 仓库初始化（幂等）与发现
│   ├── revwalk.no       ; 提交遍历与引用解析
│   ├── zlib.no          ; zlib 压缩/解压（archive/gzip）
│   └── pack.no          ; Packfile v2 读取（delta 解析）
├── tests/
│   ├── test.no               ; 统一测试运行器
│   ├── test-e2e-init.no       ; 初始化集成测试
│   ├── test-e2e-commit.no     ; 提交流水线集成测试
│   ├── test-e2e-comprehensive.no ; 全流程集成测试
│   └── ...                   ; 其余单元测试
└── package.jsonc        ; 项目配置
```

## noimg（纯 Nolang 图像处理工具库）

notools 仓库内含一个**纯 Nolang 实现的图像处理工具库**（`noimg/` 目录），类似 libvips 的设计思路，支持多格式读写与丰富的图像操作。

### 支持的格式

| 格式 | 扩展名 | 读取 | 写入 | 说明 |
|------|--------|------|------|------|
| PPM/PGM/PNM | `.ppm` `.pgm` `.pnm` | ✅ | ✅ | Portable Pixmap/Graymap（ASCII 与 Binary） |
| BMP | `.bmp` | ✅ | ✅ | Windows Bitmap（仅 24/32 位未压缩） |
| TGA | `.tga` | ✅ | ✅ | Targa（含 RLE 压缩） |
| PAM | `.pam` | ✅ | ✅ | Portable Arbitrary Map |
| PNG | `.png` | ✅ | ✅ | Portable Network Graphics（8 位，zlib 压缩，CRC32 校验，5 种扫描线滤镜，支持 Adam7 隔行解码） |
| TIFF | `.tif` `.tiff` | ✅ | ✅ | Tagged Image File Format（仅未压缩、8 位、单 strip） |
| GIF | `.gif` | ✅ | ✅ | Graphics Interchange Format（LZW 解码+隔行+透明；动画多帧提取+disposal 合成；写入用 median-cut 量化） |
| JPEG | `.jpg` `.jpeg` | ✅ | ✅ | baseline JPEG 读写（DCT+Huffman 编码/解码+IDCT+YCbCr→RGB），不支持 progressive |
| WebP | `.webp` | ⚠️ | ⚠️ | VP8L lossless 解码（Huffman+LZ77 距离+颜色缓存+predictor 逆变换(14 模式)+颜色变换逆变换(定点乘)+subtract-green+颜色索引）；不支持 lossy VP8；写入为 VP8L 容器（真实像素编码），但 **save 不写 transform 头（无 predictor/subtract-green/color-transform），与标准 WebP 解码器不互通**——仅 noimg save→noimg load 可 round-trip |

### CLI 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `info` | 显示图像属性 | `noimg info photo.png` |
| `convert` | 格式转换 | `noimg convert input.png output.jpg` |
| `resize` | 调整大小（可选插值方法） | `noimg resize in.png out.png 800 600 1` |
| `thumbnail` | 缩略图（最大边长） | `noimg thumbnail in.png out.png 128` |
| `rotate` | 旋转（90/180/270） | `noimg rotate in.png out.png 90` |
| `rot-free` | 任意角度旋转 | `noimg rot-free in.png out.png 45.0` |
| `flip` | 翻转（h/v/both） | `noimg flip in.png out.png h` |
| `crop` | 裁剪区域 | `noimg crop in.png out.png 10 10 100 100` |
| `grayscale` | 灰度转换 | `noimg grayscale in.png out.png` |
| `sepia` | 棕褐色调复古效果 | `noimg sepia in.png out.png` |
| `invert` | 反色 | `noimg invert in.png out.png` |
| `blur` | 高斯模糊 | `noimg blur in.png out.png 15` |
| `sharpen` | 锐化 | `noimg sharpen in.png out.png 150` |
| `edge` | 边缘检测（Sobel） | `noimg edge in.png out.png` |
| `emboss` | 浮雕效果 | `noimg emboss in.png out.png` |
| `oil` | 油画效果 | `noimg oil in.png out.png 3 32` |
| `median` | 中值滤波 | `noimg median in.png out.png 3` |
| `dilate` | 形态学膨胀 | `noimg dilate in.png out.png 2` |
| `erode` | 形态学腐蚀 | `noimg erode in.png out.png 2` |
| `gradient` | 形态学梯度 | `noimg gradient in.png out.png 2` |
| `vignette` | 暗角效果 | `noimg vignette in.png out.png 40` |
| `brightness` | 亮度调整 | `noimg brightness in.png out.png 20` |
| `contrast` | 对比度调整 | `noimg contrast in.png out.png 50` |
| `gamma` | Gamma 校正 | `noimg gamma in.png out.png 120` |
| `threshold` | 二值化 | `noimg threshold in.png out.png 128` |
| `posterize` | 色阶缩减 | `noimg posterize in.png out.png 4` |
| `solarize` | 日晒效果 | `noimg solarize in.png out.png 128` |
| `hist-eq` | 直方图均衡化 | `noimg hist-eq in.png out.png` |
| `hist-norm` | 直方图归一化 | `noimg hist-norm in.png out.png` |
| `hist-stretch` | 直方图拉伸 | `noimg hist-stretch in.png out.png 1` |
| `auto-level` | 自动色阶 | `noimg auto-level in.png out.png` |
| `auto-contrast` | 自动对比度 | `noimg auto-contrast in.png out.png 1` |
| `histogram` | 打印直方图 | `noimg histogram in.png` |
| `stats` | 图像统计信息 | `noimg stats in.png` |
| `entropy` | 图像香农熵 | `noimg entropy in.png` |
| `composite` | 图像合成 | `noimg composite base.png overlay.png out.png 10 10` |
| `pad` | 添加边框 | `noimg pad in.png out.png 10` |
| `band` | 提取单通道 | `noimg band in.png out.png 0` |
| `add-alpha` | 添加 Alpha 通道 | `noimg add-alpha in.png out.png` |
| `flatten` | Alpha 混平（RGBA→RGB） | `noimg flatten in.png out.png` |
| `noise` | 添加噪声 | `noimg noise in.png out.png 30` |
| `unsharp-mask` | USM 锐化（带阈值） | `noimg unsharp-mask in.png out.png 15 150 0` |
| `box-blur` | 方框模糊 | `noimg box-blur in.png out.png 3` |
| `laplacian` | Laplacian 边缘检测 | `noimg laplacian in.png out.png` |
| `otsu` | Otsu 自动阈值二值化 | `noimg otsu in.png out.png` |
| `adjust-hsv` | HSV 色彩调整 | `noimg adjust-hsv in.png out.png 10 0 0` |
| `transpose` | 矩阵转置 | `noimg transpose in.png out.png` |
| `scale` | 独立 x/y 缩放 | `noimg scale in.png out.png 50 100` |
| `embed` | 嵌入大画布 | `noimg embed in.png out.png 10 10 200 200` |
| `bandjoin2` | 两图通道拼接 | `noimg bandjoin2 r.png g.png out.png` |
| `roi-blend` | 区域混合 | `noimg roi-blend base.png overlay.png out.png 10 10 0 255` |
| `overlay-blend` | Overlay 混合 | `noimg overlay-blend in.png overlay.png out.png` |
| `remove-alpha` | 移除 Alpha 通道 | `noimg remove-alpha in.png out.png` |
| `rgb2lab` | RGB 转 Lab | `noimg rgb2lab in.png out.png` |
| `lab2rgb` | Lab 转 RGB | `noimg lab2rgb in.png out.png` |
| `rgb2cmyk` | RGB 转 CMYK | `noimg rgb2cmyk in.png out.png` |
| `cmyk2rgb` | CMYK 转 RGB | `noimg cmyk2rgb in.png out.png` |
| `watermark` | 文字水印 | `noimg watermark in.png out.png \"©2024\" 4 2` |
| `to-u16` | 8-bit 转 16-bit | `noimg to-u16 in.png out.png` |
| `to-u8` | 16-bit 转 8-bit | `noimg to-u8 in.png out.png` |
| `animate` | 创建动画 GIF | `noimg animate out.gif 20 f1.png f2.png f3.png` |

### 库 API

noimg 可作为 Nolang 库使用，通过 `lib.no` 导出以下模块：

| 模块 | 职责 |
|------|------|
| `image` | 图像创建、复制、填充、像素读写、统计、常量运算、Alpha 通道管理、属性检查 |
| `pnm` | PPM/PGM/PNM 读写 |
| `bmp` | BMP 读写（24/32 位未压缩） |
| `tga` | TGA 读写（含 RLE） |
| `pam` | PAM 读写 |
| `gif` | GIF 读写（LZW 解码+隔行+透明+动画多帧+disposal+median-cut 量化+动画写出） |
| `png` | PNG 读写（zlib 压缩、CRC32 校验、5 种滤镜、Adam7 隔行解码，仅 8 位） |
| `tiff` | TIFF 读写（仅未压缩、8 位、单 strip） |
| `jpeg` | JPEG 读写（baseline DCT+Huffman 编码/解码+IDCT+YCbCr→RGB，不支持 progressive） |
| `webp` | WebP VP8L lossless 解码（Huffman+LZ77+颜色缓存+predictor(14 模式)+颜色变换(定点乘)+subtract-green+颜色索引）；写入为 VP8L 容器（真实像素，但不写 transform 头，与标准解码器不互通） |
| `colour` | 色彩空间转换（RGB↔Gray、RGB↔HSV、RGB↔HSL、RGB↔YCbCr、RGB↔Lab、RGB↔CMYK）、亮度/对比度/Gamma/阈值/色调分离/日晒/棕褐/HSV 调整/Overlay 混合/Otsu 自动阈值 |
| `resize` | 双线性缩放、缩略图、缩放、最近邻/双三次/面积平均 |
| `rotate` | 旋转（90/180/270/任意角度）、翻转、转置/反对角转置 |
| `composite` | 裁剪、自动裁剪、合成、边框、嵌入、通道合并/提取/选择、Alpha 混平、ROI 混合、多模式混合（Normal/Multiply/Screen/Overlay/Add/Subtract/Diff/Lighten/Darken/Copy）、平铺 |
| `filter` | 卷积、高斯模糊（含可分离优化）、方框模糊、锐化（含 USM）、Sobel/Laplacian 边缘检测、浮雕、中值滤波、油画、噪声、形态学（膨胀/腐蚀/梯度）、暗角 |
| `histogram` | 直方图查找/累积/打印、均衡化/归一化/拉伸、自动色阶/对比度、LUT 应用、均值/方差/标准差/熵/百分位/CDF |
| `text` | 位图字体渲染、文字水印（5x7 点阵字体，9 种位置） |
| `image` | 8-bit/16-bit 支持（U8/U16 格式、depth 字段、转换、像素访问、统计；16-bit 暂不进 resize/filter/colour/IO 管线） |

### 构建与运行

```bash
cd noimg
no build
# 产物位于 noimg/dist/noimg

# 示例：格式转换
noimg/dist/noimg convert input.png output.jpg

# 示例：图像处理
noimg/dist/noimg blur input.png blurred.png 15
noimg/dist/noimg grayscale input.png gray.png
noimg/dist/noimg resize input.png small.png 200 200
```

### 项目结构

```
noimg/
├── main.no              ; CLI 入口与命令分发
├── lib.no               ; 库导出声明
├── src/
│   ├── image.no         ; 图像核心结构与操作
│   ├── pnm.no           ; PPM/PGM/PNM
│   ├── bmp.no           ; BMP
│   ├── tga.no           ; TGA
│   ├── pam.no           ; PAM
│   ├── png.no           ; PNG（CRC32 位运算、zlib）
│   ├── tiff.no          ; TIFF
│   ├── gif.no           ; GIF（LZW 编解码）
│   ├── jpeg.no          ; JPEG 读写（baseline DCT+Huffman 编码/解码+IDCT+YCbCr→RGB）
│   ├── webp.no          ; WebP VP8L lossless 解码（Huffman+LZ77+predictor(14 模式)+颜色变换(定点乘)+subtract-green+颜色索引）；save 不写 transform 头，仅内部 round-trip
│   ├── colour.no        ; 色彩空间转换（RGB↔Gray/HSV/HSL/YCbCr/Lab/CMYK）
│   ├── resize.no        ; 缩放
│   ├── rotate.no        ; 旋转与翻转
│   ├── composite.no     ; 合成与裁剪
│   ├── filter.no        ; 滤镜（模糊/锐化/边缘/浮雕/油画/中值/噪声/形态学/暗角）
│   ├── histogram.no     ; 直方图与统计
│   └── text.no          ; 文字渲染与水印（5x7 点阵字体）
├── tests/
│   ├── test-core.no       ; 核心图像操作测试
│   ├── test-pnm.no        ; PNM 格式往返测试
│   ├── test-colour.no     ; 色彩空间转换测试
│   ├── test-filter.no     ; 滤镜操作测试
│   ├── test-composite.no  ; 合成操作测试
│   ├── test-histogram.no  ; 直方图操作测试
│   └── test-resize-rotate.no ; 缩放与旋转测试
└── package.jsonc        ; 项目配置
```

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
- `bzip2` / `xz` / `lzma` / `zstd` 系列命令的**解压缩**使用纯 Nolang 标准库模块（`archive/bzip2`、`archive/xz`、`archive/zstd`）实现，不委托系统命令；**压缩**侧为简化实现（写入合法头 + 原始存储块），尚未实现完整 BWT / LZMA2 / FSE 压缩算法。
- `chroot` 使用原生 `os.chroot()` 系统调用，需要 root 权限。
- `stdbuf` 使用纯 Nolang 管道代理模式实现（`process-fork` + `process-pipe` + `process-dup2` + `process-exec-shell`），支持 `-o0`/`-oL`/`-oB`/`-e0`/`-eL`/`-eB` 缓冲模式。

## 项目结构

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
└── package.jsonc        # 项目配置
```

## 开发

### 构建

三个子项目各自独立构建：

```bash
# 构建 notools
cd notools
no build
cd ..
# 产物位于 notools/dist/notools

# 构建 nogit
cd nogit
no build
cd ..
# 产物位于 nogit/dist/nogit

# 构建 noimg
cd noimg
no build
cd ..
# 产物位于 noimg/dist/noimg
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
