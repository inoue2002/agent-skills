---
name: x-browse
description: "browser-use CLI 2.0を使ってX（旧Twitter）のブックマーク・タイムラインを巡回し、情報を収集してCosenseにレポートを記載するスキル。「Xチェック」「ブックマーク確認」「X巡回」「Twitterまとめ」「Xレポート」などの依頼時に使用。"
---

# X巡回・レポートスキル（x-browse）

browser-use CLI 2.0を使ってX（旧Twitter）を操作し、ブックマーク・タイムラインから情報を収集してCosenseにレポートを記載する。

## 前提条件

- **browser-use CLI 2.0** がインストール済みであること
  ```bash
  pip install browser-use
  browser-use install
  ```
- **Chromeプロファイル** にXのログイン済みセッションがあること
- **Cosenseスキル** が利用可能であること（レポート書き込みに使用）
  - `COSENSE_SID`, `COSENSE_PROJECT` 環境変数が設定済み

## browser-use CLI 基本コマンド

```bash
# Chromeプロファイルを使ってXにアクセス（ログイン済みセッションを利用）
browser-use --profile "Default" open https://x.com

# ページの状態を取得（クリック可能な要素一覧）
browser-use state

# 要素をクリック（stateで取得したインデックスを指定）
browser-use click <index>

# テキスト入力
browser-use input <index> "テキスト"

# スクロール
browser-use scroll down
browser-use scroll down --amount 3

# スクリーンショット
browser-use screenshot /tmp/x_screenshot.png

# テキスト取得
browser-use get text <index>

# HTML取得（特定セレクタ）
browser-use get html --selector "article"

# JavaScript実行（大量データ抽出用）
browser-use eval "document.querySelectorAll('article').length"

# ブラウザ終了
browser-use close
```

## 実行ワークフロー

### Step 1: ブックマーク巡回

```bash
# 1. Chromeプロファイルでブックマークページを開く
browser-use --profile "Default" open https://x.com/i/bookmarks

# 2. ページ読み込み待機
browser-use wait selector "article" --timeout 10000

# 3. 表示されたブックマークの状態を確認
browser-use state

# 4. 各ブックマークのテキストを収集
browser-use get html --selector "article"
```

**収集する情報：**
- 投稿者名・ハンドル
- 投稿内容（テキスト）
- 画像・リンクの有無
- いいね・RT数（参考）
- 投稿日時

**スクロールして追加読み込み：**
```bash
browser-use scroll down --amount 5
browser-use wait selector "article" --timeout 5000
browser-use get html --selector "article"
```

ブックマークは最新20〜30件を目安に収集する。ユーザーが件数を指定した場合はそれに従う。

### Step 2: タイムライン巡回（追加ブラウジング）

```bash
# ホームタイムラインへ移動
browser-use open https://x.com/home

# おすすめ or フォロー中タブを確認
browser-use state
# 「フォロー中」タブがあればクリックして切り替え

# タイムラインのツイートを収集
browser-use get html --selector "article"

# 必要に応じてスクロール
browser-use scroll down --amount 3
browser-use get html --selector "article"
```

**タイムラインでは以下を重点的にチェック：**
- ブックマークで見つけたトピックに関連する投稿
- バズっている投稿（エンゲージメント数が高い）
- ユーザーの関心分野に関連する技術・ニュース

### Step 3: 情報整理

収集した情報を以下の観点で整理する：

1. **カテゴリ分類**: 技術・ニュース・ツール・意見・イベント等
2. **重要度判定**: ユーザーにとっての関連性・緊急性
3. **要約作成**: 各投稿を1〜2行で要約
4. **リンク保持**: 元ツイートのURLを保持

### Step 4: Cosenseにレポート記載

cosenseスキルを使ってレポートページを作成する。

**ページタイトル**: `X巡回レポート YYYY/M/DD`

**レポートフォーマット（Cosense記法）:**
```
X巡回レポート YYYY/M/DD
[** 📌 ブックマークから]
[*** カテゴリ名]
　[投稿者名 @handle https://x.com/handle/status/ID]
　　要約テキスト
　　関連リンクがあれば記載

[** 🔄 タイムラインから]
[*** 注目トピック]
　[投稿者名 @handle https://x.com/handle/status/ID]
　　要約テキスト

[** 💡 所感・気づき]
　全体を通しての傾向やユーザーへの提案

[** メタ情報]
　巡回時刻: HH:MM
　ブックマーク確認数: N件
　タイムライン確認数: N件

[YYYY/M/DD]
```

**Cosenseへの書き込み手順:**
```bash
# 1. 同名ページの存在確認
bash /Users/inoueyousuke/.claude/skills/cosense/scripts/cosense_api.sh get-page "X巡回レポート YYYY/M/DD"

# 2. ユーザーに内容を提示して承認を得る

# 3. safe-importで作成
bash /Users/inoueyousuke/.claude/skills/cosense/scripts/cosense_api.sh safe-import '{"pages":[{"title":"X巡回レポート YYYY/M/DD","lines":["X巡回レポート YYYY/M/DD","[** 📌 ブックマークから]","..."]}]}'
```

## 注意事項

- **ブラウザ終了を忘れない**: 作業完了後は `browser-use close` でブラウザを閉じる
- **レート制限**: 短時間に大量のページ遷移やスクロールをしない。各操作の間に適度な間隔を空ける
- **Cosense書き込みは必ずユーザー承認後**: レポート内容を提示してから書き込む
- **プロファイル名の確認**: `--profile "Default"` で接続できない場合、ユーザーにChromeプロファイル名を確認する
- **個人情報への配慮**: DMやプライベートな内容は収集・記載しない
- **ブックマーク優先**: まずブックマークを確認し、その後タイムラインで補完する流れを守る
