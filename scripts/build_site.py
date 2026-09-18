#!/usr/bin/env python3
"""
Build final HTML site from confirmed page configuration.

Usage:
    python build_site.py <config.json> <output_dir/>

Output:
    output_dir/     - Complete deployable site
        ├── index.html
        ├── index.js
        ├── index.css
        ├── data.js
        └── images/
"""

import json
import shutil
import sys
from pathlib import Path

# Import translation module for bilingual support
sys.path.insert(0, str(Path(__file__).parent))
from translate import translate


def build_slide_data(page, template):
    """Build slide data for a specific template.
    
    All templates output unified structure:
    - title: Chinese text (or English if no Chinese)
    - titleEn: English translation (empty if input is English-only)
    - body: additional text content (may be empty)
    """
    base = {"type": template, "visible": True}
    text = page.get("text", "")
    images = page.get("images", [])
    summary = page.get("summary", "")
    
    # Bilingual translation
    cn_text, en_text = translate(text)
    display_title = cn_text or en_text or summary
    title_en = en_text if cn_text else ""  # Only show EN subtitle when CN exists
    
    if template == "cover":
        cover_img = page.get("cover_image", images[0] if images else "")
        return {
            **base,
            "bgImage": cover_img if cover_img else "",
            "title": display_title[:40],
            "titleEn": title_en[:60]
        }
    
    elif template == "text-center":
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        # For pure English: title only, no body
        if not cn_text and en_text:
            body_paras = []
        else:
            body_paras = [p for p in paragraphs if p.lower() != display_title.lower()]
        return {
            **base,
            "title": display_title[:40] if display_title else "",
            "titleEn": title_en[:60],
            "body": body_paras
        }
    
    elif template == "split":
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        body = paragraphs[1:3] if len(paragraphs) > 1 else []
        return {
            **base,
            "title": display_title[:30],
            "titleEn": title_en[:50],
            "body": body,
            "images": [{"src": img, "alt": ""} for img in images[:3]]
        }
    
    elif template == "image-full":
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        body_paras = paragraphs[2:] if len(paragraphs) > 2 else []
        return {
            **base,
            "bgImage": images[0] if images else "",
            "title": display_title[:30],
            "titleEn": title_en[:50],
            "body": body_paras,
            "metadata": {"panelPosition": "bottom"}
        }
    
    elif template == "image-grid":
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        body_paras = paragraphs[2:] if len(paragraphs) > 2 else []
        return {
            **base,
            "title": display_title[:30],
            "titleEn": title_en[:50],
            "body": body_paras,
            "images": [{"src": img, "alt": ""} for img in images]
        }
    
    elif template == "image-draw":
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        body_paras = paragraphs[2:] if len(paragraphs) > 2 else []
        return {
            **base,
            "bgImage": images[0] if images else "",
            "title": display_title[:30],
            "titleEn": title_en[:50],
            "body": body_paras
        }
    
    elif template == "dark-text-image":
        return {
            **base,
            "title": display_title[:30],
            "titleEn": title_en[:50],
            "body": [text[:200]] if text else [],
            "images": [{"src": img, "alt": ""} for img in images[:4]]
        }
    
    elif template == "about":
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        return {
            **base,
            "title": display_title[:30],
            "titleEn": title_en[:50],
            "body": paragraphs[:3] if paragraphs else [text[:300]],
            "images": [{"src": img, "alt": ""} for img in images[:32]],
            "metadata": {
                "gridCols": 4,
                "gridRows": min(8, max(2, (len(images) + 3) // 4))
            }
        }
    
    return base


def build_site(config_path, output_dir, extracted_dir=None):
    """Build final site."""
    config_path = Path(config_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine extracted directory (where original images are)
    if extracted_dir is None:
        extracted_dir = config_path.parent
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 1. Copy frontend template files
    frontend_dir = Path(__file__).parent.parent / "assets" / "frontend"
    
    for fname in ["index.html", "index.js", "index.css"]:
        src = frontend_dir / fname
        if src.exists():
            shutil.copy2(src, output_dir / fname)
    
    # 2. Generate data.js
    slides = []
    for page in config["pages"]:
        template = page.get("user_template", page.get("ai_template", "text-center"))
        slide = build_slide_data(page, template)
        slides.append(slide)
    
    # Extract meta
    meta = config.get("meta", {})
    theme_color = meta.get("themeColor", "#b85450")
    project_name = meta.get("projectName", "Presentation")
    
    data_js_content = f"""// Auto-generated by build_site.py
window.SLIDES_DATA = {json.dumps(slides, ensure_ascii=False, indent=2)};
window.SLIDES_META = {{
  projectName: "{project_name}",
  themeColor: "{theme_color}"
}};
"""
    
    with open(output_dir / "data.js", "w", encoding="utf-8") as f:
        f.write(data_js_content)
    
    # 3. Copy all images from extracted directory (ensures cover_image etc. are included)
    img_output = output_dir / "images"
    img_src = Path(extracted_dir) / "images"
    if img_src.exists():
        if img_output.exists():
            shutil.rmtree(img_output)
        shutil.copytree(img_src, img_output)
    
    img_count = len(list(img_output.glob("*"))) if img_output.exists() else 0
    
    print(f"Site built: {output_dir}")
    print(f"  Slides: {len(slides)}")
    print(f"  Images copied: {img_count}")
    print(f"  Theme: {theme_color}")
    
    return output_dir


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python build_site.py <config.json> <output_dir/> [--extracted-dir <dir>]")
        sys.exit(1)
    
    extracted_dir = None
    if "--extracted-dir" in sys.argv:
        idx = sys.argv.index("--extracted-dir")
        extracted_dir = sys.argv[idx + 1]
    
    build_site(sys.argv[1], sys.argv[2], extracted_dir)
