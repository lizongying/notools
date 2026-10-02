#!/usr/bin/env python3
"""cross_check.py — validate noimg PNG/JPEG encode+decode against Pillow.

Phase 1 (default): 
  - PNG: noimg-encoded PNG must decode (Pillow) byte-exact vs ground truth.
  - PNG: noimg's own decode round-trip (_png_rt.ppm) must be byte-exact vs truth.
  - JPEG: noimg-encoded JPEG must decode (Pillow) with correct size/mode and
    reasonable MAE vs ground truth; noimg's own decode (_jpg_rt.ppm) must be
    close to Pillow's decode of the same JPEG.
  - Writes Pillow-generated reference JPEGs (P_*.jpg) for decoder validation.
Phase 2 (--phase2): compare noimg decode of P_*.jpg (P_*_rt.ppm) against
  Pillow's own decode of the same files.
"""
import sys, os
import numpy as np
from PIL import Image

D = '/tmp/cross'
fails = []
def check(name, cond, detail=''):
    tag = 'PASS' if cond else 'FAIL'
    print(f'[{tag}] {name}' + (f'  ({detail})' if detail else ''))
    if not cond:
        fails.append(name)

def load_truth_pnm(path):
    """Load noimg PPM/PGM (P5/P6) via Pillow as reference pixels."""
    im = Image.open(path)
    return im

def mae(a, b):
    a = a.astype(np.int32); b = b.astype(np.int32)
    return float(np.abs(a - b).mean())

# ---------- Phase 1 ----------
if '--phase2' not in sys.argv:
    # --- PNG encode: Pillow decodes noimg PNG, compare to ground truth ---
    for name in ['A', 'C', 'D', 'E']:
        truth = np.asarray(load_truth_pnm(f'{D}/{name}.ppm').convert('RGB'))
        got = np.asarray(Image.open(f'{D}/{name}.png').convert('RGB'))
        check(f'PNG encode {name}: Pillow decode == PPM truth (exact)',
              got.shape == truth.shape and np.array_equal(got, truth),
              f'shape={got.shape}')

    # B is RGBA: no PPM truth; use noimg's own PNG round-trip as truth source
    bpng = Image.open(f'{D}/B.png')
    check('PNG encode B: mode RGBA, 32x32', bpng.mode == 'RGBA' and bpng.size == (32, 32),
          f'mode={bpng.mode} size={bpng.size}')
    brt = Image.open(f'{D}/B_png_rt.png')  # noimg decoded its own PNG
    check('PNG decode B: noimg round-trip exact (RGBA)',
          np.array_equal(np.asarray(brt), np.asarray(bpng)), f'mode={brt.mode}')

    # --- PNG decode: noimg round-trip PPM vs truth ---
    for name in ['A', 'C', 'D', 'E']:
        truth = np.asarray(load_truth_pnm(f'{D}/{name}.ppm').convert('RGB'))
        rt = np.asarray(load_truth_pnm(f'{D}/{name}_png_rt.ppm').convert('RGB'))
        check(f'PNG decode {name}: noimg round-trip == truth (exact)',
              np.array_equal(rt, truth), f'shape={rt.shape}')

    # --- JPEG encode: Pillow decodes noimg JPEG ---
    # (name, truth source, mode, jpeg file)
    jpeg_cases = [
        ('A',      f'{D}/A.ppm', 'RGB', ['A.jpg', 'A_q40.jpg', 'A_444.jpg']),
        ('C',      f'{D}/C.ppm', 'L',   ['C.jpg']),
        ('D',      f'{D}/D.ppm', 'RGB', ['D.jpg', 'D_444.jpg']),
        ('E',      f'{D}/E.ppm', 'RGB', ['E.jpg', 'E_q40.jpg', 'E_444.jpg']),
    ]
    for name, truth_path, mode, files in jpeg_cases:
        truth = np.asarray(load_truth_pnm(truth_path).convert(mode))
        for f in files:
            im = Image.open(f'{D}/{f}')
            ok_mode = (im.mode == mode) or (mode == 'RGB' and im.mode in ('RGB', 'YCbCr'))
            check(f'JPEG encode {f}: size/mode', im.size == truth.shape[1::-1] and ok_mode,
                  f'mode={im.mode} size={im.size}')
            got = np.asarray(im.convert(mode))
            m = mae(got, truth)
            check(f'JPEG encode {f}: MAE vs truth < 50', m < 50, f'mae={m:.1f}')
            # noimg's own decode of the same JPEG should match Pillow's decode closely
            stem = f.rsplit('.', 1)[0]
            rt_path = f'{D}/{name}_jpg_rt.ppm' if f == f'{name}.jpg' else None
            if rt_path and os.path.exists(rt_path):
                rt = np.asarray(load_truth_pnm(rt_path).convert(mode))
                m2 = mae(rt, got)
                check(f'JPEG decode {name}: noimg decode vs Pillow decode MAE < 8', m2 < 8, f'mae={m2:.1f}')

    # B (RGBA): jpeg drops alpha; compare RGB channels vs B.png
    btruth = np.asarray(bpng.convert('RGB'))
    for f in ['B.jpg', 'B_q40.jpg', 'B_444.jpg']:
        im = Image.open(f'{D}/{f}')
        check(f'JPEG encode {f}: size 32x32', im.size == (32, 32), f'size={im.size}')
        m = mae(np.asarray(im.convert('RGB')), btruth)
        check(f'JPEG encode {f}: MAE vs B.png RGB < 50', m < 50, f'mae={m:.1f}')

    # --- Write Pillow reference JPEGs for decoder validation (phase 2) ---
    for name, truth_path, mode in [('A', f'{D}/A.ppm', 'RGB'), ('C', f'{D}/C.ppm', 'L'),
                                    ('D', f'{D}/D.ppm', 'RGB'), ('E', f'{D}/E.ppm', 'RGB')]:
        im = load_truth_pnm(truth_path)
        im.save(f'{D}/P_{name}.jpg', quality=90)            # 4:2:0 baseline
        im.save(f'{D}/P_{name}_q30.jpg', quality=30)        # low quality
        if mode == 'RGB':
            im.save(f'{D}/P_{name}_444.jpg', quality=90, subsampling=0)  # 4:4:4
    print('Wrote Pillow reference JPEGs (P_*.jpg)')

# ---------- Phase 2 ----------
else:
    for name in ['A', 'C', 'D', 'E']:
        truth_im = load_truth_pnm(f'{D}/{name}.ppm')
        for suffix in ['', '_q30', '_444']:
            src = f'{D}/P_{name}{suffix}.jpg'
            if not os.path.exists(src):
                continue
            mode = 'L' if name == 'C' else 'RGB'
            ref = np.asarray(Image.open(src).convert(mode))
            rt = np.asarray(load_truth_pnm(f'{D}/P_{name}{suffix}_rt.ppm').convert(mode))
            ok_shape = rt.shape == ref.shape
            m = mae(rt, ref) if ok_shape else 999
            check(f'JPEG decode {name}{suffix}: noimg vs Pillow MAE < 8', ok_shape and m < 8,
                  f'shape={rt.shape} mae={m:.1f}')

print()
if fails:
    print(f'RESULT: {len(fails)} FAILURES: {fails}')
    sys.exit(1)
print('RESULT: ALL PASS')
