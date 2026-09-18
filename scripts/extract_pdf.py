#!/usr/bin/env python3
"""
Extract text, images, and thumbnails from a PDF file.

Usage:
    python extract_pdf.py <input.pdf> <output_dir/>

Output:
    output_dir/pages.json       - Page structure with text content
    output_dir/images/          - Extracted images
    output_dir/thumbnails/      - Page thumbnails (PNG)
"""

import fitz
import json
import os
import sys
from pathlib import Path

def extract_pdf(pdf_path, output_dir):
    """Extract content from PDF."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    img_dir = output_dir / "images"
    img_dir.mkdir(exist_ok=True)
    
    thumb_dir = output_dir / "thumbnails"
    thumb_dir.mkdir(exist_ok=True)
    
    doc = fitz.open(pdf_path)
    pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. Extract text
        text = page.get_text()
        
        # 2. Extract images (filter small fragments, keep top 5 per page)
        MIN_SIZE = 1024  # 1KB - skip vector fragments
        MAX_PER_PAGE = 5
        
        raw_images = []
        images = page.get_images(full=True)
        for img_idx, img in enumerate(images):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                if base_image and base_image["image"] and len(base_image["image"]) >= MIN_SIZE:
                    ext = base_image["ext"]
                    img_name = f"page_{page_num+1}_img_{img_idx+1}.{ext}"
                    img_path = img_dir / img_name
                    with open(img_path, "wb") as f:
                        f.write(base_image["image"])
                    raw_images.append((len(base_image["image"]), str(img_path.relative_to(output_dir))))
            except Exception:
                pass
        
        # Keep top 5 largest images
        raw_images.sort(key=lambda x: -x[0])
        page_images = [path for size, path in raw_images[:MAX_PER_PAGE]]
        
        # 3. Generate thumbnail
        pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))
        thumb_name = f"page_{page_num+1}.png"
        thumb_path = thumb_dir / thumb_name
        pix.save(thumb_path)
        
        pages.append({
            "page": page_num + 1,
            "text": text.strip(),
            "images": page_images,
            "thumbnail": str(thumb_path.relative_to(output_dir))
        })
    
    doc.close()
    
    # Write pages.json
    with open(output_dir / "pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    
    print(f"Extracted {len(pages)} pages")
    print(f"  Images: {sum(len(p['images']) for p in pages)}")
    print(f"  Output: {output_dir}")
    
    return pages


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_pdf.py <input.pdf> <output_dir/>")
        sys.exit(1)
    
    extract_pdf(sys.argv[1], sys.argv[2])
