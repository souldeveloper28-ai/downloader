import json, os, subprocess

print("🚀 ULTRA START")

try:
    with open("requests.json") as f:
        data = json.load(f)
except:
    data = []

os.makedirs("downloads", exist_ok=True)

files = []

# process max 3 at a time (faster + safe)
batch = data[:3]

for i, item in enumerate(batch):
    url = item["url"]
    dtype = item.get("type", "video")

    print("Downloading:", url)

    out = f"downloads/file_{i}.%(ext)s"

    try:
        if dtype == "audio":
            subprocess.run([
                "yt-dlp",
                "-x",
                "--audio-format", "mp3",
                "--no-playlist",
                "-o", out,
                url
            ], check=True)
        else:
            subprocess.run([
                "yt-dlp",
                "--no-playlist",
                "-o", out,
                url
            ], check=True)

        for f in os.listdir("downloads"):
            if f.startswith(f"file_{i}"):
                files.append(f)

    except Exception as e:
        print("ERROR:", e)

# remaining queue
remaining = data[3:]

with open("requests.json", "w") as f:
    json.dump(remaining, f)

with open("status.json", "w") as f:
    json.dump(files, f)

print("✅ DONE")
