# 🎮 Minecraft Clean Assets for PojavLauncher

[![Build Minecraft Clean Assets](https://github.com/OddBoyXD/minecraft-clean-assets/actions/workflows/build-clean-assets.yml/badge.svg)](https://github.com/OddBoyXD/minecraft-clean-assets/actions/workflows/build-clean-assets.yml)
[![Releases](https://img.shields.io/github/v/release/OddBoyXD/minecraft-clean-assets?color=blue&label=Latest%20Release)](https://github.com/OddBoyXD/minecraft-clean-assets/releases)
[![Repo](https://img.shields.io/badge/Repository-OddBoyXD%2Fminecraft--clean--assets-green)](https://github.com/OddBoyXD/minecraft-clean-assets)

Ultra-fast, lightweight, pre-filtered Minecraft asset packages created specifically for **PojavLauncher** and low-storage mobile environments.

---

## ⚡ Why Clean Assets?

Official Minecraft assets are huge (**~600 MB - 700 MB** per version). PojavLauncher usually spends 10–20 minutes downloading them on mobile connections.

Over **70% of that size is uncompressed ambient background music** that most players mute anyway!

| Feature | Official Mojang Assets | Clean Assets (This Repo) |
| :--- | :--- | :--- |
| **Download Size** | ~600 MB – 700 MB | **~160 MB** (⚡ **Over 73% size reduction**) |
| **Initial Launch Time** | 10–20 min slow mobile download | **Instant / 0 Seconds** (0 bytes needed) |
| **Sound Effects (SFX)** | 100% | **100% Preserved** (Mobs, blocks, weapons, items, footsteps, cave sounds, UI) |
| **Jukebox Music Discs** | 100% | **100% Preserved** (Pigstep, Cat, 13, Otherside, Relic, Creator, etc.) |
| **Languages & Textures**| 100% | **100% Preserved** (All international languages & GUI assets) |
| **Ambient BGM Music** | ~400 MB (heavy ambient loops) | **Stripped** (`minecraft/sounds/music/*`) |

---

## 📥 Direct Mirror Download Links

Click any link below to download the direct, pre-packaged `.zip` asset archive:

### 🌟 All-In-One Universal Bundle (Recommended)
| Package | Supports | Approximate Size | Download Link |
| :--- | :--- | :--- | :--- |
| **⚡ Universal Bundle** | **Minecraft 1.16 through Latest (1.21.4+)** | **~500 MB** | [⬇️ **Download Universal Zip**](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/universal/Minecraft-Universal-1.16-to-Latest-Filtered-Assets.zip) |

*The Universal Bundle contains index files and deduplicated assets for ALL versions from 1.16 to the latest release in a single package. Install it once and you can play ANY Minecraft version offline immediately!*

---

### 📦 Individual Version Archives
| Version | Asset Index | Archive Size | Direct Download Mirror |
| :--- | :--- | :--- | :--- |
| **Minecraft 1.21.4** | `19` / `1.21.4` | ~170 MB | [⬇️ Download 1.21.4.zip](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/v1.21.4/Minecraft-1.21.4-Filtered-Assets.zip) |
| **Minecraft 1.21.1** | `17` / `1.21.1` | ~170 MB | [⬇️ Download 1.21.1.zip](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/v1.21.1/Minecraft-1.21.1-Filtered-Assets.zip) |
| **Minecraft 1.20.4** | `12` / `1.20.4` | ~166 MB | [⬇️ Download 1.20.4.zip](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/v1.20.4/Minecraft-1.20.4-Filtered-Assets.zip) |
| **Minecraft 1.20.1** | `5` / `1.20.1`   | ~165 MB | [⬇️ Download 1.20.1.zip](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/v1.20.1/Minecraft-1.20.1-Filtered-Assets.zip) |
| **Minecraft 1.19.4** | `3` / `1.19.4`   | 167.7 MB | [⬇️ Download 1.19.4.zip](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/v1.19.4/Minecraft-1.19.4-Filtered-Assets.zip) |
| **Minecraft 1.19.2** | `1.19` / `1.19.2` | ~163 MB | [⬇️ Download 1.19.2.zip](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/v1.19.2/Minecraft-1.19.2-Filtered-Assets.zip) |
| **Minecraft 1.18.2** | `1.18` / `1.18.2` | ~160 MB | [⬇️ Download 1.18.2.zip](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/v1.18.2/Minecraft-1.18.2-Filtered-Assets.zip) |
| **Minecraft 1.17.1** | `1.17` / `1.17.1` | ~155 MB | [⬇️ Download 1.17.1.zip](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/v1.17.1/Minecraft-1.17.1-Filtered-Assets.zip) |
| **Minecraft 1.16.5** | `1.16` / `1.16.5` | ~150 MB | [⬇️ Download 1.16.5.zip](https://github.com/OddBoyXD/minecraft-clean-assets/releases/download/v1.16.5/Minecraft-1.16.5-Filtered-Assets.zip) |

👉 **[Browse All Releases & Files on GitHub](https://github.com/OddBoyXD/minecraft-clean-assets/releases)**

---

## 🛠️ How to Use with PojavLauncher

### Method 1: Using Custom PojavLauncher (One-Tap Direct Extract)
1. Download the clean assets zip file.
2. In the PojavLauncher main menu, tap the **"Direct Extract Assets"** button.
3. Select your downloaded `.zip` file.
4. The launcher will automatically extract the indexes and objects into `.minecraft/assets/` at high speed with progress feedback!
5. Launch Minecraft—it starts immediately with zero download wait time!

---

### Method 2: Manual Extraction (Any File Manager / ZArchiver)
1. Download the version zip or Universal zip.
2. Open **ZArchiver** (or any archive manager).
3. Extract the contents of the zip directly into your PojavLauncher `.minecraft` directory:
   ```
   /sdcard/Android/data/net.kdt.pojavlaunch/files/.minecraft/
   ```
   *(Or `/sdcard/Android/data/net.kdt.pojavlaunch.debug/files/.minecraft/` for debug builds)*
4. Ensure the files merge into:
   - `.minecraft/assets/indexes/*.json`
   - `.minecraft/assets/objects/*`
5. Launch the game offline!

---

## ⚙️ Building via GitHub Actions

You can trigger your own clean assets build anytime directly from GitHub:
1. Go to the [Actions tab](https://github.com/OddBoyXD/minecraft-clean-assets/actions).
2. Select **Build Minecraft Clean Assets**.
3. Click **Run workflow**.
4. Choose target:
   - `universal` (Builds the 1.16-to-Latest Universal Bundle)
   - `all` (Builds all major version archives + Universal bundle)
   - Or enter any specific version (e.g. `1.20.1`, `1.21.4`).
5. Download the artifact or access the automatically published GitHub Release!

---

## 💻 Local Script Usage

```bash
# Clone the repository
git clone https://github.com/OddBoyXD/minecraft-clean-assets.git
cd minecraft-clean-assets

# Build Universal Bundle (1.16 to Latest)
python3 generator.py --universal

# Build for a specific Minecraft version
python3 generator.py 1.20.1

# Build all versions at once
python3 generator.py --all

# Optional: also strip music discs / records (extra small size)
python3 generator.py 1.20.1 --no-records
```

---

## 📜 Technical Details & Verification
- **Hash Integrity**: Every object is verified against Mojang's official SHA-1 manifest hash upon download.
- **Offline Assurance**: Mojang index files (`assets/indexes/<ver>.json` and `<index_id>.json`) are populated so PojavLauncher's `skip = outFile.exists()` passes unconditionally for all objects.
- **Safe & Clean**: Zero APK modification required for the assets—compatible with standard PojavLauncher and all modded clients (Fabric, Forge, NeoForge, Quilt).
