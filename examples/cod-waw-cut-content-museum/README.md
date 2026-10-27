# Call of Duty: World at War: Cut Content & Prototype Museum

An interactive showcase mod for **Call of Duty: World at War** (Treyarch T4 engine / IW 3.0 fork, SP/Co-op v1.7).

It transforms the classic Nacht der Untoten bunker into a peaceful, interactive museum exhibiting unused German SS soldier character models, prototype weapons, and cut campaign assets compiled inside the game fastfiles but never featured in standard gameplay.

---

## Exhibits & Features

### Exhibit Wing 1: German Character Mannequins (Ground Floor)
Life-size standing character mannequins displayed on military crates with on-screen historical info cards:
- **Exhibit 1: SS Honor Guard (Dress Uniform)** (`char_ger_honorgd_body1_1` + `char_ger_honorguard_head1_1`):
  Cut ceremonial uniform created for Berlin levels. Character bodies and heads are fully preserved inside game fastfiles.
- **Exhibit 2: SS Honor Guard (Combat Gear)** (`char_ger_honorgd_body2_1` + `char_ger_honorguard_head2_1`):
  Field-combat variant equipped with webbed ammunition harness. Full ragdoll dismemberment sets are preserved in the T4 engine.
- **Exhibit 3: Honor Guard Zombie Prototype** (`char_ger_honorgd_body1_1` + `char_ger_honorgd_zombiehead1_1`):
  Early prototype Nazi Zombie character model with decaying flesh and tattered Honor Guard uniform, predecessor to the final Wehrmacht zombie design.
- **Exhibit 4: Wehrmacht Line Infantry** (`char_ger_wermacht_body1_1` + `char_ger_head1_1`):
  Standard German infantry uniform base model.

### Exhibit Wing 2: Prototype & Cut Weapon Arsenal (Upstairs Loft)
Elevated pedestals with slowly rotating 3D world models and proximity interaction prompts (`Press [USE] to equip`):
- **Walther P38** (`walther`): Authentic German 9mm sidearm with full viewmodel animations, cut from standard singleplayer loadouts.
- **Colt .45 "Dirty Harry"** (`colt_dirty_harry`): Developer weapon delivering 500 damage per shot with explosive rifle grenade projectile physics.
- **FG42 Paratrooper Automatic Rifle** (`fg42`): Select-fire 7.92mm paratrooper rifle with bipod mounts.
- **Scoped Kar98k Marksman Rifle** (`kar98k_scoped_zombie`): Precision German bolt-action rifle equipped with Zeiss high-magnification optic.
- **Panzerschreck** (`panzerschreck`): 88mm shoulder-fired rocket launcher with protective face blast shield.
- **Ray Gun** (`ray_gun`): The legendary alien wonder weapon prototype designed by Max Porter.

### Exhibit Wing 3: Transit Teleporters & Visitor Amenities
- **Teleporter Hub**: Instant fast-travel pads between the Ground Floor Atrium and Upstairs Arsenal.
- **Peaceful Exploration**: All zombie rounds, wave spawning, and timers are suppressed.
- **Open Floor Plan**: All couches, debris piles, and doors (`zombie_debris`, `zombie_door`) are cleared on level start.
- **Visitor Privileges**: Invulnerability and +25% sprint speed for easy navigation.
- **Infinite Ammo Monitor**: Automatically replenishes ammunition reserves so visitors can test firing and reload animations indefinitely.

---

## File Structure

```text
cod-waw-cut-content-museum/
├── maps/
│   └── nazi_zombie_prototype.gsc  # Overrides Nacht der Untoten into museum gallery
├── weapons/sp/
│   ├── walther                    # Cut Walther P38 weapon dictionary
│   └── colt_dirty_harry           # Developer Dirty Harry weapon dictionary
├── mod.arena                      # Map descriptor for CoD:WaW in-game menu
├── pack.py                        # Automated .iwd packager and mod installer
├── MODLOG.md                      # Development and verification journal
└── README.md                      # This guide
```

---

## Packaging and Installation

### One-Click Build & Install
Run the packaging script with the `--install` flag:

```powershell
python pack.py --install
```

This compiles `z_cut_content_museum.iwd` and copies it along with `mod.arena` directly to:
`%LOCALAPPDATA%\Activision\CoDWaW\mods\cod_waw_cut_content_museum\`

---

## Launching in Game

1. Launch Call of Duty: World at War (Singleplayer / Co-op).
2. Click **Mods** from the Main Menu.
3. Select `cod_waw_cut_content_museum` and click **Launch**.
4. Open the developer console (`~`) and run:
   ```text
   devmap nazi_zombie_prototype
   ```
   Or select **Solo** -> **Nacht der Untoten**.
5. Walk up to any exhibit mannequin or weapon pedestal and press **`F`** (`[{+activate}]`) to interact!
