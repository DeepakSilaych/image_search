#!/usr/bin/env python3
"""
Build a lightweight macOS app that installs dependencies on first launch.

This creates a ~50MB app that:
1. Checks for Python/dependencies on launch
2. Downloads and installs them if missing
3. Runs the actual app

Usage:
    uv run python scripts/build_lightweight.py
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Lightweight launcher script that gets bundled
LAUNCHER_SCRIPT = '''
#!/usr/bin/env python3
"""
Lightweight launcher - installs dependencies on first run
"""
import os
import sys
import subprocess
from pathlib import Path

APP_NAME = "Image Search"
APP_SUPPORT = Path.home() / "Library" / "Application Support" / "ImageSearch"
VENV_PATH = APP_SUPPORT / "venv"
REQUIREMENTS_URL = "https://raw.githubusercontent.com/DeepakSilaych/image_search/main/requirements.txt"

def show_dialog(title, message, buttons=["OK"]):
    """Show macOS dialog"""
    import subprocess
    btn_str = ", ".join(f'"{b}"' for b in buttons)
    script = f'display dialog "{message}" with title "{title}" buttons {{{btn_str}}}'
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return None

def show_progress(message):
    """Show progress notification"""
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{APP_NAME}"'
    ], capture_output=True)

def setup_environment():
    """Setup Python environment and install dependencies"""
    APP_SUPPORT.mkdir(parents=True, exist_ok=True)
    
    # Check if venv exists and is valid
    python_path = VENV_PATH / "bin" / "python"
    if python_path.exists():
        # Verify it works
        result = subprocess.run([str(python_path), "-c", "import image_search"], capture_output=True)
        if result.returncode == 0:
            return str(python_path)
    
    # Need to setup
    show_dialog(
        APP_NAME,
        "First launch setup required.\\n\\nThis will download ~500MB of AI models.\\nThis only happens once.",
        ["Continue"]
    )
    
    show_progress("Setting up Python environment...")
    
    # Create venv
    subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
    
    pip_path = VENV_PATH / "bin" / "pip"
    
    # Upgrade pip
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], capture_output=True)
    
    # Install the package
    show_progress("Installing dependencies (this may take a few minutes)...")
    
    # Get the app bundle resource path
    bundle_path = Path(__file__).parent.parent.parent
    src_path = bundle_path / "Resources" / "src"
    
    if src_path.exists():
        # Install from bundled source
        subprocess.run([
            str(pip_path), "install", "-e", str(src_path.parent)
        ], check=True)
    else:
        # Install from PyPI/GitHub
        subprocess.run([
            str(pip_path), "install", 
            "git+https://github.com/DeepakSilaych/image_search.git"
        ], check=True)
    
    show_progress("Setup complete!")
    return str(VENV_PATH / "bin" / "python")

def main():
    try:
        python_path = setup_environment()
        
        # Run the actual app
        os.execv(python_path, [python_path, "-m", "image_search"])
        
    except Exception as e:
        show_dialog("Error", f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

def main():
    print("🔨 Building Lightweight Image Search.app...")
    print("   This creates a small app that downloads dependencies on first launch.")
    
    # Create launcher
    launcher_path = PROJECT_ROOT / "src" / "image_search" / "launcher.py"
    launcher_path.write_text(LAUNCHER_SCRIPT)
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None
ROOT = Path("{PROJECT_ROOT}")

a = Analysis(
    [str(ROOT / 'src' / 'image_search' / 'launcher.py')],
    pathex=[str(ROOT / 'src')],
    binaries=[],
    datas=[
        (str(ROOT / 'src'), 'src'),
        (str(ROOT / 'requirements.txt'), '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    strip=True,
    upx=True,
    console=False,
    argv_emulation=True,
)

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=True, upx=True, name='Image Search Lite')

app = BUNDLE(
    coll,
    name='Image Search Lite.app',
    icon=str(ROOT / 'resources' / 'icon.icns') if (ROOT / 'resources' / 'icon.icns').exists() else None,
    bundle_identifier='com.personal.imagesearch.lite',
    info_plist={{
        'CFBundleName': 'Image Search',
        'CFBundleDisplayName': 'Image Search',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '12.0',
    }},
)
'''
    
    spec_path = PROJECT_ROOT / "ImageSearchLite.spec"
    spec_path.write_text(spec_content)
    
    # Run PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", str(spec_path), "--noconfirm"]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    # Cleanup
    spec_path.unlink(missing_ok=True)
    launcher_path.unlink(missing_ok=True)
    
    if result.returncode == 0:
        app_path = PROJECT_ROOT / "dist" / "Image Search Lite.app"
        size = sum(f.stat().st_size for f in app_path.rglob("*") if f.is_file()) / 1024 / 1024
        print(f"\\n✅ Success! Lightweight app created:")
        print(f"   {app_path}")
        print(f"   Size: {size:.0f} MB")
        print(f"\\n📦 On first launch, it will download ~500MB of dependencies.")
    else:
        print(f"\\n❌ Build failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

