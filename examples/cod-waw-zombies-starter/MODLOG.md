# Mod Log: Call of Duty World at War Zombies Starter Example

## Context & Objectives
- **Target Game**: Call of Duty: World at War (v1.7 Steam / Retail).
- **Target Engine**: Treyarch T4 (IW 3.0 fork).
- **Goal**: Create an original, clean-room reference starter mod proving zero-linker live iteration via `.iwd` package overriding stock scripts and weapons.
- **Constraints**: No proprietary game assets or fastfiles redistributed; must strictly follow engine limits (HUD 31-element ceiling, `fontScale >= 1.0`).

## Chronology

### 2026-10-26 - Reconnaissance & Architecture
- Inspected game executable `CoDWaW.exe` (v1.7.1263).
- Confirmed virtual memory layout: 32-bit PE with Large Address Aware (`dontaskagain.LAA`) and community engine extension `T4M`.
- Evaluated mod loading order: Files inside `%LOCALAPPDATA%\Activision\CoDWaW\mods\<modname>\*.iwd` take precedence over compiled fastfile assets.

### 2026-10-26 - Script Implementation (`nazi_zombie_prototype.gsc`)
- Created custom entry hook overriding `maps/nazi_zombie_prototype.gsc`.
- Hooked `level waittill("connected", player)` and `player waittill("spawned_player")`.
- Engineered safe HUD element constructor:
  - Ensured `fontScale` is explicitly `1.4` to avoid the known T4 engine crash where `fontScale < 1.0` triggers a floating-point underflow.
  - Added timer fade and explicit `hud destroy()` cleanup to guarantee active HUD elements never exceed the 31-element engine limit.
- Added loadout assignment giving custom weapon `colt_starter`.

### 2026-10-26 - Weapon Definition (`colt_starter`)
- Authored `weapons/sp/colt_starter` using standard CoD slash-delimited dictionary format:
  - Adjusted `clipSize` to `14`.
  - Adjusted `damage` to `150` (up from stock 20) with `minDamage` of `75`.
  - Configured proper animation and sound hooks for the M1911 Colt model.

### 2026-10-26 - Automation Packaging (`pack.py`)
- Authored Python packager creating zip archive `zombie_starter.iwd` with standard DEFLATE compression.
- Added `--install` flag targeting `%LOCALAPPDATA%\Activision\CoDWaW\mods\cod_waw_zombies_starter\`.
- Added `mod.arena` descriptor.
