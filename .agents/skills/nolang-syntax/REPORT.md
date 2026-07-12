# Nolang Language Gaps — Unix Utilities Implementation Report

This report documents language gaps, compiler bugs, and standard-library limitations discovered while implementing a set of Unix utilities (`echo`, `cat`, `ls`, `rm`, `tree`, `mv`, `touch`) in Nolang. The utilities live under `/Users/lizongying/IdeaProjects/notools/src/`, with a dispatcher in `/Users/lizongying/IdeaProjects/notools/main.no`.

The initial approach used FFI (`#{c}` annotations) to call C library functions directly. Per the user's requirement, the approach was changed to **extend the Nolang standard library** instead of using FFI. The Nolang compiler itself was modified to add native built-in functions for directory iteration, file metadata, and timestamp updates.

---

## 1. Missing `opendir` / `readdir` / `closedir` — Added as Builtins

**Affected utilities:** `ls`, `rm` (recursive mode), `tree`

**Description**

The Nolang `fs` module had no directory iteration API. Listing directory entries — the core operation for `ls`, recursive `rm`, and `tree` — was impossible using only the standard library.

**Resolution: Compiler Extended**

The Nolang compiler was modified to add `opendir`, `readdir`, `closedir` as built-in functions. The three-layer builtin registration pattern was used:

1. **`decl.go`** — C function declarations (`declare i8* @opendir(i8*)` etc.)
2. **`call_stdlib.go`** — LLVM IR generation for each builtin call, including:
   - `nullTerminateStrArg` — converts Nolang's `%str-long` (non-null-terminated `{len, data}`) to a null-terminated C string
   - `malloc` + `strcpy` to preserve `readdir` entries (readdir returns static memory that is overwritten on each call)
   - Proper `struct dirent` field access (`d_name` at offset 21 on macOS arm64, NOT 12)
3. **`os.go`** — `BuiltinMethod` registration

A new standard library function was exposed:

```nolang
fs.list-dir(path str) (entries []str)
```

**Platform-specific details discovered:**

- macOS arm64 `struct stat`: `sizeof=144`, `st_mode` at offset **4**, `st_size` at offset **96**
- macOS arm64 `struct dirent`: `sizeof=1048`, `d_name` at offset **21** (layout: `d_ino(8) + d_seekoff(8) + d_reclen(2) + d_namlen(2) + d_type(1) = 21`)
- `readdir` returns a pointer to static memory — each call overwrites the previous entry's data. Must `malloc` + `strcpy` to preserve names.
- Nolang `%str-long` strings are NOT null-terminated. C functions like `opendir`/`stat` require null-terminated strings.

---

## 2. Missing Detailed `stat` (Permissions, mtime, Owner)

**Affected utilities:** `ls -l` (only shows type and size, not permissions / mtime / owner)

**Description**

The standard library only exposed `fs.stat-size(path) (size i64)`. There was no way to read file mode, modification time, owner uid, or group gid. As a result, `ls -l` prints a synthetic format of `type size name`:

```nolang
type = '-'
fs.is-dir(full) -> type = 'd'
size = fs.stat-size(full)
size-str = sprintf('%8d', size)
print(type - ' ' - size-str - ' ' - name)
```

**Resolution: Partially fixed**

`fs.stat-size` and `fs.is-dir` were added as compiler builtins using `stat()` syscall with correct macOS arm64 offsets. Full permissions/mtime/owner display remains unimplemented.

**Suggested API**

```nolang
fs.stat(path str) (info FileInfo)

FileInfo {
    mode       i32
    size       i64
    mtime      i64
    uid        i32
    gid        i32
    is-dir     bool
    is-file    bool
    is-symlink bool
}
```

---

## 3. Missing `utimensat` / `utime` — Added as Builtin

**Affected utilities:** `touch`

**Description**

The standard library had no function to update file timestamps. `touch` could not fulfill its primary contract without FFI.

**Resolution: Compiler Extended**

`utimensat` was added as a compiler builtin. The `fs.touch(path) (ok bool)` function passes `times = NULL` to set both `atime` and `mtime` to the current time.

```nolang
// In compiler: utimensat(AT_FDCWD, nullTermStr(path), NULL, 0)
// Returns: icmp eq i32 %ret, 0 → zext i1 to i64 (0=success→true)
```

---

## 4. `!` (NOT) Operator Was Unimplemented (FIXED)

**Affected utilities:** `ls` (uses `!hidden`, `!long-format`, `!a.starts-with('-')`)

**Description**

The `!` (logical NOT) operator was completely unimplemented in the compiler. The `PrefixExpression` handler in `expr.go` only handled `-` (negation); `!` just returned the operand unchanged, meaning `!true` returned `true` and `!false` returned `false`.

**Resolution: Fixed in compiler**

Implemented `!` operator in `/Users/lizongying/IdeaProjects/no/src/build/llvm/expr.go`:

```go
case "!":
    operand := g.generateExprWithSB(sb, e.Right)
    // icmp eq i64 %operand, 0  →  i1 (true if operand was 0/false)
    // zext i1 → i64  (Nolang stores bools as i64)
```

Also updated `intExprLLVMType` to return `"i64"` for `!` expressions, preventing double-zext errors.

---

## 5. `mkdir` / `remove` / `rename` Inverted Boolean Semantics (FIXED)

**Affected utilities:** `mv` (rename), `rm` (remove), `touch` (implicit)

**Description**

C functions `mkdir`, `unlink`/`remove`, `rename` return **0 on success**. Nolang treats 0 as `false`. The builtins used `RetExt: &i64Type` which just zero-extends the i32 return to i64 — so success (0) became `false` and failure (nonzero) became `true`. This was inverted: `mv` reported errors on success.

**Resolution: Fixed in compiler**

Changed `mkdir`, `remove`, `rename` from `RetExt: &i64Type` to `CmpRet: true` in the builtin definitions. `CmpRet` does `icmp eq i32 %ret, 0` → `zext i1 to i64`, correctly mapping 0 (success) → `true`.

---

## 6. Systemic `i1` vs `i64` Type Mismatch for Booleans (FIXED)

**Affected utilities:** All utilities using boolean return values from functions

**Description**

Nolang uses `i1` for booleans in function signatures (output parameters use `i1*`) but `i64` for boolean variables. This caused LLVM type errors at every boundary:

- `'%call.zext.N defined with type i64 but expected i1'` — when storing a function call result (already zext'd to i64) into a variable typed as `i1`
- `'%call.zext.N defined with type i1 but expected i64'` — double-zext when both the call handler and the variable type conversion tried to zext

The root cause: `varLLVMType` and `intExprLLVMType` returned `i1` (from `funcResultLLVMType`) without converting to `i64` for variables/expressions that store boolean results.

**Resolution: Fixed in compiler**

- **`stmt.go`** — 4 locations in `varLLVMType` now convert `i1` → `i64`:
  ```go
  retType := ts[0]
  if retType == "i1" {
      retType = "i64"
  }
  return retType
  ```
- **`expr.go`** — 3 locations in `intExprLLVMType` apply the same `i1` → `i64` conversion.

---

## 7. `resolveModuleConstants` Replaced Local Variables (FIXED)

**Affected utilities:** `ls` (via `str.contains`)

**Description**

This was the most subtle bug. `ls -l` showed hidden files because `str.contains('a')` returned `true` for the string `'-l'`.

**Root cause traced through multiple layers:**

1. `str.contains` uses a local variable `pos`:
   ```nolang
   str.contains = (target str) (yes bool) {
       yes = false
       pos = .index(target)
       pos >= 0 -> yes = true
   }
   ```
2. `base32-decode` in `base32.no` also uses `pos = 0` inside its function body (line 123).
3. A parser bug caused function-body `LetStatement` nodes (like `pos = 0`) to leak into `modProg.Statements`, where they were treated as module-level constants.
4. `resolveModuleConstants` in `transpiler.go` replaced ALL `Identifier("pos")` nodes — including the local variable `pos` inside `str.contains` — with `IntegerLiteral(0)`.
5. The generated IR showed `icmp sge i64 0, 0` (both operands 0) instead of `icmp sge i64 %pos, 0`.

**Resolution: Fixed in compiler**

Modified `resolveModuleConstants`, `resolveModuleConstantsInStmt`, and `resolveModuleConstantsInExpr` in `/Users/lizongying/IdeaProjects/no/src/build/transpiler.go` to track local variables via a new `collectLocalNames` function. Local variables now shadow module constants during constant propagation.

```go
func resolveModuleConstantsInExpr(expr, constants, locals) {
    case *parser.Identifier:
        if locals != nil && locals[e.Value] {
            return e  // Skip local variables
        }
        // ... constant lookup ...
}
```

**Note:** The underlying parser bug (function-body statements leaking to module level) is NOT fixed. The `resolveModuleConstants` fix works around it by checking scope.

---

## 8. `vec.push` Was a Stub (FIXED)

**Affected utilities:** `ls`, `rm`, `tree` (all use `entries.push(name)`)

**Description**

The `[]t.push` method in `vec.no` was incomplete — it didn't store values or update the length.

**Resolution: Fixed in standard library**

Updated `vec.no` to use `.len = n + 1` then `.[n] = val`. The bounds check (`nolang.bounds_check(idx, len)`) requires `.len` to be updated BEFORE writing to `.[n]`.

---

## 9. `fs.get-line()` Type Mismatch Compiler Bug

**Affected utilities:** `cat` (stdin passthrough mode)

**Description**

`fs.get-line()` returns `?str`, but the internal string variable is inferred as `ptr` where it should be `i64`, causing:

```
'%getline.str.12' defined with type 'ptr' but expected 'i64'
```

**Resolution:** Not fixed — pre-existing compiler bug. Worked around by testing `cat` with file arguments only.

---

## 10. `->` Else Branch Executes Both Arms

**Affected utilities:** All utilities using the `cond -> stmt1 \n -> stmt2` pattern

**Description**

In Nolang, the `->` else syntax (`cond -> stmt1 \n -> stmt2`) executes BOTH arms when `cond` is true. This is different from a traditional if-else.

**Workaround:** Use `!cond -> stmt2` as a separate statement instead of `-> stmt2` as an else branch. This works correctly because `!` is now properly implemented (see gap #4).

---

## Additional Ergonomic Issues

### A. Verbose Argument Parsing

Every utility re-implements flag-parsing boilerplate. The `args` module has `has-flag` and `get-option`, but they don't handle combined short flags (`-rf`), value flags (`-L 2`), or positional/flag interleaving.

**Suggestion:** Add a higher-level flag parser:
```nolang
flags = args.parse(spec []ArgSpec) (positional []str, opts map)
```

### B. Inconsistent Path Joining

`mv.no` uses the `path` struct, while `ls.no`, `rm.no`, and `tree.no` use raw string concatenation (`dir - '/' - name`). The string form is brittle (no trailing-slash handling, no normalization).

**Suggestion:** Add free functions in `path` module:
```nolang
path.join(base str, child str) (out str)
path.base(p str) (out str)
```

### C. No Error Details from `fs` Operations

`fs.open(path)` returns `?file` — `nil` on failure with no error reason. `cat.no` hardcodes error messages regardless of the actual failure cause.

**Suggestion:** Have `fs.open` return an error variant with errno-derived messages.

### D. No `map` / `filter` for Slices

`tree.no` manually filters directory entries into a new slice. A `filter` method on `[]t` would simplify this.

### E. Manual `.` / `..` Filtering Everywhere

Every consumer of `fs.list-dir` repeats `name == '.' || name == '..'` filtering.

**Suggestion:** When adding `fs.list-dir`, omit `.` and `..` by default, or provide an explicit parameter.

---

## Summary Table

| # | Gap | Affected Utilities | Status |
| --- | --- | --- | --- |
| 1 | No directory iteration | ls, rm, tree | **Fixed** — added as compiler builtins (`opendir`/`readdir`/`closedir`) |
| 2 | No detailed `stat` | ls -l | Partially fixed (`stat-size`, `is-dir`); full metadata not implemented |
| 3 | No `utimensat` | touch | **Fixed** — added as compiler builtin |
| 4 | `!` operator unimplemented | ls | **Fixed** — implemented in `expr.go` |
| 5 | Inverted bool semantics for C functions | mv, rm | **Fixed** — changed to `CmpRet` |
| 6 | `i1` vs `i64` type mismatch | all | **Fixed** — 7 locations in `stmt.go` + `expr.go` |
| 7 | `resolveModuleConstants` replaces locals | ls (via str.contains) | **Fixed** — added local variable tracking |
| 8 | `vec.push` was a stub | ls, rm, tree | **Fixed** — updated `vec.no` |
| 9 | `fs.get-line()` type mismatch | cat (stdin) | Not fixed — pre-existing |
| 10 | `->` else branch bug | all | Worked around with `!cond` pattern |
| A | Verbose argument parsing | all | Worked around with manual loops |
| B | Inconsistent path joining | mv vs ls/rm/tree | Mixed approaches |
| C | No error details from `fs` | cat, mv | Hardcoded messages |
| D | No `map`/`filter` for slices | tree | Manual iteration |
| E | `.`/`..` filtering repeated | ls, rm, tree | Consequence of API design |

---

## Compiler Files Modified

All modifications were made to the Nolang compiler at `/Users/lizongying/IdeaProjects/no/`:

- **`src/build/llvm/expr.go`** — `!` operator implementation; `i1`→`i64` conversion in `intExprLLVMType` (3 locations)
- **`src/build/llvm/stmt.go`** — `i1`→`i64` conversion in `varLLVMType` (4 locations)
- **`src/build/llvm/decl.go`** — C function declarations for `opendir`, `readdir`, `closedir`, `utimensat`, `stat`, `strcpy`, `malloc`
- **`src/build/llvm/call_stdlib.go`** — LLVM IR generation for all new builtins
- **`src/build/llvm/os.go`** — `BuiltinMethod` registration for new builtins
- **`src/build/transpiler.go`** — `resolveModuleConstants` local variable tracking fix
- **`src/std/vec.no`** — `push` method implementation

## Related Files

- Dispatcher: `/Users/lizongying/IdeaProjects/notools/main.no`
- Utilities: `/Users/lizongying/IdeaProjects/notools/src/{echo,cat,ls,rm,tree,mv,touch}.no`
