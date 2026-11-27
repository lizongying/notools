#!/usr/bin/env python3
"""Development-only differential and performance checks for nosync.

The production CLI never invokes Python or rsync. This script independently
implements the rsync weak checksum and a small delta oracle, then compares the
CLI result byte-for-byte with deterministic corpora.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import random
import resource
import shutil
import stat
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BIN = ROOT / "nosync" / "dist" / "nosync"
BLOCK = 4096
MASK = 0xFFFFFFFF


def weak_direct(data: bytes) -> int:
    s1 = 0
    s2 = 0
    for value in data:
        s1 = (s1 + value) & MASK
        s2 = (s2 + s1) & MASK
    return ((s2 << 16) | (s1 & 0xFFFF)) & MASK


def weak_roll(value: int, length: int, old: int, new: int) -> int:
    s1 = value & 0xFFFF
    s2 = value >> 16
    s1 = (s1 - old + new) & MASK
    s2 = (s2 - old * length + s1) & MASK
    return ((s2 << 16) | (s1 & 0xFFFF)) & MASK


def reference_delta(source: bytes, target: bytes, block: int = BLOCK) -> list[tuple]:
    signatures: dict[int, list[tuple[int, int, bytes]]] = {}
    for offset in range(0, len(target), block):
        data = target[offset : offset + block]
        signatures.setdefault(weak_direct(data), []).append(
            (offset, len(data), hashlib.sha256(data).digest())
        )

    operations: list[tuple] = []
    literal = bytearray()
    position = 0
    rolling = 0
    while position < len(source):
        remaining = len(source) - position
        length = min(block, remaining)
        window = source[position : position + length]
        value = weak_direct(window) if position == 0 else rolling
        matched = None
        checked = 0
        for offset, candidate_length, digest in signatures.get(value, []):
            if candidate_length != length:
                continue
            checked += 1
            if checked > 256:
                break
            if hashlib.sha256(window).digest() == digest:
                matched = (offset, length)
                break
        if matched is not None:
            if literal:
                operations.append(("literal", bytes(literal)))
                literal.clear()
            operations.append(("copy", matched[0], matched[1]))
            position += length
            next_length = min(block, len(source) - position)
            rolling = weak_direct(source[position : position + next_length]) if next_length else 0
            continue

        literal.append(source[position])
        if position == 0:
            rolling = weak_direct(window)
        else:
            rolling = weak_roll(value, length, source[position - 1], source[position])
        position += 1
        if position < len(source):
            next_length = min(block, len(source) - position)
            if next_length != length:
                rolling = weak_direct(source[position : position + next_length])
    if literal:
        operations.append(("literal", bytes(literal)))
    return operations


def apply_delta(target: bytes, operations: list[tuple]) -> bytes:
    output = bytearray()
    for operation in operations:
        if operation[0] == "literal":
            output.extend(operation[1])
        else:
            _, offset, length = operation
            output.extend(target[offset : offset + length])
    return bytes(output)


def parse_stats(output: str) -> dict[str, int]:
    values: dict[str, int] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.isdigit():
            values[key.strip()] = int(value)
    return values


def invoke(binary: Path, *args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(binary), *map(str, args)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=300,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"nosync {args!r} returned {result.returncode}, expected {expect}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot(root: Path) -> dict[str, tuple]:
    result: dict[str, tuple] = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs.sort()
        files.sort()
        for name in [".", *dirs, *files]:
            path = Path(directory) if name == "." else Path(directory) / name
            relative = "." if name == "." else str(path.relative_to(root))
            info = path.lstat()
            mode = stat.S_IMODE(info.st_mode)
            mtime = info.st_mtime_ns
            if stat.S_ISLNK(info.st_mode):
                payload = ("link", os.readlink(path))
            elif stat.S_ISDIR(info.st_mode):
                payload = ("dir",)
            elif stat.S_ISREG(info.st_mode):
                payload = ("file", file_hash(path))
            else:
                payload = ("other",)
            result[relative] = (info.st_mode, mode, mtime, payload)
    return result


def differential(binary: Path, work: Path) -> None:
    rng = random.Random(0x4E4F53594E43)
    blocks = [rng.randbytes(BLOCK) for _ in range(16)]
    target = b"".join(blocks[:12])
    cases = {
        "prepend": blocks[15] + target,
        "delete": b"".join(blocks[:4] + blocks[7:12]),
        "reorder": b"".join(blocks[i] for i in [8, 2, 11, 0, 6, 4, 10, 1, 9, 3, 7, 5]),
        "duplicates": b"".join([blocks[2]] * 12),
        "short-tail": b"".join(blocks[:11]) + blocks[11][:137],
        "mixed": blocks[14] + b"".join(blocks[i] for i in [5, 0, 5, 9, 2, 11, 2, 7]) + b"tail",
    }

    for name, source in cases.items():
        case = work / name
        source_path = case / "src" / "data"
        target_path = case / "dst" / "data"
        source_path.parent.mkdir(parents=True)
        invoke(binary, "--archive", "--stats", "--block-size", str(BLOCK), str(source_path.parent) + "/", str(case / "dst"))
        source_path.write_bytes(source)
        target_path.write_bytes(target)
        os.utime(target_path, (1700000000, 1700000000))
        result = invoke(
            binary,
            "--archive",
            "--stats",
            "--block-size",
            str(BLOCK),
            "--memory-limit",
            "16M",
            str(source_path.parent) + "/",
            str(case / "dst"),
        )
        assert target_path.read_bytes() == source, f"{name}: CLI output differs from source"
        operations = reference_delta(source, target)
        assert apply_delta(target, operations) == source, f"{name}: independent delta oracle failed"
        values = parse_stats(result.stdout)
        expected_reuse = {
            "prepend": len(target),
            "delete": len(source),
            "reorder": len(target),
            "duplicates": len(target),
            "short-tail": len(source) - 137,
            "mixed": 8 * BLOCK,
        }[name]
        assert values.get("reused-bytes") == expected_reuse, (
            f"{name}: unexpected reuse, expected {expected_reuse}: {values}"
        )
        assert values.get("whole-file-fallbacks") == 0, f"{name}: unexpected fallback: {values}"
        if name == "prepend":
            assert expected_reuse * 100 >= len(target) * 95
        print(f"PASS differential {name}: reused={values.get('reused-bytes', 0)}")


def dry_run_snapshot(binary: Path, work: Path) -> None:
    case = work / "dry-run"
    source = case / "src"
    target = case / "dst"
    source.mkdir(parents=True)
    target.mkdir()
    (source / "changed").write_bytes(b"new source")
    (target / "changed").write_bytes(b"old target")
    (target / "stale").write_bytes(b"delete candidate")
    os.chmod(target / "changed", 0o640)
    os.utime(target / "changed", (1700000000, 1700000000))
    os.utime(target, (1700000001, 1700000001))
    before = snapshot(target)
    invoke(
        binary,
        "--archive",
        "--checksum",
        "--delete",
        "--dry-run",
        str(source) + "/",
        str(target),
    )
    after = snapshot(target)
    assert before == after, "dry-run changed destination content, mode, mtime, or tree shape"
    print("PASS dry-run full-tree snapshot")


def performance(binary: Path, work: Path) -> None:
    manifest = work / "manifest-100k"
    source = manifest / "src"
    source.mkdir(parents=True)
    started = time.monotonic()
    for index in range(100_000):
        (source / f"file-{index:06d}").touch()
    created = time.monotonic() - started
    started = time.monotonic()
    result = subprocess.run(
        [
            str(binary),
            "--recursive",
            "--dry-run",
            "--memory-limit",
            "256M",
            str(source) + "/",
            str(manifest / "dst"),
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        timeout=600,
    )
    elapsed = time.monotonic() - started
    assert result.returncode == 0, f"100k manifest failed: {result.stderr}"
    assert elapsed < 300, f"100k manifest took {elapsed:.1f}s, possible quadratic behavior"
    print(f"PASS manifest 100k: create={created:.2f}s sync={elapsed:.2f}s")

    large = work / "delta-64m"
    large.mkdir()
    old_path = large / "old"
    source_path = large / "src"
    target_path = large / "dst"
    block = 65536
    repeated_block = hashlib.sha256(b"repeated-block").digest() * (block // 32)
    with old_path.open("wb") as handle:
        for index in range(1024):
            handle.write(hashlib.sha256(str(index).encode()).digest() * 2048)
    target_path.write_bytes(old_path.read_bytes())
    repeated = work / "repeated-64m"
    repeated.mkdir()
    repeated_source = repeated / "src"
    repeated_target = repeated / "dst"
    with repeated_source.open("wb") as output, repeated_target.open("wb") as target:
        for _ in range(16384):
            output.write(repeated_block)
            target.write(repeated_block)
    os.utime(repeated_target, (1700000000, 1700000000))
    repeated_result = invoke(
        binary, "--stats", "--block-size", str(block), "--memory-limit", "64M",
        str(repeated_source), str(repeated_target),
    )
    repeated_values = parse_stats(repeated_result.stdout)
    assert repeated_values.get("reused-bytes") == repeated_source.stat().st_size, repeated_values
    assert repeated_values.get("whole-file-fallbacks") == 0, repeated_values
    assert repeated_result.returncode == 0
    assert file_hash(repeated_source) == file_hash(repeated_target)
    print("PASS repeated blocks: bounded collision search and exact reconstruction")

    prefix = hashlib.sha256(b"prefix").digest() * 2048
    with source_path.open("wb") as output, old_path.open("rb") as source_handle:
        output.write(prefix)
        shutil.copyfileobj(source_handle, output, length=1024 * 1024)
    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    started = time.monotonic()
    result = invoke(
        binary,
        "--stats",
        "--block-size",
        str(block),
        "--memory-limit",
        "64M",
        str(source_path),
        str(target_path),
    )
    elapsed = time.monotonic() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    values = parse_stats(result.stdout)
    reused = values.get("reused-bytes", 0)
    assert reused * 100 >= old_path.stat().st_size * 95, f"64MiB reuse below 95%: {values}"
    assert file_hash(source_path) == file_hash(target_path), "64MiB delta output mismatch"
    rss = max(before, after) / (1024 * 1024 if sys.platform == "darwin" else 1024)
    assert rss < 512, f"64MiB delta peak child RSS too high: {rss:.1f} MiB"
    print(
        f"PASS delta 64MiB: reused={reused} literal={values.get('literal-bytes', 0)} "
        f"elapsed={elapsed:.2f}s peak-rss={rss:.1f}MiB"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, default=DEFAULT_BIN)
    parser.add_argument("--performance", action="store_true")
    args = parser.parse_args()
    binary = args.binary.resolve()
    if not binary.is_file():
        parser.error(f"binary not found: {binary}; build nosync first")

    temporary_root = ROOT / "tmp"
    temporary_root.mkdir(exist_ok=True)
    temporary = tempfile.mkdtemp(prefix="nosync-differential-", dir=temporary_root)
    work = Path(temporary)
    try:
        differential(binary, work)
        dry_run_snapshot(binary, work)
        if args.performance:
            performance(binary, work)
    finally:
        shutil.rmtree(work)
    print("ALL DIFFERENTIAL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
