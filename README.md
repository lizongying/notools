# notools

Unix 常用命令行工具集，使用 [Nolang](https://github.com/lizongying/nolang) 语言实现。

## 特性

- 纯 Nolang 实现，无外部依赖
- 单一可执行文件，子命令分发
- 支持 stdin 管道与文件输入
- 友好的错误处理

## 安装

```bash
# 克隆项目
git clone git@github.com:lizongying/notools.git notools
cd notools

# 构建（需先安装 Nolang）
no build

# 产物位于 dist/main，可重命名为 notools
cp dist/main /usr/local/bin/notools
```

## 工具列表

### 文件与目录

| 命令 | 说明 | 示例 |
|------|------|------|
| `ls` | 列出目录内容 | `notools ls -l /tmp` |
| `tree` | 显示目录树 | `notools tree -L 2` |
| `cat` | 输出文件内容 | `notools cat file.txt` |
| `touch` | 创建空文件或更新时间戳 | `notools touch new.txt` |
| `mv` | 移动或重命名 | `notools mv a.txt b.txt` |
| `rm` | 删除文件或目录 | `notools rm -r dir/` |
| `chmod` | 修改文件权限 | `notools chmod 755 script.sh` |
| `find` | 递归查找文件 | `notools find . -name "*.no"` |

### 文本处理

| 命令 | 说明 | 示例 |
|------|------|------|
| `echo` | 输出参数 | `notools echo -n hello` |
| `grep` | 搜索文本模式 | `notools grep -n pattern file.txt` |
| `wc` | 统计行/词/字节 | `notools wc -l file.txt` |
| `sort` | 排序行 | `notools sort -r file.txt` |
| `uniq` | 去除连续重复行 | `notools uniq -c file.txt` |
| `sed` | 流编辑器（替换） | `notools sed 's/old/new/g' file.txt` |
| `awk` | 字段提取 | `notools awk '{print $1}' file.txt` |

### 归档

| 命令 | 说明 | 示例 |
|------|------|------|
| `tar` | 创建/解压/列出 tar 归档 | `notools tar -cf out.tar file` |
| `zip` | 创建 zip 归档 | `notools zip out.zip file1 file2` |
| `unzip` | 解压/列出 zip 归档 | `notools unzip -l out.zip` |

### 系统

| 命令 | 说明 | 示例 |
|------|------|------|
| `ps` | 列出进程 | `notools ps -ef` |
| `top` | 显示系统资源与进程 | `notools top -n 20` |

## 用法

```bash
# 通用格式
notools <command> [args]

# 管道示例
echo "hello world" | notools grep hello
notools cat file.txt | notools sort | notools uniq -c

# 查看帮助
notools
```

## 项目结构

```
notools/
├── main.no          # 入口，子命令分发
├── src/
│   ├── echo.no      # 各工具实现
│   ├── cat.no
│   ├── ls.no
│   ├── ...
│   └── top.no
└── mod.jsonc        # 项目配置
```

## 开发

```bash
# 构建
no build ./notools/main.no

# 运行
no run ./notools/main.no <command> [args]
```

## 许可证

MIT
