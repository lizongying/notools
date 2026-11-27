# struct-with-slice 调查（2026-11-25）

## 结论先说

**「按值拷贝坏拷贝」（字段清零 / 乱码 / abort trap）在 v0.4.33-dev 上未能复现**，
因此沿用的规避规则（nonpm/installer.no 的「单循环 + 不传 []dep-node」）目前
只有历史证据，不能当成已确诊的编译器 bug。

## 做过的实验（全部用 `/Users/lizongying/IdeaProjects/no/bin/no`，v0.4.33-1-ga76815ee-dirty）

| 实验 | 触发条件 | 结果 |
|---|---|---|
| A/B/C/D 基础版 | 递归 struct `pack{deps []pack}`、两次遍历、作函数引数、[]byte 对照 | 全部输出正确 |
| 加压版 | deps 非空 + graph 经函数引数 + 200 次堆分配 | 撞独立 bug（见下） |
| 非空 deps 二次遍历 | `a.deps[0].name` 逐项比对 | 两轮全对 |
| 单纯按值拷贝 | `c node = z`、函数引数 `add(n node, ...)` | 正确 |
| 真实 nonpm | `no build nonpm/main.no` | build 成功；端到端 install 受 registry 环境问题阻塞 |

## 挖到的相关 bug：struct option 的 `?T → T` 门禁失效（已修，2026-11-25 下午）

用户给出 value-match 的结果类型 join 规则：

```
t|t = t      t|?t = ?t      t|never = t
?t|?t = ?t   ?t|never = ?t  never|never = never
```

据此，下面写法 `it:node`、`-> z` 的 z 是 `?node`，join 成 `?node`，
所以 `v node` 是**非法源码**，本应由 checker 拒绝：

```
z ?node = n
v node = z: { ok -> it
    -> z }        # 结果 ?node，赋给 node ⇒ 15w45dqk
```

**根因**：`15w45dqk`（option→plain 隐式解包门禁）在 checker.go 11249 行有
前置 `isConcreteType(existingType)`；该函数只认内建标量/别名/注册 struct 字段，
自定义 struct 名（如 `node`）返回 false，整条判定被短路。于是 `?i64 → i64`
会报错，而 `?node → node`（直接赋值与经 match join 两条路径）假绿。

**修法**：新增 `optionUnwrapRejectedBeyondConcrete(target, value, expr)`，让
「值确为 option、目标确为 plain」独立于 `isConcreteType` 开火，但**排除运算符
重载方法调用**（`_add/_sub/_mul/_div/_mod` 签名虽是 `?T`，语言约定结果 plain，
该豁免原本由 isConcreteType 的 false 意外提供）。

**验证**（隔离构建 v0.4.33-dev + checker 单测 + 端到端 build）：

| 写法 | 结果 |
|---|---|
| `?node` 直接赋 `node` | 报 `15w45dqk` ✓ |
| `?node` 经 `z:{ok->it; ->z}` join 后赋 `node` | 报 `15w45dqk` ✓ |
| 赋给 `?node` 目标 / 无标注推断（`v = ...`） | 放行 ✓ |
| `_ = z:{ok->print; ->_}` 与裸 `z:{...}` 语句级 match | 放行 ✓ |
| operator `_add` 返回 `?big` 赋给 `big` | 放行（豁免保留）✓ |

改动文件（no 仓库，未提交）：`src/checker/checker.go`、
`src/checker/struct_option_assign_test.go`。

## 已修的独立 codegen bug：`icmp eq %struct`（2026-11-25 下午）

最小复现 `compiler-issues/struct-slice-match-icmp.no`（11 行）：

```
node { name str; deps []node }
z node; z.name = '?'; z.deps = []
v node = z: { ok -> it
    -> z }
```

这里 subject 是**普通 node**（非 option），`it:node`、`-> z:node`，按上面的
join 规则结果就是 `node`，`v node` 类型合法——所以 checker 放行是对的。
但它触发 LLVM verifier 报 `icmp requires integer operands`：
`%c20 = icmp eq %node %lv.30, %lv.31`。

**MIR 证据**：`eq dst=20:bool args=[15 19]`，两个操作数都是 struct `node`；
来源是对普通（非 option）struct 做 value-match，parser 降糖成
`subject == ok`，而 `emitCmp` 的 `aOpt/bOpt` 只认 `%option`/聚合 option 类型，
`%node` 落到裸 `icmp eq %node` 分支。

**定位**：`src/mir/codegen.go:7432 emitCmp`，特别是 7472-7510 的 option
判别；`src/mir/hir2mir.go` 的 `bareVariant` → `Inst.TagOnly` 设置。

**影响范围**：对普通值做 match 是合法写法（std/number.no、std/yaml.no 都有），
但只有 struct-with-slice（非平凡 struct）会踩到；基础类型 match 不触发。
这与上面的 `?T → T` 修复是**两个独立问题**。

**语义确认**（实测）：普通值 subject 的 `ok` / `err` / `nil` 臂**都不匹配**，
一律走 default（i64 / str 探针一致）。所以判别式结果恒为 false（eq）/ true（ne）。

**修法**：`src/mir/hir2mir.go` 新增 `plainVariantPattern map[ValueID]bool`。
- 非 option context 的 bare variant lowering 处（原发射同类型零值常量的分支）
  把该常量标记为 plain variant pattern；
- `lowerKInfix` 的 eq/ne 在 lower 完 lv/rv 后，若任一侧被标记，直接折成
  bool 常量（eq→false、ne→true），不再发射 struct 比较。

这样不碰 option 的 `TagOnly` 路径，也不影响容器元素 place 的
`placePresenceConst`（元素存在→ok 匹配，语义相反，先于本短路处理）。

**验证**（隔离构建 + 端到端 build + MIR 断言测试）：
- `min-icmp.no` 现 build 成功，输出 `x x`（走 default，与 i64/str 语义一致）；
- 语义探针 sem.no / sem2.no 输出完全不变；
- option subject match（c/d）、`test/std/option.no`（25/25）、
  `unwrap-value-match.no`、`enum-cross.no` 全通过；
- 新增 `src/mir/plain_value_match_variant_test.go`：MIR 层断言普通 struct
  value-match 不产生 struct 操作数 eq，option struct 仍走 TagOnly；用禁用
  短路的对照实验确认测试能抓到原 bug（红/绿验证）。

## 加压版源码

`compiler-issues/struct-slice-copy-stress.no` —— 保留完整触发形状，供后续
回归验证用（当前 icmp bug 已修，可作为历史坏拷贝的长期回归素材）。
