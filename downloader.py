import json
import os
import subprocess
import time

print("🚀 Downloader Engine Start")

# create folder
os.makedirs("downloads", exist_ok=True)

# load requests
try:
    with open("requests.json") as f:
        data = json.load(f)
    print("📥 Requests:", data)
except Exception as e:
    print("❌ Error loading requests:", e)
    data = []

if not data:
    print("⚠️ No requests found")
    exit()

files = []

for i, item in enumerate(data):
    url = item.get("url")
    dtype = item.get("type", "video")

    if not url:
        continue

    print(f"\n🎯 Processing: {url}")

    file_id = f"file_{int(time.time())}_{i}"
    output = f"downloads/{file_id}.%(ext)s"

    try:
        # 🎵 AUDIO
        if dtype == "audio":
            cmd = [
                "yt-dlp",
                "-x",
                "--audio-format", "mp3",
                "--no-playlist",
                "--geo-bypass",
                "--extractor-args", "youtube:player_client=android",
                "--force-overwrites",
                "-o", output,
                url
            ]

        # 🎬 VIDEO
        else:
            cmd = [
                "yt-dlp",
                "-f", "bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
                "--no-playlist",
                "--geo-bypass",
                "--no-check-certificate",
                "--extractor-args", "youtube:player_client=android",
                "--force-overwrites",
                "-o", output,
                url
            ]

        print("⚡ Running command:")
        print(" ".join(cmd))

        result = subprocess.run(cmd, capture_output=True, text=True)

        print("\n📤 STDOUT:\n", result.stdout)
        print("\n⚠️ STDERR:\n", result.stderr)

        if result.returncode != 0:
            print("❌ yt-dlp failed")
            continue

        # find downloaded file
        found = False
        for f in os.listdir("downloads"):
            if file_id in f:
                print(f"✅ Downloaded: {f}")
                files.append(f)
                found = True

        if not found:
            print("❌ File not found after download")

    except Exception as e:
        print("❌ ERROR:", e)

# save status
with open("status.json", "w") as f:
    json.dump(files, f)

# clear requests
with open("requests.json", "w") as f:
    json.dump([], f)

print("\n🔥 All Done")
