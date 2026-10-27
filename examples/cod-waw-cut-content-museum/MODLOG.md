# Mod Log: Call of Duty World at War Cut Content Museum

## Context & Objectives
- **Target Game**: Call of Duty: World at War (v1.7 Steam / Retail).
- **Target Engine**: Treyarch T4 (IW 3.0 fork).
- **Goal**: Create an interactive cut-content and asset museum in singleplayer using Nacht der Untoten (`nazi_zombie_prototype`) geometry.
- **Scope**: Display unused SS Honor Guard soldier models, Waffen-SS variants, cut weapons (Walther P38, Colt Dirty Harry, Scoped FG42, Panzerschreck), fast-travel teleporters, and interactive exhibits.

## Chronology

### 2026-10-26 - Asset Reconnaissance
- Inspected compiled fastfiles (`zone/english/nazi_zombie_prototype.ff` and `zone/english/common.ff`).
- Confirmed unused SS Honor Guard models are compiled in the retail `.ff` container:
  - `char_ger_honorgd_body1_1`, `char_ger_honorgd_body2_1`
  - `char_ger_honorguard_head1_1`, `char_ger_honorguard_head2_1`, `char_ger_honorgd_zombiehead1_1`
- Confirmed cut weapons and 3D world models in the container:
  - `weapon_ger_walther_pistol` / `walther`
  - `weapon_usa_colt45_pistol` / `colt_dirty_harry`
  - `weapon_ger_fg42_bipod_lmg` / `fg42`
  - `weapon_ger_panzerschreck_at` / `panzerschreck`
  - `weapon_usa_ray_gun` / `ray_gun`

### 2026-10-26 - Script Architecture (`nazi_zombie_prototype.gsc`)
- Overrode level entry point to suppress zombie rounds and clear all debris/doors (`zombie_debris`, `zombie_door`).
- Built Character Exhibit Wing with life-size pedestals (`clutter_berlin_crate_01`) and standing mannequins with head attachments (`Attach(model, "", true)`).
- Built Weapon Arsenal Wing upstairs with floating, 360-degree rotating models and proximity interaction prompts.
- Built two-way fast-travel teleporters connecting Ground Floor Atrium and Upstairs Loft.
- Added infinite ammunition monitor and invulnerability for seamless museum exploration.

### 2026-10-26 - Packaging & Deployment
- Authored `pack.py` with automatic DEFLATE packaging and `--install` targeting `%LOCALAPPDATA%\Activision\CoDWaW\mods\cod_waw_cut_content_museum\`.
- Verified packaging: generated `z_cut_content_museum.iwd` (9,671 bytes) and deployed with `mod.arena`.
