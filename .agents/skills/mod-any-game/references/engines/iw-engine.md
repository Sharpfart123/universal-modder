# Call of Duty IW Engine (IW 3.0 / Treyarch T4)

Covers **Call of Duty 4: Modern Warfare** and **Call of Duty: World at War** (PC Steam/retail x86), single-player, co-op/Zombies, and custom multiplayer.

**Identify.** Executables `CoDWaW.exe`, `CoDWaWmp.exe`, `iw3sp.exe`, `iw3mp.exe`. File formats: Fastfiles (`zone/<lang>/*.ff`), archive packages (`main/*.iwd`), loose folders (`raw/`, `mods/<name>/`), and mod tools (`bin/linker_pc.exe`, `cod2map.exe`, `cod2rad64.exe`, `CoDWaWRadiant.exe`).

---

## Engine Evolution: Why World at War (T4) Differs from Other CoD Titles

The "IW Engine" is not a static platform; it diverged significantly with each release. Techniques that work in World at War will fail in earlier or later titles:

| Engine / Game | Fastfile Version | GSC Script Format | Distinct Architecture |
|---|---|---|---|
| **IW 3.0** (*CoD4: Modern Warfare*) | `334` (`0x14E`) | Plain text RawFile | SP campaign & MP only. No Zombies, no dismemberment system. |
| **Treyarch T4** (*CoD: World at War*) | `387` (`0x183`) | Plain text RawFile | Forked from IW 3.0. Added Nazi Zombies (`_zombiemode`), 4-player co-op, limb gibbing/crawlers (`self.has_legs`), flamethrower charring masks (`clothcharr`), and Patch 1.4 script routing (`patch.ff`). |
| **IW 4.0** (*Modern Warfare 2*) | `276`+ | Encrypted / Packed | Encrypted FastFiles, altered asset headers, Steamworks matchmaking. |
| **Treyarch T5** (*Black Ops 1*) | `473` (`0x1D9`) | Plain text RawFile | Memory partitions (zones 0-4), Lua UI integration, SndBank resident audio. |
| **Treyarch T6+** (*Black Ops 2+*) | Variable | **Compiled Bytecode** | GSC scripts are compiled into binary bytecode rather than raw text. Cannot be extracted with text regex; requires a bytecode decompiler. |

> [!IMPORTANT]
> This guide and `um fastfile` specifically target **Treyarch T4 (World at War)** and **IW 3.0 (Call of Duty 4)**. Never assume FastFile formats or plain-text script structures carry over to IW 4.0+ or Black Ops 2+.


---

## 1. Filesystem & Loading Precedence
Engine resolves assets via `FS_Startup` in strict priority order:
1. **Loose files in `mods/<ModName>/`**: Highest priority. Overrides everything.
2. **Mod Archives (`mods/<ModName>/*.iwd`)**: Loaded in reverse alphabetical order (`z_*.iwd` overrides `a_*.iwd`). Standard ZIP format.
3. **Mod Fastfile (`mods/<ModName>/mod.ff`)**: Compiled binary assets (compiled menus, particle effects `.efx`, compiled shaders).
4. **Base game `raw/` and `main/`**: Stock loose assets.
5. **Base game IWDs (`main/iw_00.iwd` - `iw_27.iwd`)**: Stock textures, materials, and sounds.
6. **Base game Fastfiles (`zone/<language>/*.ff`)**: Core level and common binaries (`code_post_gfx.ff`, `common.ff`, `<map>.ff`, `patch.ff`).

> [!TIP]
> **Zero-Linker Live Iteration:** GSC/CSC scripts, IWI textures, weapons, and sound aliases can be placed loose or inside an `.iwd` in `mods/<ModName>/`. They load immediately without recompiling `mod.ff`. Only compile Fastfiles when shipping or adding binary effects (`.efx`), custom materials, or global precaches.

---

## 2. GSC & CSC Scripting Architecture

### Server GSC vs. Client CSC
* **Server GSC (`maps/`)**: Authoritative logic: damage calculations, AI navigation, score allocation, round tracking, and spawner management.
* **Client CSC (`clientscripts/`)**: Client-side cosmetics: particle attachments, dynamic light flickers, and eyeball glow billboards. Runs locally on the client to avoid consuming server entity slots (`MAX_GENTITIES`).

### Compiler & Runtime Invariants
* **Strict Single-Pass Compiler**: The engine halts map loading with `Server script compile error: unreachable code` if an unconditional `return;` is placed before existing statements. Always wrap early returns inside conditional guards:
  ```gsc
  if( IsDefined( level.mod_active ) && level.mod_active )
  {
      return;
  }
  ```
* **Singleplayer Function Scope Trap**: In Singleplayer and Nazi Zombies, `iprintln` and `iprintlnbold` are **global functions** (`iprintlnbold(msg);`), **NOT** entity member methods (`player iprintlnbold(msg);`). Calling them on `self` or a player entity fails silently.
* **PrecacheItem Rule**: Never call `PrecacheItem()` on weapons not included in the map's level fastfile. Precache misses cause fatal server script aborts during map initialization. Weapons must either be embedded in `mod.ff` via `zone_source/mod.csv` or dynamically verified against `level.zombie_weapons`.

---

## 3. 2D HUD & Renderer Rules

* **The FontScale Underflow Bug (`fontScale < 1.0`)**: In the IW3 2D renderer, `HudElem.fontScale` does not support floating point values less than `1.0` (such as `0.85` or `0.92`). Passing $< 1.0$ causes an internal UV texture projection underflow, rendering text 10× larger across the entire screen. Always keep `fontScale >= 1.0` and manage width/padding with coordinate placement.
* **Strict 31–32 Client `HudElem` Budget**: The engine allocates a hard limit of ~31 to 32 active `HudElem` structs per client. Exceeding this budget causes subsequent HUD elements to drop silently.
* **No String Auto-Wrapping**: `SetText()` does not wrap lines. Multi-line UI elements must be split into separate `HudElem` instances with explicit `y` coordinate offsets.
* **Layering & Depth**: Use `elem.sort = 1;` for backgrounds, `elem.sort = 2;` for borders, and `elem.sort = 3;` for foreground text.

---

## 4. Nazi Zombies Gameplay Systems

### Map Family Redirection (Treyarch Patch 1.4+)
Patch 1.4 redirected map startup scripts in `zone/<language>/patch.ff`:
* **Nacht der Untoten**: Calls `maps/_zombiemode_prototype::main()` and spawners in `_zombiemode_spawner_prototype.gsc`.
* **Verrückt**: Calls `maps/_zombiemode_asylum::main()` and spawners in `_zombiemode_spawner_asylum.gsc`.
* **Shi No Numa & Der Riese**: Call `maps/_zombiemode::main()` and spawners in `_zombiemode_spawner.gsc` (Der Riese uses `_zombiemode_blockers_new.gsc`).
* **Rule**: Universal zombie mods must patch and compile all 3 master scripts and all 3 spawner scripts, or maps under `patch.ff` will revert to stock vanilla logic.

### Health, Caps, and Powerups
* **Zombie Health Formula**:
  * Round 1: 150 HP (`level.zombie_vars["zombie_health_start"]`).
  * Rounds 2–9: Linear scaling: `150 + 100 * (round - 1)`.
  * Round 10+: Exponential scaling: `health = int(health * 1.1)`.
* **Entity & AI Limits**: Hard cap of 24 concurrent active zombies (`zombie_max_ai = 24`). Engine has a strict 1,024 entity limit (`MAX_GENTITIES`) unless running T4M.
* **Powerup Drop Escalation**: Cumulative score threshold `(players * 500) + 2000`, escalating by 14% (`*= 1.14`) each drop, capped at 4 drops per round maximum.
* **Pack-a-Punch Hook**: Machine checks for `level.zombie_include_weapons[current_weapon + "_upgraded"]`. Upgraded variants must strictly follow the `<weapon>_upgraded` suffix naming convention.

---

## 5. Toolchain & Map Compilation (Radiant / Cod2Map)

* **Working Directory (CWD)**: `linker_pc.exe` and `cod2map.exe` must be invoked with CWD set to `<GameRoot>\bin\`. Piped stdin (`echo. | linker_pc.exe ...`) is mandatory to avoid CLI hangs on asset warnings.
* **Concave Winding Assertion (`tris_mergeconcave.cpp:1120`)**:
  * Symptom: `cod2map.exe` aborts with `ASSERTION: w->ptCount <= ARRAY_COUNT( indices )`.
  * Cause: Complex concave brushes or high-density terrain windings during BSP merge pass.
  * Fix: Split concave brushes into convex primitives in Radiant, or pass `-keeplightmapcuts` / `-nomerge` flags to `cod2map.exe`.
* **Memory Limits & T4M**: Complex custom maps with dense texture packs require the T4M proxy (`d3d9.dll`) to raise `MAX_ASSET_IMAGES` and `MAX_STRING_LOOKUPS`.

---

## 6. FastFile (.ff) Binary Layout & Decompilation

In retail Call of Duty: World at War (T4) and Call of Duty 4 (IW 3.0), FastFiles (`.ff`) are standard zlib streams with a 12-byte header:
* **Header Layout**:
  * Bytes 0–7: Container magic (`IWffu100` for uncompressed header, `IWff0100` for compressed).
  * Bytes 8–11: 4-byte little-endian version number (`387` for WaW, `334` for CoD4).
  * Byte 12+: Standard zlib compressed payload stream (`0x78 0x01` / `0x78 0x9C`).
* **RawFile Serialized Layout**:
  Unlike later titles which compile scripts into bytecode, **World at War and CoD4 store GSC and CSC scripts as 100% human-readable plain text source code** inside `ASSET_TYPE_RAWFILE` records:
  ```text
  [0xFFFFFFFF] (4B sentinel)
  [Length]     (4B uint32 little-endian)
  [0xFFFFFFFF] (4B sentinel)
  [Name\0]     (null-terminated ASCII path, e.g. maps/nazi_zombie_factory.gsc\0)
  [Payload]    (Length bytes of raw source code or text)
  ```

### Using `um fastfile`
The toolkit includes built-in inspection and extraction commands for FastFiles:
```bash
# List all GSCs, CSCs, menus, and configs inside a FastFile
um fastfile list zone/english/patch.ff
um fastfile list zone/english/nazi_zombie_factory.ff

# Extract all raw scripts to a directory
um fastfile dump zone/english/patch.ff -o extracted_patch/
um fastfile dump zone/english/nazi_zombie_factory.ff -o der_riese_scripts/
```

## 7. IWI v6 Texture Conversion (`um iwi`)

Call of Duty games utilize Infinity Ward Image (`.iwi`) containers for textures. World at War and CoD4 use **version 6**:
* **Header Structure (28 bytes)**:
  * Bytes 0–3: Magic `IWi\x06` (ASCII `IWi` + version byte `0x06`).
  * Byte 4: Format identifier (`0x0B` = DXT1 opaque/1-bit alpha, `0x0D` = DXT5 interpolated alpha).
  * Byte 5: Flags (e.g. `0x03`).
  * Bytes 6–7: Dimensions height (`uint16_t` little-endian).
  * Bytes 8–9: Dimensions width (`uint16_t` little-endian).
  * Bytes 10–11: Depth (`uint16_t`, 1 for 2D textures).
  * Bytes 12–27: 4 mipmap end offsets (`uint32_t[4]` little-endian).
* **Reverse Mipmap Ordering**:
  Crucially, mipmaps in IWI v6 files are stored in **reverse order**: the smallest mipmap is stored first immediately following the 28-byte header, and the full-resolution base image (mip 0) is stored last at the end of the file.

### CLI Usage:
```bash
# Convert a custom PNG texture into game-ready IWI v6 format:
um iwi png2iwi hud_custom_icon.png images/hud_custom_icon.iwi --format dxt5 --mips

# Decode an existing in-game IWI v6 texture back to PNG for inspection/editing:
um iwi iwi2png images/weapon_usa_colt45.iwi raw_textures/colt.png
```

## 8. Weapon File Editing (`um weapon`)

Call of Duty weapons are defined in text files using a single-backslash delimited dictionary format starting with `WEAPONFILE\`. Over 300 properties configure ammunition, damage, viewmodels, recoil, spread, and sound effects.

### Key Weapon Attributes:
* `damage` / `minDamage`: Base hit point damage and minimum damage at maximum falloff range.
* `damageType`: `bullet`, `grenade`, `splash`, `fire`, etc.
* `clipSize` / `maxAmmo` / `startAmmo`: Magazine capacity and reserve pools.
* `fireTime`: Interval between rounds (seconds).
* `projectileModel`: Swaps hitscan bullets for simulated physics projectiles (e.g., `projectile_usa_m9a1_riflegrenade`).

### CLI Usage:
```bash
# Inspect all weapon stats or query a specific key:
um weapon get weapons/sp/colt
um weapon get weapons/sp/colt damage

# Modify specific stats and output to a mod folder:
um weapon set weapons/sp/colt damage=250 clipSize=14 -o mods/MyMod/weapons/sp/colt_modded

# Clone a weapon with presets (e.g. explosive ammo or upgraded stats):
um weapon clone weapons/sp/colt mods/MyMod/weapons/sp/colt_explosive --damage 500 --clip 14 --explosive

# Compare differences between two weapon definitions:
um weapon diff weapons/sp/colt mods/MyMod/weapons/sp/colt_explosive
```

## 9. Reference Starter Example

See `examples/cod-waw-zombies-starter/` for a complete working reference mod demonstrating:
* Zero-linker live iteration via `.iwd` packaging.
* Clean override of `maps/nazi_zombie_prototype.gsc` (Nacht der Untoten).
* Custom weapon implementation (`weapons/sp/colt_starter`).
* Crash-safe HUD implementation adhering to the `fontScale >= 1.0` requirement and 31-element limit.
* Automated packager script (`pack.py`).


