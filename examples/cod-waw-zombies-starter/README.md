# Call of Duty: World at War: Zombies Starter Mod

An original, clean-room reference example for **Call of Duty: World at War** (Treyarch T4 engine / IW 3.0 fork, SP/Co-op v1.7).

It demonstrates the engine's zero-linker live iteration workflow: overriding stock script files and deploying custom weapon definitions directly through a `.iwd` archive in `%LOCALAPPDATA%\Activision\CoDWaW\mods\<modname>\`, bypassing slow fastfile compiling and zone linking.

---

## What this example demonstrates

1. **Zero-Linker Script Overriding**:
   In Treyarch T4, any file present inside a loaded mod's `.iwd` takes precedence over files linked into the base game fastfiles (`.ff`). By providing `maps/nazi_zombie_prototype.gsc`, this mod completely overrides Nacht der Untoten's entry script without touching the user's installation or requiring the CoD:WaW Mod Tools linker.

2. **Custom Weapon Definition**:
   Provides `weapons/sp/colt_starter`, an enhanced M1911 Colt .45 featuring a 14-round magazine, 150 base damage (up from 20), and adjusted recoil.

3. **Safe HUD Engineering**:
   Demonstrates how to safely draw intro HUD text without triggering known engine crashes:
   - **Scale underflow bug**: `fontScale` must always be `>= 1.0`. Any value `< 1.0` (such as `0.8`) triggers a floating-point underflow in the T4 rendering pipeline that crashes `CoDWaW.exe`.
   - **HUD element ceiling**: Call of Duty enforces a strict limit of 31 active HUD elements per player (`MAX_HUDELEMENTS = 31`). The script fades and destroys (`hud destroy()`) the intro banner once played to avoid leaking HUD slots.

---

## Tested setup

- **Game**: Call of Duty: World at War (Steam v1.7, T4 SP/Co-op).
- **Engine**: Treyarch T4 (IW 3.0 derivative, 32-bit x86 native).
- **System**: Windows 11 x64, with or without T4M/LAA patches.
- **Dependencies**: Python 3.10+ (for `pack.py`). No proprietary SDKs, Mod Tools, or Steam Workshop tools required.

---

## File Structure

```text
cod-waw-zombies-starter/
├── maps/
│   └── nazi_zombie_prototype.gsc  # Overrides Nacht der Untoten map script
├── weapons/sp/
│   └── colt_starter               # Custom weapon properties dictionary
├── mod.arena                      # Map descriptor for CoD:WaW in-game menu
├── pack.py                        # Zip packager and local mod installer
├── MODLOG.md                      # Development and verification journal
└── README.md                      # This guide
```

---

## Packaging and Installation

### Option 1: One-Click Build and Install
Run the packaging script with the `--install` flag:

```powershell
python pack.py --install
```

This compiles `zombie_starter.iwd` and copies it along with `mod.arena` directly to:
`%LOCALAPPDATA%\Activision\CoDWaW\mods\cod_waw_zombies_starter\`

### Option 2: Manual Packaging
To build the `.iwd` archive without installing:

```powershell
python pack.py
```

Move the resulting `zombie_starter.iwd` and `mod.arena` to your `%LOCALAPPDATA%\Activision\CoDWaW\mods\cod_waw_zombies_starter\` folder.

---

## Launching the Mod in Game

1. Launch Call of Duty: World at War (Singleplayer / Co-op).
2. From the Main Menu, click **Mods**.
3. Select `cod_waw_zombies_starter` and click **Launch**. The game will restart with the mod active.
4. Open the developer console (`~`) and run:
   ```text
   devmap nazi_zombie_prototype
   ```
   Or select **Solo** -> **Nacht der Untoten**.
5. Upon spawning into the mystery room:
   - Green banner `"ZOMBIES STARTER MOD LOADED"` appears on screen and cleanly fades out after 4 seconds.
   - The player automatically equips `colt_starter` with 14 rounds in the magazine and high one-shot capability on early rounds.
