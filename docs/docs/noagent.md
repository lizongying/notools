---
sidebar_position: 5
---

# noagent（純 Nolang 自主 LLM 智能體 CLI）

notools 倉庫內含一個**純 Nolang 實現的自主 LLM 智能體 CLI**（`noagent/` 目錄），透過標準庫 `net/tls` 走 HTTPS 呼叫任何 OpenAI 相容的 `POST /v1/chat/completions` 端點，實現「模型 ↔ 工具」多輪迴圈、SSE 串流增量顯示、會話持久化與危險操作審批門控，不依賴任何外部執行環境。

## 特性

- **工具呼叫迴圈** — `read-file`、`write-file`、`edit-file`、`list-dir`、`run-shell`；模型回傳 tool_calls 後自動執行並回填結果，有界迭代直到產出最終文字
- **SSE 串流輸出** — 邊收邊列印增量內容，相容 `Transfer-Encoding: chunked` 與連線關閉定界兩種承載
- **多輪會話記憶** — 歷史依字元預算裁剪上下文；會話可儲存/恢復至 `~/.noagent/sessions/`
- **多 provider 配置** — CLI flag > 環境變量 > `~/.noagent/config.json` > 內建預設，支援多 provider profile
- **審批門控** — `run-shell` / `write-file` / `edit-file` 執行前需確認（`--yes` 跳過）；寫/編輯路徑收斂於 cwd 內，拒絕 `..` 路徑逃逸
- **純標準庫傳輸與 JSON** — raw-TLS HTTP 客戶端 + 位元組級 JSON 掃描器（`jsonx`），規避 std `http.get` 16KB 上限與 std json 執行期脆弱性

## 主要命令

| 命令 | 說明 |
|------|------|
| `noagent` | 無參進入互動式 REPL |
| `noagent run "<prompt>"` | 執行一次完整 agent 工具迴圈 |
| `noagent chat "<msg>"` | 單次補全（不走工具迴圈） |
| `noagent config show` | 列印有效配置 |
| `noagent config set <k> <v>` | 持久化一個配置值 |
| `noagent config path` | 列印配置文件路徑 |
| `noagent version` | 列印版本 |
| `noagent help` | 列印使用說明 |

### 全域 flag

```
--model <name>        模型 id
--provider <name>     provider profile 名稱
--base-url <url>      OpenAI 相容 base URL
--api-key <key>       API key（建議改用環境變量 NOAGENT_API_KEY/OPENAI_API_KEY）
--stream              透過 SSE 串流（預設）
--no-stream           停用串流
--no-tools            不向模型暴露工具
--max-turns N         agent 工具迴圈迭代上限（預設 8）
--max-retries N       重試暫時性 API 失敗（傳輸錯誤、HTTP 429/5xx），指數退避（預設 3）
--context-budget N    保留於迴圈內之內容字元上限，丟棄最舊的 tool-turn（預設 100000，0 = 關閉）
--yes, -y             自動批准危險工具
--resume <id>         以已儲存的會話 <id> 作為 `run`/REPL 的起點（不存在則報錯）
--session <id>        將對話持久化到會話 <id>：`run` 於迴圈結束後寫入一次，REPL 每輪後自動保存（未給 --session 時回退至 --resume 的 id）
--system "<text>"     設定/覆蓋系統提示
--temperature T       取樣溫度
--config <path>       另用配置文件
```

### REPL 元命令

`/help` `/model` `/tools` `/system` `/clear` `/save` `/load` `/exit`

## 配置

解析優先級（高者生效）：

1. CLI flags
2. 環境變量 — `NOAGENT_API_KEY` / `OPENAI_API_KEY`、`NOAGENT_BASE_URL`、`NOAGENT_MODEL`、`NOAGENT_PROVIDER`
3. `~/.noagent/config.json` — `{default-provider, providers: {name: {base-url, model, api-key-env, stream}}}`
4. 內建預設 — base URL `https://api.openai.com/v1`、模型 `gpt-4o-mini`、串流開啟

API key 只從環境變量或 flag 讀取，絕不寫入任何配置文件。

## 構建與運行

```bash
cd noagent
no build
# 產物位於 noagent/dist/noagent

# 設定 API key 後跑一次 agent 工具迴圈
export NOAGENT_API_KEY=sk-...
noagent run "列出 src/ 下的檔案並統計每個 .no 檔案的行數"

# 單次補全，不走工具
noagent chat "用一段話解釋尾呼叫最佳化" --no-tools

# 帶會話持久化的互動式工作
noagent --session demo
> /save
> /load demo
```

## 模組結構

| 模組 | 說明 |
|------|------|
| `main.no` | CLI 入口、子命令分發、flag 解析 |
| `src/config.no` | 配置載入 + provider profile |
| `src/httpclient.no` | raw-TLS POST（完整 body + 增量串流） |
| `src/jsonx.no` | 位元組級 JSON builder/parser（跳脫、get-path、陣列迭代） |
| `src/messages.no` | 訊息歷史、上下文裁剪、JSON 序列化 |
| `src/tools.no` | 工具註冊表 + OpenAI function schema |
| `src/toolexec.no` | 工具分派 + 執行 |
| `src/approval.no` | 危險操作門控 + cwd 路徑收斂 |
| `src/provider.no` | 請求構造、非串流 + SSE 補全、純解析接縫 |
| `src/stream.no` | SSE 框架解析 + 增量渲染 |
| `src/agent.no` | 核心模型 ↔ 工具迴圈 |
| `src/session.no` | 會話儲存/恢復（`~/.noagent/sessions/`） |
| `src/repl.no` | 互動式 REPL + 元命令 |
| `src/utils.no` | 共用輔助函數 |

## 測試

所有測試皆離線 — provider 解析透過 fixture 字串驗證，絕不觸網：

```bash
cd noagent
no run tests/run-all.no
```

完整的模組架構、工具與安全設計等信息請參見 [`noagent/README.md`](https://github.com/lizongying/notools/blob/main/noagent/README.md)。
