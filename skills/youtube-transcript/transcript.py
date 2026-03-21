#!/usr/bin/env python3
"""YouTube動画の文字起こしをダウンロードするCLIツール"""

import argparse
import shutil
import subprocess
import sys
import os
import re


def get_yt_dlp_path() -> str:
    """venv内またはシステムのyt-dlpパスを返す"""
    # 同じvenv内のyt-dlpを優先
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "yt-dlp")
    if os.path.isfile(venv_path):
        return venv_path
    # システムのyt-dlp
    system_path = shutil.which("yt-dlp")
    if system_path:
        return system_path
    print("エラー: yt-dlpが見つかりません。pip install yt-dlp を実行してください。", file=sys.stderr)
    sys.exit(1)


def extract_video_id(url: str) -> str:
    """URLまたは動画IDからvideo IDを抽出"""
    patterns = [
        r'(?:v=|\/v\/|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url


def download_transcript(url: str, lang: str = "ja", output_dir: str = "output", fmt: str = "srt") -> str | None:
    """yt-dlpで文字起こしをダウンロード"""
    os.makedirs(output_dir, exist_ok=True)
    video_id = extract_video_id(url)
    output_path = os.path.join(output_dir, video_id)

    cmd = [
        get_yt_dlp_path(),
        "--write-auto-sub",
        "--sub-lang", lang,
        "--sub-format", fmt,
        "--skip-download",
        "-o", output_path,
        url if url.startswith("http") else f"https://www.youtube.com/watch?v={url}",
    ]

    print(f"ダウンロード中: {video_id}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"エラー: {result.stderr}", file=sys.stderr)
        return None

    # 出力ファイルを探す
    for f in os.listdir(output_dir):
        if f.startswith(video_id) and f.endswith(f".{fmt}"):
            filepath = os.path.join(output_dir, f)
            print(f"保存先: {filepath}")
            return filepath

    print("字幕が見つかりませんでした。自動生成字幕がない動画の可能性があります。", file=sys.stderr)
    return None


def srt_to_text(srt_path: str) -> str:
    """SRTファイルからタイムスタンプを除去してテキストのみ抽出"""
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    text_lines = []
    for line in lines:
        line = line.strip()
        # 番号行、タイムスタンプ行、空行をスキップ
        if not line or line.isdigit() or "-->" in line:
            continue
        # HTMLタグを除去
        clean = re.sub(r"<[^>]+>", "", line)
        if clean and clean not in text_lines[-1:]:
            text_lines.append(clean)

    return "\n".join(text_lines)


def main():
    parser = argparse.ArgumentParser(description="YouTube動画の文字起こしをダウンロード")
    parser.add_argument("url", help="YouTube動画のURLまたは動画ID")
    parser.add_argument("-l", "--lang", default="ja", help="字幕の言語コード (デフォルト: ja)")
    parser.add_argument("-o", "--output", default="output", help="出力ディレクトリ (デフォルト: output)")
    parser.add_argument("-t", "--text-only", action="store_true", help="テキストのみ出力（タイムスタンプなし）")
    args = parser.parse_args()

    srt_path = download_transcript(args.url, args.lang, args.output)
    if not srt_path:
        sys.exit(1)

    if args.text_only:
        text = srt_to_text(srt_path)
        txt_path = srt_path.rsplit(".", 1)[0] + ".txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"テキスト保存先: {txt_path}")


if __name__ == "__main__":
    main()
