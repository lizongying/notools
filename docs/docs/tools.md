---
sidebar_position: 3
---

# 工具列表

> 以下為已實現並接入分發的全部命令（193 個）。`md5`/`sha*` 為 BSD 風格命名，`md5sum`/`sha*sum` 為 GNU 風格命名，兩者輸出相同。

## 文件與目錄

| 命令 | 說明 | 示例 |
|------|------|------|
| `ls` | 列出目錄內容 | `notools ls -l /tmp` |
| `dir` | 類似 `ls`，預設不彩色、按列輸出 | `notools dir` |
| `vdir` | 等同 `ls -l` | `notools vdir` |
| `tree` | 顯示目錄樹 | `notools tree -L 2` |
| `cat` | 輸出文件內容 | `notools cat file.txt` |
| `cp` | 複製文件 / 目錄（支持多源、`-r` 遞迴） | `notools cp a.txt b.txt dir/` |
| `mv` | 移動或重命名 | `notools mv a.txt b.txt` |
| `rm` | 刪除文件或目錄 | `notools rm -r dir/` |
| `ln` | 創建硬鏈接 / 符號鏈接（-s） | `notools ln -s src.txt link.txt` |
| `link` | 創建硬鏈接 | `notools link a b` |
| `unlink` | 刪除單個文件 | `notools unlink a.txt` |
| `touch` | 創建空文件或更新時間戳 | `notools touch new.txt` |
| `mkdir` | 創建目錄 | `notools mkdir -p a/b/c` |
| `rmdir` | 刪除空目錄 | `notools rmdir empty/` |
| `mkfifo` | 創建命名管道 | `notools mkfifo /tmp/pipe` |
| `mknod` | 創建特殊文件 | `notools mknod /tmp/f p` |
| `mktemp` | 安全創建臨時文件 / 目錄 | `notools mktemp -d` |
| `tempfile` | 創建臨時文件 | `notools tempfile` |
| `install` | 複製文件並設置屬性 | `notools install -m 755 a b` |
| `chmod` | 修改文件權限 | `notools chmod 755 script.sh` |
| `chown` | 修改文件屬主 | `notools chown user:group file` |
| `chgrp` | 修改文件屬組 | `notools chgrp staff file` |
| `find` | 遞迴查找文件 | `notools find . -name "*.no"` |
| `du` | 估算文件 / 目錄磁碟佔用 | `notools du dir/` |
| `df` | 顯示文件系統磁碟空間 | `notools df` |
| `stat` | 顯示文件狀態信息 | `notools stat file.txt` |
| `file` | 判斷文件類型 | `notools file data.bin` |
| `rename` | 批量重命名文件 | `notools rename 's/\.old/.new/' *.old` |
| `dd` | 按塊複製 / 轉換文件 | `notools dd if=in of=out bs=512` |
| `basename` | 取路徑末尾文件名 | `notools basename /a/b/c.txt` |
| `dirname` | 取路徑目錄部分 | `notools dirname /a/b/c.txt` |
| `pwd` | 列印當前工作目錄 | `notools pwd` |
| `readlink` | 讀取符號鏈接目標 | `notools readlink link` |
| `realpath` | 輸出規範絕對路徑 | `notools realpath ../a/b` |
| `namei` | 逐段解析路徑 | `notools namei /a/b/c` |
| `pathchk` | 檢查路徑可移植性 | `notools pathchk path` |
| `dircolors` | 輸出 ls 配色設置 | `notools dircolors` |
| `shred` | 安全擦除文件內容 | `notools shred secret.txt` |
| `truncate` | 縮減 / 擴展文件到指定大小 | `notools truncate -s 0 log` |
| `sync` | 刷新文件系統緩衝 | `notools sync` |

## 文本查看與處理

| 命令 | 說明 | 示例 |
|------|------|------|
| `echo` | 輸出參數 | `notools echo -n hello` |
| `printf` | 格式化輸出 | `notools printf '%d\n' 42` |
| `head` | 輸出文件開頭 N 行（-n N） | `notools head -n 10 file.txt` |
| `tail` | 輸出文件末尾 N 行（-n N） | `notools tail -n 5 file.txt` |
| `more` | 分頁查看文件 | `notools more file.txt` |
| `less` | 增強版分頁器（前後翻頁、搜索） | `notools less file.txt` |
| `tac` | 逆序輸出行 | `notools tac file.txt` |
| `nl` | 添加行號 | `notools nl file.txt` |
| `pr` | 分頁排版列印 | `notools pr file.txt` |
| `fold` | 折斷過長行 | `notools fold -w 80 file` |
| `fmt` | 段落重排 | `notools fmt -w 72 file` |
| `expand` | 製表符轉空格 | `notools expand file` |
| `unexpand` | 空格轉製表符 | `notools unexpand -a file` |
| `column` | 列對齊排版 | `notools column -t data` |
| `cut` | 按字段（-d/-f）或字符（-c）截取 | `echo "a,b" \| notools cut -d, -f 1` |
| `paste` | 合併文件列 | `notools paste a b` |
| `join` | 按公共字段連接 | `notools join a b` |
| `comm` | 比較兩個有序文件 | `notools comm a b` |
| `csplit` | 按模式切分文件 | `notools csplit file /pattern/` |
| `split` | 按大小 / 行數切分文件 | `notools split -l 100 file` |
| `tr` | 字符轉換 / 刪除 | `echo "abc" \| notools tr a X` |
| `rev` | 反轉每行字符 | `echo "abc" \| notools rev` |
| `grep` | 搜索文本模式 | `notools grep -n pattern file.txt` |
| `egrep` | 等同 `grep -E`（擴展正則） | `notools egrep 'a\|b' file` |
| `fgrep` | 等同 `grep -F`（固定串） | `notools fgrep literal file` |
| `sed` | 流編輯器（替換） | `notools sed 's/old/new/g' file.txt` |
| `awk` | 字段提取 | `notools awk '{print $1}' file.txt` |
| `sort` | 排序行 | `notools sort -r file.txt` |
| `uniq` | 去除連續重複行 | `notools uniq -c file.txt` |
| `shuf` | 隨機打亂行 | `notools shuf file.txt` |
| `tsort` | 拓撲排序 | `notools tsort deps` |
| `wc` | 統計行/詞/字節 | `notools wc -l file.txt` |
| `tee` | 輸出到 stdout 並同時寫入文件 | `echo hi \| notools tee out.txt` |
| `strings` | 提取可列印字串 | `notools strings bin` |
| `od` | 八進制 / 多進制轉儲 | `notools od -Ax -tx1 file` |
| `hexdump` | 十六進制轉儲 | `notools hexdump -C file` |
| `xxd` | 十六進制轉儲 / 還原 | `notools xxd file` |
| `envsubst` | 替換環境變量 | `echo '$HOME' \| notools envsubst` |
| `dos2unix` | CRLF → LF | `notools dos2unix file` |
| `unix2dos` | LF → CRLF | `notools unix2dos file` |
| `mac2unix` | CR → LF | `notools mac2unix file` |
| `unix2mac` | LF → CR | `notools unix2mac file` |
| `cmp` | 逐字節比較兩文件 | `notools cmp a b` |
| `diff` | 逐行差異比較 | `notools diff a b` |
| `diff3` | 三路差異比較 | `notools diff3 a b c` |
| `sdiff` | 並排差異比較 | `notools sdiff a b` |
| `patch` | 應用 diff 補丁 | `notools patch < fix.diff` |
| `test` | 條件求值 | `notools test -f file` |
| `[` | `test` 的同義形式 | `notools [ -f file ]` |

## 歸檔與壓縮

| 命令 | 說明 | 示例 |
|------|------|------|
| `tar` | 創建/解壓/列出 tar 歸檔 | `notools tar -cf out.tar file` |
| `zip` | 創建 zip 歸檔 | `notools zip out.zip file1 file2` |
| `unzip` | 解壓/列出 zip 歸檔 | `notools unzip -l out.zip` |
| `gzip` | gzip 壓縮 | `notools gzip file` |
| `gunzip` | gzip 解壓 | `notools gunzip file.gz` |
| `zcat` | 解壓並輸出到 stdout | `notools zcat file.gz` |
| `bzip2` | bzip2 壓縮（純 Nolang，BWT + Huffman） | `notools bzip2 file` |
| `bunzip2` | bzip2 解壓 | `notools bunzip2 file.bz2` |
| `bzcat` | 解壓 .bz2 到 stdout | `notools bzcat file.bz2` |
| `xz` | XZ 壓縮（純 Nolang，LZMA2） | `notools xz file` |
| `unxz` | XZ 解壓 | `notools unxz file.xz` |
| `xzcat` | 解壓 .xz 到 stdout | `notools xzcat file.xz` |
| `lzma` | LZMA 壓縮（傳統 `.lzma` 格式） | `notools lzma file` |
| `unlzma` | LZMA 解壓 | `notools unlzma file.lzma` |
| `lzcat` | 解壓 .lzma 到 stdout | `notools lzcat file.lzma` |
| `zstd` | Zstandard 壓縮（純 Nolang，FSE + Huffman） | `notools zstd file` |
| `unzstd` | Zstandard 解壓 | `notools unzstd file.zst` |
| `zstdcat` | 解壓 .zst 到 stdout | `notools zstdcat file.zst` |
| `compress` | LZW `.Z` 壓縮（純 Nolang） | `notools compress file` |
| `uncompress` | LZW `.Z` 解壓（純 Nolang） | `notools uncompress file.Z` |

## 系統信息與管理

| 命令 | 說明 | 示例 |
|------|------|------|
| `ps` | 列出進程 | `notools ps -ef` |
| `top` | 顯示系統資源與進程 | `notools top -n 20` |
| `free` | 顯示內存使用 | `notools free` |
| `lscpu` | 顯示 CPU 架構信息 | `notools lscpu` |
| `uname` | 列印系統信息 | `notools uname -a` |
| `arch` | 列印機器架構 | `notools arch` |
| `uptime` | 系統運行時間與負載 | `notools uptime` |
| `hostname` | 列印 / 設置主機名 | `notools hostname` |
| `domainname` | 列印 NIS 域名 | `notools domainname` |
| `hostid` | 列印主機標識 | `notools hostid` |
| `dmesg` | 列印內核日誌 | `notools dmesg` |
| `date` | 顯示系統日期與時間 | `notools date` |
| `cal` | 顯示日曆 | `notools cal` |
| `nproc` | 列印可用 CPU 數 | `notools nproc` |
| `whoami` | 列印當前用戶名 | `notools whoami` |
| `id` | 列印用戶 / 組 ID | `notools id` |
| `groups` | 列印用戶所屬組 | `notools groups` |
| `logname` | 列印登錄用戶名 | `notools logname` |
| `who` | 列出登錄會話（簡化版） | `notools who` |
| `users` | 列出當前登錄用戶名 | `notools users` |
| `pinky` | 輕量級 who（用戶信息） | `notools pinky` |
| `tty` | 列印終端名 | `notools tty` |
| `getconf` | 查詢系統配置值 | `notools getconf PATH_MAX` |
| `locale` | 列印區域設置 | `notools locale` |
| `logger` | 寫入系統日誌 | `notools logger 'msg'` |
| `env` | 顯示 / 設置環境變量運行命令 | `notools env` |
| `printenv` | 列印環境變量 | `notools printenv PATH` |
| `watch` | 週期執行命令 | `notools watch -n 1 date` |
| `clear` | 清屏 | `notools clear` |
| `reset` | 重置終端 | `notools reset` |
| `sleep` | 暫停指定時長（支持 s/m/h） | `notools sleep 1` |
| `which` | 定位可執行文件路徑 | `notools which ls` |
| `whereis` | 定位二進制 / 源碼 / 手冊 | `notools whereis ls` |
| `locate` | 基於預建資料庫的快速文件查找 | `notools locate pattern` |
| `updatedb` | 更新 `locate` 資料庫 | `notools updatedb -U /` |
| `ptx` | 生成置換索引 | `notools ptx file.txt` |

## 進程與作業控制

| 命令 | 說明 | 示例 |
|------|------|------|
| `chroot` | 切換根目錄運行命令（需 root，原生 `os.chroot()`） | `notools chroot /newroot /bin/sh` |
| `stdbuf` | 調整命令的 stdio 緩衝模式（純 Nolang 管道代理） | `notools stdbuf -oL cat file` |
| `kill` | 發送信號給進程 | `notools kill -9 1234` |
| `killall` | 按名稱殺進程 | `notools killall myapp` |
| `pgrep` | 按名稱查進程號 | `notools pgrep myapp` |
| `pkill` | 按名稱發信號 | `notools pkill myapp` |
| `pidof` | 查找運行中程序的 PID | `notools pidof myapp` |
| `nice` | 以調整後的優先級運行命令 | `notools nice -n 5 cmd` |
| `renice` | 調整運行中進程優先級 | `notools renice 5 -p 1234` |
| `nohup` | 忽略 SIGHUP 運行命令 | `notools nohup cmd &` |
| `timeout` | 限時運行命令 | `notools timeout 5 cmd` |
| `time` | 統計命令耗時 | `notools time cmd` |
| `setsid` | 在新會話中運行命令 | `notools setsid cmd` |
| `flock` | 文件鎖 | `notools flock /tmp/lock cmd` |

## 網絡

| 命令 | 說明 | 示例 |
|------|------|------|
| `curl` | 純 Nolang HTTP/1.1 客戶端（`net` TCP 實現，支持 `http://` 和 `https://`） | `notools curl https://127.0.0.1:8443/file` |
| `ping` | 純 Nolang ICMP 回顯請求（內置 `net.ping`，默認 `-c 4`，支持 IP 和域名） | `notools ping -c 4 example.com` |

## 哈希與編碼

| 命令 | 說明 | 示例 |
|------|------|------|
| `md5` | MD5 摘要（128 位，純 Nolang 實現） | `notools md5 file.txt`、`echo -n abc \| notools md5` |
| `md5sum` | MD5 摘要（GNU 風格） | `notools md5sum file.txt` |
| `sha1` | SHA-1 摘要（160 位） | `notools sha1 file.txt` |
| `sha1sum` | SHA-1 摘要（GNU 風格） | `notools sha1sum file.txt` |
| `sha224` | SHA-224 摘要（224 位） | `notools sha224 file.txt` |
| `sha224sum` | SHA-224 摘要（GNU 風格） | `notools sha224sum file.txt` |
| `sha256` | SHA-256 摘要（256 位） | `notools sha256 file.txt` |
| `sha256sum` | SHA-256 摘要（GNU 風格） | `notools sha256sum file.txt` |
| `sha384` | SHA-384 摘要（384 位，64 位字運算） | `notools sha384 file.txt` |
| `sha384sum` | SHA-384 摘要（GNU 風格） | `notools sha384sum file.txt` |
| `sha512` | SHA-512 摘要（512 位，64 位字運算） | `notools sha512 file.txt` |
| `sha512sum` | SHA-512 摘要（GNU 風格） | `notools sha512sum file.txt` |
| `cksum` | CRC 校驗和 | `notools cksum file` |
| `sum` | BSD / SYSV 校驗和 | `notools sum file` |
| `base32` | Base32 編碼 / 解碼（`-d`） | `notools base32 file` |
| `base64` | Base64 編碼/解碼（RFC 4648，`-d` 解碼） | `notools base64 file.bin`、`echo -n YWJj \| notools base64 -d` |
| `hmac` | HMAC 密鑰摘要（`-a md5\|sha1\|sha256\|sha512`，`-k` 指定密鑰，預設 sha256） | `notools hmac -a sha256 -k key message` |
| `uuencode` | UU 編碼 | `notools uuencode file` |
| `uudecode` | UU 解碼 | `notools uudecode file.uu` |
| `uuidgen` | 生成 UUID | `notools uuidgen` |
| `uuidparse` | 解析 UUID | `notools uuidparse <uuid>` |
| `mcookie` | 生成隨機 cookie | `notools mcookie` |
| `b2sum` | BLAKE2b 摘要（GNU coreutils，`-c` 校驗模式） | `notools b2sum file.txt` |

## 數學與雜項

| 命令 | 說明 | 示例 |
|------|------|------|
| `expr` | 整數算術 / 字串求值 | `notools expr 1 + 2` |
| `factor` | 質因數分解 | `notools factor 60` |
| `numfmt` | 數字格式化（K/M/G 等） | `notools numfmt --to=iec 1024` |
| `seq` | 輸出數字序列 | `notools seq 1 2 10` |
| `true` | 退出碼恆為 0 | `notools true` |
| `false` | 退出碼恆為 1 | `notools false` |
| `yes` | 重複輸出字串 | `notools yes y` |
| `getopt` | 解析命令行選項 | `notools getopt -o ab: -- -a -b x` |
| `xargs` | 從 stdin 構建並執行命令 | `find . -name '*.txt' \| notools xargs rm` |
