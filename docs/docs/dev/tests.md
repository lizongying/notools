---
sidebar_position: 2
---

# 测试

## 哈希算法验证

对照系统 shasum 进行验证：

```bash
# 基本哈希
echo -n abc | ./dist/main md5       # 900150983cd24fb0d6963f7d28e17f72
echo -n abc | ./dist/main sha224    # 23097d223405d8228642a477bda255b32aadbce4bda0b3f7e36c9da7
echo -n abc | ./dist/main sha256    # ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
echo -n abc | ./dist/main sha384    # cb00753f45a35e8bb5a03d699ac65007272c32ab0eded1631a8b605a43ff5bed...
echo -n abc | ./dist/main sha512    # ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a...
echo -n abc | ./dist/main sha1      # a9993e364706816aba3e25717850c26c9cd0d89d

# HMAC
echo -n abc | ./dist/main hmac -a sha256 -k key
# 9c196e32dc0175f86f4b1cb89289d6619de6bee699e4c378e68309ed97a1a6ab

# GNU 风格校验和（含 -c 校验模式）
echo -n abc > /tmp/test.txt
./dist/main sha224sum /tmp/test.txt     # 23097d22...  /tmp/test.txt
./dist/main sha384sum /tmp/test.txt     # cb00753f...  /tmp/test.txt
./dist/main sha224sum /tmp/test.txt > /tmp/check.txt
./dist/main sha224sum -c /tmp/check.txt  # /tmp/test.txt: OK

# 大输入（多块处理）
python3 -c "print('a'*1000, end='')" > /tmp/large.txt
./dist/main sha256 /tmp/large.txt
./dist/main sha384 /tmp/large.txt

# 用户信息
./dist/main users     # 当前登录用户名
./dist/main who       # 当前用户 + 终端
./dist/main pinky     # 轻量级用户信息
```

## 运行测试

```bash
# 测试 test 目录下所有 .no 文件
no test

# 执行单个测试文件
no test my-test.no
```

测试说明：

- 测试文件统一放在 test/ 目录下
- 每个测试文件独立构建
- 若任一测试失败，返回非零退出码

## nogit 子项目测试

nogit 是独立子项目，测试位于 `nogit/tests/`（83 个 `.no` 文件），**不走根目录的 `no test`**，需进入 `nogit/` 目录用 `no run` 逐个执行：

```bash
cd nogit

# 统一测试运行器（12 个用例，覆盖 init/config/blob/tree/commit/branch/tag/index/checkout/discover/reflog/is-ancestor）
no run tests/test.no

# 集成测试
no run tests/test-e2e-init.no            # 初始化
no run tests/test-e2e-commit.no          # 提交流水线
no run tests/test-e2e-comprehensive.no   # 全流程（22 个用例）

# 单个模块测试
no run tests/test-zlib.no
no run tests/test-object-blob.no
```

运行约定：

- 每个测试文件自带 `main`，直接打印 `PASS:` / `FAIL:` 行，末尾输出统计（如 `Passed: 22, Failed: 0`）
- 全量跑完约 83 个文件需数分钟；串行全量时统一运行器偶发假失败，单独重跑可确认
- 构造/运行需 LLVM 工具链在 `PATH` 中（见「构建」文档）

## noagent 子项目测试

noagent 是独立子项目，测试位于 `noagent/tests/`，**全部离线** —— provider/SSE 解析通过 fixture 字符串验证，绝不触网。由一个统一调度器串行跑全部模块：

```bash
cd noagent
no run tests/run-all.no   # 依次跑 test-config/jsonx/messages/provider/stream/tools/toolexec/approval
```

> **注意**：`nogit/tests` 被仓库根 `.gitignore` 命中，但测试文件本身已被 git 跟踪。提交这些文件的改动时 `git add` 会被拒，需用 `git add -f`。
