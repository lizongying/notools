#!/usr/bin/env python3
"""Pixel-exact comparison for WebP interoperability testing.

Direction A: dwebp decode of noimg-encoded webp vs original (PAM/PPM).
Direction B: noimg decode of cwebp-lossless webp vs original.
"""
import struct, sys, os

DIR = '/tmp/webp-interop'

def parse_pnm(path):
    with open(path, 'rb') as f:
        data = f.read()
    # P6 (PPM), P5 (PGM), P7 (PAM)
    if data[:2] == b'P7':
        # PAM: header ends with ENDHDR\n
        end = data.index(b'ENDHDR\n') + len(b'ENDHDR\n')
        header = data[:end].decode()
        w = h = d = 0; depth = 0; maxval = 255
        for line in header.splitlines():
            parts = line.split()
            if not parts: continue
            if parts[0] == 'WIDTH': w = int(parts[1])
            elif parts[0] == 'HEIGHT': h = int(parts[1])
            elif parts[0] == 'DEPTH': depth = int(parts[1])
            elif parts[0] == 'MAXVAL': maxval = int(parts[1])
        return w, h, depth, data[end:]
    magic = data[:2]
    # P6/P5: header = whitespace-separated tokens, comments with #
    idx = 2
    vals = []
    while len(vals) < 3:
        while idx < len(data) and data[idx:idx+1].isspace(): idx += 1
        if data[idx:idx+1] == b'#':
            while idx < len(data) and data[idx] != 0x0a: idx += 1
            continue
        start = idx
        while idx < len(data) and not data[idx:idx+1].isspace(): idx += 1
        vals.append(int(data[start:idx]))
    idx += 1  # single whitespace after maxval
    w, h, maxval = vals
    depth = 3 if magic == b'P6' else 1
    return w, h, depth, data[idx:]

def compare(a_path, b_path, label, check_alpha=False):
    aw, ah, ad, a = parse_pnm(a_path)
    bw, bh, bd, b = parse_pnm(b_path)
    if (aw, ah) != (bw, bh):
        print(f'FAIL {label}: dims {aw}x{ah} vs {bw}x{bh}')
        return False
    if ad == bd and a == b:
        print(f'PASS {label}: pixel-exact ({aw}x{ah}x{ad})')
        return True
    # handle RGBA vs RGB (dwebp may add alpha=255)
    if {ad, bd} <= {3, 4} and ad != bd:
        n = aw * ah
        if ad == 4 and bd == 3:
            rgba, rgb = a, b
        elif ad == 3 and bd == 4:
            rgba, rgb = b, a
        else:
            rgba = rgb = None
        if rgba is not None:
            ok = True
            for i in range(n):
                r4 = rgba[i*4:(i+1)*4]; r3 = rgb[i*3:(i+1)*3]
                if r4[:3] != r3: ok = False; break
                if check_alpha and r4[3] != 255: ok = False; break
            if ok:
                print(f'PASS {label}: pixel-exact ({aw}x{ah}, RGB vs RGBA alpha=255)')
                return True
    # report first diff
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            px = i // ad if ad else 0
            print(f'FAIL {label}: first byte diff at {i} (pixel {px // aw},{px % aw}): {a[i]} vs {b[i]}')
            break
    else:
        print(f'FAIL {label}: length {len(a)} vs {len(b)}')
    return False

def main():
    all_ok = True
    # Direction A: dwebp output (d1.pam..d4.pam) vs originals
    a_map = [('orig1.ppm', 'd1.pam'), ('orig2.ppm', 'd2.pam'),
             ('orig3.ppm', 'd3.pam'), ('orig4.pam', 'd4.pam')]
    for orig, dec in a_map:
        if not os.path.exists(DIR + '/' + dec):
            print(f'SKIP A: {dec} missing'); all_ok = False; continue
        all_ok &= compare(DIR + '/' + orig, DIR + '/' + dec, f'A {orig} vs {dec}')
    # Direction B: noimg decode (b1..b4) vs originals
    b_map = [('orig1.ppm', 'b1.ppm'), ('orig2.ppm', 'b2.ppm'),
             ('orig3.ppm', 'b3.ppm'), ('orig4.pam', 'b4.pam')]
    for orig, dec in b_map:
        if not os.path.exists(DIR + '/' + dec):
            print(f'SKIP B: {dec} missing'); all_ok = False; continue
        all_ok &= compare(DIR + '/' + orig, DIR + '/' + dec, f'B {orig} vs {dec}')
    print('--- ALL PASS ---' if all_ok else '--- SOME FAILED ---')
    sys.exit(0 if all_ok else 1)

if __name__ == '__main__':
    main()
