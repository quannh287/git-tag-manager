#!/bin/bash
# Build script for Git Tag Manager macOS app
# Creates a standalone .app bundle with custom icon

set -e

echo "🔧 Building Git Tag Manager..."

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/assets"
ICONSET_DIR="$ASSETS_DIR/app_icons.iconset"

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
    --hidden-import git_tag_manager \
    --hidden-import git_tag_manager.core \
    --hidden-import git_tag_manager.gui \
    run_gui.py

echo ""
echo "✅ Build complete!"
echo "📍 App location: $SCRIPT_DIR/dist/GitTagManager.app"
echo ""
echo "To install, drag GitTagManager.app to /Applications"
