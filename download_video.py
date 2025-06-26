import yt_dlp
import os

BASE_DIR = os.path.join("downloads", "videos")
RESOLUTION_ORDER = ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p']

def get_max_resolution_id(max_res):
    try:
        return RESOLUTION_ORDER.index(max_res)
    except ValueError:
        return len(RESOLUTION_ORDER) - 1

def build_format_selector(max_res):
    try:
        max_height = int(max_res.replace("p", ""))
    except:
        max_height = 1080  # default fallback
    return f"bestvideo[height<={max_height}]+bestaudio/best"

def download_from_url(url, max_quality='1080p'):
    # Probe info to check if it's a playlist or a video
    ydl_probe_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_probe_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    is_playlist = info.get('_type') == 'playlist'
    playlist_title = info.get('title') if is_playlist else None

    if is_playlist:
        outtmpl = os.path.join(BASE_DIR, f"{playlist_title}/%(playlist_index)03d - %(title)s.%(ext)s")
    else:
        outtmpl = os.path.join(BASE_DIR, "all", '%(title)s.%(ext)s')

    ydl_opts = {
        'format': build_format_selector(max_quality),
        'outtmpl': outtmpl,
        'noplaylist': not is_playlist,
        'merge_output_format': 'mp4',
        'postprocessors': [
            {'key': 'FFmpegMetadata'},
        ],
        'progress_hooks': [progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"\r⬇️  {d['_percent_str']} ETA {d['_eta_str']}", end='')
    elif d['status'] == 'finished':
        print(f"\n✅ Downloaded: {d['filename']}")

if __name__ == "__main__":
    url = input("🎥 Enter YouTube video or playlist URL: ").strip()
    max_q = input("🎯 Max quality (e.g. 1080p, 720p): ").strip().lower() or '1080p'
    os.makedirs(BASE_DIR, exist_ok=True)
    download_from_url(url, max_q)
