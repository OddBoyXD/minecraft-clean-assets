#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import zipfile
import argparse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time

MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
RESOURCE_CDN = "https://resources.download.minecraft.net"

def get_manifest():
    req = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "MinecraftCleanAssets/1.0"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_version_info(manifest, version_id):
    for v in manifest.get("versions", []):
        if v.get("id") == version_id:
            req = urllib.request.Request(v["url"], headers={"User-Agent": "MinecraftCleanAssets/1.0"})
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
    raise ValueError(f"Version '{version_id}' not found in Mojang manifest.")

def download_file(url, path, expected_hash, retries=3):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with open(path, "rb") as f:
            if hashlib.sha1(f.read()).hexdigest() == expected_hash:
                return True
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MinecraftCleanAssets/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            if hashlib.sha1(data).hexdigest() == expected_hash:
                with open(path, "wb") as f:
                    f.write(data)
                return True
        except Exception:
            pass
    return False

def build_clean_assets(version_id, output_dir="output", workers=32, keep_records=True):
    print(f"\n[+] Fetching Mojang version manifest for: {version_id}...")
    manifest = get_manifest()
    version_info = get_version_info(manifest, version_id)
    
    asset_index_info = version_info.get("assetIndex", {})
    index_url = asset_index_info.get("url")
    index_id = asset_index_info.get("id", version_id)
    
    if not index_url:
        raise ValueError(f"No asset index found for version {version_id}")
    
    print(f"[+] Fetching official asset index '{index_id}' from: {index_url}")
    req = urllib.request.Request(index_url, headers={"User-Agent": "MinecraftCleanAssets/1.0"})
    with urllib.request.urlopen(req) as resp:
        official_index = json.loads(resp.read().decode("utf-8"))
    
    official_objects = official_index.get("objects", {})
    print(f"[+] Official asset count: {len(official_objects):,} objects")
    
    # Filtering logic:
    # Remove ambient background music ('minecraft/sounds/music/...')
    # Keep jukebox records ('minecraft/sounds/records/...') if keep_records is True
    # Keep all block, mob, entity, item, ambient, step, ui sounds
    # Keep all textures, icons, language files, and metadata
    filtered_objects = {}
    removed_music_count = 0
    removed_music_bytes = 0
    
    for key, item in official_objects.items():
        if key.startswith("minecraft/sounds/music/"):
            removed_music_count += 1
            removed_music_bytes += item.get("size", 0)
            continue
        if not keep_records and key.startswith("minecraft/sounds/records/"):
            removed_music_count += 1
            removed_music_bytes += item.get("size", 0)
            continue
        filtered_objects[key] = item
    
    total_clean_bytes = sum(item.get("size", 0) for item in filtered_objects.values())
    print(f"[✓] Filtered out {removed_music_count} music tracks ({removed_music_bytes / (1024*1024):.2f} MB saved!)")
    print(f"[✓] Clean asset set: {len(filtered_objects):,} objects ({total_clean_bytes / (1024*1024):.2f} MB uncompressed)")
    
    cache_dir = os.path.join(output_dir, "cache_objects")
    os.makedirs(cache_dir, exist_ok=True)
    
    print(f"\n[+] Concurrently downloading {len(filtered_objects):,} clean asset objects ({workers} workers)...")
    start_time = time()
    downloaded = 0
    failed = 0
    
    tasks = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for key, item in filtered_objects.items():
            h = item["hash"]
            prefix = h[:2]
            url = f"{RESOURCE_CDN}/{prefix}/{h}"
            dest = os.path.join(cache_dir, prefix, h)
            tasks.append((executor.submit(download_file, url, dest, h), h, dest))
        
        for future, h, dest in tasks:
            if future.result():
                downloaded += 1
            else:
                failed += 1
            if downloaded % 500 == 0 or downloaded == len(filtered_objects):
                pct = (downloaded / len(filtered_objects)) * 100
                sys.stdout.write(f"\r[+] Progress: {downloaded}/{len(filtered_objects)} ({pct:.1f}%) | Time: {time()-start_time:.1f}s")
                sys.stdout.flush()
    
    print(f"\n[✓] Download finished in {time()-start_time:.1f}s (Downloaded: {downloaded}, Failed: {failed})")
    if failed > 0:
        raise RuntimeError(f"Failed to download {failed} assets. Please re-run to retry.")
    
    # Create clean index JSON (same format as Pojav expects)
    clean_index_content = json.dumps(official_index, separators=(',', ':')).encode('utf-8')
    
    zip_filename = f"Minecraft-{version_id}-Filtered-Assets.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n[+] Packaging PojavLauncher assets zip: {zip_path}...")
    zip_start = time()
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # 1. Store index files
        zf.writestr(f"assets/indexes/{version_id}.json", clean_index_content)
        if index_id != version_id:
            zf.writestr(f"assets/indexes/{index_id}.json", clean_index_content)
        
        # 2. Store all object files
        count = 0
        for key, item in filtered_objects.items():
            h = item["hash"]
            prefix = h[:2]
            src = os.path.join(cache_dir, prefix, h)
            arcname = f"assets/objects/{prefix}/{h}"
            zf.write(src, arcname)
            count += 1
            if count % 1000 == 0 or count == len(filtered_objects):
                sys.stdout.write(f"\r[+] Zipping: {count}/{len(filtered_objects)} objects...")
                sys.stdout.flush()
    
    zip_size_mb = os.path.getsize(zip_path) / (1024*1024)
    print(f"\n[🎉] SUCCESS! Clean Assets Zip created in {time()-zip_start:.1f}s")
    print(f"    File: {zip_path}")
    print(f"    Size: {zip_size_mb:.2f} MB (Super compact!)")
    return zip_path

def main():
    parser = argparse.ArgumentParser(description="Minecraft Clean Assets Generator for PojavLauncher")
    parser.add_argument("version", nargs="?", default="1.19.4", help="Minecraft version (e.g. 1.19.4, 1.20.1, 1.21)")
    parser.add_argument("--workers", type=int, default=32, help="Download worker threads (default: 32)")
    parser.add_argument("--out", default="output", help="Output directory")
    parser.add_argument("--no-records", action="store_true", help="Also strip music discs / records")
    args = parser.parse_args()
    
    build_clean_assets(args.version, output_dir=args.out, workers=args.workers, keep_records=not args.no_records)

if __name__ == "__main__":
    main()
