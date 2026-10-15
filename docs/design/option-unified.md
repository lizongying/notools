# notools 侧方案：算术与索引统一返回 option（实测 + 迁移）

> 状态：**测量完成，待执行**（2026-10-13）  
> 上游方案：`~/IdeaProjects/no/docs/design/option-unified.md`（编译器侧设计，`no` 仓库）  
> 本文件是**下游语料侧**的对应物：只讲 notools 工作区受影响的实测、修法与批次，不重复编译器侧设计。  
> 语料：`~/IdeaProjects/notools` 的 7 个子项目（`noagent` / `nogit` / `noimg` / `nojq` / `nonpm` / `notools` / `nouv`）  
> 基线：`no` @ `40aa9caa`（初测 `b805ed06`）；参考二进制 `/tmp/no_opt`（`v0.4.5-dirty`，带 `StdSigKey`）

---

## 0. 结论速览

| 项                       | 数值                                                                                                       |
| ----------------------- | -------------------------------------------------------------------------------------------------------- |
| 扫描档数                    | **578**（排除 `node_modules` / `tmp` / `dist` / `docs`）                                                     |
| **唯一 ERROR 点**          | **424**                                                                                                  |
| ├ option 相关             | **301**（`15w45dqk` 155、`fxxoptarg` 90、`6fgg3htw` 24、`fe0a5wt2` 14、`optunuse` 11、`oarg2` 4、`stdargtyp` 3） |
| ├ 非 option（跨模组未限定呼叫）    | 94（`4bek3xc6`，全部在 `notools`）                                                                             |
| └ 待逐点诊断（format 字串未定义变量） | 29（`mzwb28br`，全部在 `nouv`）                                                                                |
| 有错的档                    | 123                                                                                                      |
| 干净子项目                   | 无（7 个都有；`nouv` 的 55 点全是 option 相关）                                                                       |

**一句话**：这不是「7138 个已标注站点全部重写」，而是 **424 个错误点的定点修复**，其中 301 点的主修法是机械的（§3）。

上游方案 §2.2 推算的「std 4564 个已标注站点全部需要补消费」在 notools 上**没有发生** —— 原因见 §1.2 第 1、2 条。

---

## 1. 规则现状（实测）

### 1.1 判定矩阵

全部用探针逐个测出（探针见 §1.4）：

| 表达式             | 注解                 | 绑定形态                  | 结果类型      | 实测                                             |
| --------------- | ------------------ | --------------------- | --------- | ---------------------------------------------- |
| 算术 `a + b`      | 无                  | 新变量                   | `?T`      | HINT（`ovfhndld` / `ovf-int-default`），不再是 ERROR |
| 算术 `a + b`      | `#{overflow=wrap}` | 新变量                   | **`?T`**  | D1 已生效                                         |
| 算术 `a + b`      | `#{overflow=wrap}` | 重绑定既有 plain **局部**变量     | plain     | 不报错（**仅限局部**；**全域**重绑仍是 `?T`）                 |
| 算术 `a + b`      | `#{overflow=wrap}` | 显式 plain 型别 `z i64 =` | **ERROR** | `15w45dqk`（D1 已收紧；2026-10-14 用户定案 `k i64 = i + 1 #{overflow=wrap}` 是错的） |
| 索引 `arr[i]`     | 无                  | 新变量                   | `?T`      | `15w45dqk`                                     |
| 索引 `arr[i]`     | `#{index-out=…}`   | 新变量                   | **plain** | 注解**仍然解包**                                     |
| 索引 `arr[i]`     | 无                  | 显式 plain 型别 `v i64 =` | plain     | 不报错                                            |
| `str` 索引 `s[i]` | —                  | 新变量                   | `?char`   | D6 已生效                                         |
| 呼叫 `f()` 回 `?T` | —                  | 新变量                   | `?T`      | 显式 plain 型别也压不平（见 §3.5）                        |
| 呼叫 `f()` 回 `?T` | —                  | 赋给 `?T` 结果参数          | `?T`      | 报 `optunuse`（疑似误报，§1.2 第 3 条）                  |

### 1.2 与上游方案 / 现有文档的四处出入

1. **D1 只落地一半。** 算术注解**不再解包**（矩阵第 2 行），但索引注解**仍然解包**（第 6 行）。  
   上游方案 D1 说两者都不解包；`docs/docs/lang/syntax.md` L1618 也写「`#{index-out=…}` 只决定失败时怎么取值，不解包」——实测与两者都不符。  
   ⇒ **不要**按「7138 个已标注站点全部变 `?T`」规划迁移量。
2. **迁移量被高估。** 方案 §2.2 推算 std 的 4564 个已标注站点全部需要补消费；notools 实测表明**只有「新变量绑定」受影响**：  
   重绑定既有 plain 变量、显式 plain 型别都不受影响。notools 的 6298 个 `#{overflow=wrap}` 里绝大多数是 `i = i + 1` 这种重绑定，因此没炸。
3. **`optunuse` 有可疑误报。** `v = h()`（`h()` 回 `?T`，`v` 是 `?T` out-param）报 `optunuse`；而 `v = a + b`（同样 `v ?T`）不报。  
   同一个「把 option 交给 `?T` 结果参数」的动作，两条路径结论不一致。  
   ⇒ **先向编译器侧确认**，再决定这 11 个点是改代码还是改编译器（`noagent` 的 2 点就是这个形状）。
4. **HINT 建议的语法不总能解析。** 诊断建议 `x = expr: { ok -> it, -> 0 }`，实测：
   - 换行分臂 + 空臂（`docs/docs/lang/syntax.md` L1620 的写法）**可用**；
   - **逗号分臂**（`{ ok -> it, -> 0 }`）**解析失败**：`expected variable name after ',', got RARROW(->)`；
   - 该形式对**呼叫结果无效**：`d = h(): { ok -> it \n -> }` 仍报 `15w45dqk`。

### 1.3 方法学（必须遵守）

- 🔴 **不能用 `no vet <目录>` 当判据。** 目录模式有**假阳性**：实测 `no vet nouv` 报 72 个 ERROR，而逐档 vet 后 `nouv` 的真实错误是 55 点、且**位置完全不同**；`notools/src/ls.no` 目录模式被点名，单档 vet 干净。  
  目录模式还会把同一条错误在**每个 import 者**下重复上报（历史记录：原始计数约 10× 虚高）。
- 🔴 **逐档 `no vet <file>` 才是权威**，但仍有两点局限：
  - 有些错误只在**测试入口**（`*/tests/test-*.no`）下才暴露，且位置指向被引用的模块（`nouv` 的 29 个 `mzwb28br` 就是这样：报在 `nouv/src/dependency.no:266:15`，但只有 vet `nouv/tests/test-*.no` 时才出现）；
  - 跨模块错误的**位置**可能不可靠（报在函数定义行或无关语句上）。⇒ 修复时以**报错文本**为准，位置只作线索。
- 🔴 **自带参考二进制。** 平行 session 会重建 `bin/no`。本次就撞上：13:46 `bin/no` 被换成不带 `StdSigKey` 的 build，`no vet` 直接硬失败（`[no] ERROR: 標準庫簽名 key 未注入`），第一轮 sweep 因此被污染（`nouv` 被误判为 0 错误）。  
  自带二进制的建置方式见 §7.1。
- 本文件的数字来自**用 `/tmp/no_opt` 对 578 档逐档 vet**（第二轮 sweep），原始输出在 `/tmp/opt-perfile2/`。

### 1.4 探针

探针在 `~/IdeaProjects/no/tmp/zz-optprobe/*.no`（`no` 仓库的 `tmp/`，gitignored）。关键几个：

| 探针                | 内容                                                         | 结论                           |
| ----------------- | ---------------------------------------------------------- | ---------------------------- |
| `v.no`            | `#{overflow=wrap}` ⏎ `z = a + b` ⏎ `w = z`（`a`/`b` 是参数）    | **ERROR 15w45dqk** ⇒ 算术注解不解包 |
| `z1.no`           | 同上但 `z` 是既有 plain 变量（重绑定）                                  | 无错 ⇒ 重绑定不受影响                 |
| `m.no`            | `#{overflow=wrap}` ⏎ `r i64 = a + b`                       | 无错 ⇒ 显式型别可压平                 |
| `w.no`            | `#{index-out=zero}` ⏎ `v = arr[i]` ⏎ `out = v`             | 无错 ⇒ 索引注解**仍**解包             |
| `y.no`            | 无注解 ⏎ `v = arr[i]` ⏎ `out = v`                             | ERROR ⇒ 索引无注解时是 `?T`         |
| `x.no`            | `v i64 = arr[i]`                                           | 无错                           |
| `p.no`            | `h = () (r ?str) { r = 'x' }` ⏎ `f = (v ?str) { v = h() }` | ERROR `optunuse` ⇒ 疑似误报      |
| `aa.no`           | `gd-opt: { ok -> { gd = it } … }`                          | 无错 ⇒ `it` 修法可用               |
| `bb.no`           | `x = x-opt: { ⏎ ok -> it ⏎ -> ⏎ }`                         | 无错（仅空臂 WARNING）⇒ 文档式可用       |
| `cc.no` / `dd.no` | `d = h(): { … }`（呼叫结果）                                     | ERROR ⇒ 该形式对呼叫结果无效           |
| `ee.no`           | `o = h()` ⏎ `o: { ok -> d = it \n -> d = 0 }`              | 无错 ⇒ 陈述式 match 可用            |
| `ff.no`           | `d i64 = h()`                                              | ERROR ⇒ 显式型别压不平呼叫结果          |
| `gg.no`           | `bj byte = buf[j]` ⏎ `g(bj)`                               | 无错 ⇒ 引数先绑定再传可用               |

---

## 2. 语料与实测数据

### 2.1 语料规模（2026-10-13）

| 子项目     | 档数      | 行数          | `#{overflow=wrap}` | `#{index-out=…}` | `?=`  | `_ =` | `.byte(` |
| ------- | ------- | ----------- | ------------------ | ---------------- | ----- | ----- | -------- |
| noagent | 23      | 4 784       | 183                | 32               | 0     | 0     | 3        |
| nogit   | 94      | 19 742      | 817                | 12               | 0     | 0     | 66       |
| noimg   | 36      | 28 602      | 2 369              | 397              | 0     | 0     | 0        |
| nojq    | 21      | 9 018       | 251                | 60               | 0     | 1     | 52       |
| nonpm   | 152     | 16 123      | 542                | 17               | 1     | 0     | 4        |
| notools | 203     | 33 519      | 1 336              | 208              | 0     | 0     | 18       |
| nouv    | 49      | 24 967      | 800                | 114              | 0     | 0     | 6        |
| **合计**  | **578** | **136 755** | **6 298**          | **840**          | **1** | **1** | **149**  |

⚠️ notools 的 `#{overflow}` **全部是 `wrap`**（无 `clamp0`/`min`/`max`/`saturate`）；`#{index-out}` 以 `zero` 为主，另有少量 `0` / `1` / `2` / `''` / `prule{}`，以及 153 处组合写法 `#{index-out=zero,overflow=wrap}`。  
⚠️ `?=` 与 `_ =` 几乎为 0 ⇒ 语料**从未**使用「上抛」与「显式丢弃」这两条消费路径，迁移时不宜大面积引入（会改变错误传播语义）。

### 2.2 逐档 vet 结果（权威）

| 子项目     | 唯一 ERROR | 有错档数    | 错误码分布                                                                                 |
| ------- | -------- | ------- | ------------------------------------------------------------------------------------- |
| noagent | 2        | 2       | `optunuse`×1, `fxxoptarg`×1                                                           |
| nogit   | 100      | 68      | `15w45dqk`×94, `optunuse`×3, `fxxoptarg`×3                                            |
| noimg   | 80       | 6       | `fxxoptarg`×49, `15w45dqk`×22, `optunuse`×7, `fe0a5wt2`×2                             |
| nojq    | 6        | 2       | `15w45dqk`×6                                                                          |
| nonpm   | 2        | 2       | `15w45dqk`×2                                                                          |
| notools | 179      | 32      | `4bek3xc6`×94, `fxxoptarg`×33, `6fgg3htw`×23, `15w45dqk`×22, `oarg2`×4, `stdargtyp`×3 |
| nouv    | 55       | 13      | `mzwb28br`×29, `fe0a5wt2`×12, `15w45dqk`×9, `fxxoptarg`×4, `6fgg3htw`×1               |
| **合计**  | **424**  | **123** |                                                                                       |

### 2.3 错误码总览

| 错误码         | 数量  | 分布                                                           | 类别                    | 修法   |
| ----------- | --- | ------------------------------------------------------------ | --------------------- | ---- |
| `15w45dqk`  | 155 | nogit 94 / noimg 22 / notools 22 / nouv 9 / nojq 6 / nonpm 2 | option 赋给 plain       | §3.1 |
| `4bek3xc6`  | 94  | notools 94                                                   | **非 option**：跨模组未限定呼叫 | §3.6 |
| `fxxoptarg` | 90  | noimg 49 / notools 33 / nouv 4 / nogit 3 / noagent 1         | bare option 当引数       | §3.2 |
| `mzwb28br`  | 29  | nouv 29                                                      | 待诊断：format 字串未定义变量    | §3.7 |
| `6fgg3htw`  | 24  | notools 23 / nouv 1                                          | 引数型别不符（型别推断连锁）        | §3.5 |
| `fe0a5wt2`  | 14  | nouv 12 / noimg 2                                            | option 参与比较           | §3.4 |
| `optunuse`  | 11  | noimg 7 / nogit 3 / noagent 1                                | option 绑定后从未消费        | §3.3 |
| `oarg2`     | 4   | notools 4                                                    | 引数个数不符                | §3.5 |
| `stdargtyp` | 3   | notools 3                                                    | 引数型别不符                | §3.5 |

### 2.4 出错的档（分批依据）

| 子项目     | 档数 | 主要档（点）                                                                                                                                                                                      |
| ------- | -- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| noagent | 2  | `src/utils.no`(1)、`src/httpclient.no`(1)                                                                                                                                                    |
| nogit   | 68 | `tests/test.no`(13)、`src/pack.no`(9)、`main.no`(3)、`tests/test-revwalk-comprehensive.no`(3)、`tests/test-object-comprehensive.no`(3)…（`tests/` 下 60+ 档，多为同一形状）                                |
| noimg   | 6  | `src/vp8.no`(36)、`src/jpeg.no`(17)、`src/webp.no`(15)、`src/gif.no`(10)、`src/image.no`(1)、`main.no`(1)                                                                                        |
| nojq    | 2  | `src/dec.no`(4)、`src/number.no`(2)                                                                                                                                                          |
| nonpm   | 2  | `tests/test-resolve-debug.no`(1)、`tests/test-resolve-debug2.no`(1)                                                                                                                          |
| notools | 32 | `src/cat.no`(21)、`src/join.no`(18)、`src/awk.no`(17)、`src/sha384x.no`(11)、`src/sha512x.no`(11)、`src/sha256x.no`(10)、`src/md5x.no`(10)、`src/xxd.no`(10)、`src/sha1x.no`(9)、`src/stdbuf.no`(9)… |
| nouv    | 13 | `src/pep508.no`(26)、`src/jsonx.no`(6)、`src/utils.no`(4)、`src/dependency.no`(4)、`src/sdist.no`(3)…                                                                                           |

> `notools` 的 94 个 `4bek3xc6` 集中在 `sha1x/sha256x/sha384x/sha512x/md5x/xxd/stdbuf/cat/echo/ls/xargs/...`，是**跨模组限定名**问题，与 option 无关，见 §3.6。

---

## 3. 修法 recipe

> 所有 recipe 都用探针在 `/tmp/no_opt` 上验证过（§1.4）。**优先选不改变语义的写法**。

### 3.1 `15w45dqk`（155 点，占 37%）—— option 赋给 plain

**形状 A（约 86 点，`nogit/tests/*` 几乎全是这个）：`ok ->` 臂内把被匹配的 option 变量赋给 plain 变量。**

```no
; ✗ before
gd-opt: {
    ok -> {
        gd = gd-opt          ; ← ERROR: cannot assign ?str value to str variable 'gd'
        init-ok = true
    }
    nil || err -> { }
}

; ✓ after：用臂内的 it（= 解包后的值）
gd-opt: {
    ok -> {
        gd = it
        init-ok = true
    }
    nil || err -> { }
}
```

**形状 B：算术/索引结果赋给 plain 变量。** 只接受**陈述式 match（两段式解包）**这一种改法：

```no
; ✗ before
#{overflow=wrap}
z = a + b
w = z

; ✓ after（陈述式 match；失败分支显式）—— 唯一合法改法
#{overflow=wrap}
z-opt = a + b
z = 0
z-opt: {
    ok -> z = it
    -> z = 0
}
w = z
```

> 🔴 **`z i64 = a + b`（显式 plain 型别压平算术）已不再合法。** D1 落地后编译器对
> 「显式 plain 型别 + 算术」直接报 `15w45dqk`（`cannot assign ?i64 value to i64 variable`）。
> 用户 2026-10-14 定案：`k = i + 1 #{overflow=wrap}` 必须是 option；`k i64 = i + 1
> #{overflow=wrap}` 是**错的**。**不要再使用这条 recipe。**
>
> 🔴 **同行内联写法 `w = z: { ok -> it` ⏎ `-> 0 }` 实测会坏**：整段被推成
> `err | nil` 而不是 `T`，下游当引数用时报 `6fgg3htw` / `stdargtyp`
> （`expected 'i64', got 'err | nil'`）。**一律用上面的多行陈述式 match。**
>
> ⚠️ **窄型别（i8/i16/i32）**：算术恒把结果拓宽成 `?i64`，`ok -> it` 拿到的是 i64，
> 赋回 i8 会报 narrowing（`cannot assign i64 value to i8 variable`）。此时改用
> 「先声明窄型别 plain、再注解式重绑」——回绕语义不变，也不触发 `arm-should`：
>
> ```no
> z i8 = 0
> #{overflow=wrap}
> z = a + b
> ```

**形状 C（`nouv` 出现）：方向相反的报错** `cannot assign str value to ?i64 variable 'x'` —— 说明**目标变量**被推成了 `?T`，而 RHS 是 plain。  
⇒ 检查该变量的声明/首次绑定，把目标改回 plain（或给显式型别）。

**形状 D：`?char` 来源。** `nouv/src/pep508.no:331` 是 `str-char = s[i]`（`str` 索引，D6）⇒ `str-char` 收到 `?char`。  
改法：`str-char i64 = s[i]`（显式型别）或改用 `s.byte(i)`（若语义上要的是字节）。

### 3.2 `fxxoptarg`（90 点）—— bare option 当引数

```no
; ✗ before（noagent/src/httpclient.no:225）
d = hexval(b[j])            ; b[j] : ?byte

; ✓ after：先绑成 plain，再传
bj byte = b[j]
d = hexval(bj)
```

⚠️ **引数内联 match 不解析**：`d = hexval(b[j]: { ok -> it \n -> 0 })` 会报 `expected expression, got nil instead` / `expected variable name after ',', got RARROW(->)`。  
⚠️ 若 option 来自**算术**，同样先落成显式型别变量再传。  
⚠️ **先判断语义**：`b[j]` 越界时原意是「取零值继续」还是「应当报错」？前者用显式 plain 型别 / `#{index-out=zero}`，后者才用 `?=` 上抛（会改变错误传播，语料里没有先例，慎用）。

### 3.3 `optunuse`（11 点）—— 绑定后从未消费

```no
; ✗ before（nogit/src/object.no:900）—— 结果确实要丢弃
_w-opt = zlib.zlib-decompress(warmup-data)

; ✓ after
_ = zlib.zlib-decompress(warmup-data)
```

⚠️ **先排除 §1.2 第 3 条的疑似误报**：`noagent/src/utils.no:196`（`read-line = (line ?str) { line = io.read-line() }`）是「把 option 交给 `?T` 结果参数」，`nouv`/`noimg` 也有同形状。这 11 点里有多少是真问题、有多少是编译器误报，需要先跟编译器侧对齐（探针 `p.no` 可复现）。

### 3.4 `fe0a5wt2`（14 点）—— option 参与比较

```no
; ✗ before（noimg/src/jpeg.no:762-764）
#{overflow=wrap}
np = pos + 1
np < n -> { … }             ; ← ERROR: cannot compare option value 'np' (?i64) with 'n'

; ✓ after（两段式解包；显式 plain 型别 `np i64 = pos + 1` 已不合法）
#{overflow=wrap}
np-opt = pos + 1
np = 0
np-opt: {
    ok -> np = it
    -> np = 0
}
np < n -> { … }
```

### 3.5 `6fgg3htw`（24）/ `stdargtyp`（3）/ `oarg2`（4）—— 引数型别 / 个数不符

这三类**不能套模板**，必须逐点回溯。已知两类成因：

- **型别推断连锁**：上游某个绑定变成 `?T`/换型，导致下游呼叫引数不符。例：
  - `notools/src/lbracket.no:179`：`l = atoi(left)` → `argument 1 of 'atoi': expected 'str', got 'i64'`（`left` 被推成 `i64`）。
  - `notools/src/pathchk.no:42`：`c = p[i]` → `c` 是 `?char`，传给要 `char`/`i64` 的 `pathchk-is-portable`。
  - `nouv/src/pep508.no:154`：`argument 1 of 'is-name-char': expected 'i64', got '?char'`。
- **呼叫形式错误**（`oarg2`，与 option 无关）：
  ```
  ; ✗ notools/src/whereis.no:129 —— 输出参数不能用位置引数传
  split-path(path-str, bin-dirs)
  ; ✓
  bin-dirs = split-path(path-str)
  ```


### 3.6 `4bek3xc6`（94 点，全部在 `notools`）—— 跨模组未限定呼叫【非 option】

```
; ✗ before
process-pipe(...)
; ✓ after
process.process-pipe(...)
```

这是「跨模组呼叫强制 `ShortName.` 前缀」的规则，**与本次 option 改动无关**，建议**另开一批/另开 commit**，不要混进 option 迁移（否则 review 与回滚都会被污染）。  
涉及：`sha1x/sha256x/sha384x/sha512x/md5x/xxd/stdbuf/cat/echo/ls/xargs/chroot/flock-cmd/logger/nice/setsid/sync-cmd/time-cmd/watch` 等。

### 3.7 `mzwb28br`（29 点，全部在 `nouv`）—— 待诊断

`undefined variable 'out' / 'spec9' / 'backend' / 'backend2' in format string`。

- 只在 vet `nouv/tests/test-*.no` 时出现，位置指向 `nouv/src/*.no` 的函数定义行（位置不可靠）。
- 代码里搜不到 `{out}` / `{spec` 字面量 ⇒ 疑似动态拼装的格式串，或**是 option 改动导致变量作用域/绑定变化后的连锁**。
- ⇒ 先取一个最小复现（`nouv/tests/test-pep508.no` → `nouv/src/dependency.no`），确认是语料问题还是编译器问题，再决定修法。

### 3.8 可用的解包写法（速查）

| 场景                   | 可用写法                                                   | 不可用                              |
| -------------------- | ------------------------------------------------------ | -------------------------------- |
| `ok ->` 臂内取被匹配的值     | 用 `it`                                                 | —                                |
| 索引结果要 plain          | `x T = <索引 expr>`（显式 plain 型别**仍合法**）                    | —                                |
| 算术结果要 plain          | 两段式：`x-opt = <expr>` ⏎ `x = 0` ⏎ `x-opt: {` ⏎ `ok -> x = it` ⏎ `-> x = 0` ⏎ `}` | `x T = <算术 expr>`（**报 15w45dqk**）、同行内联 `x = x-opt: {…}` |
| 窄型别 i8/i16/i32 结果要 plain | 先 `x i8 = 0`，再 `#{overflow=wrap}` ⏎ `x = <算术 expr>`（注解式重绑） | 两段式 match（`it` 是 i64，赋回窄型别报 narrowing） |
| 呼叫结果要 plain          | `o = call()` ⏎ `o: {` ⏎ `ok -> … it …` ⏎ `-> …` ⏎ `}`  | `d = call(): {…}`、`d T = call()` |
| 引数位置是 option         | 先绑成 plain 变量再传                                         | 引数内联 match                       |
| 确实要丢弃                | `_ = expr`                                             | —                                |
| 上抛                   | `x ?= expr`（要求所在函数有 `?T` 结果参数；语料里几乎没用过）                | —                                |

---

## 4. 批次与顺序

原则：**先小后大**，用最小的两个子项目把脚本、判据、复现流程全部跑通，再进大项目；**`4bek3xc6` 单独一批**。

| 批次 | 子项目                 | 错误点 | 档数 | 主要错误码                                      | 出口判据                                |
| -- | ------------------- | --- | -- | ------------------------------------------ | ----------------------------------- |
| B0 | （准备）                | —   | —  | —                                          | 参考二进制建好（§7.1）、基线快照、脚本就绪             |
| B1 | noagent             | 2   | 2  | `optunuse`×1、`fxxoptarg`×1                 | 逐档 ERROR=0；`optunuse` 先与编译器侧对齐      |
| B2 | nonpm               | 2   | 2  | `15w45dqk`×2                               | 逐档 ERROR=0                          |
| B3 | nojq                | 6   | 2  | `15w45dqk`×6                               | 逐档 ERROR=0                          |
| B4 | noimg               | 80  | 6  | `fxxoptarg`×49、`15w45dqk`×22               | 逐档 ERROR=0；`vp8/jpeg/webp/gif` 行为回归 |
| B5 | nouv                | 55  | 13 | `mzwb28br`×29、`fe0a5wt2`×12                | 先解 `mzwb28br` 定性；逐档 ERROR=0         |
| B6 | notools（option 部分）  | 85  | 30 | `fxxoptarg`×33、`6fgg3htw`×23、`15w45dqk`×22 | 逐档 ERROR=0                          |
| B7 | notools（`4bek3xc6`） | 94  | —  | 跨模组限定名                                     | **独立 commit**                       |
| B8 | nogit               | 100 | 68 | `15w45dqk`×94                              | 逐档 ERROR=0；`nogit/tests/*` 批量同形状    |
| B9 | 收尾                  | —   | —  | —                                          | 全语料逐档 ERROR=0；各子项目 build 通过；文档同步    |

**每批内的固定动作**

1. `git status` 记录开工前的树状态（⚠️ 平行 session 常在改 `nojq/`，动手前先看）；
2. 改一个档 → `no vet <该档>` 确认该档归零 → 下一个档（**逐档收敛**，不要一次改一片）；
3. 一批改完 → 逐档重跑全批，与 §2.2 的基线对比：**只允许错误点减少，不允许新增**；
4. `no build` 该子项目；能跑的测试跑一遍；
5. 记一笔：批号 / 改的档 / 改前改后的错误点数。

---

## 5. 验证判据与门禁

- **主判据**：`no vet <file>`（逐档）**ERROR = 0**。目录模式不作判据（§1.3）。
- **回归判据**：
  - 逐档 ERROR 集合与基线**逐条对比**，只减不增；
  - `no build <子项目>` 通过（`noagent`/`nogit`/`noimg`/`nouv`/`nonpm`/`notools` 各有 `main.no` 入口）；
  - 行为不变：`nogit/tests/*.no`、`nojq/tests/*.no`、`nouv/tests/*.no` 等测试程序可直接跑，改前后输出 diff 应为空；
  - `noimg` 涉及编码/解码（`vp8/jpeg/webp/gif`），改后必须做**字节级**输出比对（同一输入图片编解码结果 md5 相同）。
- **基线冻结**：记录 `no` 仓库 commit（本次 `40aa9caa`）+ 参考二进制 sha256；平行 session 一旦重建 `bin/no`，本轮数字作废重测。

---

## 6. 风险

| 风险                | 表现                                                                                 | 缓解                                                           |
| ----------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **改错语义**          | 用 `?=` 上抛把原本「失败取零值」的地方变成「向上抛错」，行为改变                                                | 默认一律用**显式 plain 型别**或**陈述式 match + 显式失败值**；`?=` 仅在有明确需求时用    |
| `optunuse` 是误报    | 白改 11 个点，还可能改坏                                                                     | B1 批先做定性（探针 `p.no`），与编译器侧对齐后再动                               |
| `mzwb28br` 是编译器问题 | 29 个点无从下手                                                                          | B5 批先做最小复现定性                                                 |
| 目录模式假阳性误导         | 按 `no vet <目录>` 的清单改，改到干净档上                                                        | **只用逐档 vet**（§1.3）                                           |
| 平行 session 撞车     | `bin/no` 被换、`nojq/` 被改                                                             | 动手前 `git status` + 锁 commit；自带 `/tmp/no_opt`；`nojq` 未提交改动先不动 |
| 迁移量随时间漂移          | 编译器继续改（D1 索引侧、`s[i]` 等）⇒ 错误集变化                                                     | 每批开始前**重跑基线**；把「基线冻结」写进批记录                                   |
| 组合注解行为            | `#{index-out=zero,overflow=wrap}`（153 处）会多一条 `nolang-overflow-ineffective` WARNING | 属噪声，暂不动；若要清理，单独一批                                            |
| 把两件事混成一个 commit   | `4bek3xc6` 与 option 迁移混在一起，回滚困难                                                    | B7 独立批次、独立 commit                                            |

---

## 7. 附：工具与复现

### 7.1 建参考二进制（带 StdSigKey）

```bash
export PATH="/opt/homebrew/bin:/opt/homebrew/opt/llvm/bin:$PATH"
cd ~/IdeaProjects/no/src
go run ./checker/genstdsig >/dev/null          # 重烤签名表 + std_ast.bin（不跑 stamp，安全）
KEY=$(go run ./checker/genstdsig -key-only)
GIT_VERSION=$(git describe --tags --dirty --always)
BUILD_DATE=$(date -u '+%s')
go build -ldflags="-s -w -X main.version=$GIT_VERSION -X main.buildDate=$BUILD_DATE \
  -X github.com/lizongying/nolang/checker.StdSigKey=$KEY" -o /tmp/no_opt ./cmd/no
```

⚠️ **不要用 `make no`**：它会先跑 `stamp-traceid`，perl 改写 5 个源档的 `TraceID`，污染并行 session。

### 7.2 复现测量（逐档 vet 全语料）

```bash
cd ~/IdeaProjects/notools
NO=/tmp/no_opt
find . -name "*.no" -not -path "*/node_modules/*" -not -path "./tmp/*" \
     -not -path "*/tmp/*" -not -path "./dist/*" -not -path "./docs/*" \
  | sed 's|^\./||' | sort > /tmp/opt-filelist.txt      # 578 档
mkdir -p /tmp/opt-perfile
cat /tmp/opt-filelist.txt | xargs -P 6 -I{} sh -c \
  'f="{}"; '"$NO"' vet "$f" > "/tmp/opt-perfile/$(echo "$f" | tr "/" "_")" 2>&1'
grep -h "\[ERROR\]" /tmp/opt-perfile/* | wc -l          # 逐档 ERROR 行数（未去重）
```

去重口径：`(path, line, col, code)`。参考实现见 `~/IdeaProjects/no/.workbuddy-ai/memory/2026-10-13.md` 记录的分析脚本要点。

### 7.3 单个子项目收敛检查

```bash
NO=/tmp/no_opt
for f in $(grep -E '^(noimg|nouv|nogit|notools|nojq|nonpm|noagent)/' /tmp/opt-filelist.txt); do
  n=$($NO vet "$f" 2>&1 | grep -c '\[ERROR\]')
  [ "$n" -gt 0 ] && echo "$n  $f"
done
```

---

## 附录 A：全部错误点清单（424 点，按错误码分组）

### `15w45dqk` — 155 處

- `nogit/main.no:430:23`
- `nogit/main.no:816:30`
- `nogit/main.no:839:30`
- `nogit/src/object.no:1222:20`
- `nogit/src/pack.no:328:42`
- `nogit/src/pack.no:349:42`
- `nogit/src/pack.no:792:30`
- `nogit/src/pack.no:850:30`
- `nogit/tests/test-commit-cli-debug.no:21:14`
- `nogit/tests/test-commit-debug.no:19:14`
- `nogit/tests/test-commit-encode2.no:25:14`
- `nogit/tests/test-commit-encode3.no:25:14`
- `nogit/tests/test-commit-encode4.no:25:14`
- `nogit/tests/test-config-adv.no:19:14`
- `nogit/tests/test-config-basic.no:19:14`
- `nogit/tests/test-debug-config.no:20:14`
- `nogit/tests/test-debug-config2.no:19:14`
- `nogit/tests/test-debug-config3.no:19:14`
- `nogit/tests/test-debug-config4.no:19:14`
- `nogit/tests/test-debug-config5.no:19:14`
- `nogit/tests/test-debug-config6.no:19:14`
- `nogit/tests/test-debug-config7.no:19:14`
- `nogit/tests/test-debug-config8.no:19:14`
- `nogit/tests/test-debug-get.no:19:14`
- `nogit/tests/test-debug-step.no:19:14`
- `nogit/tests/test-debug-subsec.no:19:14`
- `nogit/tests/test-debug-subsec2.no:19:14`
- `nogit/tests/test-e2e-commit.no:25:14`
- `nogit/tests/test-e2e-comprehensive.no:95:14`
- `nogit/tests/test-e2e-comprehensive.no:239:22`
- `nogit/tests/test-e2e-init.no:23:14`
- `nogit/tests/test-idx-debug.no:22:14`
- `nogit/tests/test-idx-debug10.no:20:14`
- `nogit/tests/test-idx-debug2.no:22:14`
- `nogit/tests/test-idx-debug3.no:22:14`
- `nogit/tests/test-idx-debug4.no:20:14`
- `nogit/tests/test-idx-debug5.no:20:14`
- `nogit/tests/test-idx-debug6.no:20:14`
- `nogit/tests/test-idx-debug7.no:20:14`
- `nogit/tests/test-idx-debug8.no:33:14`
- `nogit/tests/test-idx-debug9.no:20:14`
- `nogit/tests/test-index-add.no:23:14`
- `nogit/tests/test-index-comprehensive.no:31:14`
- `nogit/tests/test-index-replace.no:23:14`
- `nogit/tests/test-object-blob.no:21:14`
- `nogit/tests/test-object-commit.no:150:14`
- `nogit/tests/test-object-comprehensive.no:28:14`
- `nogit/tests/test-object-comprehensive.no:242:21`
- `nogit/tests/test-object-comprehensive.no:391:19`
- `nogit/tests/test-object-tag.no:21:14`
- `nogit/tests/test-object-tree.no:21:14`
- `nogit/tests/test-object-tree.no:110:20`
- `nogit/tests/test-read-commit2.no:25:14`
- `nogit/tests/test-read-commit3.no:25:14`
- `nogit/tests/test-read-loose.no:25:14`
- `nogit/tests/test-refs-basic.no:20:14`
- `nogit/tests/test-refs-branches.no:21:14`
- `nogit/tests/test-refs-comprehensive.no:27:14`
- `nogit/tests/test-refs-debug.no:20:14`
- `nogit/tests/test-refs-debug2.no:20:14`
- `nogit/tests/test-refs-debug3.no:21:14`
- `nogit/tests/test-refs-debug4.no:18:14`
- `nogit/tests/test-refs-debug5.no:18:14`
- `nogit/tests/test-refs-debug6.no:18:14`
- `nogit/tests/test-refs-detached.no:20:14`
- `nogit/tests/test-repo-init.no:18:14`
- `nogit/tests/test-repo-paths.no:18:14`
- `nogit/tests/test-repo-paths.no:100:19`
- `nogit/tests/test-revwalk-comprehensive.no:30:14`
- `nogit/tests/test-revwalk-comprehensive.no:469:22`
- `nogit/tests/test-revwalk-comprehensive.no:513:23`
- `nogit/tests/test-revwalk-resolve.no:23:14`
- `nogit/tests/test-revwalk-walk.no:23:14`
- `nogit/tests/test-revwalk-walk.no:80:22`
- `nogit/tests/test-ri-debug.no:14:14`
- `nogit/tests/test-simple-refs.no:18:14`
- `nogit/tests/test-simple-refs2.no:17:14`
- `nogit/tests/test-simple-refs4.no:18:14`
- `nogit/tests/test-time-debug.no:19:14`
- `nogit/tests/test-util.no:267:19`
- `nogit/tests/test-util.no:308:20`
- `nogit/tests/test.no:48:18`
- `nogit/tests/test.no:90:19`
- `nogit/tests/test.no:123:18`
- `nogit/tests/test.no:204:18`
- `nogit/tests/test.no:253:18`
- `nogit/tests/test.no:345:18`
- `nogit/tests/test.no:415:18`
- `nogit/tests/test.no:514:18`
- `nogit/tests/test.no:611:18`
- `nogit/tests/test.no:678:18`
- `nogit/tests/test.no:749:18`
- `nogit/tests/test.no:796:18`
- `nogit/tests/test.no:870:18`
- `noimg/src/gif.no:286:18`
- `noimg/src/gif.no:287:17`
- `noimg/src/gif.no:288:15`
- `noimg/src/gif.no:289:15`
- `noimg/src/gif.no:652:37`
- `noimg/src/gif.no:704:45`
- `noimg/src/gif.no:1218:33`
- `noimg/src/jpeg.no:610:76`
- `noimg/src/jpeg.no:611:78`
- `noimg/src/jpeg.no:702:60`
- `noimg/src/jpeg.no:703:62`
- `noimg/src/jpeg.no:704:60`
- `noimg/src/jpeg.no:705:62`
- `noimg/src/jpeg.no:706:60`
- `noimg/src/jpeg.no:707:62`
- `noimg/src/jpeg.no:1222:40`
- `noimg/src/jpeg.no:1223:42`
- `noimg/src/jpeg.no:1513:27`
- `noimg/src/vp8.no:931:21`
- `noimg/src/vp8.no:3529:38`
- `noimg/src/webp.no:2836:36`
- `noimg/src/webp.no:2837:36`
- `nojq/src/dec.no:333:28`
- `nojq/src/dec.no:425:18`
- `nojq/src/dec.no:446:24`
- `nojq/src/dec.no:773:27`
- `nojq/src/number.no:146:19`
- `nojq/src/number.no:177:19`
- `nonpm/tests/test-resolve-debug.no:17:15`
- `nonpm/tests/test-resolve-debug2.no:16:15`
- `notools/src/fmt.no:95:23`
- `notools/src/hexdump.no:230:31`
- `notools/src/od.no:109:27`
- `notools/src/pr.no:949:33`
- `notools/src/pr.no:974:32`
- `notools/src/pr.no:1009:35`
- `notools/src/pr.no:1019:36`
- `notools/src/pr.no:1029:36`
- `notools/src/pr.no:1050:31`
- `notools/src/sha384x.no:103:20`
- `notools/src/sha512x.no:103:20`
- `notools/src/stdbuf.no:221:31`
- `notools/src/stdbuf.no:288:35`
- `notools/src/xxd.no:63:35`
- `notools/src/xxd.no:346:58`
- `notools/src/xxd.no:348:59`
- `notools/src/xxd.no:632:31`
- `notools/src/xxd.no:638:31`
- `notools/src/xxd.no:644:31`
- `notools/src/xxd.no:726:35`
- `notools/src/xxd.no:732:35`
- `notools/src/xxd.no:738:35`
- `nouv/src/dependency.no:298:17`
- `nouv/src/dependency.no:304:38`
- `nouv/src/jsonx.no:70:21`
- `nouv/src/markers.no:761:32`
- `nouv/src/markers.no:766:32`
- `nouv/src/pep508.no:331:32`
- `nouv/src/pep508.no:336:32`
- `nouv/src/ptoml.no:305:32`
- `nouv/src/ptoml.no:310:32`


### `4bek3xc6` — 94 處

- `notools/src/awk.no:326:12`
- `notools/src/cat.no:46:11`
- `notools/src/cat.no:49:13`
- `notools/src/cat.no:52:5`
- `notools/src/cat.no:65:18`
- `notools/src/cat.no:65:47`
- `notools/src/cat.no:73:11`
- `notools/src/cat.no:82:19`
- `notools/src/cat.no:82:40`
- `notools/src/cat.no:82:61`
- `notools/src/cat.no:87:19`
- `notools/src/cat.no:87:40`
- `notools/src/cat.no:87:61`
- `notools/src/cat.no:94:11`
- `notools/src/cat.no:97:15`
- `notools/src/cat.no:138:15`
- `notools/src/cat.no:148:23`
- `notools/src/cat.no:155:11`
- `notools/src/cat.no:161:13`
- `notools/src/cat.no:167:17`
- `notools/src/cat.no:173:13`
- `notools/src/chroot.no:49:13`
- `notools/src/chroot.no:69:5`
- `notools/src/echo.no:6:5`
- `notools/src/echo.no:26:11`
- `notools/src/echo.no:34:11`
- `notools/src/flock-cmd.no:46:11`
- `notools/src/logger.no:52:5`
- `notools/src/ls.no:68:18`
- `notools/src/ls.no:68:46`
- `notools/src/ls.no:69:5`
- `notools/src/md5x.no:65:18`
- `notools/src/md5x.no:65:47`
- `notools/src/md5x.no:68:18`
- `notools/src/md5x.no:68:46`
- `notools/src/md5x.no:82:19`
- `notools/src/md5x.no:82:40`
- `notools/src/md5x.no:82:61`
- `notools/src/md5x.no:87:19`
- `notools/src/md5x.no:87:40`
- `notools/src/md5x.no:87:61`
- `notools/src/nice.no:94:11`
- `notools/src/setsid.no:34:11`
- `notools/src/sha1x.no:53:20`
- `notools/src/sha1x.no:66:18`
- `notools/src/sha1x.no:67:18`
- `notools/src/sha1x.no:80:18`
- `notools/src/sha1x.no:81:18`
- `notools/src/sha1x.no:94:18`
- `notools/src/sha1x.no:95:18`
- `notools/src/sha1x.no:108:18`
- `notools/src/sha1x.no:109:18`
- `notools/src/sha256x.no:59:20`
- `notools/src/sha256x.no:59:49`
- `notools/src/sha256x.no:60:20`
- `notools/src/sha256x.no:60:48`
- `notools/src/sha256x.no:72:18`
- `notools/src/sha256x.no:73:23`
- `notools/src/sha256x.no:73:44`
- `notools/src/sha256x.no:76:18`
- `notools/src/sha256x.no:77:23`
- `notools/src/sha256x.no:77:44`
- `notools/src/sha384x.no:65:18`
- `notools/src/sha384x.no:65:47`
- `notools/src/sha384x.no:68:18`
- `notools/src/sha384x.no:68:46`
- `notools/src/sha384x.no:82:19`
- `notools/src/sha384x.no:82:40`
- `notools/src/sha384x.no:82:61`
- `notools/src/sha384x.no:87:19`
- `notools/src/sha384x.no:87:40`
- `notools/src/sha384x.no:87:61`
- `notools/src/sha512x.no:65:18`
- `notools/src/sha512x.no:65:47`
- `notools/src/sha512x.no:68:18`
- `notools/src/sha512x.no:68:46`
- `notools/src/sha512x.no:82:19`
- `notools/src/sha512x.no:82:40`
- `notools/src/sha512x.no:82:61`
- `notools/src/sha512x.no:87:19`
- `notools/src/sha512x.no:87:40`
- `notools/src/sha512x.no:87:61`
- `notools/src/stdbuf.no:138:15`
- `notools/src/stdbuf.no:148:23`
- `notools/src/stdbuf.no:155:11`
- `notools/src/stdbuf.no:161:13`
- `notools/src/stdbuf.no:167:17`
- `notools/src/stdbuf.no:173:13`
- `notools/src/stdbuf.no:326:12`
- `notools/src/sync-cmd.no:6:5`
- `notools/src/time-cmd.no:26:11`
- `notools/src/watch.no:97:15`
- `notools/src/xargs.no:73:11`
- `notools/src/xxd.no:554:1`

### `fxxoptarg` — 90 處

- `noagent/src/httpclient.no:225:23`
- `nogit/src/pack.no:402:38`
- `nogit/src/pack.no:464:36`
- `nogit/src/pack.no:475:39`
- `noimg/src/gif.no:342:29`
- `noimg/src/jpeg.no:2586:19`
- `noimg/src/vp8.no:1342:17`
- `noimg/src/vp8.no:1353:17`
- `noimg/src/vp8.no:1573:19`
- `noimg/src/vp8.no:1576:19`
- `noimg/src/vp8.no:1579:19`
- `noimg/src/vp8.no:1582:19`
- `noimg/src/vp8.no:3109:29`
- `noimg/src/vp8.no:3117:29`
- `noimg/src/vp8.no:3125:29`
- `noimg/src/vp8.no:3504:23`
- `noimg/src/vp8.no:3507:23`
- `noimg/src/vp8.no:3510:23`
- `noimg/src/vp8.no:3544:39`
- `noimg/src/vp8.no:3595:33`
- `noimg/src/vp8.no:3620:41`
- `noimg/src/vp8.no:3639:24`
- `noimg/src/vp8.no:3643:24`
- `noimg/src/vp8.no:3653:23`
- `noimg/src/vp8.no:3662:23`
- `noimg/src/vp8.no:3665:23`
- `noimg/src/vp8.no:3887:17`
- `noimg/src/vp8.no:3894:21`
- `noimg/src/vp8.no:4057:26`
- `noimg/src/vp8.no:4459:31`
- `noimg/src/vp8.no:4484:31`
- `noimg/src/vp8.no:4509:30`
- `noimg/src/vp8.no:4530:26`
- `noimg/src/vp8.no:4541:26`
- `noimg/src/vp8.no:4555:30`
- `noimg/src/vp8.no:4556:30`
- `noimg/src/vp8.no:4557:30`
- `noimg/src/vp8.no:4573:30`
- `noimg/src/vp8.no:4574:30`
- `noimg/src/vp8.no:4575:30`
- `noimg/src/webp.no:1160:40`
- `noimg/src/webp.no:1161:40`
- `noimg/src/webp.no:1162:44`
- `noimg/src/webp.no:1163:47`
- `noimg/src/webp.no:1204:47`
- `noimg/src/webp.no:1211:56`
- `noimg/src/webp.no:1222:64`
- `noimg/src/webp.no:1236:78`
- `noimg/src/webp.no:1258:64`
- `noimg/src/webp.no:1275:75`
- `noimg/src/webp.no:1291:69`
- `noimg/src/webp.no:1323:77`
- `noimg/src/webp.no:1356:49`
- `notools/src/awk.no:388:28`
- `notools/src/awk.no:407:34`
- `notools/src/awk.no:899:28`
- `notools/src/awk.no:899:47`
- `notools/src/awk.no:912:24`
- `notools/src/awk.no:939:24`
- `notools/src/awk.no:965:20`
- `notools/src/awk.no:1007:24`
- `notools/src/awk.no:1022:24`
- `notools/src/awk.no:1067:24`
- `notools/src/awk.no:1105:20`
- `notools/src/awk.no:1173:33`
- `notools/src/awk.no:1189:51`
- `notools/src/awk.no:1216:28`
- `notools/src/awk.no:1242:24`
- `notools/src/cat.no:50:34`
- `notools/src/column.no:68:22`
- `notools/src/column.no:93:22`
- `notools/src/column.no:115:22`
- `notools/src/join.no:515:24`
- `notools/src/join.no:516:24`
- `notools/src/join.no:545:42`
- `notools/src/join.no:566:43`
- `notools/src/join.no:583:36`
- `notools/src/join.no:586:40`
- `notools/src/join.no:599:32`
- `notools/src/join.no:613:32`
- `notools/src/lbracket.no:47:23`
- `notools/src/sha224x.no:67:33`
- `notools/src/sha224x.no:67:64`
- `notools/src/sha224x.no:68:33`
- `notools/src/sha224x.no:68:63`
- `notools/src/test-cmd.no:50:34`
- `nouv/src/dependency.no:672:33`
- `nouv/src/jsonx.no:415:47`
- `nouv/src/jsonx.no:416:41`
- `nouv/src/jsonx.no:452:40`

### `mzwb28br` — 29 處

- `nouv/src/dependency.no:266:15`
- `nouv/src/pep508.no:34:15`
- `nouv/src/pep508.no:53:19`
- `nouv/src/pep508.no:61:15`
- `nouv/src/pep508.no:80:19`
- `nouv/src/pep508.no:88:15`
- `nouv/src/pep508.no:108:23`
- `nouv/src/pep508.no:116:19`
- `nouv/src/pep508.no:124:15`
- `nouv/src/pep508.no:144:23`
- `nouv/src/pep508.no:152:19`
- `nouv/src/pep508.no:160:15`
- `nouv/src/pep508.no:180:23`
- `nouv/src/pep508.no:188:19`
- `nouv/src/pep508.no:196:15`
- `nouv/src/pep508.no:214:15`
- `nouv/src/pep508.no:239:15`
- `nouv/src/pep508.no:258:19`
- `nouv/src/pep508.no:285:19`
- `nouv/src/pep508.no:293:15`
- `nouv/src/pep508.no:318:15`
- `nouv/src/pep508.no:336:15`
- `nouv/src/sdist.no:59:15`
- `nouv/src/sdist.no:76:15`
- `nouv/src/sdist.no:114:23`
- `nouv/src/utils.no:26:19`
- `nouv/src/utils.no:42:15`
- `nouv/src/utils.no:90:15`
- `nouv/src/version.no:24:15`

### `6fgg3htw` — 24 處

- `notools/src/join.no:517:22`
- `notools/src/join.no:518:22`
- `notools/src/join.no:523:35`
- `notools/src/join.no:532:35`
- `notools/src/join.no:584:32`
- `notools/src/join.no:587:33`
- `notools/src/join.no:600:25`
- `notools/src/join.no:600:44`
- `notools/src/join.no:614:25`
- `notools/src/join.no:614:44`
- `notools/src/lbracket.no:179:29`
- `notools/src/lbracket.no:186:29`
- `notools/src/lbracket.no:193:29`
- `notools/src/lbracket.no:200:29`
- `notools/src/lbracket.no:207:29`
- `notools/src/lbracket.no:214:29`
- `notools/src/pathchk.no:42:43`
- `notools/src/test-cmd.no:174:34`
- `notools/src/test-cmd.no:181:34`
- `notools/src/test-cmd.no:188:34`
- `notools/src/test-cmd.no:195:34`
- `notools/src/test-cmd.no:202:34`
- `notools/src/test-cmd.no:209:34`
- `nouv/src/pep508.no:154:26`

### `fe0a5wt2` — 14 處

- `noimg/src/image.no:764:16`
- `noimg/src/jpeg.no:764:16`
- `nouv/src/config.no:65:8`
- `nouv/src/config.no:99:8`
- `nouv/src/httpclient.no:65:8`
- `nouv/src/installer.no:65:8`
- `nouv/src/installer.no:99:8`
- `nouv/src/jsonx.no:65:8`
- `nouv/src/jsonx.no:99:8`
- `nouv/src/pep508.no:65:8`
- `nouv/src/pep508.no:99:8`
- `nouv/src/registry.no:99:8`
- `nouv/src/utils.no:99:8`
- `nouv/src/venv.no:65:8`

### `optunuse` — 11 處

- `noagent/src/utils.no:196:5`
- `nogit/src/object.no:900:5`
- `nogit/src/pack.no:540:5`
- `nogit/src/pack.no:737:5`
- `noimg/main.no:501:24`
- `noimg/src/gif.no:196:29`
- `noimg/src/gif.no:493:5`
- `noimg/src/jpeg.no:654:41`
- `noimg/src/jpeg.no:655:41`
- `noimg/src/jpeg.no:1255:13`
- `noimg/src/jpeg.no:1256:13`

### `oarg2` — 4 處

- `notools/src/whereis.no:129:15`
- `notools/src/whereis.no:160:26`
- `notools/src/whereis.no:170:23`
- `notools/src/whereis.no:180:26`

### `stdargtyp` — 3 處

- `notools/src/awk.no:423:18`
- `notools/src/patch.no:94:41`
- `notools/src/patch.no:100:49`
