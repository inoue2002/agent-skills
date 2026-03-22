---
name: ship-app
description: React NativeでiPhoneアプリを作成し、ビルドからApp Store提出まで自動化します。「アプリ作って」「ship-app」「App Store提出」「iPhoneアプリ」と言われたらこのスキルを使用してください。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [アプリの説明]
---

# ship-app: React Native iPhone App Builder & Deployer

MacBook上でReact NativeのiPhoneアプリを作成し、ビルド〜App Store提出まで一気通貫で自動化するスキル。

## 前提条件

以下がMacBookにインストールされていること：
- Xcode（最新版推奨）
- Node.js（18以上）
- Ruby（fastlane用）
- CocoaPods（`sudo gem install cocoapods`）
- fastlane（`sudo gem install fastlane`）
- Apple Developer Programに加入済み

## ワークフロー

### Phase 1: ヒアリング

ユーザーに以下を確認：
- **アプリ名**: アプリの名前
- **概要**: 何をするアプリか
- **主な機能**: 画面構成と機能一覧
- **Bundle ID**: `com.example.appname` 形式（提案してもよい）
- **ターゲットiOSバージョン**: デフォルト 16.0

### Phase 2: プロジェクト生成

```bash
# React Native プロジェクト作成
npx @react-native-community/cli init <AppName> --pm npm

cd <AppName>
```

### Phase 3: コード実装

ユーザーの要件に基づいてコードを実装する：

1. **画面構成**: React Navigationを使ったナビゲーション
2. **UIコンポーネント**: 各画面のUI実装
3. **ロジック**: ビジネスロジック・状態管理
4. **アイコン/スプラッシュ**: アプリアイコンとスプラッシュスクリーンの設定

必要なパッケージのインストール例：
```bash
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
```

### Phase 4: iOS固有の設定

```bash
cd ios && pod install && cd ..
```

**Info.plist の設定：**
- `CFBundleDisplayName`: アプリ表示名
- `CFBundleIdentifier`: Bundle ID
- `CFBundleShortVersionString`: バージョン番号
- `NSAppTransportSecurity`: 必要に応じて

**署名の設定（xcodeプロジェクト内）：**
- Development Team ID
- Provisioning Profile
- Code Signing Identity

### Phase 5: fastlane セットアップ

```bash
cd ios
fastlane init
```

**Fastfile の設定：**

```ruby
default_platform(:ios)

platform :ios do
  desc "Build and upload to App Store Connect"
  lane :release do
    # バージョン番号のインクリメント（オプション）
    # increment_build_number

    # ビルド
    build_app(
      workspace: "<AppName>.xcworkspace",
      scheme: "<AppName>",
      export_method: "app-store",
      clean: true
    )

    # App Store Connect にアップロード
    upload_to_app_store(
      skip_metadata: false,
      skip_screenshots: true,
      submit_for_review: false,
      automatic_release: false,
      force: true
    )
  end

  desc "Build for TestFlight"
  lane :beta do
    build_app(
      workspace: "<AppName>.xcworkspace",
      scheme: "<AppName>",
      export_method: "app-store",
      clean: true
    )

    upload_to_testflight(
      skip_waiting_for_build_processing: true
    )
  end

  desc "Build only (no upload)"
  lane :build_only do
    build_app(
      workspace: "<AppName>.xcworkspace",
      scheme: "<AppName>",
      export_method: "app-store",
      clean: true
    )
  end
end
```

**Appfile の設定：**

```ruby
app_identifier("<bundle_id>")
apple_id("<apple_id>")
team_id("<team_id>")
```

### Phase 6: App Store Connect メタデータ

fastlane の `metadata` ディレクトリに以下を設定：

```
ios/fastlane/metadata/ja/
├── name.txt              # アプリ名
├── subtitle.txt          # サブタイトル（30文字以内）
├── description.txt       # 説明文
├── keywords.txt          # キーワード（カンマ区切り、100文字以内）
├── privacy_url.txt       # プライバシーポリシーURL
├── support_url.txt       # サポートURL
└── release_notes.txt     # リリースノート
```

### Phase 7: ビルド & 提出

```bash
cd ios

# ビルドのみ（確認用）
fastlane build_only

# TestFlight に配信
fastlane beta

# App Store に提出
fastlane release
```

## 実行コマンドまとめ

| フェーズ | コマンド |
|---------|---------|
| プロジェクト生成 | `npx @react-native-community/cli init <App>` |
| 依存インストール | `npm install && cd ios && pod install` |
| ビルド確認 | `cd ios && fastlane build_only` |
| TestFlight配信 | `cd ios && fastlane beta` |
| App Store提出 | `cd ios && fastlane release` |

## トラブルシューティング

### CocoaPods エラー
```bash
cd ios && pod deintegrate && pod install
```

### 署名エラー
```bash
# 証明書の確認
fastlane match development
fastlane match appstore
```

### ビルドエラー
```bash
# クリーンビルド
xcodebuild clean -workspace <App>.xcworkspace -scheme <App>
cd ios && fastlane build_only
```

## 注意事項

- **Apple Developer Program**（年額$99）への加入が必須
- 初回提出時は App Store Connect でアプリを事前登録する必要がある
- スクリーンショットは手動またはfastlane snapshotsで用意
- プライバシーポリシーURLが必要（App Store審査要件）
- 審査には通常1〜3日かかる
- このスキルはMacBook上のClaude Codeで実行すること（xcodebuild が必要）
