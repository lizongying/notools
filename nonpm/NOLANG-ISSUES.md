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

## 问题 3: `process.process-run` 函数不存在

**严重程度**: 低（已修复）

**描述**:
代码中使用了 `process.process-run` 函数，但标准库中不存在此函数。正确的函数名是 `process.process-system`。

**错误信息**:
```
Error: compilation error: unknown function: process.process-run
```

**当前 workaround**:
- 将所有 `process.process-run` 替换为 `process.process-system`
- 注意 `process.process-system` 不返回值，不能赋值给变量

---

## 问题 4: `_` 作为占位变量不被支持

**严重程度**: 低（已修复）

**描述**:
Nolang 不支持使用 `_` 作为占位变量（如 `_, ok = func()`）。

**错误信息**:
```
Error: expected variable name after ',', got UNDERSCORE
```

**当前 workaround**:
- 使用命名变量替代 `_`（如 `content, ok = func()`）

---

## 问题 5: `json.from-str` 等函数在自定义模块中不可用

**严重程度**: 中

**描述**:
当导入自定义的 `json` 模块（`# /nonpm/src/json`）后，`json.from-str`、`json.from-num`、`json.from-bool` 等标准库函数无法通过 `json.` 前缀访问，因为它们被自定义模块遮蔽。

**错误信息**:
```
Error: compilation error: unknown function 'json.from-str': module 'json' has no top-level function 'from-str'
```

**当前 workaround**:
- 在自定义 `json.no` 模块中添加 `new-str`、`new-num`、`new-bool` 包装函数

---

## 问题 6: `json.from-str`/`json.from-num`/`json.from-bool` 导致 LLVM option 类型错误

**严重程度**: 中

**描述**:
调用 `json.from-str(s)` 等函数创建 JSON 值时，LLVM 优化器遇到未初始化的 `%option` 类型。

**错误信息**:
```
error: expected value token
    store %option , %option* %val
                  ^
```

**触发场景**:
- `json.no` 中的 `new-str`、`new-num`、`new-bool` 函数
- 可能与 `json.parse` 函数返回 `?json-value`（option 类型）有关

---

## 问题 7: `fs.write` 传入空字符串变量导致 LLVM integer type 错误

**严重程度**: 中

**描述**:
当 `fs.write(fd, str_var, str_var.len)` 中的 `str_var` 可能为空时，LLVM 生成了 `i8* 0` 空指针。

**错误信息**:
```
error: integer constant must have integer type
    call i64 @write(i32 %trunc, i8* 0, i64 0)
```

**触发场景**:
- `lockfile.no` 的 `generate` 函数中 `fs.write(fd, cfg.node-linker, cfg.node-linker.len)` 当 `cfg.node-linker` 为空时

---

## 问题 8: `sha1.sha1-hex` 参数为空导致 LLVM 错误

**严重程度**: 低

**描述**:
`sha1.sha1-hex` 函数被调用时第一个参数为空。

**错误信息**:
```
call void @sha1.sha1-hex(, %str-long* %vso.tmp.NNN)
```

---

## 问题 9: 编译器 Go 运行时 panic

**严重程度**: 高

**描述**:
`test-resolver.no` 编译时触发了 Nolang 编译器（Go 编写）的运行时 panic（goroutine 崩溃）。

**错误信息**:
```
goroutine 1 [running]:
... runtime panic ...
```

---

## 问题 10: `use` 路径解析错误

**严重程度**: 低

**描述**:
`# /nonpm/src/run` 导入路径被解析为 `UNKNOWN(36)` token。

**错误信息**:
```
Error: compilation error: parser errors: expected identifier in use path, got UNKNOWN(36)
```

---

## 测试运行结果汇总

| 测试文件 | 状态 | 通过/失败 | 备注 |
|---------|------|----------|------|
| test-semver.no | ✅ 通过 | 全部通过 | |
| test-utils.no | ✅ 通过 | 27/0 | 跳过文件 I/O 和 arr-join |
| test-config.no | ✅ 通过 | 25/0 | 修复 save-project |
| test-lockfile.no | ⚠️ 编译通过但 0 测试执行 | 0/0 | 长字符串比较可能被 LLVM 优化掉 |
| test-json.no | ❌ 编译失败 | - | json.from-str 导致 option 类型错误 |
| test-workspace.no | ❌ 编译失败 | - | `_` 变量名问题 |
| test-linker.no | ❌ 编译失败 | - | LLVM trunc 错误 |
| test-tarball.no | ❌ 编译失败 | - | sha1.sha1-hex 参数为空 |
| test-resolver.no | ❌ 编译失败 | - | 编译器 Go panic |
| test-run.no | ❌ 编译失败 | - | 导入路径解析错误 |
| test-publish.no | ❌ 编译失败 | - | LLVM str-long 错误 |
| test-registry.no | ❌ 编译失败 | - | LLVM json-value 类型错误 |
