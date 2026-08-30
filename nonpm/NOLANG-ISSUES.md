# Nolang 编译器问题记录

在 nonpm 测试过程中遇到的 Nolang 编译器问题，供后续处理。

## 问题 1: ~~LLVM IR str-long vs vec 类型不匹配~~（已解决）

**严重程度**: 无（已解决）

**描述**:
~~当 `str` 类型变量（特别是长字符串 >127 字节，即 `str-long`）被传递给某些标准库函数时，LLVM 优化器会将 `str-long` 类型与 `vec` 类型混淆。~~

**根本原因**:
`fs.read-file` 返回 `[]byte`（`%vec`），但代码中将其赋值给 `str` 类型变量（`%str-long`），导致类型不匹配。

**解决方案**:
- 使用 `fs.read-str(path) (?str)` 替代 `fs.read-file(path) ([]byte)` 读取文件内容为字符串
- 将 `utils.no` 的 `read-file` 函数改为调用 `fs.read-str` 并通过 match 提取 `str`
- 将所有源文件中的 `fs.read-file(X).to-str()` 链式调用改为两步赋值或直接使用 `fs.read-str`

**注意**:
虽然此问题已解决，但新编译器 `adc35d8` 引入了问题 13（`O-APPEND` 平台条件编译失败），导致所有测试仍无法通过。

---

## 问题 2: 函数名 `read` 与标准库冲突导致多值返回被错误解析

**严重程度**: 中

**描述**:
当模块中定义了名为 `read` 的函数，且该函数返回多个值 `(content str, ok bool)` 时，编译器可能将其与标准库的某个 `read` 函数混淆，导致认为只返回 1 个值。

**错误信息**:
```
Error: compilation error: validation errors: function returns 1 value(s) but 2 target(s) provided
```

**触发场景**:
- `lockfile.no` 中的 `read = (dir str) (content str, ok bool)` 函数

**当前 workaround**:
- 将函数重命名为 `read-lockfile` 等不与标准库冲突的名称

---

## 问题 3: `process.process-run` 函数不存在（已修正）

**严重程度**: 低（已修复）

**描述**:
nonpm 代码中使用了 `process.process-run` 函数，但标准库中不存在此函数。

根据 `/Users/lizongying/IdeaProjects/no/src/std/process.no` 的实现：
- `process-system = (cmd str) (status i64)` — 内建函数，**返回 `status i64`**（C `system()` 的原始 wait status）
- `process-shell = (cmd str) (status i64)` — 已弃用的包装，调用 `process-system`，返回 `status i64`
- `process.shell = (cmd str) (code i64)` — 推荐使用的便捷函数（spawn + wait 组合），返回正确的退出码
- `process.cmd = (program, args, dir, input, env, timeout, merge-err) (out, stderr, code, err)` — 完整功能的子进程执行器

**错误信息**:
```
Error: compilation error: unknown function: process.process-run
```

**修复方案**:
- 将所有 `process.process-run` 替换为 `process.process-system`
- **`process.process-system` 返回 `status i64`**（原始 wait status），可以赋值给变量
- 推荐使用 `process.shell()` 替代 `process.process-system()`，因为前者返回正确的退出码
- 完整功能场景应使用 `process.cmd()` 获取 stdout/stderr 输出

**注意**:
之前错误地认为 `process.process-system` 不返回值。实际上它返回 `status i64`，代码中应保留对返回值的赋值。

---

## 问题 4: ~~`_` 作为占位变量不被支持~~（非问题，编译器版本 bug）

**严重程度**: 无（误报）

**描述**:
~~Nolang 不支持使用 `_` 作为占位变量~~。实际上 Nolang **已经原生支持** `_` 作为占位变量。以下是标准用法：

```nolang
; 使用 _ 忽略不需要的返回值（占位變數）
_, b = swap(5, 3)   ; 只取第二個值，忽略第一個
a, _ = swap(5, 3)   ; 只取第一個值，忽略第二個
_, _ = swap(5, 3)   ; 忽略全部返回值（呼叫僅為副作用）
```

之前遇到的编译错误是旧版本编译器（`b530eab`）的 bug，在新版本编译器（`85cf832`）中已修复。**无需任何代码修改**，`_` 占位变量可以正常使用。

---

## 问题 5: ~~`json.from-str` 等函数在自定义模块中不可用~~（已解决）

**严重程度**: 无（已解决）

**描述**:
~~当导入自定义的 `json` 模块（`# /nonpm/src/json`）后，`json.from-str`、`json.from-num`、`json.from-bool` 等标准库函数无法通过 `json.` 前缀访问，因为它们被自定义模块遮蔽。~~

**解决方案**:
将 `json.no` 重命名为 `pj.no`，避免模块名与标准库 `json` 冲突。现在标准库的 `json` 模块可以通过 `json.` 前缀正常访问。

---

## 问题 6: ~~`json.from-str`/`json.from-num`/`json.from-bool` 导致 LLVM option 类型错误~~（已解决）

**严重程度**: 无（已解决）

**描述**:
~~调用 `json.from-str(s)` 等函数创建 JSON 值时，LLVM 优化器遇到未初始化的 `%option` 类型。~~

**解决方案**:
标准库 `json` 模块不存在 `from-str`、`from-num`、`from-bool` 函数。重写 `pj.no` 正确使用标准库 API（`json.parse`、`json.get-str`、`json.set-str` 等）后，此问题不再存在。

---

## 问题 7: ~~`fs.write` 传入空字符串变量导致 LLVM integer type 错误~~（已解决）

**严重程度**: 无（已解决）

**描述**:
~~当 `fs.write(fd, str_var, str_var.len)` 中的 `str_var` 可能为空时，LLVM 生成了 `i8* 0` 空指针。~~

该问题在新版本编译器中已修复。

---

## 问题 8: ~~`sha1.sha1-hex` 参数为空导致 LLVM 错误~~（已解决）

**严重程度**: 无（已解决）

**描述**:
~~`sha1.sha1-hex` 函数被调用时第一个参数为空。~~

该问题在新版本编译器中已修复。

---

## 问题 9: ~~编译器 Go 运行时 panic~~（已解决）

**严重程度**: 无（已解决）

**描述**:
~~`test-resolver.no` 编译时触发了 Nolang 编译器（Go 编写）的运行时 panic（goroutine 崩溃）。~~

该问题在新版本编译器中已修复。

---

## 问题 10: ~~`use` 路径解析错误~~（已解决）

**严重程度**: 无（已解决）

**描述**:
~~`# /nonpm/src/run` 导入路径被解析为 `UNKNOWN(36)` token。~~

该问题在新版本编译器中已修复。

---

## 问题 11: 标准库 `json.stringify` 中 `f64.to-str()` LLVM 代码生成 bug

**严重程度**: 高（阻塞所有 JSON 相关功能）

**描述**:
标准库 `json.no` 的 `json-pool.stringify` 方法（第 626 行）中调用 `num-val.to-str()`，其中 `num-val` 明确声明为 `f64` 类型（第 592 行 `num-val f64 = 0.0`）。但 LLVM 代码生成时没有正确分派到 `f64.to-str` 方法，而是生成了无接收者的 `@to-str()` 调用。

根据标准库 `number.no`（第 534-537 行）的注释，编译器应该有 fallback 机制：当变量 LLVM 类型为 `double` 时自动分派到 `f64.to-str`。但此 fallback 在 `json-pool.stringify` 方法中不工作。

**错误信息**:
```
opt: error: use of undefined value '@to-str'
    call void @to-str()
              ^
```

**触发场景**:
- 只要编译标准库 `json.no` 模块（即使不调用 `stringify`），编译器会编译整个模块的所有方法
- 最小复现：`v = json.parse('{"a":1}')` 即可触发

**影响范围**:
- 所有使用 `json.parse` 的测试和源文件都无法编译
- `test-json.no`、`test-workspace.no`、`test-resolver.no`、`test-run.no`、`test-registry.no` 等

**状态**: 已在当前编译器版本（`2c171f5`）中修复。IR 正确生成 `call void @f64.to-str(double* %"num-val", %str-long* ...)`。

**当前残留问题**:
- `test-json.no` 仍有运行时 segfault（非编译错误），可能与 `json.parse` 返回 `%option` 类型的内存管理有关，需另行排查。

---

## 问题 12: `[]str.join(sep)` 方法调用与自定义 `join` 函数冲突

**严重程度**: 低（已修复）

**描述**:
当模块中定义了 `join = (parts []str, sep str) (out str)` 函数后，方法调用 `arr.join(sep)` 会被编译器解析为对自定义 `join` 函数的方法调用形式，导致参数数量不匹配。

**错误信息**:
```
Error: compilation error: function argument errors: line 358, column 19: function 'join' expects at least 2 argument(s), got 1
```

**解决方案**:
将 `arr.join(sep)` 改为函数调用 `join(arr, sep)`。

---

## 问题 13: 编译器 `adc35d8` 平台条件编译回退 — `O-APPEND` 未定义

**严重程度**: 高（阻塞所有引用 fs 模块的测试）

**描述**:
新编译器版本 `adc35d8`（2026-08-30）中，标准库 `fs.no` 的平台条件编译 `#{mac-arm64}` 没有正确工作，导致 `O-APPEND` 常量未定义。之前版本 `85cf832` 中此问题不存在。

**错误信息**:
```
opt: error: use of undefined value '%O-APPEND'
    %"O-APPEND.val" = load i64, i64* %"O-APPEND"
```

**触发场景**:
- 只要编译引用了 `fs` 模块的标准库代码（如 `fs.write-str`、`fs.open-write` 等），就会触发
- 影响所有测试文件

**状态**: 已在当前编译器版本（`2c171f5`）中修复。`test-utils.no`、`test-config.no`、`test-lockfile.no` 均能编译通过。

---

## 问题 14: 编译器 `adc35d8` 多值返回类型推断回退

**严重程度**: 高

**描述**:
新编译器版本 `adc35d8` 中，多值返回的函数调用存在类型推断回退。`semver.parse` 返回 `(ver semver-version, ok bool)`，但编译器生成 `codegen error: function "parse" has 2 output params but generateCallExpression returned void call`。之前版本 `85cf832` 中此问题不存在。

**错误信息**:
```
codegen error: function "parse" has 2 output params but generateCallExpression returned void call (not handled as expression)
opt: error: '%call.tmp' defined with type '%str-long' but expected 'i64'
```

**根本原因**:
`semver.to-string` 函数中 `s = v.major.to-str() - '.' - v.minor.to-str() - '.' - v.patch.to-str()` 使用 `-` 作为字符串拼接。当接收者是结构体字段（`v.major`，`DotExpression` 而非 `Identifier`）时，编译器的 `isStringExpr` 无法推断 `v.major.to-str()` 的返回类型为 `%str-long`，导致 `-` 运算符被误判为字节算术而非字符串拼接。

具体来说，`exprResultLLVMType` 处理 `CallExpression` 的 `DotExpression` 分支时，仅处理了 `dot.Receiver` 为 `Identifier` 的情况，未处理 `dot.Receiver` 为 `DotExpression`（结构体字段）、`IndexExpression`（数组元素）等非简单标识符接收者的情况。

**修复**:
在 `src/build/llvm/expr.go` 的 `exprResultLLVMType` 函数中，为 `CallExpression` 的 `DotExpression` 分支增加了非 `Identifier` 接收者的回退逻辑：递归调用 `exprResultLLVMType(dot.Receiver)` 解析接收者类型，再通过类型前缀候选列表查找方法返回类型。

**修复后状态**:
- `test-semver.no` 编译通过，大部分测试 PASS
- 残留问题：Test 15（numeric pre-release 比较）FAIL；`max-satisfying` 函数在 `*` 范围测试时运行时 abort trap（疑似未初始化结构体变量的堆释放问题）
- `codegen error: function "parse" has 2 output params...` 警告为误报，不影响编译

---

## 测试运行结果汇总（编译器版本 `2c171f5`，2026-08-30）

> **更新**: 问题 11（f64.to-str）、13（O-APPEND）已在当前编译器版本中修复。问题 14（结构体字段方法调用返回类型推断）已修复。

| 测试文件 | 状态 | 通过/失败 | 备注 |
|---------|------|----------|------|
| test-semver.no | ✅ 编译通过 / 部分运行失败 | 30 PASS / 2 FAIL | 问题 14 已修复；Test 15 FAIL + max-satisfying 运行时 abort（内存问题） |
| test-utils.no | ✅ 全部通过 | PASS | 问题 13 已修复 |
| test-config.no | ✅ 全部通过 | PASS | 问题 13 已修复 |
| test-lockfile.no | ✅ 编译通过 | - | 问题 13 已修复 |
| test-json.no | ❌ 运行时崩溃 | - | 问题 11 已修复（编译通过）；segfault 疑似 json.parse 返回 option 内存问题 |
| test-workspace.no | ❌ 解析错误 | - | workspace.no 使用 `_` 占位变量语法被解析为错误（非编译器 bug） |
| test-linker.no | ❌ LLVM 优化失败 | - | 需进一步排查 |
| test-tarball.no | ❌ LLVM 优化失败 | - | 需进一步排查 |
| test-resolver.no | ❌ 编译错误 | - | `starts-with`/`slice` 方法调用参数检查（疑似问题 12 类冲突） |
| test-run.no | ❌ LLVM 优化失败 | - | 需进一步排查 |
| test-publish.no | ❌ LLVM 优化失败 | - | 需进一步排查 |
| test-registry.no | ❌ 编译错误 | - | `starts-with`/`slice` 方法调用参数检查（疑似问题 12 类冲突） |
| test-installer.no | ❌ 编译错误 | - | `remove`/`starts-with`/`slice` 方法调用参数检查 |

## 已修复问题汇总

| 问题 | 修复方式 | 修复位置 |
|------|---------|--------|
| 11 (f64.to-str LLVM bug) | 编译器已在新版本中修复 | - |
| 13 (O-APPEND 平台条件编译) | 编译器已在新版本中修复 | - |
| 14 (结构体字段方法调用返回类型推断) | `exprResultLLVMType` 增加非 Identifier 接收者回退 | `src/build/llvm/expr.go` ~L1865 |

## 待解决问题

| 问题 | 严重程度 | 描述 |
|------|---------|------|
| 15 (新) | 中 | `max-satisfying` 函数运行时 abort trap：未初始化结构体变量 `best-v semver` 的堆释放问题 |
| 16 (新) | 中 | `test-json.no` 运行时 segfault：`json.parse` 返回 `%option` 类型的内存管理问题 |
| 17 (新) | 低 | `codegen error: function "parse" has 2 output params...` 警告为误报（不影响编译，但应消除噪音） |
