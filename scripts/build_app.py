#!/usr/bin/env python3
"""
Build macOS .app bundle for Image Search

Usage:
    uv run python scripts/build_app.py
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESOURCES = PROJECT_ROOT / "resources"


def main():
    print("🔨 Building Image Search.app...")
    
    # Create spec file dynamically
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from pathlib import Path

block_cipher = None
ROOT = Path("{PROJECT_ROOT}")

datas = []
binaries = []
hiddenimports = []

for pkg in ['mlx', 'mlx_clip', 'deepface', 'qdrant_client', 'cv2', 'PIL']:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

datas += [
    (str(ROOT / 'src' / 'image_search'), 'image_search'),
]

hiddenimports += [
    'image_search',
    'image_search.core',
    'image_search.gui',
    'image_search.app',
    'mlx.core',
    'sklearn.metrics.pairwise',
    'cv2',
    'PIL.Image',
    'ocrmac',
]

a = Analysis(
    [str(ROOT / 'src' / 'image_search' / 'app.py')],
    pathex=[str(ROOT / 'src')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'tkinter', 'PyQt5', 'PySide6',
        # Exclude unused DeepFace backends (saves ~500MB)
        'torch', 'torchvision', 'torchaudio',
        'paddle', 'paddlepaddle',
        'mxnet',
        # Exclude unused TF components
        'tensorboard', 'tensorflow_estimator',
    ],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Image Search',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    argv_emulation=True,
)

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='Image Search')

app = BUNDLE(
    coll,
    name='Image Search.app',
    icon=str(ROOT / 'resources' / 'icon.icns') if (ROOT / 'resources' / 'icon.icns').exists() else None,
    bundle_identifier='com.personal.imagesearch',
    info_plist={{
        'CFBundleName': 'Image Search',
        'CFBundleDisplayName': 'Image Search',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '12.0',
        'NSPhotoLibraryUsageDescription': 'Image Search needs access to index and search your photos.',
        'NSDesktopFolderUsageDescription': 'Image Search needs access to find photos on your Desktop.',
        'NSDocumentsFolderUsageDescription': 'Image Search needs access to find photos in Documents.',
        'NSDownloadsFolderUsageDescription': 'Image Search needs access to find photos in Downloads.',
    }},
)
'''
    
    spec_path = PROJECT_ROOT / "ImageSearch.spec"
    spec_path.write_text(spec_content)
    
    # Run PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", str(spec_path), "--noconfirm"]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print(f"\n❌ Build failed")
        spec_path.unlink(missing_ok=True)
        sys.exit(1)
    
    app_path = PROJECT_ROOT / "dist" / "Image Search.app"
    
    # Ad-hoc code sign the app
    print("\n🔏 Code signing (ad-hoc)...")
    sign_result = subprocess.run(
        ["codesign", "--force", "--deep", "--sign", "-", str(app_path)],
        capture_output=True
    )
    if sign_result.returncode == 0:
        print("   ✓ Signed successfully")
    else:
        print("   ⚠ Signing failed (app may still work)")
    
    # Remove quarantine attribute
    print("🔓 Removing quarantine...")
    subprocess.run(["xattr", "-cr", str(app_path)], capture_output=True)
    print("   ✓ Quarantine removed")
    
    # Cleanup
    spec_path.unlink(missing_ok=True)
    
    print(f"\n✅ Success! App created at:\n   {app_path}")
    print(f"\n📦 To create DMG: ./scripts/create_dmg.sh")
    print(f"🚀 To run: open '{app_path}'")


if __name__ == "__main__":
    main()
