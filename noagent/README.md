# noagent

Pure Nolang implementation of an **autonomous LLM agent CLI** — talks to any OpenAI-compatible `POST /v1/chat/completions` endpoint over raw TLS, runs a model ↔ tool loop, streams SSE deltas, persists sessions, and gates dangerous tools behind approval. No external runtime dependencies.

## Features

- **Tool-calling loop** — `read-file`, `write-file`, `edit-file`, `list-dir`, `run-shell`; tool calls returned by the model are executed and their results fed back, with bounded iterations until a final answer is produced
- **SSE streaming** — incremental deltas printed as they arrive; tolerates both `Transfer-Encoding: chunked` and close-delimited streams
- **Multi-turn memory** — conversation history trimmed by a character budget; sessions saved/restored under `~/.noagent/sessions/`
- **Multi-provider config** — priority: CLI flags > env vars > `~/.noagent/config.json` > built-in defaults, with named provider profiles
- **Approval gating** — `run-shell` / `write-file` / `edit-file` ask for confirmation (`--yes` bypasses); write/edit targets are normalized and confined to the current working directory (`..` escapes are rejected)
- **Pure-stdlib transport & JSON** — raw `net/tls` HTTP client plus a byte-level JSON scanner (`jsonx`), avoiding the std `http.get` 16 KB cap and std json runtime fragility

## Installation

```bash
# Build from source (requires the Nolang toolchain)
cd noagent
no build
# Binary lands in noagent/dist/noagent

# Or download a prebuilt binary from GitHub Releases (see root README)
```

## Commands

| Command | Description |
|---------|-------------|
| `noagent` | Start the interactive REPL |
| `noagent run "<prompt>"` | Run one autonomous agent tool loop |
| `noagent chat "<msg>"` | Single completion (no tool loop) |
| `noagent config show` | Print effective configuration |
| `noagent config set <k> <v>` | Persist a config value |
| `noagent config path` | Print the config file path |
| `noagent version` | Print version |
| `noagent help` | Print usage |

### Global flags

```
--model <name>        model id
--provider <name>     provider profile name
--base-url <url>      OpenAI-compatible base URL
--api-key <key>       API key (prefer env NOAGENT_API_KEY/OPENAI_API_KEY)
--stream              stream via SSE (default)
--no-stream           disable streaming
--no-tools            do not expose tools to the model
--max-turns N         cap agent tool-loop iterations (default 8)
--max-retries N       retry transient API failures — transport errors, HTTP 429/5xx — with exponential backoff (default 3)
--context-budget N    cap message content kept in the loop; drops the oldest tool-turns (a tool_calls turn is always dropped whole with its results, never orphaned) (default 100000 chars, 0 = off)
--yes, -y             auto-approve dangerous tools
--resume <id>         resume a saved session
--session <id>        use/assign session id
--system "<text>"     set/override system prompt
--temperature T       sampling temperature
--config <path>       alternate config file
```

### REPL meta commands

`/help` `/model` `/tools` `/system` `/clear` `/save` `/load` `/exit`

## Configuration

Resolution order (highest wins):

1. CLI flags
2. Environment variables — `NOAGENT_API_KEY` / `OPENAI_API_KEY`, `NOAGENT_BASE_URL`, `NOAGENT_MODEL`, `NOAGENT_PROVIDER`
3. `~/.noagent/config.json` — `{default-provider, providers: {name: {base-url, model, api-key-env, stream}}}`
4. Built-in defaults — base URL `https://api.openai.com/v1`, model `gpt-4o-mini`, streaming on

API keys are only ever read from the environment or flags — they are never written to any config file.

## Usage

```bash
export NOAGENT_API_KEY=sk-...

# One-shot agent run with tools
noagent run "list the files in src/ and count the lines of each .no file"

# Single completion without tools
noagent chat "explain tail-call optimization in one paragraph" --no-tools

# Interactive session with streaming and session persistence
noagent --session demo
> /save
> /load demo
```

## Project structure

```
noagent/
├── main.no              # CLI entry, subcommand dispatch, flag parsing
├── src/
│   ├── config.no        # config loading + provider profiles
│   ├── httpclient.no    # raw-TLS POST (full body + incremental stream)
│   ├── jsonx.no         # byte-level JSON builder/parser (escape, get-path, array iter)
│   ├── messages.no      # message history, context trimming, JSON serialization
│   ├── tools.no         # tool registry + OpenAI function schemas
│   ├── toolexec.no      # tool dispatch + execution
│   ├── approval.no      # dangerous-op gating + cwd path containment
│   ├── provider.no      # request building, non-stream + SSE completion, pure parse seams
│   ├── stream.no        # SSE frame parsing + incremental rendering
│   ├── agent.no         # core model ↔ tool loop
│   ├── session.no       # session save/restore under ~/.noagent/sessions/
│   ├── repl.no          # interactive REPL + meta commands
│   └── utils.no         # shared helpers
└── tests/
    ├── run-all.no       # offline test scheduler
    └── test-*.no        # per-module unit tests (CI never touches the network)
```

## Testing

All tests are offline — provider parsing is exercised through fixture strings, never live HTTP:

```bash
cd noagent
no run tests/run-all.no
```

## License

MIT
