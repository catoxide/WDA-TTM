# WDA-TTM — Thornborn Towers Remake

A **fan remake** that gives [When Dungeons Arise](https://www.curseforge.com/minecraft/mc-mods/when-dungeons-arise)'s **thornborn_towers** structure custom chest loot. It ships as both a **datapack** and a **data-only NeoForge mod**.

> The structure / building is by the **When Dungeons Arise** team (Aurelj, DiamonDtown, Zephyrusj). We did **not** modify the building — we only replaced the chest contents with our own loot. See [LICENSE](LICENSE).

## Prerequisite mods
All of the following are required (the pack overrides a DDA structure and uses their blocks/items):

| Mod | Why it's needed |
|---|---|
| **When Dungeons Arise (DDA)** | the base structure this overrides — required |
| **Create** (6.0.x) | structure blocks + chest loot items |
| **Supplementaries** | structure blocks + chest loot items (pulls in **Moonlight** automatically) |
| **Quark** | structure blocks (bundles **Zeta** automatically) |

## Minecraft version
- **Tested on: 1.21.1**
- Theoretically compatible with any version supported by **Create 6.0** (1.20.1, 1.21.1, or newer).

## Installation

### As a datapack
1. Put the `datapack/` folder — or [`dist/WDA-TTM-1.21.1.zip`](dist/WDA-TTM-1.21.1.zip) — into your world's `datapacks/` folder.
2. `/reload` (or re-enter the world).

### As a mod (NeoForge)
1. Put [`dist/WDA-TTM-1.21.1-neoforge-1.0.1.jar`](dist/WDA-TTM-1.21.1-neoforge-1.0.1.jar) into your `mods/` folder.
2. The game refuses to launch without the prerequisite mods above; they are declared in the jar's metadata.

In both cases, find a **thornborn_towers** structure in a **new region** — structures do not retro-generate in already-generated chunks.

## Repository layout

```
datapack/                  the content: 3 loot tables + 27 structure NBTs
mods/<loader>-<mc>/        per-target mod metadata
targets.json               mod id, version, and per-target build facts
tools/build.py             builds every artifact into dist/
dist/                      release artifacts
```

The mod jars contain **no Java code**. They use NeoForge's `lowcodefml` language loader, which treats the jar as a data pack plus `META-INF/neoforge.mods.toml`. Like other mod jars, they keep `pack.mcmeta` at the root.

## Building

```sh
python tools/build.py
```

This writes:

- `dist/WDA-TTM-<mc>.zip` — the datapack
- `dist/<artifact from targets.json>` — the mod jar

The script fails if `targets.json` and a target's metadata disagree on mod id or version, or if `pack.mcmeta`'s `pack_format` differs from `targets.json`. Archives are written deterministically (fixed timestamps, forward-slash paths).

Useful flags:

```sh
python tools/build.py --list
python tools/build.py --target neoforge-1.21.1
python tools/build.py --datapack-only
```

### Bumping the version
Change `version` in `targets.json` **and** the `[[mods]] version` in the target's metadata. The build refuses to run if they diverge.

### Adding a loader / Minecraft target
1. Create `mods/<loader>-<mc>/` and add the loader's metadata (`META-INF/neoforge.mods.toml` for NeoForge, `META-INF/mods.toml` for legacy Forge).
2. Add a target entry to `targets.json` (`metadata`, `metadataDest`, `artifact`, `datapackArtifact`).
3. Run `python tools/build.py --target <name>`.

`datapack/pack.mcmeta` is shared by all targets, so its `pack_format` must match the newest supported data-pack format. It is currently **48** (1.21.1).

## Notes
- Non-commercial fan work. Structures © When Dungeons Arise team.

## Credit
- Structures: **When Dungeons Arise** (Aurelj, DiamonDtown, Zephyrusj)
- Custom loot + packaging: **WDA-TTM**
