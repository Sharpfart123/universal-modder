#include common_scripts\utility;
#include maps\_utility;

// Call of Duty: World at War: Cut Content & Asset Museum
// Overrides Nacht der Untoten (nazi_zombie_prototype) into an interactive showcase.

main()
{
	// Initialize map visual and ambient particle effects
	maps\nazi_zombie_prototype_fx::main();

	// Precache display assets, character models, and weapons
	precache_museum_assets();

	// Player connection and lifecycle listeners
	level thread on_player_connect();

	// Open all bunker debris, doors, and barricades immediately
	level thread clear_all_blockers();

	// Construct museum wings and exhibits
	level thread spawn_character_mannequins();
	level thread spawn_weapon_pedestals();
	level thread setup_transit_teleporters();
}

precache_museum_assets()
{
	// Character models (compiled in retail prototype.ff and common.ff)
	precacheModel("char_ger_honorgd_body1_1");
	precacheModel("char_ger_honorgd_body2_1");
	precacheModel("char_ger_honorguard_head1_1");
	precacheModel("char_ger_honorguard_head2_1");
	precacheModel("char_ger_honorgd_zombiehead1_1");
	precacheModel("char_ger_head1_1");
	precacheModel("char_ger_wermacht_body1_1");

	// Display pedestal props
	precacheModel("clutter_berlin_crate_01");

	// Weapon display 3D world models
	precacheModel("weapon_ger_walther_pistol");
	precacheModel("weapon_usa_colt45_pistol");
	precacheModel("weapon_ger_fg42_bipod_lmg");
	precacheModel("weapon_ger_kar98_scoped_rifle");
	precacheModel("weapon_ger_panzerschreck_at");
	precacheModel("weapon_usa_ray_gun");

	// Weapons
	precacheItem("walther");
	precacheItem("colt_dirty_harry");
	precacheItem("fg42");
	precacheItem("kar98k_scoped_zombie");
	precacheItem("panzerschreck");
	precacheItem("ray_gun");
}

on_player_connect()
{
	for(;;)
	{
		level waittill("connected", player);
		player thread on_player_spawned();
	}
}

on_player_spawned()
{
	self endon("disconnect");

	for(;;)
	{
		self waittill("spawned_player");

		// Museum visitor privileges: invulnerability & enhanced movement
		self enableInvulnerability();
		self setMoveSpeedScale(1.25);

		// Starter loadout: Cut Walther P38 sidearm
		self takeAllWeapons();
		self giveWeapon("walther");
		self switchToWeapon("walther");
		self setSpawnWeapon("walther");
		self giveMaxAmmo("walther");

		// Display introductory museum HUD banner
		self thread show_museum_intro_hud();

		// Keep ammo replenished so visitor can test firing/reload anims freely
		self thread infinite_ammo_monitor();

		// Proximity hint monitor for exhibits
		self thread museum_proximity_monitor();
	}
}

show_museum_intro_hud()
{
	self endon("disconnect");

	// Create crash-safe HUD banner: fontScale >= 1.0 (avoids T4 float underflow crash)
	hud = newClientHudElem(self);
	hud.alignX = "center";
	hud.alignY = "middle";
	hud.horzAlign = "center";
	hud.vertAlign = "middle";
	hud.x = 0;
	hud.y = -70;
	hud.fontScale = 1.35;
	hud.color = (0.2, 0.9, 0.4);
	hud.alpha = 0;
	hud.glowColor = (0, 0, 0);
	hud.glowAlpha = 1;
	hud setText("WORLD AT WAR: CUT CONTENT & PROTOTYPE MUSEUM");

	hud fadeOverTime(1.0);
	hud.alpha = 1;

	subhud = newClientHudElem(self);
	subhud.alignX = "center";
	subhud.alignY = "middle";
	subhud.horzAlign = "center";
	subhud.vertAlign = "middle";
	subhud.x = 0;
	subhud.y = -45;
	subhud.fontScale = 1.1;
	subhud.color = (0.9, 0.9, 0.9);
	subhud.alpha = 0;
	subhud setText("Explore unused soldier uniforms, prototype weapons, and cut assets.");

	subhud fadeOverTime(1.0);
	subhud.alpha = 1;

	wait 5.0;

	hud fadeOverTime(1.5);
	hud.alpha = 0;
	subhud fadeOverTime(1.5);
	subhud.alpha = 0;
	wait 1.5;

	hud destroy();
	subhud destroy();
}

clear_all_blockers()
{
	// Wait for map entity initialization
	wait 0.2;

	// Remove all debris couches, rubble piles, and blocker volumes
	debris = getentarray("zombie_debris", "targetname");
	for(i = 0; i < debris.size; i++)
	{
		if(isdefined(debris[i]))
		{
			debris[i] delete();
		}
	}

	doors = getentarray("zombie_door", "targetname");
	for(i = 0; i < doors.size; i++)
	{
		if(isdefined(doors[i]))
		{
			doors[i] delete();
		}
	}
}

// ---------------------------------------------------------------------------
// EXHIBIT WING 1: UNUSED SOLDIER CHARACTER MODELS
// ---------------------------------------------------------------------------

spawn_character_mannequins()
{
	wait 0.5;

	// Exhibit 1: SS Honor Guard Dress Uniform (Ground Floor Atrium)
	spawn_mannequin_station(
		(200, 80, 8),
		(0, 180, 0),
		"char_ger_honorgd_body1_1",
		"char_ger_honorguard_head1_1",
		"^2[EXHIBIT 1] ^3SS Honor Guard (Dress Uniform)^7\nCut German Honor Guard uniform created for Berlin levels. Character models and heads are compiled inside game fastfiles but unused in standard campaign squads."
	);

	// Exhibit 2: SS Honor Guard Combat Gear (Ground Floor Atrium)
	spawn_mannequin_station(
		(200, -80, 8),
		(0, 180, 0),
		"char_ger_honorgd_body2_1",
		"char_ger_honorguard_head2_1",
		"^2[EXHIBIT 2] ^3SS Honor Guard (Combat Gear)^7\nField-combat variant with webbed ammunition harness. Full ragdoll dismemberment sets are preserved in the T4 engine."
	);

	// Exhibit 3: Honor Guard Zombie Prototype (Ground Floor West Alcove)
	spawn_mannequin_station(
		(50, 140, 8),
		(0, 270, 0),
		"char_ger_honorgd_body1_1",
		"char_ger_honorgd_zombiehead1_1",
		"^2[EXHIBIT 3] ^3Honor Guard Zombie Prototype^7\nEarly Nazi Zombie character model with decaying skin and tattered Honor Guard uniform, predecessor to the final Wehrmacht zombie design."
	);

	// Exhibit 4: Wehrmacht Line Infantry (East Help Room)
	spawn_mannequin_station(
		(780, 620, 8),
		(0, 90, 0),
		"char_ger_wermacht_body1_1",
		"char_ger_head1_1",
		"^2[EXHIBIT 4] ^3Wehrmacht Line Infantry^7\nStandard German infantry uniform base model."
	);
}

spawn_mannequin_station(origin, angles, body_model, head_model, info_text)
{
	// Display pedestal
	pedestal = spawn("script_model", origin);
	pedestal setModel("clutter_berlin_crate_01");
	pedestal.angles = angles;

	// Mannequin standing on pedestal (crate height is ~24 units)
	mannequin_origin = origin + (0, 0, 24);
	mannequin = spawn("script_model", mannequin_origin);
	mannequin setModel(body_model);
	mannequin.angles = angles;
	if (isdefined(head_model) && head_model != "")
	{
		mannequin attach(head_model, "", true);
	}

	// Register exhibit in level registry
	if (!isdefined(level.museum_exhibits))
	{
		level.museum_exhibits = [];
	}

	exhibit = spawnstruct();
	exhibit.origin = origin;
	exhibit.info_text = info_text;
	exhibit.type = "character";

	level.museum_exhibits[level.museum_exhibits.size] = exhibit;
}

// ---------------------------------------------------------------------------
// EXHIBIT WING 2: PROTOTYPE & CUT WEAPONS (UPSTAIRS ARSENAL)
// ---------------------------------------------------------------------------

spawn_weapon_pedestals()
{
	wait 0.5;

	// Upstairs Balcony & Hallway Pedestals
	// 1. Walther P38
	spawn_weapon_display_station(
		(380, 620, 184),
		"weapon_ger_walther_pistol",
		"walther",
		"Walther P38 (Cut Campaign Pistol)",
		"^3Walther P38^7: Fully functional German 9mm sidearm with authentic viewmodel animations, cut from standard SP loadouts."
	);

	// 2. Colt .45 'Dirty Harry'
	spawn_weapon_display_station(
		(440, 620, 184),
		"weapon_usa_colt45_pistol",
		"colt_dirty_harry",
		"Colt .45 'Dirty Harry' (Developer Weapon)",
		"^3Colt .45 'Dirty Harry'^7: Developer test weapon delivering 500 damage per shot with explosive rifle grenade projectile physics."
	);

	// 3. FG42 Paratrooper Rifle
	spawn_weapon_display_station(
		(500, 620, 184),
		"weapon_ger_fg42_bipod_lmg",
		"fg42",
		"FG42 Paratrooper Automatic Rifle",
		"^3FG42^7: Select-fire 7.92mm paratrooper rifle with bipod mounts."
	);

	// 4. Scoped Kar98k Sniper
	spawn_weapon_display_station(
		(380, 700, 184),
		"weapon_ger_kar98_scoped_rifle",
		"kar98k_scoped_zombie",
		"Kar98k Scoped Marksman Rifle",
		"^3Kar98k Scoped^7: Precision German bolt-action rifle equipped with Zeiss high-magnification optic."
	);

	// 5. Panzerschreck Heavy Anti-Tank Rocket
	spawn_weapon_display_station(
		(440, 700, 184),
		"weapon_ger_panzerschreck_at",
		"panzerschreck",
		"Panzerschreck (Raketenpanzerbuechse 54)",
		"^3Panzerschreck^7: 88mm shoulder-fired rocket launcher with protective face blast shield."
	);

	// 6. Ray Gun Wonder Weapon Prototype
	spawn_weapon_display_station(
		(500, 700, 184),
		"weapon_usa_ray_gun",
		"ray_gun",
		"Ray Gun (Zombie Wonder Weapon)",
		"^3Ray Gun^7: The legendary alien sidearm designed by Max Porter, firing green atomic plasma rings."
	);
}

spawn_weapon_display_station(origin, model_name, weapon_id, display_name, info_text)
{
	// Pedestal base
	base = spawn("script_model", origin);
	base setModel("clutter_berlin_crate_01");

	// Floating, rotating weapon model
	weapon_origin = origin + (0, 0, 32);
	weapon_ent = spawn("script_model", weapon_origin);
	weapon_ent setModel(model_name);
	weapon_ent thread spin_weapon_display();

	// Register exhibit in level registry
	if (!isdefined(level.museum_exhibits))
	{
		level.museum_exhibits = [];
	}

	exhibit = spawnstruct();
	exhibit.origin = origin;
	exhibit.weapon_id = weapon_id;
	exhibit.display_name = display_name;
	exhibit.info_text = info_text;
	exhibit.type = "weapon";

	level.museum_exhibits[level.museum_exhibits.size] = exhibit;
}

spin_weapon_display()
{
	self endon("death");
	for(;;)
	{
		self rotateYaw(360, 4.0);
		wait 4.0;
	}
}

// ---------------------------------------------------------------------------
// EXHIBIT WING 3: TRANSIT TELEPORTERS
// ---------------------------------------------------------------------------

setup_transit_teleporters()
{
	wait 0.5;

	// Ground Floor Pad -> Warps to Upstairs Arsenal
	level.tp_ground = (100, 100, 0);

	// Upstairs Pad -> Warps to Ground Floor Atrium
	level.tp_upstairs = (350, 600, 184);

	exhibit_down = spawnstruct();
	exhibit_down.origin = level.tp_ground;
	exhibit_down.target_pos = (400, 600, 190);
	exhibit_down.type = "teleport";
	exhibit_down.prompt = "Press ^3[{+activate}]^7 to warp upstairs to Weapons Arsenal";

	exhibit_up = spawnstruct();
	exhibit_up.origin = level.tp_upstairs;
	exhibit_up.target_pos = (150, 0, 10);
	exhibit_up.type = "teleport";
	exhibit_up.prompt = "Press ^3[{+activate}]^7 to warp downstairs to Uniform Exhibits";

	level.museum_exhibits[level.museum_exhibits.size] = exhibit_down;
	level.museum_exhibits[level.museum_exhibits.size] = exhibit_up;
}

// ---------------------------------------------------------------------------
// VISITOR INTERACTION & PROXIMITY WATCHER
// ---------------------------------------------------------------------------

museum_proximity_monitor()
{
	self endon("disconnect");

	for(;;)
	{
		wait 0.1;

		if (!isdefined(level.museum_exhibits))
		{
			continue;
		}

		closest_exhibit = undefined;
		closest_dist = 64; // Interaction range

		for(i = 0; i < level.museum_exhibits.size; i++)
		{
			ex = level.museum_exhibits[i];
			d = distance(self.origin, ex.origin);
			if (d < closest_dist)
			{
				closest_dist = d;
				closest_exhibit = ex;
			}
		}

		if (isdefined(closest_exhibit))
		{
			if (closest_exhibit.type == "weapon")
			{
				self setLowerMessage("Press ^3[{+activate}]^7 to equip " + closest_exhibit.display_name);

				if (self useButtonPressed())
				{
					self takeAllWeapons();
					self giveWeapon(closest_exhibit.weapon_id);
					self switchToWeapon(closest_exhibit.weapon_id);
					self giveMaxAmmo(closest_exhibit.weapon_id);

					self iprintln("^2Equipped: ^7" + closest_exhibit.display_name);
					self iprintln(closest_exhibit.info_text);
					wait 1.0;
				}
			}
			else if (closest_exhibit.type == "character")
			{
				self setLowerMessage("Press ^3[{+activate}]^7 to inspect Exhibit");

				if (self useButtonPressed())
				{
					self iprintln(closest_exhibit.info_text);
					wait 1.5;
				}
			}
			else if (closest_exhibit.type == "teleport")
			{
				self setLowerMessage(closest_exhibit.prompt);

				if (self useButtonPressed())
				{
					self setOrigin(closest_exhibit.target_pos);
					self playSound("weap_raise");
					wait 1.0;
				}
			}
		}
		else
		{
			self clearLowerMessage();
		}
	}
}

infinite_ammo_monitor()
{
	self endon("disconnect");

	for(;;)
	{
		wait 1.0;
		weap = self getCurrentWeapon();
		if (isdefined(weap) && weap != "none")
		{
			self giveMaxAmmo(weap);
		}
	}
}
