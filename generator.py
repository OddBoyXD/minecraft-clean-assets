#!/usr/bin/env python3
"""
Minecraft Clean Assets Generator for PojavLauncher
Downloads Mojang asset indexes, strips heavy ambient music (~300MB+),
retains 100% sound effects, jukebox music discs, UI textures, and languages,
and creates clean, instant-launch asset packages.
"""

import os
import sys
import json
import hashlib
import zipfile
import argparse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from time import time

MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
RESOURCE_CDN = "https://resources.download.minecraft.net"

# Standard major release versions from 1.16 to latest
DEFAULT_VERSIONS = [
    "1.16.5",
    "1.17.1",
    "1.18.2",
    "1.19.2",
    "1.19.3",
    "1.19.4",
    "1.20.1",
    "1.20.2",
    "1.20.4",
    "1.20.6",
    "1.21.1",
    "1.21.3",
    "1.21.4",
]

def get_manifest():
    req = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "MinecraftCleanAssets/2.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_all_releases_from_116(manifest):
    releases = [v for v in manifest.get("versions", []) if v.get("type") == "release"]
    results = []
    found = False
    for v in reversed(releases):
        if v.get("id") == "1.16":
            found = True
        if found:
            results.append(v)
    return list(reversed(results))

def get_version_info(manifest, version_id):
    for v in manifest.get("versions", []):
        if v.get("id") == version_id:
            req = urllib.request.Request(v["url"], headers={"User-Agent": "MinecraftCleanAssets/2.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
    raise ValueError(f"Version '{version_id}' not found in Mojang manifest.")

def download_file(url, path, expected_hash, retries=3):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                if hashlib.sha1(f.read()).hexdigest() == expected_hash:
                    return True
        except Exception:
            pass
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MinecraftCleanAssets/2.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            if hashlib.sha1(data).hexdigest() == expected_hash:
                with open(path, "wb") as f:
                    f.write(data)
                return True
        except Exception:
            pass
    return False

def build_single_version(version_id, manifest, output_dir="output", cache_dir=None, workers=32, keep_records=True):
    print(f"\n{'='*60}")
    print(f"[*] Processing Minecraft {version_id}...")
    print(f"{'='*60}")
    
    version_info = get_version_info(manifest, version_id)
    asset_index_info = version_info.get("assetIndex", {})
    index_url = asset_index_info.get("url")
    index_id = asset_index_info.get("id", version_id)
    
    if not index_url:
        print(f"[-] No asset index found for version {version_id}, skipping.")
        return None
    
    req = urllib.request.Request(index_url, headers={"User-Agent": "MinecraftCleanAssets/2.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        official_index = json.loads(resp.read().decode("utf-8"))
    
    official_objects = official_index.get("objects", {})
    
    # Filter out ambient background music
    filtered_objects = {}
    removed_music = 0
    removed_bytes = 0
    for key, item in official_objects.items():
        if key.startswith("minecraft/sounds/music/"):
            removed_music += 1
            removed_bytes += item.get("size", 0)
            continue
        if not keep_records and key.startswith("minecraft/sounds/records/"):
            removed_music += 1
            removed_bytes += item.get("size", 0)
            continue
        filtered_objects[key] = item
    
    clean_bytes = sum(item.get("size", 0) for item in filtered_objects.values())
    print(f"[✓] Objects: {len(filtered_objects):,} | Stripped music: {removed_music} ({removed_bytes/(1024*1024):.1f} MB saved) | Size: {clean_bytes/(1024*1024):.1f} MB")
    
    if cache_dir is None:
        cache_dir = os.path.join(output_dir, "cache_objects")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Download missing objects concurrently
    tasks = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for key, item in filtered_objects.items():
            h = item["hash"]
            prefix = h[:2]
            url = f"{RESOURCE_CDN}/{prefix}/{h}"
            dest = os.path.join(cache_dir, prefix, h)
            tasks.append((executor.submit(download_file, url, dest, h), h, dest))
        
        done = 0
        for future, h, dest in tasks:
            if future.result():
                done += 1
            if done % 1000 == 0 or done == len(filtered_objects):
                sys.stdout.write(f"\r[+] Downloaded: {done}/{len(filtered_objects)} ({done/len(filtered_objects)*100:.1f}%)")
                sys.stdout.flush()
    print()
    
    # Build clean zip
    clean_index_content = json.dumps(official_index, separators=(',', ':')).encode('utf-8')
    zip_filename = f"Minecraft-{version_id}-Filtered-Assets.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    os.makedirs(output_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        zf.writestr(f"assets/indexes/{version_id}.json", clean_index_content)
        if index_id != version_id:
            zf.writestr(f"assets/indexes/{index_id}.json", clean_index_content)
        
        seen_hashes = set()
        for key, item in filtered_objects.items():
            h = item["hash"]
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            prefix = h[:2]
            src = os.path.join(cache_dir, prefix, h)
            arcname = f"assets/objects/{prefix}/{h}"
            zf.write(src, arcname)
    
    size_mb = os.path.getsize(zip_path) / (1024*1024)
    print(f"[🎉] Created: {zip_filename} ({size_mb:.2f} MB)")
    return zip_path

def build_universal_bundle(manifest, output_dir="output", cache_dir=None, workers=48, keep_records=True):
    print(f"\n{'='*70}")
    print(f"[*] Building UNIVERSAL Clean Assets Bundle (Minecraft 1.16 to Latest)...")
    print(f"{'='*70}")
    
    releases = get_all_releases_from_116(manifest)
    print(f"[+] Found {len(releases)} release versions from 1.16 to latest ({releases[0]['id']} -> {releases[-1]['id']})")
    
    if cache_dir is None:
        cache_dir = os.path.join(output_dir, "cache_objects")
    os.makedirs(cache_dir, exist_ok=True)
    
    all_filtered_objects = {}  # hash -> item
    version_indexes = {}      # filename -> content
    
    for v in releases:
        vid = v["id"]
        try:
            v_info = get_version_info(manifest, vid)
            ainfo = v_info.get("assetIndex", {})
            aurl = ainfo.get("url")
            iid = ainfo.get("id", vid)
            if not aurl:
                continue
            
            req = urllib.request.Request(aurl, headers={"User-Agent": "MinecraftCleanAssets/2.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
            data = json.loads(content.decode("utf-8"))
            
            version_indexes[f"assets/indexes/{vid}.json"] = content
            if iid != vid:
                version_indexes[f"assets/indexes/{iid}.json"] = content
            
            for key, item in data.get("objects", {}).items():
                if key.startswith("minecraft/sounds/music/"):
                    continue
                if not keep_records and key.startswith("minecraft/sounds/records/"):
                    continue
                all_filtered_objects[item["hash"]] = item
        except Exception as e:
            print(f"[-] Error on version {vid}: {e}")
    
    total_mb = sum(item.get("size", 0) for item in all_filtered_objects.values()) / (1024*1024)
    print(f"[✓] Total deduplicated clean objects across all versions: {len(all_filtered_objects):,} ({total_mb:.2f} MB)")
    print(f"[✓] Total version indexes to bundle: {len(version_indexes):,}")
    
    print(f"\n[+] Downloading clean objects with {workers} workers...")
    tasks = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for h, item in all_filtered_objects.items():
            prefix = h[:2]
            url = f"{RESOURCE_CDN}/{prefix}/{h}"
            dest = os.path.join(cache_dir, prefix, h)
            tasks.append((executor.submit(download_file, url, dest, h), h, dest))
        
        done = 0
        for future, h, dest in tasks:
            if future.result():
                done += 1
            if done % 1000 == 0 or done == len(all_filtered_objects):
                sys.stdout.write(f"\r[+] Downloaded: {done}/{len(all_filtered_objects)} ({done/len(all_filtered_objects)*100:.1f}%)")
                sys.stdout.flush()
    print()
    
    zip_filename = "Minecraft-Universal-1.16-to-Latest-Filtered-Assets.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n[+] Packaging Universal Bundle: {zip_path}...")
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for arcname, content in version_indexes.items():
            zf.writestr(arcname, content)
        
        count = 0
        for h in all_filtered_objects.keys():
            prefix = h[:2]
            src = os.path.join(cache_dir, prefix, h)
            arcname = f"assets/objects/{prefix}/{h}"
            zf.write(src, arcname)
            count += 1
            if count % 2000 == 0 or count == len(all_filtered_objects):
                sys.stdout.write(f"\r[+] Packaging: {count}/{len(all_filtered_objects)} objects...")
                sys.stdout.flush()
    print()
    
    size_mb = os.path.getsize(zip_path) / (1024*1024)
    print(f"\n[🎉] SUCCESS! Universal Bundle created: {zip_filename} ({size_mb:.2f} MB)")
    return zip_path

def main():
    parser = argparse.ArgumentParser(description="Minecraft Clean Assets Generator for PojavLauncher")
    parser.add_argument("version", nargs="?", default=None, help="Minecraft version (e.g. 1.19.4, 1.20.1, 1.21.1, all, universal)")
    parser.add_argument("--all", action="store_true", help="Build clean zips for all popular versions + universal bundle (1.16 to latest)")
    parser.add_argument("--universal", action="store_true", help="Build a single Universal All-In-One clean assets bundle (1.16 to latest)")
    parser.add_argument("--workers", type=int, default=32, help="Download worker threads (default: 32)")
    parser.add_argument("--out", default="output", help="Output directory")
    parser.add_argument("--no-records", action="store_true", help="Also strip music discs / records")
    args = parser.parse_args()
    
    manifest = get_manifest()
    cache_dir = os.path.join(args.out, "cache_objects")
    
    if args.universal or args.version == "universal":
        build_universal_bundle(manifest, output_dir=args.out, cache_dir=cache_dir, workers=args.workers, keep_records=not args.no_records)
    elif args.all or args.version == "all":
        print(f"\n[+] Building clean assets for ALL major versions (1.16 to latest)...")
        for v in DEFAULT_VERSIONS:
            build_single_version(v, manifest, output_dir=args.out, cache_dir=cache_dir, workers=args.workers, keep_records=not args.no_records)
        print(f"\n[+] Now generating Universal All-In-One bundle...")
        build_universal_bundle(manifest, output_dir=args.out, cache_dir=cache_dir, workers=args.workers, keep_records=not args.no_records)
    else:
        v = args.version or "1.19.4"
        build_single_version(v, manifest, output_dir=args.out, cache_dir=cache_dir, workers=args.workers, keep_records=not args.no_records)

if __name__ == "__main__":
    main()
