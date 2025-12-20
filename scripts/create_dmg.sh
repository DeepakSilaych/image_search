#!/bin/bash
# Create a distributable DMG file

set -e

APP_NAME="Image Search"
DMG_NAME="ImageSearch-1.0.0"
DIST_DIR="dist"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

if [ ! -d "${DIST_DIR}/${APP_NAME}.app" ]; then
    echo "❌ App not found. Run build_app.py first."
    exit 1
fi

echo "📦 Creating DMG..."

# Remove quarantine from app
echo "🔓 Removing quarantine attributes..."
xattr -cr "${DIST_DIR}/${APP_NAME}.app"

# Ad-hoc sign if not already signed
echo "🔏 Ensuring app is signed..."
codesign --force --deep --sign - "${DIST_DIR}/${APP_NAME}.app" 2>/dev/null || true

# Create a temporary folder for DMG contents
rm -rf "${DIST_DIR}/dmg_contents"
mkdir -p "${DIST_DIR}/dmg_contents"
cp -R "${DIST_DIR}/${APP_NAME}.app" "${DIST_DIR}/dmg_contents/"

# Create a symbolic link to Applications folder
ln -sf /Applications "${DIST_DIR}/dmg_contents/Applications"

# Create README for installation
cat > "${DIST_DIR}/dmg_contents/README.txt" << 'EOF'
Image Search - Installation
============================

1. Drag "Image Search.app" to the Applications folder
2. Open the app from Applications

If you see "cannot be opened" error:
- Right-click the app → Open → Click "Open" in dialog
- Or run in Terminal: xattr -cr /Applications/Image\ Search.app

Enjoy searching your photos!
EOF

# Remove old DMG if exists
rm -f "${DIST_DIR}/${DMG_NAME}.dmg"

# Create the DMG
hdiutil create -volname "${APP_NAME}" \
    -srcfolder "${DIST_DIR}/dmg_contents" \
    -ov -format UDZO \
    "${DIST_DIR}/${DMG_NAME}.dmg"

# Cleanup
rm -rf "${DIST_DIR}/dmg_contents"

# Get size
SIZE=$(du -h "${DIST_DIR}/${DMG_NAME}.dmg" | cut -f1)

echo ""
echo "✅ Created: ${DIST_DIR}/${DMG_NAME}.dmg (${SIZE})"
echo ""
echo "📤 Share this file with others!"
echo ""
echo "Note: Recipients should right-click → Open on first launch,"
echo "      or run: xattr -cr /Applications/Image\\ Search.app"
