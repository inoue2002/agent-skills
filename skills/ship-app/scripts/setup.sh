#!/bin/bash
# ship-app: React Native プロジェクトのセットアップスクリプト
# Usage: bash setup.sh <AppName> <BundleID>

set -e

APP_NAME="$1"
BUNDLE_ID="$2"

if [ -z "$APP_NAME" ] || [ -z "$BUNDLE_ID" ]; then
  echo "Usage: bash setup.sh <AppName> <BundleID>"
  echo "Example: bash setup.sh MyApp com.example.myapp"
  exit 1
fi

echo "=== Creating React Native project: $APP_NAME ==="
npx @react-native-community/cli init "$APP_NAME" --pm npm

cd "$APP_NAME"

echo "=== Installing dependencies ==="
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context

echo "=== Installing CocoaPods ==="
cd ios
pod install
cd ..

echo "=== Setting up fastlane ==="
cd ios
mkdir -p fastlane

cat > fastlane/Appfile << EOF
app_identifier("$BUNDLE_ID")
# apple_id("your@email.com")  # Set your Apple ID
# team_id("XXXXXXXXXX")       # Set your Team ID
EOF

cat > fastlane/Fastfile << FASTFILE
default_platform(:ios)

platform :ios do
  desc "Build and upload to App Store Connect"
  lane :release do
    build_app(
      workspace: "$APP_NAME.xcworkspace",
      scheme: "$APP_NAME",
      export_method: "app-store",
      clean: true
    )

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
      workspace: "$APP_NAME.xcworkspace",
      scheme: "$APP_NAME",
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
      workspace: "$APP_NAME.xcworkspace",
      scheme: "$APP_NAME",
      export_method: "app-store",
      clean: true
    )
  end
end
FASTFILE

# メタデータディレクトリ作成
mkdir -p fastlane/metadata/ja

echo "$APP_NAME" > fastlane/metadata/ja/name.txt
echo "" > fastlane/metadata/ja/subtitle.txt
echo "" > fastlane/metadata/ja/description.txt
echo "" > fastlane/metadata/ja/keywords.txt
echo "" > fastlane/metadata/ja/release_notes.txt

cd ..

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. Edit ios/fastlane/Appfile with your Apple ID and Team ID"
echo "  2. Set up code signing in Xcode"
echo "  3. Fill in metadata files in ios/fastlane/metadata/ja/"
echo "  4. Run: cd ios && fastlane build_only"
