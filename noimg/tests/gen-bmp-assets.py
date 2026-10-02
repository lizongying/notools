#!/usr/bin/env python3
# gen_bmp.py — build BMP sub-format files + a 24-bit reference for noimg decoder testing.
# All formats are LOSSLESS for the chosen source (565-exact palette of <=16 colors,
# so expected == source). Saves reference24.ppm (P6) and the generated BMPs.
import struct, sys
import os as _os
OUT = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bmp-assets")
_os.makedirs(OUT, exist_ok=True)
W, H = 16, 12

# 16-color 565-exact palette: r in {0,8,16,24}, g in {0,4,8,12}, b in {0,8}
def palette(k):
    r = (k % 4) * 8
    g = ((k // 4) % 4) * 4
    b = (k % 2) * 8
    return (r, g, b)

# source: pixel = palette[(x + y) % 16]
S = [[palette((x + y) % 16) for x in range(W)] for y in range(H)]

# 16-bit (565) is quantized: the 8-bit channels do not all round-trip. The
# correct reference for the 16-bit decode is the 565 round-trip of the source.
def to565(r, g, b):
    return ((r // 8) << 11) | ((g // 4) << 5) | (b // 8)

def from565(val):
    r = ((val >> 11) & 31) * 255 // 31
    g = ((val >> 5) & 63) * 255 // 63
    b = (val & 31) * 255 // 31
    return (r, g, b)

S16 = [[from565(to565(*S[y][x])) for x in range(W)] for y in range(H)]

def write_ppm(path, img):
    with open(path, 'wb') as f:
        f.write(b'P6\n%d %d\n255\n' % (W, H))
        for y in range(H):
            for x in range(W):
                r, g, b = img[y][x]
                f.write(bytes([r, g, b]))

write_ppm(OUT + '/reference24.ppm', S)
write_ppm(OUT + '/reference16.ppm', S16)

def bmp_file_header(data_offset, bpp, compression, w, h, pal_count):
    hdr = bytearray()
    hdr += b'BM'
    hdr += struct.pack('<I', 0)  # placeholder; each builder recomputes
    hdr += struct.pack('<HH', 0, 0)
    hdr += struct.pack('<I', data_offset)
    return hdr

def dib_header(w, h, bpp, compression, colors_used=0):
    hdr = bytearray()
    hdr += struct.pack('<I', 40)
    hdr += struct.pack('<i', w)
    hdr += struct.pack('<i', h)
    hdr += struct.pack('<H', 1)  # planes
    hdr += struct.pack('<H', bpp)
    hdr += struct.pack('<I', compression)
    hdr += struct.pack('<I', 0)  # image size (0 = ok)
    hdr += struct.pack('<II', 2835, 2835)
    hdr += struct.pack('<I', colors_used)
    hdr += struct.pack('<I', 0)
    return hdr

# palette bytes (B,G,R,0) * count
def palette_bytes(count):
    pb = bytearray()
    for k in range(count):
        r, g, b = palette(k)
        pb += bytes([b, g, r, 0])
    return pb

PAL16 = palette_bytes(16)
PAL2 = bytearray([0, 0, 0, 0, 255, 255, 255, 0])  # black, white

def row_pad(row_bytes):
    return (4 - (row_bytes % 4)) % 4

# 24-bit BI_RGB
def build_24():
    pix = bytearray()
    for y in range(H - 1, -1, -1):  # bottom-up
        for x in range(W):
            r, g, b = S[y][x]
            pix += bytes([b, g, r])
        pix += b'\x00' * row_pad(W * 3)
    data_off = 54
    out = bmp_file_header(data_off, 24, 0, W, H, 0)
    # fix filesize
    filesize = 14 + 40 + len(pix)
    out = bytearray(b'BM') + struct.pack('<I', filesize) + struct.pack('<HH', 0, 0) + struct.pack('<I', data_off)
    out += dib_header(W, H, 24, 0)
    out += pix
    return out

# 32-bit BI_RGB (BGRA)
def build_32():
    pix = bytearray()
    for y in range(H - 1, -1, -1):
        for x in range(W):
            r, g, b = S[y][x]
            pix += bytes([b, g, r, 255])
        pix += b'\x00' * row_pad(W * 4)
    data_off = 54
    filesize = 14 + 40 + len(pix)
    out = bytearray(b'BM') + struct.pack('<I', filesize) + struct.pack('<HH', 0, 0) + struct.pack('<I', data_off)
    out += dib_header(W, H, 32, 0)
    out += pix
    return out

# 16-bit 565 BI_RGB
def build_16():
    pix = bytearray()
    for y in range(H - 1, -1, -1):
        for x in range(W):
            r, g, b = S[y][x]
            val = ((r // 8) << 11) | ((g // 4) << 5) | (b // 8)
            pix += struct.pack('<H', val)
        pix += b'\x00' * row_pad(W * 2)
    data_off = 54
    filesize = 14 + 40 + len(pix)
    out = bytearray(b'BM') + struct.pack('<I', filesize) + struct.pack('<HH', 0, 0) + struct.pack('<I', data_off)
    out += dib_header(W, H, 16, 0)
    out += pix
    return out

# 8-bit paletted BI_RGB
def build_8():
    pix = bytearray()
    for y in range(H - 1, -1, -1):
        for x in range(W):
            idx = (x + y) % 16
            pix += bytes([idx])
        pix += b'\x00' * row_pad(W)
    data_off = 54 + 16 * 4
    filesize = 14 + 40 + len(PAL16) + len(pix)
    out = bytearray(b'BM') + struct.pack('<I', filesize) + struct.pack('<HH', 0, 0) + struct.pack('<I', data_off)
    out += dib_header(W, H, 8, 0, colors_used=16)
    out += PAL16
    out += pix
    return out

# 4-bit paletted BI_RGB
def build_4():
    pix = bytearray()
    for y in range(H - 1, -1, -1):
        for x in range(0, W, 2):
            hi = (x + y) % 16
            lo = (x + 1 + y) % 16 if x + 1 < W else 0
            pix += bytes([(hi << 4) | lo])
        pix += b'\x00' * row_pad(W // 2)
    data_off = 54 + 16 * 4
    filesize = 14 + 40 + len(PAL16) + len(pix)
    out = bytearray(b'BM') + struct.pack('<I', filesize) + struct.pack('<HH', 0, 0) + struct.pack('<I', data_off)
    out += dib_header(W, H, 4, 0, colors_used=16)
    out += PAL16
    out += pix
    return out

# 1-bit BI_RGB
def build_1():
    pix = bytearray()
    for y in range(H - 1, -1, -1):
        for x in range(0, W, 8):
            byte = 0
            for bit in range(8):
                xi = x + bit
                if xi < W:
                    val = 1 if ((xi + y) % 2 == 0) else 0  # checkerboard white/black
                    byte |= (val << (7 - bit))
            pix += bytes([byte])
        pix += b'\x00' * row_pad((W + 7) // 8)
    data_off = 54 + 2 * 4
    filesize = 14 + 40 + len(PAL2) + len(pix)
    out = bytearray(b'BM') + struct.pack('<I', filesize) + struct.pack('<HH', 0, 0) + struct.pack('<I', data_off)
    out += dib_header(W, H, 1, 0, colors_used=2)
    out += PAL2
    out += pix
    return out

# 1-bit checkerboard reference
S1 = [[(255, 255, 255) if ((x + y) % 2 == 0) else (0, 0, 0) for x in range(W)] for y in range(H)]
write_ppm(OUT + '/reference1.ppm', S1)

# RLE8 (compression 1) over 8-bit indices
def rle8_encode(indices):
    # indices: list per row (bottom-up order)
    out = bytearray()
    for row in indices:
        x = 0
        while x < len(row):
            runval = row[x]
            run = 1
            while x + run < len(row) and run < 255 and row[x + run] == runval:
                run += 1
            # emitted as encoded run if run>=2 helps, but spec allows literal for run<2 too; use encoded when run>=2
            if run >= 2:
                out += bytes([run, runval])
                x += run
            else:
                # literal: gather a run of non-repeating or until max length
                lit = [runval]
                x += 1
                while x < len(row) and len(lit) < 255 and not (len(lit) >= 2 and row[x] == row[x-1]):
                    # stop literal if we'd start a 2+ run
                    if len(lit) >= 1 and row[x] == lit[-1]:
                        break
                    lit.append(row[x])
                    x += 1
                out += bytes([0, len(lit)])
                out += bytes(lit)
                if len(lit) % 2 == 1:
                    out += b'\x00'
        out += b'\x00\x00'  # end of row
    out += b'\x00\x01'  # end of bitmap
    return out

# RLE4 (compression 2) over 4-bit indices
def rle4_encode(indices):
    out = bytearray()
    for row in indices:
        x = 0
        while x < len(row):
            runval = row[x] & 15
            run = 1
            while x + run < len(row) and run < 255 and (row[x + run] & 15) == runval:
                run += 1
            if run >= 2:
                out += bytes([run, (runval << 4) | runval])
                x += run
            else:
                litnibbles = [runval]
                x += 1
                while x < len(row) and len(litnibbles) < 255:
                    if len(litnibbles) >= 1 and (row[x] & 15) == litnibbles[-1]:
                        break
                    litnibbles.append(row[x] & 15)
                    x += 1
                out += bytes([0, len(litnibbles)])
                for i in range(0, len(litnibbles), 2):
                    hi = litnibbles[i]
                    lo = litnibbles[i + 1] if i + 1 < len(litnibbles) else 0
                    out += bytes([(hi << 4) | lo])
                if len(litnibbles) % 2 == 1:
                    out += b'\x00'
        out += b'\x00\x00'
    out += b'\x00\x01'
    return out

def build_rle8():
    idx_rows = []
    for y in range(H - 1, -1, -1):
        idx_rows.append([(x + y) % 16 for x in range(W)])
    pix = rle8_encode(idx_rows)
    data_off = 54 + 16 * 4
    filesize = 14 + 40 + len(PAL16) + len(pix)
    out = bytearray(b'BM') + struct.pack('<I', filesize) + struct.pack('<HH', 0, 0) + struct.pack('<I', data_off)
    out += dib_header(W, H, 8, 1, colors_used=16)
    out += PAL16
    out += pix
    return out

def build_rle4():
    idx_rows = []
    for y in range(H - 1, -1, -1):
        idx_rows.append([(x + y) % 16 for x in range(W)])
    pix = rle4_encode(idx_rows)
    data_off = 54 + 16 * 4
    filesize = 14 + 40 + len(PAL16) + len(pix)
    out = bytearray(b'BM') + struct.pack('<I', filesize) + struct.pack('<HH', 0, 0) + struct.pack('<I', data_off)
    out += dib_header(W, H, 4, 2, colors_used=16)
    out += PAL16
    out += pix
    return out

builders = {
    'f24': (build_24, 'reference24.ppm'),
    'f32': (build_32, 'reference24.ppm'),
    'f16': (build_16, 'reference16.ppm'),
    'f8': (build_8, 'reference24.ppm'),
    'f4': (build_4, 'reference24.ppm'),
    'f1': (build_1, 'reference1.ppm'),
    'rle8': (build_rle8, 'reference24.ppm'),
    'rle4': (build_rle4, 'reference24.ppm'),
}

for name, (fn, ref) in builders.items():
    data = fn()
    with open(OUT + '/' + name + '.bmp', 'wb') as f:
        f.write(data)
    print(f'wrote {name}.bmp ({len(data)} bytes) vs {ref}')

print('done')
