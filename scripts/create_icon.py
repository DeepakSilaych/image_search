#!/usr/bin/env python3
"""
Create macOS .icns icon from PNG
"""
import subprocess
import shutil
from pathlib import Path

def create_icns(png_path: str, output_path: str = "icon.icns"):
    """Convert PNG to macOS icns format"""
    png = Path(png_path)
    iconset = Path("AppIcon.iconset")
    
    # Create iconset directory
    iconset.mkdir(exist_ok=True)
    
    # Required sizes for macOS icons
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        # Normal resolution
        out_file = iconset / f"icon_{size}x{size}.png"
        subprocess.run([
            "sips", "-z", str(size), str(size),
            str(png), "--out", str(out_file)
        ], capture_output=True)
        
        # Retina resolution (2x)
        if size <= 512:
            out_file_2x = iconset / f"icon_{size}x{size}@2x.png"
            subprocess.run([
                "sips", "-z", str(size * 2), str(size * 2),
                str(png), "--out", str(out_file_2x)
            ], capture_output=True)
    
    # Convert iconset to icns
    subprocess.run([
        "iconutil", "-c", "icns", str(iconset), "-o", output_path
    ])
    
    # Cleanup
    shutil.rmtree(iconset)
    
    print(f"✅ Created {output_path}")
    return output_path


if __name__ == "__main__":
    create_icns("profile.png", "icon.icns")

