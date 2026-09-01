---
sidebar_position: 1
---

# 构建

五个子项目各自独立构建：

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
}
```

`no build` 在根目录无参数运行时，会并行构建工作区内所有包。

## 前置要求

- 安装 [Nolang](https://github.com/lizongying/nolang) 编译器
- `no version` 确认安装成功
