#include maps\_utility;
#include common_scripts\utility;

// Call of Duty: World at War (Treyarch T4) Zombies Starter Mod
// Demonstrates live script override via .iwd archive without re-linking fastfiles.

main()
{
	// Execute map FX setup
	maps\nazi_zombie_prototype_fx::main();

	// Listen for player connections to inject our starter loadout and welcome HUD
	level thread on_player_connect();
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

		// Display introductory HUD element safely adhering to engine rules:
		// 1. fontScale must be >= 1.0 (float underflow crash in T4 engine if < 1.0)
		// 2. HUD count must stay well below 31 per-player limit
		self thread show_starter_hud("ZOMBIES STARTER MOD LOADED", (0.2, 0.9, 0.4));

		// Grant custom starter weapon
		self takeAllWeapons();
		self giveWeapon("colt_starter");
		self switchToWeapon("colt_starter");
		self setSpawnWeapon("colt_starter");

		self iprintln("^2Starter Loadout: ^7Colt .45 Upgraded (14 Rounds, 150 Damage)");
	}
}

show_starter_hud(text, color)
{
	self endon("disconnect");

	hud = newClientHudElem(self);
	hud.alignX = "center";
	hud.alignY = "middle";
	hud.horzAlign = "center";
	hud.vertAlign = "middle";
	hud.x = 0;
	hud.y = -80;
	hud.fontScale = 1.4; // Safe: never < 1.0
	hud.color = color;
	hud.alpha = 0;
	hud.glowColor = (0, 0, 0);
	hud.glowAlpha = 1;
	hud setText(text);

	hud fadeOverTime(1.0);
	hud.alpha = 1;
	wait 4.0;
	hud fadeOverTime(1.5);
	hud.alpha = 0;
	wait 1.5;
	hud destroy();
}
