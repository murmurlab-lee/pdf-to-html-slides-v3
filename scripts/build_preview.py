#!/usr/bin/env python3
"""
Build interactive preview site for user confirmation.

Usage:
    python build_preview.py <config.json> <output_dir/>

Output:
    output_dir/     - Preview site (deployable)
        ├── index.html      (preview entry point)
        ├── preview.html    (same as index.html)
        ├── index.js
        ├── index.css
        ├── preview-slide.html
        └── images/ + thumbnails/
"""

import json
import shutil
import sys
from pathlib import Path

# Import build_slide_data to reuse the same data generation logic
sys.path.insert(0, str(Path(__file__).parent))
from build_site import build_slide_data


def build_preview(config_path, output_dir, extracted_dir=None):
    """Build preview site.
    
    Reuses build_slide_data() from build_site.py to ensure
    preview and final site have identical slide data.
    """
    config_path = Path(config_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine extracted directory (where original images/thumbnails are)
    if extracted_dir is None:
        extracted_dir = config_path.parent
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 1. Generate slides data (reuses build_slide_data for consistency)
    slides = []
    for page in config["pages"]:
        template = page.get("user_template", page.get("ai_template", "text-center"))
        slide = build_slide_data(page, template)
        slides.append(slide)
    
    # 2. Copy frontend template files (excluding index.html - we'll use preview.html)
    frontend_dir = Path(__file__).parent.parent / "assets" / "frontend"
    
    for fname in ["index.js", "index.css", "preview.html", "preview-slide.html"]:
        src = frontend_dir / fname
        if src.exists():
            shutil.copy2(src, output_dir / fname)
    
    # 3. Inject pages config and slides data into preview.html
    preview_path = output_dir / "preview.html"
    with open(preview_path, "r", encoding="utf-8") as f:
        preview_html = f.read()
    
    # Inject pages config
    pages_json = json.dumps(config["pages"], ensure_ascii=False)
    preview_html = preview_html.replace('__PAGES_JSON__', pages_json)
    
    # Inject slides data
    slides_json = json.dumps(slides, ensure_ascii=False)
    preview_html = preview_html.replace('__SLIDES_JSON__', slides_json)
    
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(preview_html)
    
    # 4. Copy preview.html to index.html so it serves as the entry point
    shutil.copy2(preview_path, output_dir / "index.html")
    
    # 5. Copy thumbnails
    thumb_src = Path(extracted_dir) / "thumbnails"
    thumb_dst = output_dir / "thumbnails"
    if thumb_src.exists():
        if thumb_dst.exists():
            shutil.rmtree(thumb_dst)
        shutil.copytree(thumb_src, thumb_dst)
    
    # 6. Copy all images
    img_src = Path(extracted_dir) / "images"
    img_dst = output_dir / "images"
    if img_src.exists():
        if img_dst.exists():
            shutil.rmtree(img_dst)
        shutil.copytree(img_src, img_dst)
    
    print(f"Preview site built: {output_dir}")
    print(f"  Entry: {output_dir}/index.html")
    print(f"  Pages: {len(config['pages'])}")
    
    return output_dir


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python build_preview.py <config.json> <output_dir/> [--extracted-dir <dir>]")
        sys.exit(1)
    
    extracted_dir = None
    if "--extracted-dir" in sys.argv:
        idx = sys.argv.index("--extracted-dir")
        extracted_dir = sys.argv[idx + 1]
    
    build_preview(sys.argv[1], sys.argv[2], extracted_dir)
