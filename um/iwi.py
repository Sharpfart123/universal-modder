"""Call of Duty IWI v6 texture converter and decoder.

    um iwi png2iwi input.png output.iwi [--format dxt1|dxt5] [--mips]
    um iwi iwi2png input.iwi output.png

Converts between standard PNG images and Call of Duty: World at War / CoD4
IWI version 6 textures. Supports DXT1 (diffuse/opaque) and DXT5 (alpha/normal),
as well as reverse mipmap order required by the Treyarch T4 / IW 3.0 engine.
"""
from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from um.common import die

# IWI v6 Header Constants
IWI_MAGIC = b"IWi"
IWI_VERSION = 6

# Format IDs
FMT_ARGB8 = 0x01
FMT_RGB8 = 0x02
FMT_A8 = 0x04
FMT_DXT1 = 0x0B
FMT_DXT3 = 0x0C
FMT_DXT5 = 0x0D


def _rgb_to_565(rgb: np.ndarray) -> int:
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def _565_to_rgb(c: int) -> np.ndarray:
    r = (c >> 11) & 0x1F
    g = (c >> 5) & 0x3F
    b = c & 0x1F
    return np.array([(r * 255) // 31, (g * 255) // 63, (b * 255) // 31], dtype=np.uint8)


def _encode_dxt1_block(block_rgb: np.ndarray) -> bytes:
    pixels = block_rgb.reshape(16, 3)
    c_min = pixels.min(axis=0)
    c_max = pixels.max(axis=0)

    c0 = _rgb_to_565(c_max)
    c1 = _rgb_to_565(c_min)

    if c0 < c1:
        c0, c1 = c1, c0
        c_max, c_min = c_min, c_max
    elif c0 == c1:
        return struct.pack("<HHI", c0, c1, 0)

    c_max_f = c_max.astype(float)
    c_min_f = c_min.astype(float)
    pal = np.array([
        c_max_f,
        c_min_f,
        (2.0 * c_max_f + c_min_f) / 3.0,
        (c_max_f + 2.0 * c_min_f) / 3.0,
    ])

    diff = pixels[:, np.newaxis, :] - pal[np.newaxis, :, :]
    dist = (diff ** 2).sum(axis=2)
    best = np.argmin(dist, axis=1)

    mask = 0
    for idx, b in enumerate(best):
        mask |= int(b) << (idx * 2)

    return struct.pack("<HHI", c0, c1, mask)


def _encode_dxt5_alpha_block(alpha_block: np.ndarray) -> bytes:
    a_min = int(alpha_block.min())
    a_max = int(alpha_block.max())
    if a_max == a_min:
        return struct.pack("<BB", a_max, a_min) + b"\x00" * 6

    pal = [a_max, a_min]
    for i in range(1, 7):
        pal.append(int(((7 - i) * a_max + i * a_min) / 7))
    pal_arr = np.array(pal, dtype=float)

    diff = alpha_block[:, np.newaxis] - pal_arr[np.newaxis, :]
    dist = diff ** 2
    best = np.argmin(dist, axis=1)

    mask = 0
    for idx, b in enumerate(best):
        mask |= int(b) << (idx * 3)

    return struct.pack("<BB", a_max, a_min) + mask.to_bytes(6, "little")


def encode_dxt(image: Image.Image, fmt: str = "dxt1") -> bytes:
    """Encode a PIL Image to DXT1 or DXT5 raw payload."""
    w, h = image.size
    pad_w = (w + 3) & ~3
    pad_h = (h + 3) & ~3

    img = image.convert("RGBA")
    if (w, h) != (pad_w, pad_h):
        padded = Image.new("RGBA", (pad_w, pad_h), (0, 0, 0, 0))
        padded.paste(img, (0, 0))
        img = padded

    arr = np.array(img, dtype=np.uint8)
    out_blocks = []

    for by in range(0, pad_h, 4):
        for bx in range(0, pad_w, 4):
            block = arr[by : by + 4, bx : bx + 4]
            if fmt == "dxt5":
                alpha_block = block[:, :, 3].flatten()
                out_blocks.append(_encode_dxt5_alpha_block(alpha_block))
            color_block = block[:, :, :3]
            out_blocks.append(_encode_dxt1_block(color_block))

    return b"".join(out_blocks)


def png_to_iwi(src: str | Path, dst: str | Path, fmt_name: str = "dxt1", generate_mips: bool = False):
    """Convert PNG to Call of Duty IWI v6 format."""
    src_p = Path(src)
    dst_p = Path(dst)
    if not src_p.is_file():
        die(f"source image not found: {src_p}")

    im = Image.open(src_p)
    w, h = im.size

    fmt_id = FMT_DXT5 if fmt_name.lower() == "dxt5" else FMT_DXT1
    flags = 0xC1 if generate_mips else 0x03

    # Build mip levels
    mips = [im]
    if generate_mips:
        cur_w, cur_h = w, h
        while cur_w > 4 and cur_h > 4:
            cur_w = max(4, cur_w // 2)
            cur_h = max(4, cur_h // 2)
            mips.append(im.resize((cur_w, cur_h), Image.Resampling.LANCZOS))

    # Encode mips in reverse order: smallest first, full mip0 last
    encoded_mips = []
    for mip in reversed(mips):
        encoded_mips.append(encode_dxt(mip, fmt_name.lower()))

    # Calculate mip offsets from end
    header_len = 28
    total_len = header_len + sum(len(m) for m in encoded_mips)

    mip_offsets = [total_len, total_len, total_len, total_len]
    if generate_mips and len(mips) >= 4:
        # Offsets where mips end in the file
        cur_end = total_len
        # mip0 ends at total_len
        mip_offsets[0] = cur_end
        # mip1 ends before mip0
        cur_end -= len(encoded_mips[-1])
        mip_offsets[1] = cur_end
        # mip2 ends before mip1
        cur_end -= len(encoded_mips[-2])
        mip_offsets[2] = cur_end
        # mip3 ends before mip2
        cur_end -= len(encoded_mips[-3])
        mip_offsets[3] = cur_end

    header = (
        IWI_MAGIC
        + struct.pack("<BBBHHHIIII", IWI_VERSION, fmt_id, flags, h, w, 1, *mip_offsets)
    )

    dst_p.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_p, "wb") as f:
        f.write(header)
        for m in encoded_mips:
            f.write(m)

    print(f"Created IWI v6: {dst_p} ({w}x{h}, {fmt_name.upper()}, {total_len:,} bytes)")


def _decode_dxt1_block(data: bytes) -> np.ndarray:
    c0, c1, mask = struct.unpack("<HHI", data)
    p0 = _565_to_rgb(c0).astype(float)
    p1 = _565_to_rgb(c1).astype(float)

    if c0 > c1:
        pal = [p0, p1, (2.0 * p0 + p1) / 3.0, (p0 + 2.0 * p1) / 3.0]
    else:
        pal = [p0, p1, (p0 + p1) / 2.0, np.array([0, 0, 0], dtype=float)]

    pixels = np.zeros((16, 3), dtype=np.uint8)
    for idx in range(16):
        b = (mask >> (idx * 2)) & 3
        pixels[idx] = pal[b].astype(np.uint8)

    return pixels.reshape(4, 4, 3)


def _decode_dxt5_alpha_block(data: bytes) -> np.ndarray:
    a0, a1 = struct.unpack("<BB", data[:2])
    mask = int.from_bytes(data[2:], "little")

    if a0 > a1:
        pal = [float(a0), float(a1)]
        for i in range(1, 7):
            pal.append(((7 - i) * a0 + i * a1) / 7.0)
    else:
        pal = [float(a0), float(a1)]
        for i in range(1, 5):
            pal.append(((5 - i) * a0 + i * a1) / 5.0)
        pal.append(0.0)
        pal.append(255.0)

    alphas = np.zeros(16, dtype=np.uint8)
    for idx in range(16):
        b = (mask >> (idx * 3)) & 7
        alphas[idx] = int(pal[b])

    return alphas.reshape(4, 4)


def iwi_to_png(src: str | Path, dst: str | Path):
    """Decode a Call of Duty IWI v6 texture to PNG."""
    src_p = Path(src)
    dst_p = Path(dst)
    if not src_p.is_file():
        die(f"IWI file not found: {src_p}")

    with open(src_p, "rb") as f:
        data = f.read()

    if data[:3] != IWI_MAGIC:
        die("not a valid IWI file (bad magic)")
    ver = data[3]
    if ver != 6:
        die(f"unsupported IWI version: {ver} (expected version 6)")

    fmt_id, flags = struct.unpack("<BB", data[4:6])
    h, w, d = struct.unpack("<HHH", data[6:12])
    mip_offsets = struct.unpack("<IIII", data[12:28])

    # mip0 is stored at the end of the file
    mip0_end = mip_offsets[0]
    blocks_w = (w + 3) // 4
    blocks_h = (h + 3) // 4

    if fmt_id in (FMT_DXT1,):
        block_size = 8
        mip0_len = blocks_w * blocks_h * block_size
        mip0_start = mip0_end - mip0_len
        payload = data[mip0_start:mip0_end]

        img_arr = np.zeros((blocks_h * 4, blocks_w * 4, 3), dtype=np.uint8)
        offset = 0
        for by in range(blocks_h):
            for bx in range(blocks_w):
                bdata = payload[offset : offset + 8]
                img_arr[by * 4 : by * 4 + 4, bx * 4 : bx * 4 + 4] = _decode_dxt1_block(bdata)
                offset += 8

        out_img = Image.fromarray(img_arr[:h, :w], "RGB")

    elif fmt_id in (FMT_DXT3, FMT_DXT5):
        block_size = 16
        mip0_len = blocks_w * blocks_h * block_size
        mip0_start = mip0_end - mip0_len
        payload = data[mip0_start:mip0_end]

        img_arr = np.zeros((blocks_h * 4, blocks_w * 4, 4), dtype=np.uint8)
        offset = 0
        for by in range(blocks_h):
            for bx in range(blocks_w):
                bdata = payload[offset : offset + 16]
                alphas = _decode_dxt5_alpha_block(bdata[:8])
                rgb = _decode_dxt1_block(bdata[8:])
                img_arr[by * 4 : by * 4 + 4, bx * 4 : bx * 4 + 4, :3] = rgb
                img_arr[by * 4 : by * 4 + 4, bx * 4 : bx * 4 + 4, 3] = alphas
                offset += 16

        out_img = Image.fromarray(img_arr[:h, :w], "RGBA")
    else:
        die(f"unsupported format ID in IWI: 0x{fmt_id:02X}")

    dst_p.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(dst_p, "PNG")
    print(f"Decoded {src_p.name} -> {dst_p} ({w}x{h})")


def main(a):
    if a.cmd == "png2iwi":
        png_to_iwi(a.src, a.dst, a.format, a.mips)
    elif a.cmd == "iwi2png":
        iwi_to_png(a.src, a.dst)


def register(sub):
    p = sub.add_parser(
        "iwi",
        help="convert between PNG and Call of Duty IWI v6 textures",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")

    q = cs.add_parser("png2iwi", help="convert a PNG image into a game-ready IWI v6 file")
    q.add_argument("src", help="input PNG file")
    q.add_argument("dst", help="output IWI file")
    q.add_argument("--format", choices=["dxt1", "dxt5"], default="dxt1", help="texture compression (default: dxt1)")
    q.add_argument("--mips", action="store_true", help="generate reverse mipmap hierarchy")
    q.set_defaults(func=main)

    q = cs.add_parser("iwi2png", help="decode an in-game IWI v6 texture into a PNG image")
    q.add_argument("src", help="input IWI file")
    q.add_argument("dst", help="output PNG file")
    q.set_defaults(func=main)
