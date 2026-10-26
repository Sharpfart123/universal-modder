#!/usr/bin/env python3
"""Packs the Call of Duty: World at War Zombies starter mod into a game-ready .iwd archive."""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import zipfile
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Package Call of Duty: World at War Zombies starter mod.")
    ap.add_argument("--out", "-o", default="zombie_starter.iwd", help="Output .iwd filename (default: zombie_starter.iwd)")
    ap.add_argument("--install", action="store_true", help="Install directly to %%LOCALAPPDATA%%\\Activision\\CoDWaW\\mods\\cod_waw_zombies_starter")
    args = ap.parse_args()

    mod_dir = Path(__file__).resolve().parent
    out_iwd = mod_dir / args.out

    print(f"Packaging {out_iwd.name}...")
    with zipfile.ZipFile(out_iwd, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for folder in ["maps", "weapons"]:
            target = mod_dir / folder
            if target.exists():
                for root, _, files in os.walk(target):
                    for file in files:
                        p = Path(root) / file
                        arcname = p.relative_to(mod_dir).as_posix()
                        print(f"  + {arcname}")
                        zf.write(p, arcname)

    print(f"Successfully created {out_iwd} ({out_iwd.stat().st_size:,} bytes).")

    if args.install:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            print("ERROR: LOCALAPPDATA environment variable not found.", file=sys.stderr)
            sys.exit(1)
        target_mod_dir = Path(local_app_data) / "Activision" / "CoDWaW" / "mods" / "cod_waw_zombies_starter"
        target_mod_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out_iwd, target_mod_dir / out_iwd.name)
        arena_src = mod_dir / "mod.arena"
        if arena_src.exists():
            shutil.copy2(arena_src, target_mod_dir / "mod.arena")
        print(f"Installed mod to: {target_mod_dir}")
        print("Launch CoDWaW, select Mods -> 'cod_waw_zombies_starter', and launch Nacht der Untoten.")


if __name__ == "__main__":
    main()
