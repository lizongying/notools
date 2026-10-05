---
sidebar_position: 1
---

# 构建

六个子项目各自独立构建：

```bash
# 构建 notools
cd notools
no build
cd ..
# 产物位于 notools/dist/notools

# 构建 nogit
cd nogit
no build
cd ..
# 产物位于 nogit/dist/nogit

# 构建 noimg
cd noimg
no build
cd ..
# 产物位于 noimg/dist/noimg

# 构建 nouv
cd nouv
no build
cd ..
# 产物位于 nouv/dist/nouv

# 构建 nonpm
cd nonpm
no build
cd ..
# 产物位于 nonpm/dist/nonpm

# 构建 noagent
cd noagent
no build
cd ..
# 产物位于 noagent/dist/noagent
```

## 工作区配置

项目根目录下的 `workspace.jsonc` 描述了单仓多包工作区：

```jsonc
{
  "notools": "./notools",
  "nogit": "./nogit",
  "noimg": "./noimg",
  "nouv": "./nouv",
  "nonpm": "./nonpm",
  "noagent": "./noagent",
}
```

`no build` 在根目录无参数运行时，会并行构建工作区内所有包。

## 前置要求

- 安装 [Nolang](https://github.com/lizongying/nolang) 编译器
- `no version` 确认安装成功
- LLVM 工具链需在 `PATH` 中（nogit 等项目走 LLVM 后端，需要 `llvm-config` 等可执行文件；macOS Homebrew 通常为 `/opt/homebrew/opt/llvm/bin`）

## 构建注意事项

- **`no build` 会回写源码**：它会规范化语法，并可能把 `package.jsonc` 的 `compiler.version` 提升到当前编译器版本。提交前请确认这类改动是否属于本次变更，不属于则还原，避免混入构建噪音。
- **`compiler version mismatch: package.jsonc requires "0.3.11", current compiler is "dev"`** 是常见告警而非错误：本地编译器版本与 `package.jsonc` 声明不一致时出现，构建仍会成功。若用 dev 版编译器，注意不要提交被自动改动的 `package.jsonc`。
- 子项目的测试文件也会被编译进 `dist/`（如 `nogit/dist/test-*`），属于正常产物。
