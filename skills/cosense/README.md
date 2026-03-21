# cosense-skill

Cosense（旧Scrapbox）のページ操作を行う Claude Code / Agent スキル。

## 機能

- ページの読み取り（JSON / プレーンテキスト）
- ページ一覧の取得
- 全文検索
- ページの新規作成
- ページの編集（自動バックアップ付き）
- バックアップ・リストア

## インストール

```bash
npx skills add inoue2002/cosense-skill
```

## セットアップ

以下の環境変数を設定してください：

```bash
export COSENSE_SID="s:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.xxxxx"
export COSENSE_PROJECT="your-project-name"
export COSENSE_BACKUP_DIR="/path/to/backups"  # 任意（デフォルト: /tmp/cosense_backups）
```

### SID の取得方法

1. ブラウザで [Cosense](https://scrapbox.io) にログイン
2. DevTools → Application → Cookies → `connect.sid` の値をコピー

## 安全機能

- **自動バックアップ**: `safe-import` コマンドで既存ページを自動保存してから上書き
- **重複チェック**: 新規作成前に同名ページの存在を確認
- **リストア**: バックアップからワンコマンドで復元可能

## ライセンス

MIT
