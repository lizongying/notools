# Nolang 编译器问题记录

在 nonpm 测试过程中遇到的 Nolang 编译器问题，供后续处理。

## 问题 1: LLVM IR str-long vs vec 类型不匹配

**严重程度**: 高（影响大部分模块）

**描述**: 
当 `str` 类型变量（特别是长字符串 >127 字节，即 `str-long`）被传递给某些标准库函数（如 `json.stringify`, `fs.read-file` 返回值赋值给变量后再传递）时，LLVM 优化器会将 `str-long` 类型与 `vec` 类型混淆，导致编译错误。

**错误信息**:
```
error: '%var.val.NNN' defined with type '%str-long = type { i64, i64, i64 }' but expected '%vec = type { i64, i64, i64 }'
```

**触发场景**:
1. `json.stringify(val, buf)` — 当 `buf` 是 `str` 类型（通过 `with-len` 创建）时
2. `json.stringify-pretty(val, buf, indent)` — 同上
3. `content = fs.read-file(path)` 然后 `content == other_str` — 字符串比较
4. `content = fs.read-file(path)` 然后 `cfg.raw = content` — 赋值给结构体字段
5. 字符串拼接 `content = content - '...' - var` 后传给 `utils.write-file(path, content)`
6. 长字符串字面量赋值给变量后传给函数参数

**当前 workaround**:
- 避免将 `fs.read-file` 返回值存储在变量中再传递给其他函数
- 使用 `fs.open-write` + `fs.write` 替代字符串拼接 + `utils.write-file`
- 跳过涉及文件 I/O 的测试

**受影响的源文件**:
- `src/utils.no`: `write-json-file`, `read-json-file`
- `src/config.no`: `load-global`, `load-project`, `save-project`
- `src/lockfile.no`: `generate`, `check-valid`, `read-lockfile`
- `src/json.no`: `stringify`, `stringify-pretty`, `parse-file`, `write-json`
- `src/workspace.no`, `src/publish.no`, `src/registry.no`, `src/tarball.no` 等

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

**当前 workaround**:
- 无（需要编译器修复 fallback 机制）

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

## 测试运行结果汇总

| 测试文件 | 状态 | 通过/失败 | 备注 |
|---------|------|----------|------|
| test-semver.no | ✅ 通过 | 全部通过 | |
| test-utils.no | ✅ 通过 | 27/0 | 跳过文件 I/O |
| test-config.no | ✅ 通过 | 25/0 | 修复 save-project |
| test-lockfile.no | ⚠️ 编译通过但 0 测试执行 | 0/0 | 长字符串比较可能被 LLVM 优化掉 |
| test-json.no | ❌ 编译失败 | - | 问题 11: f64.to-str() LLVM bug |
| test-workspace.no | ❌ 编译失败 | - | 问题 11: 导入 pj.no 间接编译 json 模块 |
| test-linker.no | ❌ 编译失败 | - | 问题 11: 导入 pj.no 间接编译 json 模块 |
| test-tarball.no | ❌ 未验证 | - | 待验证 |
| test-resolver.no | ❌ 编译失败 | - | 问题 11: 导入 pj.no 间接编译 json 模块 |
| test-run.no | ❌ 编译失败 | - | 问题 11: 导入 pj.no 间接编译 json 模块 |
| test-publish.no | ❌ 未验证 | - | 待验证 |
| test-registry.no | ❌ 编译失败 | - | 问题 11: 导入 pj.no 间接编译 json 模块 |
