import json
import os
import subprocess
import time

print("🚀 Downloader Engine Start")

# ensure folder
os.makedirs("downloads", exist_ok=True)

# load requests
try:
    with open("requests.json") as f:
        data = json.load(f)
except:
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

    print(f"🎯 Processing: {url}")

    file_id = f"file_{int(time.time())}_{i}"
    output = f"downloads/{file_id}.%(ext)s"

    try:
        if dtype == "audio":
            cmd = [
                "yt-dlp",
                "-x",
                "--audio-format", "mp3",
                "--no-playlist",
                "--force-overwrites",
                "--no-warnings",
                "-o", output,
                url
            ]
        else:
            cmd = [
                "yt-dlp",
                "--no-playlist",
                "--force-overwrites",
                "--no-warnings",
                "-o", output,
                url
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        # check downloaded file
        for f in os.listdir("downloads"):
            if file_id in f:
                print(f"✅ Downloaded: {f}")
                files.append(f)

    except Exception as e:
        print("❌ ERROR:", e)

# save status
with open("status.json", "w") as f:
    json.dump(files, f)

# clear processed requests
with open("requests.json", "w") as f:
    json.dump([], f)

print("🔥 All Done")
