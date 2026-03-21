---
name: xmind
description: XMindマインドマップファイル(.xmind)をMarkdown形式に変換するスキル。論文のシナリオ構成、アイデア整理、研究の構造化などに使用するマインドマップをテキストベースで扱う。「XMindをMarkdownに変換」「マインドマップを読み込んで」「.xmindファイルを解析」「XMindの内容を表示」などの依頼時に使用。
---

# XMind

XMind 8ファイルの読み込み・作成・編集を行うスキル。公式SDK（xmind-sdk-python）を使用。

> **対応バージョン**: XMind 8 (XML形式)
> XMind Zen以降（JSON形式）には対応していません。

## セットアップ（初回のみ）

スクリプト実行前に依存関係をインストール：

```bash
# スキルディレクトリで実行
pip install -r requirements.txt
```

または直接：

```bash
python3 -m pip install xmind
```

> **Note**: macOSでHomebrewのPythonを使用している場合は `python3 -m pip install --user xmind` を使用

## コマンド

### 新規作成

```bash
python scripts/xmind_cli.py create output.xmind --root "中心トピック"
```

### 構造表示

```bash
python scripts/xmind_cli.py show file.xmind
```

出力例：
```
=== Sheet 1 ===
研究論文
  - 1. はじめに
    > 背景と目的（ノート）
    // 要確認（コメント）
    - 背景
  - 2. 関連研究
```

### Markdown変換

```bash
# ヘッダー形式（デフォルト）
python scripts/xmind_cli.py markdown file.xmind

# 箇条書き形式
python scripts/xmind_cli.py markdown file.xmind --style bullets
```

### トピック追加

```bash
# 基本
python scripts/xmind_cli.py add file.xmind --parent "親トピック" --topic "新トピック"

# ノート・コメント・マーカー・ラベル付き
python scripts/xmind_cli.py add file.xmind --parent "親" --topic "子" \
  --note "メモ" --comment "コメント" --marker "priority-1" --label "重要"
```

### トピック編集

```bash
python scripts/xmind_cli.py edit file.xmind --target "対象トピック" \
  --title "新タイトル" --note "新ノート" --comment "追加コメント"
```

---

## 対応機能

| 機能 | 読み込み | 書き込み |
|------|:-------:|:-------:|
| トピック | ✅ | ✅ |
| ノート (notes) | ✅ | ✅ |
| コメント (comments) | ✅ | ✅ |
| マーカー (markers) | ✅ | ✅ |
| ラベル (labels) | ✅ | ✅ |
