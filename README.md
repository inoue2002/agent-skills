# Agent Skills

A collection of custom skills for Claude Code. Skills are packaged instructions and scripts that extend agent capabilities.

Skills follow the [Agent Skills](https://agentskills.io/) format.

## Available Skills

| Skill | Description |
|-------|-------------|
| **coconala** | ココナラに出品する商品を作成（サムネイル画像生成、タイトル・説明文作成） |
| **cosense** | Cosense（旧Scrapbox）のページ読み取り・検索・新規作成・編集 |
| **nanobanana-image** | Google Gemini APIを使った画像生成・編集 |
| **okane-skills** | 家計簿の残高予測・シミュレーション |
| **secretary** | Cosenseの日付ページからタスク管理・優先度提案・持ち越し検出を行う秘書エージェント |
| **xmind** | XMindマインドマップファイル(.xmind)をMarkdown形式に変換 |
| **ship-app** | React NativeでiPhoneアプリを作成し、ビルド〜App Store提出まで自動化 |
| **youtube-transcript** | YouTube動画の文字起こし・字幕抽出 |

## Installation

```bash
npx skills add inoue2002/agent-skills
```

## Skill Structure

Each skill contains:
- `SKILL.md` - Instructions for the agent
- `scripts/` - Helper scripts for automation (optional)
- `references/` - Supporting documentation (optional)

## Private Skills

Non-public skills are available in a separate private repository:

- [inoue2002/agent-skills-private](https://github.com/inoue2002/agent-skills-private) (requires access)

## License

MIT
