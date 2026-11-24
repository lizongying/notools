# Agent 指南 — notools 工作区

本文件面向 AI 编码代理，帮助其在阅读后准确理解本仓库的结构、构建 / 验收口径与 Nolang 编码约定，
稳定生成风格一致、可编译、符合规范的 Nolang（`.no`）代码。

> 范围：修改 `notools/` `nogit/` `noimg/` `nojq/` `nonpm/` `nouv/` `noagent/` 七个子项目的 `.no` 源码、
> 测试与文档，以及 `.agents/` 下的 skill / 规则 / 计划产物时遵循本文件。
> 本仓库是 Nolang **编译器的下游语料仓库**，不是编译器本身：语言与编译器的完整权威指南在
> `/Users/lizongying/IdeaProjects/no/AGENTS.md`，本文件只做项目约定 + 语言精要 + 本项目特有的坑。
> 不含任何贡献流程 / 评审 / LLM 使用政策章节。

**权威顺序（冲突时按此裁决）**：实测 > 本 `AGENTS.md`（项目约定与语言精简）>
`.agents/rules/nolang-red-lines.md`（红线全文，从上游同步）>
`.agents/skills/nolang-core`（语言 / std / 构建深层知识）>
`docs/design/*.md`、`compiler-issues/README.md` > 记忆笔记。

---

## 1. 仓库概览

### 1.1 目录结构与子项目职责

| 路径 | 职责 | 入口 / 产物 |
| --- | --- | --- |
| `notools/` | Unix 命令行工具集（193 个子命令，单一可执行文件分发） | `main.no` 分发 → `src/*.no`；`dist/notools` |
| `nogit/` | 纯 Nolang Git 实现，不依赖系统 `git` 二进制 | `main.no` → `src/{object,refs,index,pack,zlib,...}.no` |
| `noimg/` | 纯 Nolang 图像处理库（9 种格式读写、55+ 种操作） | `main.no`（CLI）+ `lib.no`（导出 API）→ `src/*.no` |
| `nojq/` | 纯 Nolang JSON 处理（jq 1.7 兼容） | `main.no` → `src/{lexer,parser,binder,eval,...}.no` |
| `nonpm/` | pnpm 克隆：虚拟存储 + 隔离 `node_modules` | `main.no` → `src/{tarball,semver,workspace,...}.no` |
| `nouv/` | uv/pip 克隆：registry API、wheel/sdist、venv | `main.no` → `src/{registry,installer,wheel,version,...}.no` |
| `noagent/` | 自主 LLM 智能体 CLI：OpenAI 兼容、工具调用、SSE、会话持久化 | `main.no` → `src/{agent,provider,toolexec,approval,...}.no` |
| `compiler-issues/` | 编译器缺陷的最小复现与回归守卫（`.no` 可直接单独构建） | 见该目录 `README.md` |
| `docs/` | Docusaurus 文档站；`docs/design/option-unified.md` 是 option 迁移的语料侧权威 | — |
| `scripts/smoke.sh` | 本地 smoke 套件，镜像 CI 的六个发布目标 | `scripts/smoke.sh [--build] [suite...]` |
| `.github/workflows/build.yml` | tag push 触发：变更检测 → 6 目标交叉编译 → smoke → Release | — |
| `.agents/skills/`、`.agents/rules/` | 由根 `make sync-agents` 从 nolang 仓库稀疏同步；本地改动要想到上游 | — |
| `.agents/plans/`、`.agents/specs/` | AI 产出的计划 / 规格落盘目录（见 §1.5） | — |
| `workspace.noml` | 工作区根定义，登记七个包路径 | — |
| `Makefile` | 只有 `sync-agents` / `help`；**没有** `make no` / `make test` | — |
| `tests/`、`tmp/`、`bin/`、`dist/` | gitignored 的一次性产物 / 复现目录 | — |

注意：CI / Release 只覆盖 **6 个发布目标**（不含 `nojq`），但 `workspace.noml` 登记 7 个包；
改 `nojq` 不会触发 CI 构建。

### 1.2 包、入口与导入

- 每个子项目有一份 `package.noml`：`compiler.version` 目前统一钉 `v0.4.27`，`output: '/dist'`。
  本地实际使用的 `no` 可能不是这个版本——排查前先 `no version` 核对（见 §4.3）。
- 入口是 `main.no`（v0.1.34 起子命令直接作为顶层脚本运行，不再包一层 `main`）；库入口是 `lib.no`（如 `noimg/lib.no`）。
- 测试档用工作区根起始的绝对路径导入，如 `# /nogit/src/oid`；标准库模块自动加载，
  不要重新添加裸 `# std/fmt`（`no fmt` 会自动清理）。
- 模块名 = 导入路径末段（`std/crypto/sha256.no` → `sha256`）；函数名**不要**带模块名前缀。
- 同一包内的文件共享一个平面作用域：单文件 `no vet` 报错不一定是入口级错误
  （历史案例：`nojq/src/parser.no` 单档报 `bi-code` 未定义，`no vet nojq/main.no` 为 0）。

### 1.3 构建 / 测试 / 验收工作流

```bash
# no build 会调 llvm-config / clang，PATH 必须含 Homebrew LLVM
export PATH="/opt/homebrew/opt/llvm/bin:/opt/homebrew/bin:$PATH"
NO="${NO:-/Users/lizongying/IdeaProjects/no/bin/no}"   # smoke.sh 的默认编译器，可用 NO= 覆盖

cd <subproject> && "$NO" build        # 产物落在 <subproject>/dist/<name>
"$NO" vet <subproject>/main.no        # 入口级 vet = 权威判据（应 0 error）
NOLANG_AST_CACHE_OFF=1 "$NO" vet <file>   # 编译器变动 / A-B 对照时关磁盘 AST 缓存
"$NO" run <subproject>/tests/test.no  # 单档测试（有测试入口的子项目）
scripts/smoke.sh --build              # 重建 6 个发布目标并跑 smoke
scripts/smoke.sh nogit noimg          # 只跑指定套件（针对已构建二进制）
```

- 🔴 **目录级 `no vet <dir>` 有假阳性，不能当判据**：同一错误会在每个 import 者下重复上报；
  历史实测 `no vet nouv` 报 72 个 ERROR，逐档实为 0。以**入口级 vet + 实际 build** 定性。
- 强门：七个子项目全部 `no build` 成功（见 `.agents/plans/CODE_REVIEW.md` §6.5）。
- 🔴 **`no build` 会规范化源码并写回**：在 option-match 臂间插空行、展开 `-> {}`、移动注解，
  可能产生大量纯格式 diff。提交前必须区分「逻辑改动」与「构建噪音」，不要把噪音顺手提交。
- 大项目构建超过前台默认超时属正常，应后台跑；沙箱环境可能需要关闭才能调起 LLVM 工具链。
- 判据只认退出码与 `ALL TESTS PASSED` / smoke 的 PASS/FAIL 计数，不要凭「输出看起来像通过」宣布绿灯。

### 1.4 Skill 与规则的使用

仓库把语言 / 编译器的深层知识放在 skill 里，AGENTS.md 只是面向代理的精简版。

- **优先级**：工作区 skill（`.agents/skills/`）优先于同名 / 同功能的用户级 skill。
  由 `make sync-agents` 从 nolang 仓库同步，改本地副本前先想上游是否也该改。
- **权威顺序**：见文件开头；红线全文在 `.agents/rules/nolang-red-lines.md`。
- `nolang-core` 加载协议：先读 `SKILL.md` 的开关表 → `build` / `verify` 常驻，
  `syntax` / `std` 命中 trigger 才载 → 子视图（`syntax/` 7 个、`std/` 10 个）只挑一两个，
  **不要整目录硬读**；单次加载正文上限 1200 行。
- 旧 skill 名（`nolang-syntax` / `nolang-std` / `nolang-build` / `nolang-vet` / `nolang-debug` /
  `nolang-memory` / `nolang-builtin` / `nolang-path-resolution` / `nolang-selfhost-perf` /
  `nolang-docs-i18n` / `nolang-release`）仍是触发词，说旧名等价于加载对应模块。

### 1.5 AI 工作产物落盘约定

| 产物 | 目录 | 说明 |
| --- | --- | --- |
| 计划 / 审查报告 | `.agents/plans/` | 实施计划、任务拆解、阶段验收顺序 |
| 规格 / 技术方案 | `.agents/specs/` | 需求规格、接口契约、设计决策（现有多为 `spec.md` / `tasks.md` / `checklist.md` 三件套） |

- 文件名一律**小写 kebab-case + `.md`**；沿用现有文件格式（计划可带 YAML frontmatter）。
- 探针、dump、一次性 scratch 放项目内 `tmp/`（gitignored），不要放进 plan / spec 目录，
  也不要放系统 `/tmp` 后指望仓库能检索到。
- `.workbuddy-ai/{plans,rules,skills,specs,memory}` 是指向 `.agents/*` 与 `.workbuddy/memory` 的符号链接，
  不要删除或重名替换。
- `nogit/tests/` 等目录被根 `.gitignore` 命中，但其中 test 文件是 **tracked** 的：
  更新后必须 `git add -f <path>` 才能 stage（见 §4.4）。

---

## 2. 黄金法则

**绝不修改合法、语法正确的 Nolang 代码来「修」疑似编译器 / 解析器 bug。** 遇到疑似工具错误：
报告 + 最小复现 + 期望 / 实际，放进 `compiler-issues/`，不要改合法代码去绕。

唯一例外：用户明确要求规避**已确认**的编译器缺陷时，必须在代码旁写注释说明触发条件与实测证据
（例：nonpm 对 struct-with-slice 值拷贝坏拷贝的规避注释，见 §4.3）。

---

## 3. Nolang 语言精要（完整版见 `../no/AGENTS.md` 与 skill）

### 3.1 语句、注释、命名

- 行注释用 `;`（首选）；`;;` 换行进入块注释、再 `;;` 换行结束。
  `;` / `;;` 是**注释标记，不是语句分隔符**；`,` 也不能连接语句；**每条语句独占一行**。
- 4 空格缩进，禁用 Tab；每个非空 `.no` 文件以恰好一个末尾换行结尾。
- **全局常量 / 变量大写开头**（`MAX-SIZE`）；局部 / 参数 / 函数 / 结构体名小写 kebab-case；
  文件名（含目录名）用 `-` 不用 `_`。
- 🔴 **双引号是 char 字面量**：`"中"` 是 `char`，`'hello'` 才是 `str`；
  `"'"` 是 i32，把它当 `str` 传给 `starts-with-str` 或参与 `-` 拼接不报错但结果错。
- 文档注释写在条目正上方，说明行**只写名字不写类型**（`; data: input bytes`，
  不是 `; data []byte: input bytes`）；签名摘要行照实写完整签名。
- 不要用分割线 banner（`; ═══ 标题 ═══`）：注释会成为**下一条声明**的 doc，
  banner 会把无关章节名并进它的文档头。确需独立标题时紧跟一行 `...` 挂住。

### 3.2 函数、option、索引

- 函数是 read-only input / writable output 模型：`name = (inputs) (outputs) { }`。
  输入只读（标量按值、复合类型按只读引用）；命名输出可写；调用方可把输出槽直接绑回已有变量
  （即使该变量同时是接收者 / 输入也合法），用不到的输出用 `_` 丢弃。
- **参数默认值不支持**；可选性用 `?T` + 调用端显式传 `nil` / `ok(...)`；变参 `..t` 支持；
  参数 / 结果上限 64 个。
- 方法：`type.method = (inputs) (rest-outputs...) { }`，体内用 `.` 指代 `self`。
- **option `?T` 是三态**（`ok` / `nil` / `err`），优先用它替代 `(val, ok bool)` 双返回。
  解包优先 `ok -> ...(it)...`；用户自定义枚举变体的载荷才必须具名 `ok(v) ->`。
  `err ->` 臂的 `it` 是结构化错误 `err.err`，取消息用 `it.msg()`，不是 `str`。
- `?=` 上抛要求所在函数有 `?T` 结果参数，**或**语句位于块 match `{ ... }: { ... }` 主体内；
  两者皆非是编译错误。结果参数自动初始化为 nil，无需写 `result = nil`。
- 🔴 **索引读取恒返回 `?T`**（`#{index-out}` 已移除）：`v = a[i]` 是 option，
  必须 match / `?=` / 块 match 消费；显式 plain 型别标注不是逃生口。
- `#{overflow=wrap}` 只作用于**下一陈述**（L3）：独占一行置于目标上方，或同行尾随；
  写在函数头 / 块头对 codegen 无效（且当前 vet 可能不报）。一行一注解。
- 字符串拼接用 `-`；不写 `free`（deferred move + 作用域退出自动销毁）；
  协程只能在 `awy { co ... }` 组内用 `co`（`go` 非关键字、`run` 已移除）。

### 3.3 控制流

- 条件分支写成 `{}` 包裹的短路链：`{ c1 -> b1 \n c2 -> b2 \n -> b }`；
  **有 else 就必须把所有臂包进 `{}`**，裸写的独占 `->` 会静默折叠到最近一条裸 if。
- match：`x: { nil -> ... \n err -> ... \n ok -> ... \n -> 兜底 }`。
  臂只能换行分隔；多语句臂体必须用 `-> { ... }`；不同臂的绑定变量不得同名（不同类型会静默串型）。
- 循环：`(cond) { }`、`!! { }`、`! { }`、`n * { }`；
  遍历：`i <- [a..b): { }`（区间，start > end 自动递减）与 `i <- xs: { }`（数组 / 字符串逐码点 / vec）。
  `<-` 是遍历不是循环。
- 关键字别名 `ctn` / `brk` / `rtn` 等价于 continue / break / return；
  `*`/`**`/`***` 简写暂不推荐使用，写关键字。

### 3.4 格式化

- `no fmt` 是 4 空格风格与语句排版的唯一权威；改动文件提交前跑一遍确认 fixed point。
- 标准库在编译器仓库，**本仓库不直接改 `src/std`**；若确需上游修复，去 nolang 仓库走 `make no` 流程。

---

## 4. 本项目特有的陷阱（血泪清单）

### 4.1 `str` 索引写产生 0x01 tag 字节

- 🔴 循环内对 `str` 的动态索引 option 写 `s[i]: { ok -> it = v }` 实测写入的是 **option 的 tag 字节 0x01**，
  不是字符载荷：N 次循环得到 N 个控制字节。v0.1.35 修了 md5x / sha* 系列，曾遗漏
  od / xxd / blake2bx / mcookie 与 nogit 的 util / index / pack / oid（2026-11-21 已专项修复）。
- 安全写法：**字符串拼接** `out = out - ch`（参照 `hashutil.bytes-to-hex`），或逐字节走 `[]byte`
  再 `to-bytes-str()`。实测**固定索引** `s[0]` / `s[1]` 与 `[]byte` / `[]i64` 索引写是安全的，
  不要一刀切改所有索引。
- 附带：MD5 输出是**小端字组序**（内部值已字节反转，与 `store-le-u32` 双重抵消），
  别按大端推理去「修正」顺序。

### 4.2 不可信输入：路径、大小、名称

- 归档解压条目名、nogit ref 名 / tree 条目名：统一净化（复用 `safe-archive-path` / `safe-entry-name`），
  拒绝 `..`、绝对路径 / 盘符、反斜杠、NUL、控制字符；拼接后校验结果仍在目标目录内。
  Zip Slip 在本仓库曾有 6+ 处独立实现，新增解压入口必须先找公共原语。
- 图像解码器的 w/h 必须与输入长度挂钩（防几十字节触发展开百 GB 的分配炸弹）；
  HTTP 响应体、解压输出、字符串乘法都要有硬上限。
- 写操作（`fs.open-write` / `fs.write` / mkdir）返回值必须逐级检查，失败上报而不是静默返回 ok。
- 上游 stdlib 的 TLS 不校验服务端身份（`no/src/std/net/tls.no`），影响 nonpm / nouv / noagent 的
  https 下载与 API Key；涉及不可信端点时不能假定链路安全，修复点在 nolang 编译器仓库。

### 4.3 编译器 / 运行时已知行为

- `os.args().len()` 才是参数个数；`argc = os.args() - 1` 是**最后一个参数的下标**。
  各子项目写法不一（有的已用 `.len()`），写遍历前先看同文件的既有写法。
- `utils.trim-str()` 结果的 `.len()` 恒为 0（内容正确）——判空一律用 `.len-bytes()`。
- 循环体内 `i = i + 1` 放在中间且后面跟嵌套条件块会丢元素甚至 segfault；自增放循环体末尾
  （含 `continue` 的循环不能盲目搬）。
- `?str` 命名返回参数不要直接 `r = s`（会生成悬垂载荷），先过局部或 `s - ''`。
- **struct-with-slice 按值拷贝坏拷贝**（nonpm `dep-node`，含 `[]dep-node` 字段）：
  只在拥有该 slice 的同一函数框架内、**任何重分配之前**，用一个循环读取元素并把标量字段拷到局部就地使用；
  绝不把 `[]dep-node` 传参、也绝不在下载 / 解压之后再读。
- option-match 的**多语句块**别写成同行多语句 `ok -> { a = it; b = true }`：
  解析器会误判，导致后续函数未注册、级联报 `unknown function`。用单语句内联，或每行独占语句的块。
- D1 option 算术：`x = a + b` 得到 `?T`；`#{overflow=wrap}` 不解压，给 plain 型别变量重赋值会报错。
  用 match / `?=` 显式消费。跨版本 A-B 对比时加 `NOLANG_AST_CACHE_OFF=1` 绕开 AST 磁盘缓存。
- 编译报错的位置**不一定可靠**：以报错文本为准，位置只作线索；注意区分本轮 diff 引入的错误、
  预存的版本兼容问题与 lint 命名提示（见 `.agents/plans/CODE_REVIEW.md` §6.5.3）。

### 4.4 协作、git 与发版

- 工作区常有**多个并发 session** 改同一棵树：动工前后各跑一次 `git status --porcelain`；
  不属于本任务的已修改文件一律不碰、不「顺手修复」。
- 🔴 **禁止** `git checkout` / `reset` / `restore` / `stash` / `clean` / `push --force` 等会丢弃或覆盖工作区 / 历史的操作。
  回看旧版用 `git show <rev>:<path>` / `git diff <rev> -- <path>`；要比对实验用 `git worktree add` 到隔离目录。
- 🔴 **禁止 `git add -A`**：只 stage 用户逐项确认过的路径；`add` / `commit` / `tag` / `push` 前逐步确认。
- 发版走 `.agents/skills/nolang-core/modules/m92-release.md`：HISTORY.md 的**第一个 `## ` 段落**即 Release 正文，
  标题须与 tag 完全一致；CI 由 tag push 触发、按子项目变更检测构建、`sed` 注入 VERSION 到 `main.no`。

---

## 5. 改完就验收（顺序固定）

1. `no vet <受影响子项目>/main.no` = 0 error（必要时 `NOLANG_AST_CACHE_OFF=1`；目录级 vet 不算数）。
2. 受影响子项目 `no build` 成功；涉及面广时七个全部构建。
3. 跑相关测试档 `no run <subproject>/tests/test-*.no` 或 `scripts/smoke.sh <suite>`。
4. 安全相关改动必须补**恶意输入回归测试**：路径穿越、尺寸炸弹、写入失败，
   以及数据输出工具与系统工具 / Python 的逐字节对照。
5. `git diff` 逐项区分逻辑改动与 `no build` 格式噪音；`git status --porcelain` 复核改动边界。
6. 不要代为提交；等用户逐项确认要 stage 的路径。
