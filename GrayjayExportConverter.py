import os
import json
import csv
import urllib.parse
from datetime import datetime, timezone
import zipfile
import tempfile


def parse_youtube_id(url):
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    return qs.get('v', [None])[0]


def epoch_to_iso8601_millis(epoch):
    dt = datetime.fromtimestamp(int(epoch), tz=timezone.utc)
    ms = dt.microsecond // 1000
    time_str = dt.strftime('%Y-%m-%dT%H:%M:%S') + f'.{ms:03d}Z'
    return time_str


def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def extract_zip(export_zip_path):
    temp_dir = tempfile.TemporaryDirectory()
    with zipfile.ZipFile(export_zip_path, 'r') as zf:
        zf.extractall(temp_dir.name)
    return temp_dir


def main():
    export_path = input("Enter the path to the GrayJay export (zip or directory): ").strip()

    parent_dir = os.path.dirname(export_path) or '.'
    output_path = os.path.join(parent_dir, "converter_output")
    ensure_dir_exists(output_path)

    # If input is a zip, extract it and adjust export_path
    if export_path.lower().endswith('.zip'):
        temp_dir_obj = extract_zip(export_path)
        export_path = temp_dir_obj.name  # Now export_path is the extracted directory
        process_export_directory(export_path, output_path)
        # After processing, you can cleanup the temporary directory
        temp_dir_obj.cleanup()
    else:
        # Assume export_path is a directory
        process_export_directory(export_path, output_path)


    print("Conversion complete! Files saved in:", output_path)


def process_export_directory(export_path, output_path):
    # Normalize export_path
    export_path = os.path.normpath(export_path)

    stores_path = os.path.join(export_path, "stores")

    history_path = os.path.join(stores_path, "history")
    playlists_path = os.path.join(stores_path, "Playlists")
    subscriptions_path = os.path.join(stores_path, "Subscriptions")
    watch_later_path = os.path.join(stores_path, "Watch_later")

    # Create a playlists subdirectory inside the output directory
    playlists_dir = os.path.join(output_path, "playlists")
    ensure_dir_exists(playlists_dir)

    # 1. Convert History to watch-history.json
    watch_history = []
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            entries = json.loads(f.read().strip())
            for entry in entries:
                parts = entry.split("|||")
                if len(parts) >= 4:
                    url = parts[0]
                    epoch = parts[1]
                    title = parts[3]
                    if url.startswith("https://www.youtube.com/watch?"):
                        # Replace '=' and '&' for safety in JSON strings
                        safe_url = url.replace('=', '\\u003d').replace('&', '\\u0026')
                        record = {
                            "header": "YouTube",
                            "title": "Watched " + title,
                            "titleUrl": safe_url,
                            "subtitles": [{
                                "name": "Unknown Channel",
                                "url": "https://www.youtube.com/"
                            }],
                            "time": epoch_to_iso8601_millis(epoch),
                            "products": ["YouTube"],
                            "activityControls": ["YouTube watch history"]
                        }
                        watch_history.append(record)

    with open(os.path.join(output_path, "watch-history.json"), "w", encoding="utf-8") as wf:
        json.dump(watch_history, wf, indent=2, ensure_ascii=False)

    # 2. Convert Subscriptions
    subscriptions_data = []
    if os.path.exists(subscriptions_path):
        with open(subscriptions_path, "r", encoding="utf-8") as f:
            subs = json.loads(f.read().strip())
            for sub in subs:
                if "youtube.com/channel/" in sub:
                    channel_id = sub.split("/channel/")[-1]
                    channel_url = f"https://www.youtube.com/channel/{channel_id}"
                    subscriptions_data.append([channel_id, channel_url, "Unknown"])

    with open(os.path.join(output_path, "subscriptions.csv"), "w", encoding="utf-8", newline="") as wf:
        writer = csv.writer(wf)
        writer.writerow(["Channel ID", "Channel URL", "Channel title"])
        writer.writerows(subscriptions_data)

    # 3. Convert Playlists
    if os.path.exists(playlists_path):
        with open(playlists_path, "r", encoding="utf-8") as f:
            playlists = json.loads(f.read().strip())
            for playlist_data in playlists:
                lines = playlist_data.split("\n")
                playlist_name = lines[0].strip() if lines else "Untitled Playlist"
                urls = lines[1:]
                youtube_entries = []
                for u in urls:
                    if "youtube.com/watch?v=" in u:
                        vid = parse_youtube_id(u)
                        if vid:
                            ts = datetime.now(timezone.utc).isoformat()
                            youtube_entries.append([vid, ts])

                if youtube_entries:
                    filename = f"{playlist_name} videos.csv"
                    with open(os.path.join(playlists_dir, filename), "w", encoding="utf-8", newline="") as pf:
                        writer = csv.writer(pf)
                        writer.writerow(["Video ID", "Playlist video creation timestamp"])
                        writer.writerows(youtube_entries)

    # 4. Watch_later as a playlist
    if os.path.exists(watch_later_path):
        with open(watch_later_path, "r", encoding="utf-8") as f:
            watch_later = json.loads(f.read().strip())
            youtube_entries = []
            for u in watch_later:
                if "youtube.com/watch?v=" in u:
                    vid = parse_youtube_id(u)
                    if vid:
                        ts = datetime.now(timezone.utc).isoformat()
                        youtube_entries.append([vid, ts])

            if youtube_entries:
                with open(os.path.join(playlists_dir, "Watch later videos.csv"), "w", encoding="utf-8", newline="") as pf:
                    writer = csv.writer(pf)
                    writer.writerow(["Video ID", "Playlist video creation timestamp"])
                    writer.writerows(youtube_entries)


if __name__ == "__main__":
    main()
