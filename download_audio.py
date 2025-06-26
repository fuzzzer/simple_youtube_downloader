import yt_dlp
import os
import argparse

BASE_DIR = os.path.join("downloads", "audio")

def detect_info(url):
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def build_output_template(info):
    if info.get('_type') == 'playlist':
        return os.path.join(BASE_DIR, '%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s'), True
    else:
        return os.path.join(BASE_DIR, 'all/%(title)s.%(ext)s'), False

def download_best_audio(url, quality='320'):
    info = detect_info(url)
    outtmpl, is_playlist = build_output_template(info)
    os.makedirs(BASE_DIR, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'noplaylist': not is_playlist,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
        'progress_hooks': [download_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_hook(d):
    if d['status'] == 'finished':
        print(f"\n✅ Audio downloaded: {d['filename']}")
    elif d['status'] == 'downloading':
        print(f"\r⬇️  {d['_percent_str']} of {d['info_dict']['title']}...", end='')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube best audio downloader")
    parser.add_argument('--url', help="YouTube video or playlist URL", required=False)
    parser.add_argument('--quality', help="Audio quality (e.g. 320, 256, 192)", default="320")
    args = parser.parse_args()

    url = args.url or input("🎧 Enter YouTube URL (video or playlist): ").strip()
    download_best_audio(url, args.quality)
