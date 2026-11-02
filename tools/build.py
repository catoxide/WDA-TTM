#!/usr/bin/env python3
"""Build the WDA-TTM datapack zip and per-loader data-only mod jars into dist/."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)
MANIFEST = b"Manifest-Version: 1.0\r\nCreated-By: WDA-TTM build\r\n\r\n"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_config() -> dict:
    config_path = ROOT / "targets.json"
    if not config_path.is_file():
        fail(f"missing {config_path}")
    with config_path.open("rb") as handle:
        config = json.load(handle)
    for key in ("modId", "version", "datapack", "datapackPackFormat", "targets"):
        if key not in config:
            fail(f"targets.json is missing '{key}'")
    if not config["targets"]:
        fail("targets.json defines no targets")
    return config


def validate_datapack(config: dict) -> Path:
    datapack = ROOT / config["datapack"]
    mcmeta_path = datapack / "pack.mcmeta"
    if not mcmeta_path.is_file():
        fail(f"missing {mcmeta_path}")
    with mcmeta_path.open("rb") as handle:
        mcmeta = json.load(handle)
    actual_format = mcmeta.get("pack", {}).get("pack_format")
    if actual_format != config["datapackPackFormat"]:
        fail(
            f"pack_format is {actual_format}, "
            f"targets.json says {config['datapackPackFormat']}"
        )
    return datapack


def validate_metadata(config: dict, target_name: str, target: dict) -> Path:
    metadata_path = ROOT / target["metadata"]
    if not metadata_path.is_file():
        fail(f"{target_name}: missing {metadata_path}")
    with metadata_path.open("rb") as handle:
        metadata = tomllib.load(handle)
    if metadata.get("modLoader") != "lowcodefml":
        fail(f"{target_name}: modLoader must be 'lowcodefml'")
    mods = metadata.get("mods") or []
    if len(mods) != 1:
        fail(f"{target_name}: expected exactly one [[mods]] entry")
    if mods[0].get("modId") != config["modId"]:
        fail(f"{target_name}: modId is {mods[0].get('modId')!r}, expected {config['modId']!r}")
    if mods[0].get("version") != config["version"]:
        fail(f"{target_name}: version is {mods[0].get('version')!r}, expected {config['version']!r}")
    return metadata_path


def datapack_entries(datapack: Path) -> list[tuple[str, bytes]]:
    entries: list[tuple[str, bytes]] = []
    for path in sorted(p for p in datapack.rglob("*") if p.is_file()):
        arcname = path.relative_to(datapack).as_posix()
        if "\\" in arcname:
            fail(f"refusing backslash in archive path: {arcname}")
        entries.append((arcname, path.read_bytes()))
    if not entries:
        fail(f"no files found under {datapack}")
    return entries


def write_zip(destination: Path, entries: list[tuple[str, bytes]]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for arcname, payload in entries:
            info = zipfile.ZipInfo(arcname, FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)


def report(destination: Path) -> None:
    digest = hashlib.sha1(destination.read_bytes()).hexdigest()
    size = destination.stat().st_size
    print(f"  {destination.relative_to(ROOT).as_posix()}  {size} bytes  sha1 {digest}")


def build_datapack(config: dict, datapack: Path, artifact: str) -> None:
    entries = datapack_entries(datapack)
    destination = DIST / artifact
    write_zip(destination, entries)
    report(destination)


def build_mod(config: dict, target_name: str, target: dict, metadata: Path, datapack: Path) -> None:
    metadata_dest = target["metadataDest"].lstrip("/")
    if metadata_dest.split("/")[0] != "META-INF":
        fail(f"{target_name}: metadata must live under META-INF/")
    entries: list[tuple[str, bytes]] = [
        ("META-INF/MANIFEST.MF", MANIFEST),
        (metadata_dest, metadata.read_bytes()),
    ]
    entries.extend(datapack_entries(datapack))
    destination = DIST / target["artifact"]
    write_zip(destination, entries)
    report(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", help="build a single target, e.g. neoforge-1.21.1")
    parser.add_argument("--datapack-only", action="store_true", help="skip mod jars")
    parser.add_argument("--list", action="store_true", help="list targets and exit")
    args = parser.parse_args()

    config = load_config()
    targets = config["targets"]
    if args.list:
        for name, target in targets.items():
            print(f"{name}: {target['artifact']}")
        return
    if args.target and args.target not in targets:
        fail(f"unknown target {args.target!r}; known: {', '.join(targets)}")

    datapack = validate_datapack(config)
    selected = {args.target: targets[args.target]} if args.target else targets
    metadata = {
        name: validate_metadata(config, name, target)
        for name, target in selected.items()
    }

    print("datapack:")
    datapack_artifacts = {
        target["datapackArtifact"] for target in selected.values()
    }
    for artifact in sorted(datapack_artifacts):
        build_datapack(config, datapack, artifact)

    if not args.datapack_only:
        print("mods:")
        for name, target in selected.items():
            build_mod(config, name, target, metadata[name], datapack)


if __name__ == "__main__":
    main()
