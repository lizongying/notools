#!/usr/bin/env bash
#
# Local smoke test runner — mirrors the smoke suites in .github/workflows/build.yml.
#
# Differences from CI:
#   * runs against the NATIVE binary in <subproject>/dist/<name> instead of
#     dist/<name>-linux-amd64
#   * VERSION is read from each subproject's main.no instead of the git tag
#   * adds Homebrew LLVM to PATH (the `no` build needs llvm-config on PATH)
#
# Usage:
#   scripts/smoke.sh            # run all smoke suites against existing binaries
#   scripts/smoke.sh --build    # rebuild every subproject first, then smoke test
#   scripts/smoke.sh notools nogit   # only run the named suites

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NO="${NO:-/Users/lizongying/IdeaProjects/no/bin/no}"

# `no build` shells out to llvm-config / clang.
export PATH="/opt/homebrew/opt/llvm/bin:/opt/homebrew/bin:$PATH"

BUILD_FIRST=0
TARGETS=()
for arg in "$@"; do
  case "$arg" in
    --build) BUILD_FIRST=1 ;;
    *) TARGETS+=("$arg") ;;
  esac
done
[ ${#TARGETS[@]} -eq 0 ] && TARGETS=(notools nogit noimg nouv nonpm noagent nosync)

TOTAL_PASS=0
TOTAL_FAIL=0
SUITE_FAILS=()

PASS=0
FAIL=0

check() {
  local desc="$1" actual="$2" expected="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    echo "    expected: '$expected'"
    echo "    actual:   '$actual'"
    FAIL=$((FAIL + 1))
  fi
}

checkfile() {
  local desc="$1" path="$2"
  if [ -f "$path" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    FAIL=$((FAIL + 1))
  fi
}

checkdir() {
  local desc="$1" path="$2"
  if [ -d "$path" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    FAIL=$((FAIL + 1))
  fi
}

# version_of <subproject> — read VERSION = '...' from main.no
version_of() {
  sed -n "s/^VERSION = '\(.*\)'\$/\1/p" "$ROOT/$1/main.no" | head -1
}

# ── build ──────────────────────────────────────────────────────────
do_build() {
  local p="$1"
  echo "--- building $p ---"
  (cd "$ROOT/$p" && "$NO" build 2>&1 | tail -15)
  if [ -x "$ROOT/$p/dist/$p" ]; then
    return 0
  fi
  return 1
}

suite_header() {
  echo ""
  echo "============================================"
  echo "  $1 smoke test"
  echo "============================================"
}

suite_footer() {
  local name="$1"
  echo "============================================"
  echo "  $name: $PASS passed, $FAIL failed"
  echo "============================================"
  TOTAL_PASS=$((TOTAL_PASS + PASS))
  TOTAL_FAIL=$((TOTAL_FAIL + FAIL))
  [ "$FAIL" -eq 0 ] || SUITE_FAILS+=("$name")
}

want() {
  local t="$1"
  for x in "${TARGETS[@]}"; do [ "$x" = "$t" ] && return 0; done
  return 1
}

# ── notools ────────────────────────────────────────────────────────
if want notools; then
  PASS=0; FAIL=0
  suite_header notools
  BIN="$ROOT/notools/dist/notools"
  [ "$BUILD_FIRST" -eq 1 ] && do_build notools
  if [ ! -x "$BIN" ]; then
    echo "  FAIL: binary missing: $BIN"; FAIL=$((FAIL+1))
  else
    VER="$(version_of notools)"

    echo "=== echo ==="
    out=$(echo "hello notools" | "$BIN" echo)
    check "echo stdin" "$out" "hello notools"

    echo "=== version ==="
    out=$("$BIN" version)
    check "version" "$out" "notools v$VER (pure Nolang)"

    echo "=== md5 ==="
    out=$(echo -n abc | "$BIN" md5)
    check "md5(abc)" "$out" "900150983cd24fb0d6963f7d28e17f72"

    echo "=== sha1 ==="
    out=$(echo -n abc | "$BIN" sha1)
    check "sha1(abc)" "$out" "a9993e364706816aba3e25717850c26c9cd0d89d"

    echo "=== sha256 ==="
    out=$(echo -n abc | "$BIN" sha256)
    check "sha256(abc)" "$out" "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"

    echo "=== sha512 ==="
    out=$(echo -n abc | "$BIN" sha512)
    check "sha512(abc)" "$out" "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f"

    echo "=== hmac ==="
    out=$(echo -n abc | "$BIN" hmac -a sha256 -k key)
    check "hmac-sha256(abc,key)" "$out" "9c196e32dc0175f86f4b1cb89289d6619de6bee699e4c378e68309ed97a1a6ab"

    echo "=== basename ==="
    out=$("$BIN" basename /tmp/foo/bar.txt)
    check "basename" "$out" "bar.txt"

    echo "=== dirname ==="
    out=$("$BIN" dirname /tmp/foo/bar.txt)
    check "dirname" "$out" "/tmp/foo"

    echo "=== seq ==="
    out=$("$BIN" seq 1 5 | tr '\n' ' ')
    check "seq 1 5" "$out" "1 2 3 4 5 "
  fi
  suite_footer notools
fi

# ── nogit ──────────────────────────────────────────────────────────
if want nogit; then
  PASS=0; FAIL=0
  suite_header nogit
  BIN="$ROOT/nogit/dist/nogit"
  [ "$BUILD_FIRST" -eq 1 ] && do_build nogit
  if [ ! -x "$BIN" ]; then
    echo "  FAIL: binary missing: $BIN"; FAIL=$((FAIL+1))
  else
    VER="$(version_of nogit)"
    WORK=/tmp/nogit-smoke-test

    echo "=== nogit version ==="
    out=$("$BIN" version)
    check "version" "$out" "nolang-git v$VER (pure nolang)"

    echo "=== nogit init ==="
    rm -rf "$WORK"
    out=$("$BIN" init "$WORK" 2>&1)
    echo "  init output: $out"
    checkdir ".git dir created" "$WORK/.git"
    checkfile "HEAD file exists" "$WORK/.git/HEAD"
    checkdir "objects dir exists" "$WORK/.git/objects"
    checkdir "refs/heads dir exists" "$WORK/.git/refs/heads"

    echo "=== nogit add + commit ==="
    echo "hello nogit" > "$WORK/readme.txt"
    (cd "$WORK" && "$BIN" add readme.txt 2>&1) && { echo "  PASS: nogit add succeeded"; PASS=$((PASS+1)); } \
      || { echo "  FAIL: nogit add failed"; FAIL=$((FAIL+1)); }
    out=$(cd "$WORK" && "$BIN" commit -m "initial commit" 2>&1)
    echo "  commit output: $out"
    checkfile "main branch created" "$WORK/.git/refs/heads/main"

    echo "=== nogit log ==="
    out=$(cd "$WORK" && "$BIN" log 2>&1)
    echo "  log output: $out"
    if echo "$out" | grep -q "initial commit"; then
      echo "  PASS: log shows commit message"; PASS=$((PASS+1))
    else
      echo "  FAIL: log missing commit message"; FAIL=$((FAIL+1))
    fi

    echo "=== nogit object integrity (extra: zlib + sha1 vs filename) ==="
    python3 - "$WORK" <<'PY'
import sys, zlib, glob, hashlib
work = sys.argv[1]
bad = 0
n = 0
for p in sorted(glob.glob(work + '/.git/objects/*/*')):
    raw = open(p, 'rb').read()
    try:
        d = zlib.decompress(raw)
    except Exception as e:
        print('  FAIL: %s not valid zlib: %s' % (p, e))
        bad += 1
        continue
    n += 1
    h = hashlib.sha1(d).hexdigest()
    name = p.split('/')[-2] + p.split('/')[-1]
    if h != name:
        print('  FAIL: %s content hashes to %s' % (name, h))
        bad += 1
print('  checked %d objects, %d bad' % (n, bad))
PY
    if [ "$(python3 - "$WORK" <<'PY'
import sys, zlib, glob, hashlib
work = sys.argv[1]
bad = 0
for p in sorted(glob.glob(work + '/.git/objects/*/*')):
    raw = open(p, 'rb').read()
    try:
        d = zlib.decompress(raw)
    except Exception:
        bad += 1
        continue
    if hashlib.sha1(d).hexdigest() != p.split('/')[-2] + p.split('/')[-1]:
        bad += 1
sys.stdout.write(str(bad))
PY
)" = "0" ]; then
      echo "  PASS: all loose objects valid + self-consistent"; PASS=$((PASS+1))
    else
      echo "  FAIL: loose objects invalid"; FAIL=$((FAIL+1))
    fi
  fi
  suite_footer nogit
fi

# ── noimg ──────────────────────────────────────────────────────────
if want noimg; then
  PASS=0; FAIL=0
  suite_header noimg
  BIN="$ROOT/noimg/dist/noimg"
  [ "$BUILD_FIRST" -eq 1 ] && do_build noimg
  if [ ! -x "$BIN" ]; then
    echo "  FAIL: binary missing: $BIN"; FAIL=$((FAIL+1))
  else
    VER="$(version_of noimg)"

    echo "=== noimg version ==="
    out=$("$BIN" version)
    check "version" "$out" "img v$VER (pure Nolang image processing)"

    echo "=== noimg convert (PPM -> BMP) ==="
    printf 'P3\n2 2\n255\n255 0 0 0 255 0 0 0 255 255 255 0\n' > /tmp/test.ppm
    "$BIN" convert /tmp/test.ppm /tmp/test_out.bmp 2>&1
    if [ -f /tmp/test_out.bmp ]; then
      echo "  PASS: BMP output created"; PASS=$((PASS+1))
      SIZE=$(wc -c < /tmp/test_out.bmp | tr -d ' ')
      if [ "$SIZE" -gt 50 ]; then
        echo "  PASS: BMP file size reasonable ($SIZE bytes)"; PASS=$((PASS+1))
      else
        echo "  FAIL: BMP file too small ($SIZE bytes)"; FAIL=$((FAIL+1))
      fi
    else
      echo "  FAIL: BMP output not created"; FAIL=$((FAIL+1))
    fi

    echo "=== noimg convert (PPM -> PNG) ==="
    "$BIN" convert /tmp/test.ppm /tmp/test_out.png 2>&1
    if [ -f /tmp/test_out.png ]; then
      echo "  PASS: PNG output created"; PASS=$((PASS+1))
      SIG=$(xxd -l 8 -p /tmp/test_out.png)
      check "PNG signature" "$SIG" "89504e470d0a1a0a"
    else
      echo "  FAIL: PNG output not created"; FAIL=$((FAIL+1))
    fi

    echo "=== noimg convert (PPM -> TGA) ==="
    "$BIN" convert /tmp/test.ppm /tmp/test_out.tga 2>&1
    checkfile "TGA output created" /tmp/test_out.tga

    echo "=== noimg info ==="
    out=$("$BIN" info /tmp/test.ppm 2>&1)
    # NOTE: CI uses `grep -qi "width\|height\|2\b"`. On BSD grep (macOS) `\|` is
    # NOT alternation in BRE — it is a literal, so that pattern never matches.
    # Use -E with real alternation instead; same intent, portable.
    if echo "$out" | grep -Eqi "width|height"; then
      echo "  PASS: info shows image properties"; PASS=$((PASS+1))
    else
      echo "  FAIL: info output unexpected: $out"; FAIL=$((FAIL+1))
    fi

    echo "=== noimg grayscale ==="
    "$BIN" grayscale /tmp/test.ppm /tmp/gray_out.ppm 2>&1
    checkfile "grayscale output created" /tmp/gray_out.ppm

    echo "=== noimg invert ==="
    "$BIN" invert /tmp/test.ppm /tmp/inv_out.ppm 2>&1
    checkfile "invert output created" /tmp/inv_out.ppm
  fi
  suite_footer noimg
fi

# ── nouv ───────────────────────────────────────────────────────────
if want nouv; then
  PASS=0; FAIL=0
  suite_header nouv
  BIN="$ROOT/nouv/dist/nouv"
  [ "$BUILD_FIRST" -eq 1 ] && do_build nouv
  if [ ! -x "$BIN" ]; then
    echo "  FAIL: binary missing: $BIN"; FAIL=$((FAIL+1))
  else
    VER="$(version_of nouv)"

    echo "=== nouv version ==="
    out=$("$BIN" version)
    check "version" "$out" "nouv $VER"

    echo "=== nouv help ==="
    out=$("$BIN" help | head -1)
    check "help" "$out" "nouv — pure Nolang implementation of uv"

    echo "=== nouv init ==="
    rm -rf /tmp/nouv-smoke-test
    out=$("$BIN" init /tmp/nouv-smoke-test 2>&1)
    checkfile "pyproject.toml created" /tmp/nouv-smoke-test/pyproject.toml
    checkfile "README.md created" /tmp/nouv-smoke-test/README.md
    checkfile ".gitignore created" /tmp/nouv-smoke-test/.gitignore

    echo "=== nouv cache dir ==="
    out=$("$BIN" cache dir 2>&1)
    if echo "$out" | grep -q "nouv"; then
      echo "  PASS: cache dir returned"; PASS=$((PASS+1))
    else
      echo "  FAIL: cache dir unexpected: $out"; FAIL=$((FAIL+1))
    fi
  fi
  suite_footer nouv
fi

# ── nonpm ──────────────────────────────────────────────────────────
if want nonpm; then
  PASS=0; FAIL=0
  suite_header nonpm
  BIN="$ROOT/nonpm/dist/nonpm"
  [ "$BUILD_FIRST" -eq 1 ] && do_build nonpm
  if [ ! -x "$BIN" ]; then
    echo "  FAIL: binary missing: $BIN"; FAIL=$((FAIL+1))
  else
    VER="$(version_of nonpm)"

    echo "=== nonpm version ==="
    out=$("$BIN" version)
    check "version" "$out" "nonpm $VER"

    echo "=== nonpm help ==="
    out=$("$BIN" help | head -1)
    check "help" "$out" "noNpm — pure Nolang implementation of pnpm"

    echo "=== nonpm init ==="
    rm -rf /tmp/nonpm-smoke-test
    out=$("$BIN" init /tmp/nonpm-smoke-test 2>&1)
    checkfile "package.json created" /tmp/nonpm-smoke-test/package.json

    echo "=== nonpm cache dir ==="
    out=$("$BIN" cache dir 2>&1)
    if echo "$out" | grep -q "nonpm"; then
      echo "  PASS: cache dir returned"; PASS=$((PASS+1))
    else
      echo "  FAIL: cache dir unexpected: $out"; FAIL=$((FAIL+1))
    fi
  fi
  suite_footer nonpm
fi

# ── nosync ────────────────────────────────────────────────────────
if want nosync; then
  PASS=0; FAIL=0
  nosync_required() {
    local desc="$1"
    shift
    if "$@"; then
      return 0
    fi
    echo "  FAIL: $desc"; FAIL=$((FAIL+1))
    return 1
  }
  suite_header nosync
  BIN="$ROOT/nosync/dist/nosync"
  [ "$BUILD_FIRST" -eq 1 ] && do_build nosync
  if [ ! -x "$BIN" ]; then
    echo "  FAIL: binary missing: $BIN"; FAIL=$((FAIL+1))
  else
    VER="$(version_of nosync)"
    WORK="$(mktemp -d "$ROOT/tmp/nosync-smoke.XXXXXX")"
    SRC="$WORK/src"
    DST="$WORK/dst"
    mkdir -p "$SRC"
    printf 'alpha' > "$SRC/a"

    echo "=== nosync version ==="
    if out=$("$BIN" --version); then
      check "version" "$out" "nosync $VER"
    else
      echo "  FAIL: version command"; FAIL=$((FAIL+1))
    fi

    echo "=== first copy ==="
    if "$BIN" -a "$SRC/" "$DST"; then
      echo "  PASS: initial copy"; PASS=$((PASS+1))
    else
      echo "  FAIL: initial copy"; FAIL=$((FAIL+1))
    fi
    if cmp -s "$SRC/a" "$DST/a"; then
      echo "  PASS: copied bytes"; PASS=$((PASS+1))
    else
      echo "  FAIL: copied bytes"; FAIL=$((FAIL+1))
    fi

    echo "=== unchanged ==="
    if out=$("$BIN" -a --stats "$SRC/" "$DST"); then
      check "unchanged updates" "$(printf '%s\n' "$out" | awk '$1 == "updated:" {print $2}')" "0"
    else
      echo "  FAIL: unchanged sync command"; FAIL=$((FAIL+1))
    fi

    echo "=== delta ==="
    if python3 - "$SRC/data" <<'PY'
import hashlib, sys
blocks = [hashlib.sha256(str(i).encode()).digest() * 128 for i in range(10)]
open(sys.argv[1], 'wb').write(b''.join(blocks))
PY
    then
      :
    else
      echo "  FAIL: create delta fixture"; FAIL=$((FAIL+1))
    fi
    nosync_required 'copy delta fixture' "$BIN" -a "$SRC/" "$DST"
    if python3 - "$SRC/data" <<'PY'
import hashlib, sys
path = sys.argv[1]
data = open(path, 'rb').read()
prefix = hashlib.sha256(b'prepend').digest() * 128
open(path, 'wb').write(prefix + data)
PY
    then
      :
    else
      echo "  FAIL: prepend delta fixture"; FAIL=$((FAIL+1))
    fi
    if out=$("$BIN" -a --stats --block-size 4096 "$SRC/" "$DST"); then
      reused=$(printf '%s\n' "$out" | awk '$1 == "reused-bytes:" {print $2}')
      case "$reused" in
        ''|*[!0-9]*) echo "  FAIL: delta reuse >= 95% (invalid reused=$reused)"; FAIL=$((FAIL+1)) ;;
        *) if [ "$reused" -ge 38912 ]; then
          echo "  PASS: delta reuse >= 95%"; PASS=$((PASS+1))
        else
          echo "  FAIL: delta reuse >= 95% (reused=$reused)"; FAIL=$((FAIL+1))
        fi ;;
      esac
    else
      echo "  FAIL: delta sync command"; FAIL=$((FAIL+1))
      reused=''
    fi
    if cmp -s "$SRC/data" "$DST/data"; then
      echo "  PASS: delta bytes"; PASS=$((PASS+1))
    else
      echo "  FAIL: delta bytes"; FAIL=$((FAIL+1))
    fi

    echo "=== checksum ==="
    printf 'omega' > "$DST/a"
    if python3 - "$SRC/a" "$DST/a" <<'PY'
import os, sys
for path in sys.argv[1:]:
    os.utime(path, (1700000000, 1700000000))
PY
    then
      :
    else
      echo "  FAIL: set checksum fixture mtimes"; FAIL=$((FAIL+1))
    fi
    nosync_required 'checksum sync command' "$BIN" -a --checksum "$SRC/" "$DST"
    if cmp -s "$SRC/a" "$DST/a"; then
      echo "  PASS: checksum detects equal size/mtime"; PASS=$((PASS+1))
    else
      echo "  FAIL: checksum detects equal size/mtime"; FAIL=$((FAIL+1))
    fi

    echo "=== delete ==="
    printf 'stale' > "$DST/stale"
    nosync_required 'delete sync command' "$BIN" -a --delete "$SRC/" "$DST"
    if [ ! -e "$DST/stale" ]; then
      echo "  PASS: stale entry deleted"; PASS=$((PASS+1))
    else
      echo "  FAIL: stale entry deleted"; FAIL=$((FAIL+1))
    fi

    echo "=== dry-run ==="
    if python3 - "$BIN" "$SRC" "$DST" <<'PY'
import hashlib, os, stat, subprocess, sys
binary, source, target = sys.argv[1:]
def snapshot(root):
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in ['.', *sorted(dirs), *sorted(files)]:
            path = directory if name == '.' else os.path.join(directory, name)
            rel = '.' if name == '.' else os.path.relpath(path, root)
            info = os.lstat(path)
            if stat.S_ISLNK(info.st_mode):
                payload = ('link', os.readlink(path))
            elif stat.S_ISDIR(info.st_mode):
                payload = ('dir',)
            else:
                with open(path, 'rb') as handle:
                    payload = ('file', hashlib.sha256(handle.read()).hexdigest())
            result[rel] = (info.st_mode, info.st_mtime_ns, payload)
    return result
before = snapshot(target)
subprocess.run([binary, '-a', '--checksum', '--delete', '--dry-run', source + '/', target], check=True)
assert snapshot(target) == before, 'dry-run changed target tree'
PY
    then
      echo "  PASS: dry-run full-tree snapshot"; PASS=$((PASS+1))
    else
      echo "  FAIL: dry-run full-tree snapshot"; FAIL=$((FAIL+1))
    fi

    echo "=== mode and mtime ==="
    chmod 640 "$SRC/a"
    touch -t 202001010000 "$SRC/a"
    nosync_required 'metadata sync command' "$BIN" -a "$SRC/" "$DST"
    if [ "$(uname)" = Darwin ]; then
      mode_of() { stat -f '%Lp' "$1"; }
      mtime_of() { stat -f '%m' "$1"; }
    else
      mode_of() { stat -c '%a' "$1"; }
      mtime_of() { stat -c '%Y' "$1"; }
    fi
    check "preserved mode" "$(mode_of "$DST/a")" "$(mode_of "$SRC/a")"
    check "preserved mtime" "$(mtime_of "$DST/a")" "$(mtime_of "$SRC/a")"

    echo "=== links and overlap ==="
    mkdir "$WORK/outside"
    printf 'outside' > "$WORK/outside/sentinel"
    ln -s "$WORK/outside" "$SRC/escape"
    nosync_required 'skip links by default command' "$BIN" -r "$SRC/" "$DST"
    if [ ! -e "$DST/escape" ] && [ ! -L "$DST/escape" ]; then
      echo "  PASS: links skipped by default"; PASS=$((PASS+1))
    else
      echo "  FAIL: links skipped by default"; FAIL=$((FAIL+1))
    fi
    nosync_required 'copy links without following command' "$BIN" -a "$SRC/" "$DST"
    if [ -L "$DST/escape" ]; then
      echo "  PASS: link copied without following"; PASS=$((PASS+1))
    else
      echo "  FAIL: link copied without following"; FAIL=$((FAIL+1))
    fi
    if "$BIN" -a "$SRC" "$SRC/child" >/dev/null 2>&1; then
      echo "  FAIL: overlapping roots rejected"; FAIL=$((FAIL+1))
    else
      echo "  PASS: overlapping roots rejected"; PASS=$((PASS+1))
    fi

    if python3 - "$WORK" <<'PY'
import shutil, sys
shutil.rmtree(sys.argv[1])
PY
    then
      :
    else
      echo "  FAIL: clean nosync smoke workspace"; FAIL=$((FAIL+1))
    fi
  fi
  suite_footer nosync
fi

# ── noagent ────────────────────────────────────────────────────────
if want noagent; then
  PASS=0; FAIL=0
  suite_header noagent
  BIN="$ROOT/noagent/dist/noagent"
  [ "$BUILD_FIRST" -eq 1 ] && do_build noagent
  if [ ! -x "$BIN" ]; then
    echo "  FAIL: binary missing: $BIN"; FAIL=$((FAIL+1))
  else
    VER="$(version_of noagent)"

    echo "=== noagent version ==="
    out=$("$BIN" version)
    check "version" "$out" "noagent $VER"

    echo "=== noagent help ==="
    out=$("$BIN" help | head -1)
    check "help" "$out" "noagent $VER — pure Nolang autonomous LLM agent CLI"

    echo "=== noagent config show (defaults, no network) ==="
    out=$("$BIN" config show 2>&1)
    if echo "$out" | grep -q "provider:"; then
      echo "  PASS: config show prints provider"; PASS=$((PASS+1))
    else
      echo "  FAIL: config show unexpected: $out"; FAIL=$((FAIL+1))
    fi
    if echo "$out" | grep -q "base-url:"; then
      echo "  PASS: config show prints base-url"; PASS=$((PASS+1))
    else
      echo "  FAIL: config show missing base-url: $out"; FAIL=$((FAIL+1))
    fi
  fi
  suite_footer noagent
fi

echo ""
echo "############################################"
echo "  TOTAL: $TOTAL_PASS passed, $TOTAL_FAIL failed"
if [ ${#SUITE_FAILS[@]} -gt 0 ]; then
  echo "  Failing suites: ${SUITE_FAILS[*]}"
fi
echo "############################################"
[ "$TOTAL_FAIL" -eq 0 ] || exit 1
