# nogit

纯 [Nolang](https://github.com/lizongying/nolang) 实现的 Git 版本控制系统，不依赖系统 `git` 二进制，从底层数据结构到 CLI 命令全部使用 Nolang 编写。

## 特性

- 纯 Nolang 实现：不调用系统 `git`，从 SHA-1 哈希到 zlib 压缩均为原生代码
- Loose 对象存储：blob / tree / commit / tag 以 zlib 压缩的 loose 对象形式存储在 `.git/objects/`
- Packfile v2 读取：支持读取 Git packfile 格式，包括 ofs-delta 和 ref-delta 增量对象
- Git index v2：完整支持暂存区（staging area）读写
- Reflog：记录 HEAD 和分支引用的变更历史
- 仓库发现：从当前目录向上搜索 `.git` 目录
- 配置管理：支持 `user.name` / `user.email` 等 config 读写

## 安装

### 方式一：从 Releases 下载预编译二进制

```bash
# Linux amd64 示例
curl -fsSL -o nogit https://github.com/lizongying/notools/releases/latest/download/nogit-linux-amd64
chmod +x nogit && sudo mv nogit /usr/local/bin/
```

### 方式二：从源码构建

```bash
cd nogit
no build
# 产物位于 nogit/dist/git
```

## 命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| `init [path]` | 初始化新仓库（幂等，可重复执行） | `nogit init myrepo` |
| `add <path>` | 将文件或目录写入 blob 并加入暂存区（支持递归添加目录） | `nogit add file.txt`、`nogit add .` |
| `commit -m <msg>` | 从暂存区创建 tree 和 commit 对象 | `nogit commit -m 'initial'` |
| `log [count]` | 遍历提交历史 | `nogit log -n 10` |
| `status` | 显示当前分支、已暂存与未暂存的变更 | `nogit status` |
| `branch [name] [-d <name>]` | 列出、创建或删除分支 | `nogit branch dev`、`nogit branch -d dev` |
| `checkout <name>` | 切换分支并还原工作树 | `nogit checkout dev` |
| `tag <name> [-a <name> -m <msg>] [-d <name>]` | 创建轻量/标注标签或删除标签 | `nogit tag v1.0`、`nogit tag -a v1.0 -m 'msg'` |
| `show <ref>` | 显示对象类型与内容 | `nogit show HEAD` |
| `cat-file <opt> <ref>` | 按类型/引用查看对象（`-t`/`-s`/`-p`） | `nogit cat-file -p HEAD` |
| `hash-object [-w] <file>` | 计算文件 SHA-1（`-w` 写入对象库） | `nogit hash-object -w file` |
| `ls-tree <ref>` | 列出 tree 内容 | `nogit ls-tree HEAD` |
| `ls-files` | 列出暂存区文件 | `nogit ls-files` |
| `rev-parse <ref>` | 将引用解析为 OID | `nogit rev-parse HEAD` |
| `write-tree` | 从暂存区写入 tree 对象 | `nogit write-tree` |
| `rm <path> [--cached]` | 从暂存区和工作树中删除文件 | `nogit rm file.txt` |
| `reset [ref]` | 重置 HEAD 和索引到指定引用 | `nogit reset HEAD` |
| `update-ref <ref> <oid>` | 更新引用 | `nogit update-ref refs/heads/x <oid>` |
| `config <key> [val]` | 读取或设置配置项 | `nogit config user.name 'Alice'` |
| `reflog` | 显示 HEAD reflog | `nogit reflog` |

## 快速开始

```bash
# 初始化仓库
nogit init my-project
cd my-project

# 配置用户信息
nogit config user.name 'Alice'
nogit config user.email 'alice@example.com'

# 创建文件并提交
echo "hello" > file.txt
nogit add file.txt
nogit commit -m 'initial commit'

# 查看历史
nogit log

# 创建分支
nogit branch dev
nogit checkout dev
```

## 底层模块

| 模块 | 职责 |
|------|------|
| `util` | 通用工具函数（hex 编解码、字节查找、整数转字符串等） |
| `oid` | SHA-1 对象标识符、对象头构造、hash-object |
| `object` | Blob / Tree / Commit / Tag 对象的写入与读取（loose 格式） |
| `refs` | 引用管理：分支、标签、HEAD、symbolic-ref、reflog |
| `config` | Git config 文件解析与读写 |
| `index` | 暂存区（Git index v2）读写 |
| `repository` | 仓库初始化、`.git` 目录发现、路径辅助函数 |
| `revwalk` | 提交遍历、引用解析、祖先检测 |
| `zlib` | zlib 压缩 / 解压（deflate / inflate、Adler-32） |
| `pack` | Packfile v2 读取（变量长头、ofs-delta、ref-delta） |

## 项目结构

```
nogit/
├── main.no              ; CLI 入口与命令分发
├── package.jsonc        ; 项目配置
├── src/
│   ├── util.no          ; 通用工具
│   ├── oid.no           ; SHA-1 对象标识
│   ├── object.no        ; 对象读写（blob/tree/commit/tag）
│   ├── refs.no          ; 引用与 reflog
│   ├── config.no        ; 配置文件
│   ├── index.no         ; 暂存区（index v2）
│   ├── repository.no    ; 仓库初始化（幂等）与发现
│   ├── revwalk.no       ; 提交遍历与引用解析
│   ├── zlib.no          ; zlib 压缩/解压（archive/gzip）
│   └── pack.no          ; Packfile v2 读取（delta 解析）
├── tests/
│   ├── test.no               ; 统一测试运行器
│   ├── test-e2e-init.no       ; 初始化集成测试
│   ├── test-e2e-commit.no     ; 提交流水线集成测试
│   ├── test-e2e-comprehensive.no ; 全流程集成测试
│   └── ...                   ; 其余单元测试
└── dist/                ; 构建产物
```

## 已知限制

- 不支持 `git merge`（合并操作）
- 不支持 `git pull` / `git push`（远程仓库交互）
- 不支持 `git rebase`（变基操作）
- 不支持 `git diff`（差异比较，暂存区与工作树之间）
- 不支持 `git stash`（暂存修改）
- 不支持子模块（submodule）
- Packfile 仅支持读取，不支持写入
- 不支持 shallow clone

## 许可证

MIT
