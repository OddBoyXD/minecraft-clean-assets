# ⚡ Minecraft Clean Assets Generator for PojavLauncher

Ultra-fast generator that downloads and packages clean, lightweight Minecraft assets for **PojavLauncher** on Android.

---

### 🎯 Why Use Clean Assets?
- **Standard Mojang 1.19.4 Assets**: **~600 MB** (Over 326 MB is heavy background music tracks).
- **Clean Assets**: **~160 MB** (Over **73% size reduction!**).
- **100% SFX & Textures Intact**:
  - ✅ All block breaking, placing, and stepping sounds
  - ✅ All mob & animal sounds
  - ✅ All item, weapon, and tool sounds
  - ✅ All ambient cave, weather, and environmental sounds
  - ✅ All UI click, inventory, and experience sounds
  - ✅ All Jukebox music discs / records (Pigstep, Cat, Wait, etc.)
  - ✅ All languages and GUI title backgrounds
  - ❌ Stripped: Background ambient music ()

---

### 🚀 Usage

#### 1. Instant Cloud Generation (GitHub Actions)
1. Go to the **Actions** tab in this repository.
2. Select **Build Minecraft Clean Assets**.
3. Click **Run workflow**, enter the version (e.g. , , , ), and click **Run**.
4. Download the generated zip artifact or release directly to your device!

#### 2. Local / Terminal Generation
```bash
# Generate clean assets for Minecraft 1.19.4
python3 generator.py 1.19.4

# Generate for Minecraft 1.20.1
python3 generator.py 1.20.1

# Also strip music discs / records (for extreme data saving)
python3 generator.py 1.19.4 --no-records
```

---

### 📦 PojavLauncher Integration
Extract the generated `Minecraft-<version>-Filtered-Assets.zip` directly into:
```
/sdcard/Android/data/net.kdt.pojavlaunch/files/.minecraft/
```
Or use the one-tap **Direct Extract Assets** button in your custom PojavLauncher build.
