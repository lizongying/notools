#!/usr/bin/env bash
# 验证 smoke 的 nosync 必需命令失败时不会假绿。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REAL_BIN="${1:-$ROOT/nosync/dist/nosync}"
if [ ! -x "$REAL_BIN" ]; then
  echo "nosync binary missing: $REAL_BIN" >&2
  exit 1
fi
REAL_BIN="$(cd "$(dirname "$REAL_BIN")" && pwd)/$(basename "$REAL_BIN")"

mkdir -p "$ROOT/tmp"
WORK="$(mktemp -d "$ROOT/tmp/nosync-smoke-exit.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/scripts" "$WORK/nosync/dist" "$WORK/tmp"
cp "$ROOT/scripts/smoke.sh" "$WORK/scripts/smoke.sh"
cp "$ROOT/nosync/main.no" "$WORK/nosync/main.no"

cat > "$WORK/nosync/dist/nosync" <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail
for arg in "$@"; do
  if [ "$arg" = "-r" ] && [ "${NOSYNC_INJECT_RECURSIVE_FAILURE:-0}" = "1" ]; then
    exit 42
  fi
done
exec "$NOSYNC_REAL_BIN" "$@"
WRAPPER
chmod +x "$WORK/nosync/dist/nosync"

export NOSYNC_REAL_BIN="$REAL_BIN"
export NOSYNC_INJECT_RECURSIVE_FAILURE=0
if ! bash "$WORK/scripts/smoke.sh" nosync > "$WORK/control.log" 2>&1; then
  cat "$WORK/control.log"
  echo "control smoke run failed" >&2
  exit 1
fi
grep -q 'nosync: 14 passed, 0 failed' "$WORK/control.log"

export NOSYNC_INJECT_RECURSIVE_FAILURE=1
if bash "$WORK/scripts/smoke.sh" nosync > "$WORK/fault.log" 2>&1; then
  cat "$WORK/fault.log"
  echo "fault-injected smoke run unexpectedly passed" >&2
  exit 1
fi
grep -q 'FAIL: skip links by default command' "$WORK/fault.log"
grep -q 'nosync: 14 passed, 1 failed' "$WORK/fault.log"

echo "NOSYNC SMOKE EXIT TESTS PASSED"
