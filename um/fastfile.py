"""Call of Duty FastFile (.ff) inspector and script/rawfile extractor.

    um fastfile list zone/english/patch.ff
    um fastfile dump zone/english/patch.ff -o extracted/
    um fastfile dump zone/english/nazi_zombie_factory.ff -o extracted/

Decompresses retail Call of Duty: World at War (T4) and Call of Duty 4 (IW 3.0)
FastFiles and extracts all embedded RawFiles (GSC scripts, CSC client scripts,
menu files, CSV string/sound tables, arena files, and configs). In these titles,
GSC/CSC gameplay scripts are stored as 100% human-readable plain text source.
"""
from __future__ import annotations

import os
import re
import struct
import sys
import zlib
from pathlib import Path

from um.common import die


RAWFILE_PATTERN = re.compile(
    rb"\xff\xff\xff\xff(.{4})\xff\xff\xff\xff([a-zA-Z0-9_/\\.-]+(?:\.[a-zA-Z0-9_]+))\x00",
    re.DOTALL,
)


SUPPORTED_VERSIONS = {
    387: "Call of Duty: World at War (Treyarch T4)",
    5: "Call of Duty 4: Modern Warfare (IW 3.0)",
    334: "Call of Duty 4: Modern Warfare (IW 3.0 asset v334)",
}


def decompress_fastfile(path: str | Path) -> tuple[int, bytes]:
    """Decompress a Call of Duty FastFile, returning (version, decompressed_bytes)."""
    p = Path(path)
    if not p.is_file():
        die(f"FastFile not found: {p}")

    with open(p, "rb") as f:
        magic = f.read(8)
        if magic not in (b"IWffu100", b"IWff0100"):
            die(f"unrecognized FastFile header magic: {magic!r} in {p.name}")
        version = struct.unpack("<I", f.read(4))[0]
        compressed_data = f.read()

    if version not in SUPPORTED_VERSIONS:
        print(
            f"WARNING: FastFile version {version} detected in {p.name}.\n"
            f"  This extractor specifically targets Treyarch T4 (WaW v387) and IW 3.0 (CoD4 v334).\n"
            f"  Later IW engines (MW2/IW 4.0, Black Ops/T5, BO2/T6) use different layouts, encryption,\n"
            f"  or compiled GSC bytecode instead of plain-text RawFiles.",
            file=sys.stderr,
        )

    try:
        decompressed = zlib.decompress(compressed_data)
    except zlib.error as e:
        die(f"failed to decompress {p.name}: {e}")

    return version, decompressed


def extract_rawfiles(data: bytes) -> dict[str, bytes]:
    """Scan decompressed FastFile payload for serialized RawFile assets."""
    rawfiles = {}
    for m in RAWFILE_PATTERN.finditer(data):
        length = struct.unpack("<I", m.group(1))[0]
        name = m.group(2).decode("utf-8", errors="ignore").replace("\\", "/")
        start = m.end()

        # Sanity checks on length and file payload boundary
        if 0 < length <= (len(data) - start):
            payload = data[start : start + length]
            # Verify payload doesn't span out-of-bounds
            if len(payload) == length:
                rawfiles[name] = payload

    return rawfiles


def list_fastfile(path: str | Path):
    """List all embedded RawFiles within a FastFile."""
    version, data = decompress_fastfile(path)
    p = Path(path)
    files = extract_rawfiles(data)

    print(f"FastFile: {p.name} (version {version}, decompressed {len(data):,} bytes)")
    if not files:
        print("  no RawFiles (.gsc, .csc, .menu, .csv, .cfg) found in this FastFile.")
        return

    print(f"  found {len(files)} RawFiles:")
    total_bytes = 0
    for name, payload in sorted(files.items()):
        total_bytes += len(payload)
        print(f"    {len(payload):8,} B  {name}")
    print(f"  total raw content: {total_bytes:,} bytes across {len(files)} files.")


def dump_fastfile(path: str | Path, out_dir: str | Path | None = None):
    """Extract all embedded RawFiles to disk."""
    version, data = decompress_fastfile(path)
    p = Path(path)
    files = extract_rawfiles(data)

    target_dir = Path(out_dir) if out_dir else Path(p.stem + "_extracted")
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting {len(files)} files from {p.name} (version {version}) -> {target_dir}...")
    extracted_count = 0
    total_bytes = 0

    for name, payload in files.items():
        # Prevent directory traversal attacks
        clean_name = os.path.normpath(name).lstrip("/\\")
        if clean_name.startswith(".."):
            continue

        dest_file = target_dir / clean_name
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_bytes(payload)
        extracted_count += 1
        total_bytes += len(payload)

    print(f"Successfully extracted {extracted_count} files ({total_bytes:,} bytes) into {target_dir}/")


def main(a):
    if a.cmd == "list":
        list_fastfile(a.file)
    elif a.cmd == "dump":
        dump_fastfile(a.file, a.out)


def register(sub):
    import argparse

    p = sub.add_parser(
        "fastfile",
        help="inspect and extract Call of Duty FastFiles (.ff)",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")

    q = cs.add_parser("list", help="list GSCs, CSCs, menus, and raw assets inside a .ff file")
    q.add_argument("file", help="path to .ff FastFile")
    q.set_defaults(func=main)

    q = cs.add_parser("dump", help="extract all embedded scripts and rawfiles from a .ff file to disk")
    q.add_argument("file", help="path to .ff FastFile")
    q.add_argument("-o", "--out", help="destination directory (defaults to <name>_extracted/)")
    q.set_defaults(func=main)
