# Nano Banana 2 Image Skill

Google Gemini API の Nano Banana 2 機能を使った画像生成スキル for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## 機能

- テキストから画像生成
- 画像から画像生成（image-to-image）
- 画像編集（背景変更、要素追加/削除など）
- 複数バリエーション生成
- アスペクト比・解像度指定（0.5K〜4K）
- 高精度テキストレンダリング
- Google検索グラウンディング

## インストール

```bash
npx skills add inoue2002/nanobanana-image-skill
```

## 前提条件

環境変数 `NANOBANANA_SKILL_GOOGLE_API_KEY` を設定してください。

### APIキーの取得と永続化

1. [Google AI Studio](https://aistudio.google.com/) でAPIキーを取得
2. `~/.claude/settings.json` に追加：

```json
{
  "env": {
    "NANOBANANA_SKILL_GOOGLE_API_KEY": "your-api-key"
  }
}
```

## 使い方

Claude Code で以下のような依頼をすると、このスキルが自動的に使用されます：

- 「猫の画像を生成して」
- 「この画像をアニメ風にして」
- 「横長の風景画像を作って」
- 「3パターン作って」

## モデル

| モデル | 特徴 |
|--------|------|
| Nano Banana 2 (`flash`, デフォルト) | Pro品質×Flash速度 |
| Nano Banana Pro (`pro`) | 高度なコンテキスト対応 |

## ライセンス

MIT
