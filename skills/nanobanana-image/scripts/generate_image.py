#!/usr/bin/env python3
"""Nano Banana 2 (Gemini API) を使用して画像を生成するスクリプト

機能:
- テキストから画像生成
- 画像から画像生成（image-to-image）
- 複数バリエーション生成
- アスペクト比・サイズ指定
- 高精度テキストレンダリング
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# 利用可能なモデル
MODELS = {
    "flash": "gemini-3.1-flash-image-preview",  # Nano Banana 2 (Pro品質×Flash速度)
    "pro": "gemini-3-pro-image-preview",         # Nano Banana Pro (高度なコンテキスト対応)
}

DEFAULT_MODEL = "flash"  # デフォルトはNano Banana 2

ASPECT_RATIOS = [
    "1:1", "1:4", "1:8",
    "2:3", "3:2", "3:4", "4:1", "4:3", "4:5",
    "5:4", "8:1", "9:16", "16:9", "21:9",
]
IMAGE_SIZES = ["0.5K", "1K", "2K", "4K"]  # 0.5K(512px)はNano Banana 2のみ

# Google検索グラウンディング用ツール
GOOGLE_SEARCH_TOOL = {"google_search": {}}


def get_api_key():
    """環境変数からAPIキーを取得"""
    key = os.environ.get("NANOBANANA_SKILL_GOOGLE_API_KEY")
    if not key:
        print("Error: NANOBANANA_SKILL_GOOGLE_API_KEY を設定してください", file=sys.stderr)
        print("永続化: ~/.claude/settings.json の env に追加", file=sys.stderr)
        print("取得方法: https://aistudio.google.com/", file=sys.stderr)
        sys.exit(1)
    return key


def load_image_as_base64(image_path: str) -> tuple[str, str]:
    """画像ファイルを読み込んでBase64エンコード"""
    path = Path(image_path)
    if not path.exists():
        print(f"Error: 画像ファイルが見つかりません: {image_path}", file=sys.stderr)
        sys.exit(1)

    suffix = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(suffix, "image/png")

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return data, mime_type


def generate_image(
    prompt: str,
    output_path: str,
    model: str = DEFAULT_MODEL,
    input_images: list[str] | None = None,
    count: int = 1,
    aspect_ratio: str | None = None,
    image_size: str | None = None,
    use_search: bool = False,
) -> list[str]:
    """Gemini APIを使用して画像を生成

    Args:
        prompt: 生成プロンプト
        output_path: 出力ファイルパス
        model: 使用するモデル (flash/pro)
        input_images: 参照画像のパスリスト
        count: 生成する画像の数
        aspect_ratio: アスペクト比
        image_size: 画像サイズ
        use_search: Google検索グラウンディングを使用するか

    Returns:
        生成された画像ファイルのパスリスト
    """
    api_key = get_api_key()
    model_id = MODELS.get(model, MODELS[DEFAULT_MODEL])
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"

    # パーツを構築
    parts = []

    # 入力画像がある場合は追加
    if input_images:
        for img_path in input_images:
            img_data, mime_type = load_image_as_base64(img_path)
            parts.append({
                "inlineData": {
                    "mimeType": mime_type,
                    "data": img_data
                }
            })

    # テキストプロンプト
    parts.append({"text": prompt})

    # ペイロード構築
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
        }
    }

    # Google検索グラウンディングを使用する場合
    if use_search:
        payload["tools"] = [GOOGLE_SEARCH_TOOL]

    # 画像設定
    image_config = {}
    if aspect_ratio:
        image_config["aspectRatio"] = aspect_ratio
    if image_size:
        image_config["imageSize"] = image_size
    if count > 1:
        image_config["numberOfImages"] = count

    if image_config:
        payload["generationConfig"]["imageConfig"] = image_config

    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"API Error ({e.code}): {error_body}", file=sys.stderr)
        sys.exit(1)

    # 画像データを抽出
    candidates = result.get("candidates", [])
    if not candidates:
        print("Error: 画像が生成されませんでした", file=sys.stderr)
        sys.exit(1)

    parts = candidates[0].get("content", {}).get("parts", [])
    saved_files = []
    image_index = 0

    output_base = Path(output_path)
    stem = output_base.stem
    suffix = output_base.suffix or ".png"
    parent = output_base.parent

    for part in parts:
        if "inlineData" in part:
            image_data = part["inlineData"]["data"]
            image_bytes = base64.b64decode(image_data)

            if count == 1 and image_index == 0:
                file_path = output_path
            else:
                file_path = str(parent / f"{stem}_{image_index + 1}{suffix}")

            with open(file_path, "wb") as f:
                f.write(image_bytes)

            saved_files.append(file_path)
            image_index += 1

        elif "text" in part:
            # テキストレスポンスがある場合は表示
            print(f"Model response: {part['text']}")

    if not saved_files:
        print("Error: 画像データが見つかりません", file=sys.stderr)
        sys.exit(1)

    for f in saved_files:
        print(f"画像を保存しました: {f}")

    return saved_files


def main():
    parser = argparse.ArgumentParser(
        description="Nano Banana 2 で画像を生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # テキストから画像生成
  %(prog)s "夕焼けのビーチ" -o beach.png

  # 参照画像を使って生成
  %(prog)s "この画像をアニメ風にして" -i reference.png -o anime.png

  # 複数バリエーション生成
  %(prog)s "かわいい猫" -n 3 -o cat.png

  # アスペクト比指定
  %(prog)s "横長の風景" --aspect 16:9 -o landscape.png
""")

    parser.add_argument("prompt", help="画像生成のプロンプト")
    parser.add_argument("-o", "--output", default="output.png",
                        help="出力ファイルパス (default: output.png)")
    parser.add_argument("-m", "--model", choices=list(MODELS.keys()),
                        default=DEFAULT_MODEL,
                        help=f"使用するモデル (default: {DEFAULT_MODEL})")
    parser.add_argument("-i", "--input", action="append", dest="input_images",
                        help="参照画像のパス（複数指定可）")
    parser.add_argument("-n", "--count", type=int, default=1,
                        help="生成する画像の数 (default: 1)")
    parser.add_argument("--aspect", choices=ASPECT_RATIOS,
                        help="アスペクト比")
    parser.add_argument("--size", choices=IMAGE_SIZES,
                        help="画像サイズ")
    parser.add_argument("--search", action="store_true",
                        help="Google検索グラウンディングを使用（最新情報を反映）")

    args = parser.parse_args()

    generate_image(
        prompt=args.prompt,
        output_path=args.output,
        model=args.model,
        input_images=args.input_images,
        count=args.count,
        aspect_ratio=args.aspect,
        image_size=args.size,
        use_search=args.search,
    )


if __name__ == "__main__":
    main()
