#!/bin/bash
# Build script for Git Tag Manager macOS app
# Creates a standalone .app bundle with custom icon and DMG

set -e

echo "🔧 Building Git Tag Manager..."

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/assets"
ICONSET_DIR="$ASSETS_DIR/app_icons.iconset"

# Get version from package
VERSION=$(python3 -c "from manager import __version__; print(__version__)")
echo "📌 Version: $VERSION"

# 1. Create .icns from PNG
echo "📦 Creating icon..."
mkdir -p "$ICONSET_DIR"

# Resize to all required sizes
sips -z 16 16     "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_16x16.png" > /dev/null
sips -z 32 32     "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_16x16@2x.png" > /dev/null
sips -z 32 32     "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_32x32.png" > /dev/null
sips -z 64 64     "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_32x32@2x.png" > /dev/null
sips -z 128 128   "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_128x128.png" > /dev/null
sips -z 256 256   "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_128x128@2x.png" > /dev/null
sips -z 256 256   "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_256x256.png" > /dev/null
sips -z 512 512   "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_256x256@2x.png" > /dev/null
sips -z 512 512   "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_512x512.png" > /dev/null
sips -z 1024 1024 "$ASSETS_DIR/app_icons.png" --out "$ICONSET_DIR/icon_512x512@2x.png" > /dev/null

# Convert to .icns
iconutil -c icns "$ICONSET_DIR" -o "$ASSETS_DIR/app_icons.icns"
echo "✅ Icon created: $ASSETS_DIR/app_icons.icns"

# Cleanup iconset folder
rm -rf "$ICONSET_DIR"

# 2. Build with PyInstaller
echo "🚀 Building app with PyInstaller..."
cd "$SCRIPT_DIR"

# Clean previous builds
rm -rf build dist *.spec

pyinstaller --noconfirm --onedir --windowed \
    --name "GitTagManager" \
    --icon "$ASSETS_DIR/app_icons.icns" \
    --collect-all tkinterdnd2 \
    --collect-all customtkinter \
    --add-data "assets:assets" \
    --hidden-import manager \
    --hidden-import manager.core \
    --hidden-import manager.gui \
    run_gui.py

echo "✅ App bundle created!"

# 3. Update Info.plist with version
echo "📝 Setting version in Info.plist..."
INFO_PLIST="$SCRIPT_DIR/dist/GitTagManager.app/Contents/Info.plist"
# Use Add if key doesn't exist, otherwise Set
/usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string $VERSION" "$INFO_PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" "$INFO_PLIST"
/usr/libexec/PlistBuddy -c "Add :CFBundleVersion string $VERSION" "$INFO_PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $VERSION" "$INFO_PLIST"

# 4. Create DMG
echo "💿 Creating DMG..."

APP_NAME="GitTagManager"
DMG_NAME="GitTagManager-${VERSION}"
DMG_DIR="$SCRIPT_DIR/dist/dmg"
DMG_PATH="$SCRIPT_DIR/dist/$DMG_NAME.dmg"

# Cleanup previous DMG
rm -rf "$DMG_DIR" "$DMG_PATH"

# Create DMG folder structure
mkdir -p "$DMG_DIR"
cp -R "$SCRIPT_DIR/dist/$APP_NAME.app" "$DMG_DIR/"

# Create symbolic link to Applications
ln -s /Applications "$DMG_DIR/Applications"

# Create DMG using hdiutil
hdiutil create -volname "$APP_NAME $VERSION" \
    -srcfolder "$DMG_DIR" \
    -ov -format UDZO \
    "$DMG_PATH"

# Cleanup
rm -rf "$DMG_DIR"

echo ""
echo "✅ Build complete!"
echo "📌 Version: $VERSION"
echo "📍 App location: $SCRIPT_DIR/dist/GitTagManager.app"
echo "💿 DMG location: $SCRIPT_DIR/dist/$DMG_NAME.dmg"
echo ""
echo "To install: Open DMG and drag GitTagManager to Applications"
