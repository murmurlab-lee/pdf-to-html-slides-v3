#!/usr/bin/env python3
"""
Generate page configuration with AI template matching.

Two-step process:
1. Rule engine handles obvious cases (cover, text-only, etc.)
2. Agent uses vision capability for ambiguous cases (via generated report)

Usage:
    python generate_config.py <extracted_dir/> <output_path> [--report-only]

The --report-only flag generates a markdown report for agent review
instead of auto-assigning templates.
"""

import json
import sys
from pathlib import Path


def rule_match(page):
    """Rule-based template matching. Returns (template, confidence, reason)."""
    img_count = len(page["images"])
    text = page.get("text", "")
    text_len = len(text.strip())
    
    # Rule 1: First page → cover
    if page["page"] == 1:
        return "cover", 95, "First page is always cover"
    
    # Rule 2: No images + has text → text-center
    if img_count == 0 and text_len > 0:
        return "text-center", 90, "No images, text only"
    
    # Rule 3: 1 image + short text (<80 chars) → image-full
    if img_count == 1 and text_len < 80:
        return "image-full", 85, "Single image with minimal text"
    
    # Rule 4: 1 image + longer text → split
    if img_count == 1 and text_len >= 80:
        return "split", 80, "Single image with substantial text"
    
    # Rule 5: 2-4 images → image-grid (small grid)
    if 2 <= img_count <= 4:
        return "image-grid", 75, f"{img_count} images"
    
    # Rule 6: 5+ images → image-grid (large grid)
    if img_count >= 5:
        return "image-grid", 75, f"{img_count} images (large grid)"
    
    # Fallback
    return "text-center", 60, "Fallback"


def select_cover_image(extracted_dir, pages):
    """Select the best cover image from all pages.
    
    Strategy: Find the largest image file (by bytes) across all pages.
    Renderings/photos are typically much larger than logos or thumbnails.
    Skip the cover page itself (page 1) unless it has no alternatives.
    """
    candidates = []
    
    for page in pages:
        page_num = page["page"]
        for img_rel in page.get("images", []):
            img_path = extracted_dir / img_rel
            if img_path.exists():
                size = img_path.stat().st_size
                # Penalize page 1 images (usually logo/text) by 80%
                score = size * 0.2 if page_num == 1 else size
                candidates.append((score, size, img_rel))
    
    if not candidates:
        return None
    
    # Sort by score descending, pick the best
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][2]  # Return the relative path


def generate_config(extracted_dir, output_path, report_only=False):
    """Generate page configuration."""
    extracted_dir = Path(extracted_dir)
    
    with open(extracted_dir / "pages.json", "r", encoding="utf-8") as f:
        pages = json.load(f)
    
    config = {
        "meta": {
            "projectName": "",
            "themeColor": ""
        },
        "pages": [],
        "confirmed": False
    }
    
    # Select best cover image: largest image across all pages (typically the hero render)
    cover_image = select_cover_image(extracted_dir, pages)
    
    ambiguous_pages = []
    
    for page in pages:
        template, confidence, reason = rule_match(page)
        
        # Generate summary (first 60 chars of text)
        summary = page["text"][:60].replace("\n", " ").strip() if page["text"] else ""
        
        page_config = {
            "page": page["page"],
            "thumbnail": page["thumbnail"],
            "ai_template": template,
            "user_template": template,
            "summary": summary,
            "images": page["images"],
            "text": page["text"],
            "confidence": confidence,
            "match_reason": reason
        }
        
        # Assign cover image to the cover page (page 1)
        if page["page"] == 1 and cover_image:
            page_config["cover_image"] = cover_image
        
        config["pages"].append(page_config)
        
        # Flag ambiguous pages (confidence < 80) for agent review
        if confidence < 80:
            ambiguous_pages.append(page_config)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"Generated config for {len(pages)} pages")
    print(f"  Auto-matched: {len(pages) - len(ambiguous_pages)}")
    print(f"  Ambiguous (needs review): {len(ambiguous_pages)}")
    
    # Generate report for ambiguous pages
    if ambiguous_pages:
        report_path = Path(output_path).with_suffix('.report.md')
        generate_report(config, ambiguous_pages, report_path)
        print(f"  Report: {report_path}")
    
    return config


def generate_report(config, ambiguous_pages, report_path):
    """Generate markdown report for agent review."""
    lines = [
        "# Template Matching Report",
        "",
        "## Ambiguous Pages (Needs Review)",
        "",
        "Please review these pages and confirm or adjust the template assignment.",
        "Available templates: cover, text-center, split, image-full, image-grid, image-draw, dark-text-image, about",
        "",
    ]
    
    for page in ambiguous_pages:
        lines.extend([
            f"### Page {page['page']} (confidence: {page['confidence']})",
            f"- **AI recommended**: `{page['ai_template']}` ({page['match_reason']})",
            f"- **Summary**: {page['summary']}",
            f"- **Images**: {len(page['images'])}",
            f"- **Text length**: {len(page['text'])} chars",
            f"- **Thumbnail**: `{page['thumbnail']}`",
            "",
            "To change: set pages[{}].user_template to desired template".format(page['page'] - 1),
            "",
        ])
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_config.py <extracted_dir/> <output_path> [--report-only]")
        sys.exit(1)
    
    report_only = "--report-only" in sys.argv
    generate_config(sys.argv[1], sys.argv[2], report_only)
