# Nolang 编译器问题记录与最小复现

记录日期：2026-11-05
编译器源码：`/Users/lizongying/IdeaProjects/no`（dev，HEAD `33027788`）
验证二进制：`/Users/lizongying/no/bin/no`（`make no` 构建并 install）
复现方式：在文件所在目录执行 `no build <file>.no`；构建产物 `dist/<name>` 可直接运行

所有 `.no` 文件都是**最小复现或回归守卫**，可直接单独构建。`filter-exports-block/` 是目录型复现（`package.jsonc` + `lib.no` + `mod.no` + `main.no`），需从 notools 根目录构建。

---

## Issue 1 — `os.arg(i + 1)` 的「静默解包」（已由其他 session 修复）

**真正的问题是静默的错误结果，不是报错。**

| 项目 | 内容 |
|---|---|
| 触发 | 先声明 plain 变量，再重指派：`x str = ''` … `x = os.arg(i + 1)` |
| 旧行为 | 编译通过。`os.arg` 返回 `?str`，但只有 payload 被读进 plain `str`，tag（ok / nil / err）被丢弃 → 越界时得到**空字符串**而不是错误 |
| 当前行为 | 报 `15w45dqk`：`cannot assign ?str value to str variable 'x'; an option cannot be unwrapped implicitly` |
| 结论 | **报错是合理的**，属于修复生效，不要改回静默通过 |
| 修复位置 | `src/checker/checker.go` → `validateStmtTypes`，新增「重指派到已存在的 plain 变量」也套用 D1 规则（结果参数同样不豁免） |

复现：

- `os-arg-silent-unwrap.no` — 应报 `15w45dqk`
- `os-arg-new-binding.no` — 对照组，新绑定推断为 `?str` 并用 match 消费，应构建成功

正确写法（任选）：两步 unwrap（`k = <expr>` 后 `v = k: { ok -> it ... }`）、match 语句、`k ?= <expr>`、或显式丢弃 `_ = <expr>`。

---

## Issue 2 — 布尔结果 infix 被误当作「可错算术」做 option 捕获（本次修复）

### 现象

```nolang
s = 'hello'
lb = s[0]        // 安全索引 → ?char
b = lb == 10     // 期望 bool
! b -> print('y')
```

LLVM 验证失败：

```
repro.ll:1906:20: error: '%lv.65' defined with type '%option = type { i64, [3 x i64] }' but expected 'i1'
  %c40 = xor i1 1, %lv.65
```

命中 notools 的 `tail-run`（`ends-nl`）、`pr-run`（`stdin-src`）、`du-walk`（`skip`）、`pr-cell`（`is-tab`）等多个布尔变量。

### 根因（MIR 层证据）

`b` 的 slot 被分配成 **`?i64`** 而非 `bool`，并生成 ok / err / nil 三臂捕获链：

| 分支 | 实际降级 |
|---|---|
| ok 臂 | `v24 = lb`（直接把整个 option 赋给结果，没有比较） |
| err 臂 | `v24 = lb` |
| nil 臂（且 `lb == nil`） | 才执行真正的 `payload(lb) == 10`（正确的 bool），却又 `option-wrap` 成 `?i64` |
| 后续 | `not v24` → `xor i1 1, %option` → 报错 |

来源：`src/parser/lowering.go` → `maybeCaptureOptionAssign`

```go
case *InfixExpression:
    inner = "i64"          // 所有 infix 一律硬编码
```

该函数 1416 行的短路只放行 `isOptionArithOperator`（`+ - * / %`）；比较与逻辑运算符不在其中，于是 `==` / `&&` 也被当成可错算术，合成 `?i64`。函数自身的注释（1473–1493）已写明 `inner = "i64"` **只对整数算术成立**，但代码只覆写了 `f64` / `str` 两种例外，漏掉了布尔结果。

对照实验（缩小触发边界）：

| 源码 | 结果 |
|---|---|
| `b = lb == 10` + `! b` | ❌ 失败（原始问题） |
| `b bool = lb == 10` + `! b` | ✅ 显式标注 bool 后，`eq dst=25:bool` 直接 payload 比较 |
| `lb == 10 -> ...`（直接作条件） | ✅ `if` 条件对 option 有处理 |
| `b = lb == 10` + `b -> ...`（不用 `!`） | ✅ 同上 |
| `x = lb + 1`（算术） | ✅ |

### 修复

在 `src/parser/lowering.go`：

1. 新增 `isBoolResultInfixOperator(op)`：`== != < <= > >= && ||`
2. 在 `maybeCaptureOptionAssign` 取得 `root` 后，对这类根提前 `return nil`，跳过 option 捕获

理由与 `src/mir/index_compare_test.go` 的語言契約一致：比较在 `emitCmp` 直接对 `?T` 取 payload 比较得 bool，安全索引越界的 nil 自然给出 false，不传播 option。

### 验证

- `make test`（带 `LD_FLAGS_WITH_SIG` 注入）：**EXIT=0，0 FAIL**（此前裸 `go test ./...` 的 7 个 FAIL 全部是 `StdSigKey 未注入` 的环境错误，与代码无关）
- 语义用例全部正确（比较真/假、内联安全索引越界 `a[oob] == 5`、`&&` 链），无崩溃
- 不改编译器的规避方式：显式写 `b bool = lb == 10`

复现与守卫：

- `option-compare-bool.no` — 最小复现
- `safe-index-compare.no` — 跳过捕获后安全索引仍需越界保护

---

## Issue 3 — 多值解构漏检 → void 分支条件 → 无效 IR（已修复）

### 现象

修好 Issue 2 后 notools 主项目暴露（此前被第一个错误掩盖，验证器一次只报一处）：

```
notools.ll:217530:23: error: void type only allowed for function results
  %cb.80895 = icmp ne void undef, 0
  br i1 %cb.80895, label %namei_run.bb72, label %namei_run.bb73
```

`nonpm` 修掉 Issue 5 后也出现同款错误（`cmd_link`、`get_latest_version`），确认是共性问题。

### 独立最小复现（本次完成）

`void-cond-multitarget.no`：

```nolang
j = json.parse('{"name":"x"}')
j: {
    ok -> {
        nv = it.get('name')
        nv: {
            ok -> {
                s, found = it.str()
                {
                    found -> print('has')

                    -> print('no')
                }
            }

            -> {
            }
        }
    }

    -> {
    }
}
```

修复前稳定输出 `void-cond-multitarget.ll:2020:21: error: void type only allowed for function results / %cb.129 = icmp ne void undef, 0`。

### 根因链条

| 环节 | 位置 | 问题 |
|---|---|---|
| 1. 签名表分两张 | `src/checker/stdsig_gen.go` | std **方法**签名在 `embeddedStdMethodSigs`（`json.json.str` / `json.str` → `?str`），与模块函数 `embeddedStdFuncSigs` 分离 |
| 2. checker 漏检 | `src/checker/funcargs.go` → `lookupReturnCount` | 只调 `CollectStdModuleSignatures()`，**从不查 `CollectStdMethodSigs()`**；`it.str()` / `json.str(v)` 返回 `-1` → `rfzrw1nh` 的 `expectedReturns >= 0` 门槛不满足，静默跳过 |
| 3. MIR 丢弃多余 target | `src/mir/hir2mir.go` → `lowerMultiAssign`(12870) / `lowerMultiAssignCall`(12917) | `for i, t := range targets { if i >= len(dsts) { break } }` — 第二个 target 根本不进 `l.locals` |
| 4. 读到未绑定名字 | `src/mir/codegen.go` → `loadVal`(5483) | KindVoid → `("void","undef")` |
| 5. 生成无效 IR | `src/mir/codegen.go` → `emitTerm(OpCondBr)`(17442) | `vT != "i1"` 无条件生成 `icmp ne void undef, 0` |

`fs.readlink('/tmp')` 之所以会正确报 `rfzrw1nh`，是因为它是**模块级自由函数**（`fs.readlink` 在 funcSigs 里）且 builtin 裸名表也命中；换成任何 std **方法**就漏检。`it` 是 match 的隐式绑定，`checker/funcargs.go:625` 明确 `delete(varTypes, "it")`，连 `baseType.method` 都构造不出来。

`docs/design/option-unified.md` §3.3 规定消费 `?T` 只有 `?=`、`x: { ok -> ... }`、`_ = expr` 三条路径；`s, found = it.str()` 是迁移前 `(T, ok bool)` 的过时写法，**不能**在 MIR 层把缺失结果补成 `i1 false` 来兼容 —— 那等于承认静默拆包，且 `found` 恒 false 会产生更难查的静默错误行为。

### 修复

1. `src/checker/funcargs.go` → `lookupReturnCount`：引入 `CollectStdMethodSigs()`，在 DotExpression 的 `isVar` / `else` 两分支补查 `module.method`、`module.struct.method`、裸方法名；对 `it` 这类无类型 receiver 增加「方法名后缀唯一匹配」兜底 —— 遍历 methodSigs 中所有 `.methodName` 结尾的键，**仅当所有候选返回数量一致**时采用，歧义仍返回 `-1`（保留「无法确定则跳过」契约，避免误伤）。
2. `src/mir/codegen.go` → `emitTerm(OpCondBr)`：`vT == "void"` 时不再生成 `icmp`，改为 `c.fail(...)` 累加诊断并停止发射该 terminator；`EmitLLVM` 把 `c.errs` 聚合成 `zodppsnm`。这是纵深防御，覆盖 checker 未来被绕过的其它 void 来源。
3. `src/checker/farg_bare_option_test.go`：新增 `TestMultiAssignStdMethodReturnCountRejected`（`it.str()` / `json.str(v)` 应报 `rfzrw1nh`）与 `TestMultiAssignUserFunctionReturnCountOK`（合法双结果函数不误报）。

### 验证

- 修复后 `void-cond-multitarget.no`：`void-cond-multitarget.no:8:26: [ERROR] ... function returns 1 value(s) but 2 target(s) provided [rfzrw1nh]` —— 从 LLVM verifier 崩溃变成带行号的源码诊断。
- `make no` 重建 + `make test`：**EXIT=0，0 FAIL**。
- 影响面：`nogit` / `nojq` / `nouv` 不含此类过时写法，不受影响；`nonpm` / `notools` 中残留的 `x, ok = it.str()` 现在会明确报错，需按 Issue 1 的写法迁移。

---

## Issue 4 — noimg 的项目本地 struct 未注册进 MIR（源码侧已解决，编译器侧可改）

```
EmitLLVM: setfield: field "depth" not found on "image.image" (struct key "image.image") [3nktiaae]
```

`noimg/src/image.no:7..20` 明确定义了 `image { … depth i64 … }`（13 个字段），但 `NOLANG_MIR_DUMP_MIR=1` 的 `### structs (15)` 段里**只有 std 的 struct，完全没有 `image.image`**。所以不是字段缺失，而是**项目本地 struct 定义没有被注册到 MIR 的 `StructFields` 表**；`src/mir/codegen.go:11747` 的 `mod.FieldIndex("image.image", "depth")` 因此必然返回 false。

进一步定位：`noimg/main.no` 的 111 行 import **全部是函数级**（`# /noimg/src/image.new`、`pnm.load` …），**没有任何模块级（无点号）import**。因此 `image.no` 的文件级 `image { … }` 定义从未进入 HIR，`collectStructFields`（`src/mir/hir2mir.go:738`，只扫 `pkg.Top` 的 `KStructDef`）自然注册不到。HIR dump 里 12 个 struct 全是 std，也印证了这点。

**解决方案（已实测有效）**：在 `main.no` 的 import 区补一行模块级导入

```nolang
# /noimg/src/image
```

加完后 `setfield depth` 立即消失（暴露出下一个链式错误 `unknown callee i64.to-i64 in func jpeg-decode-progressive [4qhyyund]`，属另一问题）。该改动涉及项目源码且有并行 session，本次**未保留**，仅记录解法。备选的编译器侧方案：让函数级 import 同时带上同文件里的类型/struct 定义。

---

## Issue 5 — `?T` 赋给 struct 字段绕过检查，生成坏 IR（已复现，源码侧已规避）

### 现象

`nonpm` 修掉 `15w45dqk` 后暴露：

```
nonpm.ll:7334:19: error: '%lv.1744' defined with type '%option = type { i64, [3 x i64] }' but expected '%str-long = type { i64, i64, ptr }'
  store %str-long %lv.1744, %str-long* %gp.1745
```

### 最小复现

`setfield-option.no`：

```nolang
box {
    name str
    n i64
}
make-box = () (b box) {
    b.name = ''
    b.n = 0
    return
}
g = (i i64) {
    c = make-box()
    c.name = os.arg(i + 1)
    print(c.name)
}
g(0)
```

稳定复现 `store %str-long %lv.N, %str-long* %gp.N`。

### 根因与源码位置

`nonpm/main.no` 的 `cmd-install` 原本是：

```nolang
i < argc -> cfg.registry = os.arg(i + 1)
i < argc -> cfg.store-dir = os.arg(i + 1)
```

`nonpm/src/config.no` 的 `config` 第 0 个字段是 `registry str`，IR 中 `getelementptr %config_config ... i32 0, i32 0` 正是它。`15w45dqk`（D1 规则）只覆盖「重指派到已存在的 plain 变量」，**setfield 赋值路径未做 option 检查**；codegen 直接把整个 `%option` store 进 `%str-long*`。

### 解决方案

- **源码侧（本次已采用）**：两步 unwrap 后再赋值，改完该 IR 错误消失：

  ```nolang
  i < argc -> {
      #{overflow=wrap}
      reg-arg = os.arg(i + 1)
      cfg.registry = reg-arg: {
          ok -> it

          -> ''
      }
  }
  ```

- **编译器侧（待修）**：把 D1 规则扩展到 `setfield` 赋值，让这类写法在 checker 层就报 `15w45dqk`，而不是生成无效 IR。这是 Issue 1 规则收紧的自然延伸。

---

## Issue 6 — `eprint` 收到 bare `?T` 时 checker 漏检（已复现，待修）

### 最小复现

`eprint-option.no`：

```nolang
x = os.arg(1)
eprint(x)
```

→ `Error: ... EmitLLVM: eprint expects str/i64/byte/char/bool arg, got %option [w9ajg8ow]`

对照组 `eprint('v=' - x)`（字符串拼接）**构建成功**，说明只有直接传 bare option 才触发。notools 主项目修好 Issue 3 后暴露的正是这个错误。

### 判断

与 Issue 5 同类：D1 / `3604icnf` 覆盖了普通变量重指派与普通函数实参，但 **builtin `print` / `eprint` 的 option 实参**没有被 checker 拦下，而是一路走到 codegen 才报 `w9ajg8ow`，且该诊断缺少源码行号与函数名。

### 解决方案

- 源码侧：先 unwrap 再打印（`x = os.arg(1): { ok -> it ... }` 后 `eprint(x)`），或 `x: { ok -> eprint(it) ... }`。
- 编译器侧（待修）：把 bare-option 实参检查扩展到 builtin `eprint` / `print`，在 checker 层带行号报错；或至少给 `w9ajg8ow` 补上函数名与位置。

---

## Issue 7 — `lib.no` 导出过滤漏掉巢状区块内的 callee（已修复）

> **更正**：本问题此前被记录为「函数级 import 的 lazy-load 漏加载同文件内部函数（待修）」，该判断**是错的**。下面保留推翻过程，供后续排查参考。

### 现象

`noimg` 依次修好 Issue 4（`image.image`）、progressive JPEG 的 `i64.to-i64`、`vp8.vp8-br` 后，稳定停在：

```
Error: ... EmitLLVM: unknown callee jpeg-read-block-444 in func jpeg-encode-scan [4qhyyund]
```

### 旧假说为何无效

| 尝试 | 结果 | 事后解释 |
|---|---|---|
| 补模块级 `# /noimg/src/jpeg` | 仍缺这两个 | `processUseAndMerge` 的去重键是 `use.Path`，不是 `(Path, Function)`；函数级 import 本来就等价于整模块导入 |
| 补函数级 `# /noimg/src/jpeg.jpeg-read-block-444` / `-420` | 错误不变 | 同上，且 `use.Function` 只在同时有 `Alias` 时才点名筛选，这些 import 全被去重跳过 |
| 删掉 `jpeg.load` / `jpeg.save` 函数级 import | 错误不变 | 同上 |
| 重命名成不含共同前缀的名字 | 错误跟着名字变 | 名字解析本身没问题，是定义被过滤 |

真正线索是「定义在文件**中间**被删、前后函数都在」：`jpeg-read-block-420` / `-444` 之后的 `jpeg-dct-8x8`、`jpeg-quantize`、`jpeg-encode-block` 全部正常注册，所以不是文件尾部截断，也不是 reachability worklist 的深度问题。

### 逐层定位（全部为实测）

| 步骤 | 结论 |
|---|---|
| 独立 Go parse `noimg/src/jpeg.no` | `ERRORS=0`，42 statements / 31 个 `FunctionDefinition`，`-420` 在 `[33]`、`-444` 在 `[34]`，`GenericParams=0` → **parser 完全正常** |
| `NOLANG_AST_CACHE_OFF=1` 重建 | 结果不变 → 排除 Tier-1 磁盘 AST 缓存 |
| `NOLANG_DEBUG_SELF=1` → `/tmp/merged_dump.txt` | merged 只有 25 个 `jpeg-*` 函数，原始 27 个，缺的正好是连续这两个 |
| 临时 pipeline trace（`CompileTarget` 各 pass 后计数） | **`after-mergeModules` 就已经缺**，后续 stdLoad / prefix / monomorph / secondStage / finalize 都只是保持缺失 |
| 同一 trace 细化到 `processUseAndMerge` | `parseFile:CACHE:.../jpeg.no` = **42 stmts、两个定义都在**；`merge:resolveUse:/noimg/src/jpeg` = **40 stmts、两个都不在** → 丢在 `resolveFile` |
| 直接调用 `checker.FilterByExports` | `BEFORE=31 AFTER=29 stmts=40`，`REMOVED` 恰好 `-420` / `-444` |

### 根因

`src/build/transpiler_resolve.go` 的 `resolveFile` 对含 `lib.no` 的包一律跑 `checker.FilterByExports`。`noimg/lib.no` 是导出白名单，只列了 `jpeg.load` / `save` / `save-quality` / `save-quality-subsampling` 四个公开函数。

`src/checker/funcargs.go` 的 `filterByExports` 会从公开函数出发，**传递收集同模块 callee** 来决定还要保留哪些内部 helper（否则内部函数全被过滤、呼叫点悬空）。它的 `walkStmts` 只处理 5 种 statement：`LetStatement` / `ExpressionStatement` / `MultiAssignStatement` / `ReturnStatement` / `ForStatement`，**缺 `*parser.BlockStatement`**。

Nolang 的 `{ cond -> {...} -> {...} }` if-group 正是 `BlockStatement`（探针在该文件命中 **35 次未处理节点**）。整个巢状区块被跳过，于是**只在 `jpeg-encode-scan` 深层 subsampling 分支里被呼叫**的 `-420` / `-444` 没进 keep-set → 定义被过滤、呼叫点保留 → codegen 报 `4qhyyund`。其余 25 个内部函数因为在浅层分支或其它函数里也有呼叫而被正常收集。

附带确认：HIR/MIR 里的 `enqueueCallee` 静默丢弃、AST 缓存、数字后缀词法、签名重复去重、`[64]f64` 类型、`GenericParams` 过滤全部排除。

### 修复

`src/checker/funcargs.go` → `filterByExports.walkStmts` 补一个 case（唯一改动）：

```go
case *parser.BlockStatement:
    // A bare `{ ... }` group (if-group / match group with arms) is a
    // statement in its own right. Without this case the whole nested
    // group is skipped, so helpers called only from a nested arm are
    // dropped from the export keep-set and later report
    // "unknown callee" in MIR codegen.
    if s != nil {
        walkStmts(s.Statements)
    }
```

回归守卫 `src/checker/filter_exports_block_test.go`：**双向验证过** —— 带修复 `PASS`，临时撤掉该 case 后 `FAIL` 且报错为 `helper called only from a nested block was dropped from the export keep-set`。

### 最小复现

`compiler-issues/filter-exports-block/`（`package.jsonc` + `lib.no` + `mod.no` + `main.no`）。`lib.no` 只导出 `public-fn`，而它只在两层巢状 if-group 里呼叫 `nested-helper`：

```bash
cd /Users/lizongying/IdeaProjects/notools
export PATH=/opt/homebrew/opt/llvm/bin:$PATH
no build compiler-issues/filter-exports-block/main.no
./dist/main        # 修复后输出 3
```

修复前：`unknown callee nested-helper in func public-fn [4qhyyund]`。

> 注意 `open` 不能用作函数名（与 builtin 冲突，会报 `unknown callee open in func main`），复现里改用 `public-fn`。

### 验证

- `make no` 重建 + 新增 `checker` 回归测试：`ok github.com/lizongying/nolang/checker`。
- `make test`：`checker` / `mir` / `parser` / `lsp` / `fmt` 等 package 全 ok；**唯一 FAIL** 是 `parser/dump` 的 `TestCheckerSugarDriftIsWithinKnownSet`（`ovfhndld` 新 drift + 6 个 stale allowlist entries），属并行 session 的 checker/lowering 改动，与只作用于 import 导出过滤的本次修复无关。
- **7 个子项目全量回归：7/7 `Build successful`**（`noimg` 首次通过）。

### 本次保留的源码侧修复

`noimg/main.no` 补 3 行模块级 import（`# /noimg/src/image`、`vp8`、`jpeg`）解决 `image.image` / `vp8.vp8-br` 的 struct 注册；`noimg/src/jpeg.no` 的 `jpeg-decode-progressive` 补 6 个显式 `f64` 标注（与 baseline 解码函数一致），消除 `i64.to-i64`。这三处让 noimg 连过前 3 层错误，Issue 7 修完后全绿。

---

## 7 个子项目回归（最终：7/7 全绿）

验证二进制：`make no` 重建后的 dev `no`；日志 `/tmp/regression_final2.log`。

| 项目 | 结果 | 关键修复 |
|---|---|---|
| noagent | ✅ | 无需额外改动 |
| nogit | ✅ | 1 处 `15w45dqk` 两步 unwrap |
| nojq | ✅ | 10 处 `15w45dqk` 两步 unwrap |
| nouv | ✅ | 9 处 `15w45dqk` 两步 unwrap；`cmd-add` 语句式 match → 两步 unwrap 表达式 + `resolved != ''`（消 `3604icnf`） |
| nonpm | ✅ | setfield option（Issue 5）两步 unwrap；`src/*.no` 23 处旧 `(T, ok bool)` 解构 → option match；`cmd-link` 同 |
| noimg | ✅ | 3 行模块级 import 注册 struct + 6 个显式 `f64` 标注 + **Issue 7 编译器修复**（`FilterByExports` 补 `BlockStatement`） |
| notools | ✅ | `rename.no` 从源头 unwrap 安全索引（`src = files[i]`）；`namei.no` / `readlink.no` 共 3 处 `fs.readlink` 旧解构 → option match |

**21 处 `15w45dqk` 全部消除，7 个项目均 `Build successful`。** 过程中从 LLVM verifier 崩溃一路收敛到可读的源码诊断，最后剩下的两个真正编译器缺陷（Issue 3、Issue 7）都在编译器侧修掉并配了回归测试。

### 编译器侧仍待修（不影响 7/7 构建）

| Issue | 状态 | 说明 |
|---|---|---|
| Issue 5 | 源码侧已规避，编译器待修 | 把 D1 规则扩展到 `setfield` 赋值，让 `c.field = os.arg(...)` 在 checker 层报 `15w45dqk` |
| Issue 6 | 源码侧已规避，编译器待修 | bare `?T` 传给 `print` / `eprint` 的检查；`w9ajg8ow` 已补函数名但缺行号 |
| Issue 4 | 源码侧已解决，编译器可改 | 函数级 import 可考虑连同文件的 struct / 类型定义一起带入，省掉手写模块级 import |

`make test` 目前唯一 FAIL 是 `parser/dump` 的 sugar-drift allowlist（并行 session 改 checker/lowering 导致白名单陈旧：`ovfhndld` 新增、6 个 stale entries），与本次修复无关。

---

## 环境注意事项

- `no build` 需要 `PATH` 含 `/opt/homebrew/opt/llvm/bin`，且需关闭沙箱；大项目构建超过前台默认超时，应后台执行。
- **`no build` 会规范化源码并写回磁盘**：会在 option-match 臂之间插空行、展开 `-> {}`、移动注解，产生大量纯格式 diff（本轮 `noimg/src/jpeg.no` 与 `notools/src/*.no` 的 M 多半来自这里）。提交前务必区分「逻辑改动」与「构建噪音」。
- 保留 IR：`NOLANG_MIR_DUMP_LL=1`（打印 `[MIR] emitted LLVM -> <path>`）；MIR / HIR 分别用 `NOLANG_MIR_DUMP_MIR=1` / `NOLANG_MIR_DUMP_HIR=1`。
- `NOLANG_DEBUG_SELF=1` 会把 merge 完成后的 `merged.Statements` 逐条写到 `/tmp/merged_dump.txt`；`NOLANG_AST_CACHE_OFF=1` 可强制全新 parse、排除 Tier-1 磁盘 AST 缓存干扰。
- 定位「某函数在 pipeline 哪一阶段消失」时，可在 `CompileTarget` 各 pass 之后临时插入 env-gated 计数；本轮用它把 Issue 7 从 HIR 一路收敛到 `resolveFile`。诊断补丁已全部移除。
- 编译器测试必须走 `make test`（注入 `StdSigKey`），裸 `go test ./...` 会因签名 key 为空而硬失败；改完编译器源码必须 `make no` 重建并 install 才生效。
- 本工作区存在并行 session；**HEAD 会被别的 session 推进**（本轮 `compiler-issues/README.md`、21 处适配、`noimg` 修改都已被提交进 `ea8506f` / `62d07ef`）。提交前须 `git status --porcelain` 全量核对改动边界。
