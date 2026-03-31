import json, os, subprocess

# load requests
try:
    with open("requests.json") as f:
        data = json.load(f)
except:
    data = []

os.makedirs("downloads", exist_ok=True)

files = []

for i, item in enumerate(data):
    url = item["url"]
    dtype = item.get("type", "video")
    out = f"downloads/file_{i}.%(ext)s"

    try:
        if dtype == "audio":
            subprocess.run([
                "yt-dlp","-x","--audio-format","mp3","-o",out,url
            ])
        else:
            subprocess.run([
                "yt-dlp","-o",out,url
            ])

        # find file
        for f in os.listdir("downloads"):
            if f.startswith(f"file_{i}"):
                files.append(f)

    except:
        pass

# save status
with open("status.json", "w") as f:
    json.dump(files, f)

# clear requests
with open("requests.json", "w") as f:
    json.dump([], f)
