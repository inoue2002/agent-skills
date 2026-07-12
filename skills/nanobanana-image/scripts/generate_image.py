#!/usr/bin/env python3
"""Nano Banana (Gemini Interactions API) を使用して画像を生成するスクリプト

機能:
- テキストから画像生成
- 画像から画像生成（image-to-image、最大14枚）
- 複数バリエーション生成
- アスペクト比・サイズ指定
- Google検索グラウンディング（Web検索・画像検索）
- 思考レベル制御（thinking_level）
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

API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

# 利用可能なモデル
MODELS = {
    "lite": "gemini-3.1-flash-lite-image",  # Nano Banana 2 Lite (最速・最安、1Kのみ)
    "flash": "gemini-3.1-flash-image",      # Nano Banana 2 (万能・デフォルト)
    "pro": "gemini-3-pro-image",            # Nano Banana Pro (プロ品質・複雑な指示向け)
}

DEFAULT_MODEL = "flash"  # デフォルトはNano Banana 2

ASPECT_RATIOS = [
    "1:1", "1:4", "1:8",
    "2:3", "3:2", "3:4", "4:1", "4:3", "4:5",
    "5:4", "8:1", "9:16", "16:9", "21:9",
]
IMAGE_SIZES = ["512", "0.5K", "1K", "2K", "4K"]  # 512(=0.5K)はflashのみ、liteは1Kのみ
THINKING_LEVELS = ["minimal", "high"]  # flashのみ指定可能

MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


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

    mime_type = MIME_TYPES.get(path.suffix.lower(), "image/png")

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return data, mime_type


def validate_options(model: str, image_size: str | None, use_search: bool,
                     use_image_search: bool, thinking: str | None):
    """モデルごとの制約をチェック"""
    errors = []
    if model == "lite":
        if image_size and image_size != "1K":
            errors.append("lite は 1K のみ対応です（--size を外すか 1K を指定）")
        if use_search or use_image_search:
            errors.append("lite は Google検索グラウンディング非対応です（--model flash / pro を使用）")
        if thinking:
            errors.append("lite は --thinking 非対応です")
    if model == "pro":
        if image_size == "512":
            errors.append("512(0.5K) は flash のみ対応です")
        if use_image_search:
            errors.append("--image-search は flash のみ対応です")
        if thinking:
            errors.append("--thinking は flash のみ対応です")

    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def build_payload(
    prompt: str,
    model_id: str,
    input_images: list[str] | None,
    aspect_ratio: str | None,
    image_size: str | None,
    use_search: bool,
    use_image_search: bool,
    thinking: str | None,
) -> dict:
    """Interactions API のリクエストペイロードを構築"""
    input_blocks = []

    # 入力画像がある場合は追加
    if input_images:
        for img_path in input_images:
            img_data, mime_type = load_image_as_base64(img_path)
            input_blocks.append({
                "type": "image",
                "mime_type": mime_type,
                "data": img_data,
            })

    # テキストプロンプト
    input_blocks.append({"type": "text", "text": prompt})

    payload = {
        "model": model_id,
        "input": input_blocks,
    }

    # Google検索グラウンディング
    if use_search or use_image_search:
        search_types = []
        if use_search:
            search_types.append("web_search")
        if use_image_search:
            search_types.append("image_search")
        payload["tools"] = [{"type": "google_search", "search_types": search_types}]

    # 出力形式（アスペクト比・サイズ）。出力mime_typeはAPI側がimage/jpeg固定
    image_format = {"type": "image"}
    if aspect_ratio:
        image_format["aspect_ratio"] = aspect_ratio
    if image_size:
        image_format["image_size"] = image_size
    payload["response_format"] = [{"type": "text"}, image_format]

    # 思考レベル（flashのみ）
    if thinking:
        payload["generation_config"] = {"thinking_level": thinking}

    return payload


def call_api(payload: dict, api_key: str) -> dict:
    """Interactions API を呼び出す"""
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=600) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"API Error ({e.code}): {error_body}", file=sys.stderr)
        sys.exit(1)


def extract_outputs(interaction: dict) -> tuple[list[bytes], list[str]]:
    """レスポンスのstepsから画像とテキストを抽出"""
    images = []
    texts = []
    for step in interaction.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for block in step.get("content", []):
            if block.get("type") == "image":
                images.append(base64.b64decode(block["data"]))
            elif block.get("type") == "text" and block.get("text"):
                texts.append(block["text"])
    return images, texts


def generate_image(
    prompt: str,
    output_path: str,
    model: str = DEFAULT_MODEL,
    input_images: list[str] | None = None,
    count: int = 1,
    aspect_ratio: str | None = None,
    image_size: str | None = None,
    use_search: bool = False,
    use_image_search: bool = False,
    thinking: str | None = None,
) -> list[str]:
    """Gemini Interactions APIを使用して画像を生成

    Args:
        prompt: 生成プロンプト
        output_path: 出力ファイルパス
        model: 使用するモデル (lite/flash/pro)
        input_images: 参照画像のパスリスト（最大14枚）
        count: 生成する画像の数（枚数分リクエストを繰り返す）
        aspect_ratio: アスペクト比
        image_size: 画像サイズ
        use_search: Google Web検索グラウンディングを使用するか
        use_image_search: Google画像検索グラウンディングを使用するか（flashのみ）
        thinking: 思考レベル minimal/high（flashのみ）

    Returns:
        生成された画像ファイルのパスリスト
    """
    api_key = get_api_key()
    model_id = MODELS.get(model, MODELS[DEFAULT_MODEL])

    if image_size == "0.5K":
        image_size = "512"
    validate_options(model, image_size, use_search, use_image_search, thinking)

    output_base = Path(output_path)
    stem = output_base.stem
    suffix = output_base.suffix or ".png"
    parent = output_base.parent

    payload = build_payload(
        prompt=prompt,
        model_id=model_id,
        input_images=input_images,
        aspect_ratio=aspect_ratio,
        image_size=image_size,
        use_search=use_search,
        use_image_search=use_image_search,
        thinking=thinking,
    )

    saved_files = []
    image_index = 0

    for attempt in range(count):
        interaction = call_api(payload, api_key)
        images, texts = extract_outputs(interaction)

        for text in texts:
            print(f"Model response: {text}")

        for image_bytes in images:
            if count == 1 and image_index == 0:
                file_path = output_path
            else:
                file_path = str(parent / f"{stem}_{image_index + 1}{suffix}")

            with open(file_path, "wb") as f:
                f.write(image_bytes)

            saved_files.append(file_path)
            image_index += 1

    if not saved_files:
        print("Error: 画像データが見つかりません", file=sys.stderr)
        sys.exit(1)

    for f in saved_files:
        print(f"画像を保存しました: {f}")

    return saved_files


def main():
    parser = argparse.ArgumentParser(
        description="Nano Banana (Gemini API) で画像を生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # テキストから画像生成
  %(prog)s "夕焼けのビーチ" -o beach.png

  # 参照画像を使って生成
  %(prog)s "この画像をアニメ風にして" -i reference.png -o anime.png

  # 複数バリエーション生成
  %(prog)s "かわいい猫" -n 3 -o cat.png

  # アスペクト比・サイズ指定
  %(prog)s "横長の風景" --aspect 16:9 --size 2K -o landscape.png

  # 最速・最安のLiteモデル
  %(prog)s "シンプルなアイコン" -m lite -o icon.png

  # 検索グラウンディング + 画像検索（flashのみ）
  %(prog)s "ケツァールの正確な壁紙" --search --image-search -o quetzal.png

  # 思考レベルを上げて複雑なプロンプトに対応（flashのみ）
  %(prog)s "複雑な構図のシーン" --thinking high -o scene.png
""")

    parser.add_argument("prompt", help="画像生成のプロンプト")
    parser.add_argument("-o", "--output", default="output.png",
                        help="出力ファイルパス (default: output.png)")
    parser.add_argument("-m", "--model", choices=list(MODELS.keys()),
                        default=DEFAULT_MODEL,
                        help=f"使用するモデル (default: {DEFAULT_MODEL})")
    parser.add_argument("-i", "--input", action="append", dest="input_images",
                        help="参照画像のパス（複数指定可、最大14枚）")
    parser.add_argument("-n", "--count", type=int, default=1,
                        help="生成する画像の数 (default: 1)")
    parser.add_argument("--aspect", choices=ASPECT_RATIOS,
                        help="アスペクト比")
    parser.add_argument("--size", choices=IMAGE_SIZES,
                        help="画像サイズ（512/0.5Kはflashのみ、liteは1Kのみ）")
    parser.add_argument("--search", action="store_true",
                        help="Google Web検索グラウンディングを使用（最新情報を反映、lite非対応）")
    parser.add_argument("--image-search", action="store_true",
                        help="Google画像検索グラウンディングを使用（flashのみ）")
    parser.add_argument("--thinking", choices=THINKING_LEVELS,
                        help="思考レベル (flashのみ、default: minimal)")

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
        use_image_search=args.image_search,
        thinking=args.thinking,
    )


if __name__ == "__main__":
    main()
