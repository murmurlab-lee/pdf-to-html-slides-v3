# PDF to HTML Slides v3

Convert architectural design presentation PDFs into interactive, fullscreen HTML slide decks with bilingual CN/EN support.

## Repository

https://github.com/murmurlab-lee/pdf-to-html-slides-v3

## Features

- 8 adaptive templates (cover, text-center, split, image-full, image-grid, image-draw, dark-text-image, about)
- Automatic Chinese-to-English translation with two-line layout
- Smart image filtering (skip <1KB fragments, max 5 per page)
- Interactive preview before generation
- Content protection (anti-copy, anti-print)
- Responsive design (desktop/tablet/mobile)

## File Structure

```
pdf-to-html-slides-v3/
├── SKILL.md                      # Skill documentation
├── README.md                     # This file
├── references/
│   ├── templates.json            # 8-template adaptive rules
│   └── matching-rules.md         # PDF→template matching rules
├── scripts/
│   ├── extract_pdf.py            # Step 1: PDF extraction
│   ├── translate.py              # CN→EN bilingual translation
│   ├── generate_config.py        # Step 2: AI template matching
│   ├── build_preview.py          # Step 3: Interactive preview
│   └── build_site.py             # Step 5: Final site build
└── assets/
    └── frontend/
        ├── index.html            # Entry (loads data.js)
        ├── index.js              # Components + slide engine + protection (347KB)
        ├── index.css             # Styles + responsive + anti-print
        ├── preview.html          # Interactive preview page
        ├── preview-slide.html    # Single slide preview renderer
        └── data.js.template      # Data placeholder
```

## Note on index.js

The `assets/frontend/index.js` file (347KB bundled frontend) exceeds API upload limits. Please upload it manually via GitHub web interface or git CLI:

```bash
git clone https://github.com/murmurlab-lee/pdf-to-html-slides-v3.git
cd pdf-to-html-slides-v3
# Copy index.js to assets/frontend/
git add assets/frontend/index.js
git commit -m "Add index.js"
git push
```
