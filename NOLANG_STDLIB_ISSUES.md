# Nolang 标准库问题 & 待实现清单

> 目的：记录在使用 Nolang 编写 `notools`（一套 Unix 命令行工具）过程中发现的
> **标准库已有问题（bug）** 与 **需要标准库补充实现的能力**，方便 Nolang 改进。
>
> 编译器：`/Users/lizongying/IdeaProjects/no/bin/no`
> （macOS arm64，版本 `5b4f734`，构建时间 2026-07-24 11:05 —— 用户 07-24 再次修复；新增 `tls.no` 纯 Nolang TLS 1.2/1.3 客户端；`net.no` 同日更新）
> 标准库：`NOLANG_STD_SRC=/Users/lizongying/IdeaProjects/no/src/std`
> 复现通用前置：
> ```bash
> export NOLANG_STD_SRC=/Users/lizongying/IdeaProjects/no/src/std
> BIN=/Users/lizongying/IdeaProjects/no/bin/no
> clean() { find . -maxdepth 1 -name 'nolang*' -exec rm -rf {} + 2>/dev/null; }
> ```

---

## 〇、本轮（2026-07-23）状态总览

用户修复 `no` 后，对比 07-22 的变化：

**已修复（✅）**
- ✅ **N3 / B5 每进程只能写一次文件**：现在同一进程可多次 `fs.open-write`+`fs.write`+`fs.close`（双写验证 `A=[AAA] B=[BBB]`）。`cp` 多源复制在「一次性写」层面已无障碍，只剩优化器对「循环内基名拼接」的 mis-compile（见 B11）。
- ✅ **N1 ICMP / 原生 ping**：标准库新增 `net.ping(host) (?i64)` 与 `net.ping-count(host, count)`，纯 Nolang 实现 ICMP Echo（校验和、SOCK_DGRAM macOS / SOCK_RAW Linux）。`ping.no` 已改用它，loopback 实测正常（`seq=1 rtt=124 us`）。

**仍然存在的问题（❌）**
- ❌ **B1 `http.http-get` 仍编译失败**（错误形态变化：ptr/i64 → GEP 空指针）。
- ❌ **B8 `dns-resolve` 任何输入都崩溃**（含 IP 字面量）。
- ❌ **B9 `net-recv` 的 `str-long` GEP codegen bug**：在独立小二进制里崩溃，但在完整 `main.no` 二进制里 codegen 正常（`curl` 实测可用）。
- ❌ B2/B3/B4/B6 未重新验证，按既有记录保留（手工规避法仍有效）。

**构建稳定性（B7 细化）**
- 单次 `clean + build` **可靠成功**；但**紧挨着的快速连续多次构建会失败**——推测是 `/tmp` 下 LLVM IR 临时文件名碰撞（每次构建的 `nolang<pid>` 目录互相干扰）。**务必「一次构建一条命令」**，不要写 `for` 循环连跑多次 build。

---

## 〇·五、2026-07-24 复测（用户再次修复 `no` 后）

用户于 07-24 11:05 重建 `no`（版本 `5b4f734`），并新增纯 Nolang `tls.no`、更新 `net.no`。针对「curl/ping 是否仍只支持 IP 字面量、curl 是否仍不支持 https」的复测结论：

**未解决（❌）—— 主机名与 https 仍不可用**
- ❌ **B8 `dns.dns-resolve` 进一步恶化**：原先是运行时 `index out of bounds` 崩溃；现升级为**编译期 GEP 空指针错误**——只要源码里出现 `dns.dns-resolve(...)` 调用，整个程序 `opt` 阶段即报 `getelementptr inbounds %str-long, %str-long* , i32 0, i32 0` / `expected value token`，**根本无法生成二进制**。（`dns.no` 本身 07-18 以来未变，问题在编译器/codegen。）
- ❌ **B10 `net-dial` 仍不解析主机名**：`net.no` 07-24 更新，但**未加入任何主机名解析**。`net-dial('localhost',...)`→-1、`net-dial('example.com',80)`→-1、`net-dial('127.0.0.1',...)`→正常 fd。grep `net.no` 仅见 `net-dial` 直接 `socket+connect` 处理 host 为 IP，无 `dns`/`getaddrinfo` 调用。
- ❌ **N8 HTTPS 仍不可用（新增阻塞 B12）**：纯 Nolang `tls.no` 已存在（TLS 1.2/1.3 客户端，底层用 `net-dial`），但 (1) 它依赖 `net-dial` → 受 B10 限制只能 IP 字面量；(2) 实测用 `tls-dial`/`c.connect`+`c.recv` 写 https 客户端时，`ok -> n = it`（`?i64` 的 `it` 绑定）在 `opt` 阶段报 `use of undefined value '%it'`（新增 **B12**，codegen bug），导致即使 IP 字面量 https 也**无法编译/运行**。

**复测中确认可用 / 不变**
- ✅ `net-dial` IP 字面量、`net` TCP 原语、`net.ping` 正常（`net.no` 更新未破坏既有能力）。
- ✅ B5 一次性写修复仍有效。
- ❌ B1 `http.http-get` 复测**仍编译失败**（同样 GEP 错误，错误位置/形态与 07-23 一致）。
- ⚠️ **option-match 语法陷阱（新发现，记为 G1）**：自定义 optional（如 `?tls-conn`）的匹配**必须**写成 `nil -> *` / `err -> *` / `ok -> { ... }`——默认分支 `->` 不覆盖 `err`/`ok`、且 `err -> {块}`/`nil -> {块}` 会被判「missing err/ok」；而内建 optional（如 `?i64`）可用 `ok ->` + `-> {块}` 默认式（或 `nil/err -> *; ok -> n = it`）。`it` 在 `ok` 分支内可用，但见 B12。

---

## 一、需要标准库实现的能力（缺失 / 不完整）

| # | 能力 | 影响 | 说明 / 现状 |
|---|------|------|------------|
| N1 | **ICMP / 原生 raw socket（`SOCK_RAW`）** | `ping` | ✅ **已实现**：`net.ping` / `net.ping-count`（见 `no/src/std/net/net.no`）。`ping.no` 已纯 Nolang 化。 |
| N2 | **可用的 HTTP(S) 客户端** | `curl` | 部分可用：`net/http.http-get` 仍坏（B1），但**可用 `net` TCP 原语手写 HTTP/1.1 客户端**（见 `src/curl.no`，IP 字面量 URL 实测可用）。主机名需 DNS（B8 坏）；HTTPS/TLS 暂无纯 Nolang 路径。 |
| N3 | **修复「每进程只能写一次文件」** | `cp`/`tee` 多文件 | ✅ **已修复**（用户本轮）。 |
| N4 | **修复 `str.split()` 内置函数** | 文本处理命令 | 仍坏（B4，未重新验证）；手工逐字节扫描规避法（W2）稳定可用。 |
| N5 | **修复 / 补全 `fs.write-file` 与 `fs.copy-file`** | 写/拷贝文件惯用法 | 仍坏（B2/B3，未重新验证）。 |
| N6 | **`os.exit` 接受 `i64`** | 透传退出码 | 仍坏（B6，未重新验证）；`os.exit(1)` / `os.exit(0)` 字面量可用。 |
| **N7** | **DNS 解析（主机名→IP）** | `curl` 主机名、任何需要解析的命令 | ❌ **`dns.dns-resolve` 任何输入崩溃**（B8）。`net-dial` 只接受 IP，不解析主机名。这是 `curl` 暂只支持 IP 字面量 URL 的根因。 |
| **N8** | **HTTPS / TLS 纯 Nolang 路径** | `curl https://` | ⚠️ **`tls.no` 已存在**（07-24 新增，TLS 1.2/1.3 客户端，纯 Nolang 不依赖 OpenSSL，底层用 `net-dial`/`net-send`/`net-recv`）。但当前**仍不可用**：(1) `tls-conn.connect` 直接 `net-dial` → 受 B10 限制只能 IP 字面量；(2) `c.recv` 的 `?i64` 用 `it` 绑定触发 B12 codegen 崩溃，连 IP 字面量 https 也编不出。等 B10+B12 修复后，`curl` 可改为 `tls-dial`/`c.send`/`c.recv` 实现 https（IP 字面量优先），届时再开放 `https://`。 |

---

## 二、标准库已有问题（bug，附复现）

### B1. `net/http.http-get` 编译失败（GEP 空指针）
调用 `http.http-get(url)` 时 LLVM 优化阶段报错，**整个程序无法编译**。

复现：
```nolang
main = () {
    resp = http.http-get('http://example.com')
    resp: {
        nil -> print('FAILED')
        -> print(resp.status-code.to-str())
    }
}
```
当前错误（2026-07-23 构建）：
```
opt: .../t_http_get.ll:908:72: error: expected value token
    %str-long.len.gep.39 = getelementptr inbounds %str-long, %str-long* , i32 0, i32 0
Error: build error: LLVM optimization failed: exit status 1
```
`http-response` 结构体（含 `body` 等字段）的 codegen 生成了**空的指针操作数** GEP。影响：N2（原生 `curl` 经 `http` 模块）受阻；`net/http` 模块整体不可用。

### B2. `fs.write-file(p, data []byte)` 编译失败（vec vs ptr）【未重新验证】
`str.to-bytes()` 返回 `vec`，`fs.write-file` 的 `data` 要 `[]byte`（`ptr`），LLVM opt 报 `'%vec' but expected 'ptr'`。
规避：用 `fs.open-write`+`fs.write(fd, str, n)`+`fs.close`（W1）。

### B3. `fs.copy-file(src, dst)` 静默写空文件【未重新验证】
返回 `rc=0` 但目标文件为空。规避：手写 `read-file`+`open-write`+`write`+`close`（W1）。

### B4. `str.split()` 导致整个二进制崩溃【未重新验证】
`content.split('\n')` 使整个二进制运行时崩溃（rc=137/139）。
规避：W2 手动逐字节扫描。`[]str` 的 `push`/索引本身正常。

### B5. 每进程只能成功写一次文件 —— ✅ 已修复（N3）
用户本轮已修复。现可多次写文件（双写验证 `A=[AAA] B=[BBB]`）。

### B6. `os.exit` 不接受 `i64`【未重新验证】
`os.exit(rc)`（`rc` 为 `i64` 变量）或 `os.exit(rc & 255)` 编译失败（`exit` 形参 `i32`）。
字面量 `os.exit(1)` / `os.exit(0)` 可用（见 `ping.no`/`curl.no`/`ln.no`）。

### B7（通用）. 优化器非确定性 + 快速连续构建的临时文件碰撞
- 每次 `no build` 必须先 `clean` 删掉 `nolang*`（位于 `main.no` 同级），否则随机出现 `PHI node entries do not match predecessors` / `use of undefined value` 等优化错误。
- **新发现**：即使每次都 `clean`，**一条命令里紧挨着连跑多次 `build` 仍会连续失败**（实测 40 次全败）。推测是 `/tmp` 下 LLVM IR 临时目录（`nolang<pid>`）在快速连续构建间互相碰撞。
- **规避**：**一次构建一条 Bash 命令**，不要在单个脚本里 `for` 循环连跑多次 build；单次 `clean + build` 通常一次成功。

### B8. `dns.dns-resolve` / `dns.dns-dial` 任何输入崩溃 → **07-24 升级为编译期错误**
`dns.dns-resolve(任何字符串)`（含 IP 字面量 `'127.0.0.1'`）**现在直接导致整个程序无法编译**（07-23 及更早是运行时 `index out of bounds` 崩溃 rc=1；07-24 起变为 `opt` 阶段 GEP 空指针错误）。`dns-dial` 内部也调用解析，同样无法编译。

复现（2026-07-24，版本 `5b4f734`）：
```nolang
main = () {
    ip = dns.dns-resolve('127.0.0.1')   # 仅调用即令编译失败
    ip: { nil -> print('NIL'); -> print(ip) }
}
```
```
opt: .../t_dns.ll:340690:75: error: expected value token
    %str-long.len.gep.222493 = getelementptr inbounds %str-long, %str-long* , i32 0, i32 0
Error: build error: LLVM optimization failed: exit status 1
```
注意：`dns.no` 自 07-18 未变，问题在编译器/codegen 对 `dns-resolve` 返回 `?str` 的处理。
影响：N7。`net-dial` 只接受 IP，所以 `curl http://example.com/...` 无法解析主机名（当前 `curl.no` 对主机名走「could not connect（DNS 损坏）」的优雅报错）。需要修复 DNS 解析后才能支持主机名 URL。

### B9. `net.net-recv` 的 `str-long` GEP codegen bug（上下文相关）
`net-recv(fd, buf, n)` 的底层调用 `recv(fd, str-long.data, n, 0)`。在**独立小二进制**里复现时崩溃（rc=137，或 GEP 空指针）；但在**完整 `main.no` 二进制**里 codegen 正常，`curl` 实测可完成 HTTP 读取并返回正文。

独立探针复现（崩溃）：
```nolang
main = () {
    fd = net.net-dial('127.0.0.1', 8099)
    net.net-send(fd, 'GET / HTTP/1.0\r\n\r\n', 16)
    buf str = ' '.repeat(4096)
    rn = net.net-recv(fd, buf, 4096)   # 崩溃点
    print(rn.to-str())
}
```
在 `main.no` 完整二进制中（含 curl）：`curl http://127.0.0.1:8099/test.txt` 正常返回正文（rc=0）。
影响：低（当前完整二进制可用），但属于潜在的 codegen 不确定性，建议排查 `str-long` 缓冲在小型函数内的 GEP 生成。

### B10. `net-dial` 不解析主机名
`net.net-dial(host, port)` 注释明确要求「host: 目标 IP 地址」。`net-dial('localhost', 8099)` 返回 -1；`net-dial('example.com', 80)` 返回 -1；`net-dial('127.0.0.1', 8099)` 返回正常 fd（实测 5）。**07-24 `net.no` 更新后复测，仍未加入任何主机名解析**（`net.no` 内 `net-dial` 仅 `socket+connect`，无 `dns`/`getaddrinfo` 调用）。主机名解析依赖 B8 的 DNS 修复；`tls.no` 的 `tls-conn.connect` 同样直接调用 `net-dial`，故 https 也只接受 IP 字面量。

### B11. 优化器对「循环内基名拼接」mis-compile（影响 `cp` 多源）
`cp-target(src, dir)` 做 `dir - '/' - bn`（字符串拼接）若在**循环内**调用，会让含该命令的二进制编译失败/运行异常（Heisenbug）。因此 `cp.no` 暂对多源复制显式报错（rc=1），单源复制（含复制到目录）正常。一次性写已修复（B5），多源复制剩下的唯一障碍是此优化器问题。

### B12. option-match 中 `it` 绑定（`?i64` 的 `ok -> n = it`）codegen 报 `undefined %it`
在 `?i64`（内建 optional）匹配的 `ok` 分支里用 `it` 绑定返回值并赋给变量，LLVM `opt` 阶段报 `use of undefined value '%it'`，整个程序无法编译。实测于 `tls.no` 的 `c.recv(buf, n)`（返回 `?i64`）路径：
```nolang
c tls-conn
c.init()
ok = c.connect('127.0.0.1', 8443)
ok == false -> { print('handshake failed'); return }
buf str = ' '.repeat(4096)
r = c.recv(buf, 4096)
r: {
    ok -> n = it                 # ← opt 报错：use of undefined value '%it'
    -> { c.close(); print('recv fail'); return }
}
```
```
opt: .../t_tls.ll:342510:39: error: use of undefined value '%it'
    %it.val.223357 = load i64, i64* %it
Error: build error: LLVM optimization failed: exit status 1
```
注意：纯 `ok -> print('x' - it.to-str())` 之类把 `it` 直接用于表达式（不赋给新变量）是否也触发，尚未单独验证；但本路径「`it` 赋给新变量」必崩。
影响：N8（HTTPS/TLS 纯 Nolang 路径）。即使 B10（DNS）修好，`c.recv` 的 `it` 绑定不过关，https 客户端仍无法落地。优先级：高（与 B8/B1 同级，直接阻塞 `curl` 主机名/https）。

### G1. option-match 语法陷阱（非 bug，但极易踩）
- 自定义 optional（如 `?tls-conn`）：匹配分支**必须**写全 `nil -> *` / `err -> *` / `ok -> { ... }`；默认分支 `->` 不覆盖 `err`/`ok`，且 `err -> {块}`/`nil -> {块}` 会被判「missing err, ok」而编译失败。即：`nil`/`err` 分支体只能是 `*`（跳过），`ok` 分支才是真正的 `{块}`。
- 内建 optional（如 `?i64`）：可用 `ok ->` + `-> {块}`（默认式，默认覆盖 nil/err），或 `nil -> *` / `err -> *` / `ok -> n = it`（三分支式，见 B12 注意）。
- 嵌套限制：option-match 内**再嵌套** option-match 超过 1 层深度会触发解析错误「missing err, ok」；应把内层逻辑抽到独立函数（见 `http.no` 风格）。

---

## 三、当前可用的规避写法（已验证）

### W1. 单次/多次文件写入（一次性写已修复）
```nolang
data = fs.read-file(src)
fd = fs.open-write(dst)
n = data.len            # 单独存长度变量
fs.write(fd, data, n)  # 字符串形式
fs.close(fd)
# 现已可在一个进程内多次调用上述序列（双写验证通过）
```

### W2. 手动逐字节拆分（替代崩溃的 `split()`）
```nolang
lines []str
start = 0
i <- [0..content.len): {
    content[i] == 10 -> {          # 10 == '\n'
        lines.push(content.slice(start, i))
        start = i + 1
    }
}
start < content.len -> lines.push(content.slice(start, content.len))
```
循环内首次赋值的标量需在循环**外**预先声明；`[]str.push`/索引安全。

### W3. 取基名用 `path.base()`（勿手写 slice/拼接）
```nolang
pp = path{ p: src }
bn = pp.base()   # 索引赋值实现，无拼接循环，安全
```

### W4. `net.ping` 实现原生 ping（纯 Nolang，✅ 可用）
```nolang
net.ping-count('127.0.0.1', 4)        # 多次；打印 seq/rtt
# 或单次：r ?i64 = net.ping('127.0.0.1')
```
注意：参数为 **IP**（不解析主机名，见 B8/B10）。

### W5. 用 `net` TCP 原语手写 HTTP 客户端（纯 Nolang，`curl.no` 采用）
```nolang
fd = net.net-dial(ip, port)          # ip 必须是 IP 字面量（B8/B10）
net.net-send(fd, req, req.len)
buf str = ' '.repeat(8192)
rn = net.net-recv(fd, buf, 8192)      # 完整二进制中可用（B9）
# 累积字节、定位 \r\n\r\n、截取 body
```
实测 `curl http://127.0.0.1:8099/file` 返回正文、`-o` 写文件、`http://host/` 优雅报错。

### W6. 仍需系统命令委托时（仅 `ln` 暂未纯 Nolang 化）
`fs` 标准库**没有** `symlink`/`hardlink` 内置（`grep` 仅见 `unlink`），无法纯 Nolang 实现 `ln`。当前 `ln.no` 仍 `process.process-system('ln ...')` 委托系统命令——这是**已知唯一仍依赖 libc 的命令**，待标准库补充 `fs.symlink`/`fs.link`（需编译器转发 `symlink`/`link` C 函数）后改为纯 Nolang。

---

## 四、对 Nolang 改进的优先级建议

1. **最高**：B8（DNS 编译期 GEP 崩溃，07-24 恶化）、B1（http.http-get 编译失败）、**B12**（`it` 绑定 codegen 崩溃）—— 三者直接阻塞 `curl` 主机名 / https / `http` 模块。
2. **高**：B10（net-dial 不解析主机名，需补 `getaddrinfo` 或复用 `dns-resolve`）、B9（net-recv codegen 不确定性）、B11（循环内拼接 mis-compile）、B7（构建临时文件碰撞）—— 影响构建与运行稳定性。
3. **中**：N4/N5/N6 —— 恢复 `split()`、修复 `write-file`/`copy-file`、放宽 `os.exit` 形参。
4. **低但基础**：N8（等 B10+B12 后接 `tls.no` 实现 https）、B2/B3/B4/B6 重新验证、G1 option-match 语法文档化。

---

*记录自 `notools` 项目：curl/ping 改为纯 Nolang 实现（2026-07-23，用户修复 `no` 后）。`ping` 已纯 Nolang 可用；`curl` 已纯 Nolang（net TCP），受 B8/B1 阻塞于主机名/https。`2026-07-24 复测：用户再次修复 `no`（v5b4f734，新增 `tls.no`），但主机名(B8/B10)与 https(N8/B12) 仍不可用——B8 由运行时崩溃恶化为编译期 GEP 错误，https 新增 B12（`it` 绑定 codegen 崩溃）。*
