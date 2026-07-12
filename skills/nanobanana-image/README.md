# Nano Banana Image Skill

Google Gemini API（Interactions API）の Nano Banana 機能を使った画像生成スキル for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## 機能

- テキストから画像生成
- 画像から画像生成（image-to-image、参照画像最大14枚）
- 画像編集（背景変更、要素追加/削除など）
- 複数バリエーション生成
- アスペクト比・解像度指定（512px〜4K）
- 高精度テキストレンダリング
- Google検索グラウンディング（Web検索・画像検索）
- 思考レベル制御（thinking_level）

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

| モデル | モデル名 | 特徴 |
|--------|---------|------|
| Nano Banana 2 (`flash`, デフォルト) | gemini-3.1-flash-image | 万能・Pro品質×Flash速度 |
| Nano Banana 2 Lite (`lite`) | gemini-3.1-flash-lite-image | 最速・最安（1Kのみ） |
| Nano Banana Pro (`pro`) | gemini-3-pro-image | プロ品質・複雑な指示向け |

## ライセンス

MIT
