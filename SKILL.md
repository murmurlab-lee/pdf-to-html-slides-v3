---
name: pdf-to-html-slides-v3
description: Convert architectural design presentation PDFs into interactive, fullscreen HTML slide decks with bilingual CN/EN support. Use when the user uploads a PDF file and wants to create a shareable HTML presentation with slide navigation. Features 8 adaptive templates, automatic Chinese-to-English translation with two-line layout, smart image filtering, responsive design, content protection, and mandatory interactive preview before generation.
---

# PDF to HTML Slides V3

Convert architectural design PDFs into interactive fullscreen HTML slide decks.

## Target Users

Architects, interior designers, landscape designers who need to share PDF presentations as browsable HTML websites.

## Core Workflow (6 Steps)

### Step 1: Extract Content

```bash
python scripts/extract_pdf.py <input.pdf> <output_dir/>
```

Extracts text, images, and page thumbnails from PDF.

Output: `output_dir/pages.json` + `images/` + `thumbnails/`

### Step 2: Generate Configuration

```bash
python scripts/generate_config.py <output_dir/> <output_dir/pages_config.json>
```

Rule engine auto-matches obvious cases. Agent reviews ambiguous pages via vision analysis.

Output: `pages_config.json` + optional `pages_config.report.md`

**Agent Action**: Read the generated report (if any ambiguous pages) and use vision capability to view thumbnails. Adjust template assignments by modifying `user_template` fields.

### Step 3: Build Preview (Mandatory)

```bash
python scripts/build_preview.py <output_dir/pages_config.json> <preview_dir/> --extracted-dir <extracted_dir/>
```

Generates interactive preview site with:
- Thumbnail list per page
- AI-recommended template display
- Dropdown to change template per page
- Batch selection mode
- Real-time preview rendering
- Auto-save to localStorage

**Deploy preview** and show user. User can:
- Click thumbnails to preview each page
- Change template via dropdown
- Select multiple pages and batch-change
- Confirm or provide text instructions

### Step 4: User Confirmation

User reviews preview and either:
- **Confirms all AI recommendations** → proceed to Step 5 with pages_config.json
- **Changes via text instructions** → agent modifies pages_config.json directly
- **Changes via preview dropdown** → click "确认并生成HTML" to download `pages_confirmed.json`

**Important**: `pages_confirmed.json` downloads to user's local computer. Agent cannot read it automatically. User must upload it back to agent, or use text instructions instead.

### Step 5: Build Final Site

**If user made changes in preview and uploaded `pages_confirmed.json`:**
```bash
python scripts/build_site.py <path/to/uploaded/pages_confirmed.json> <dist/> --extracted-dir <extracted_dir/>
```

**If user confirmed without changes (or used text instructions):**
```bash
python scripts/build_site.py <output_dir/pages_config.json> <dist/> --extracted-dir <extracted_dir/>
```

Assembles final site with:
- Frontend template (original code, data-driven)
- Generated `data.js`
- Copied images
- Content protection enabled

### Step 6: Deploy

```bash
# Deploy dist/ folder
```

## File Structure

```
pdf-to-html-slides-v3/
├── SKILL.md
├── references/
│   ├── templates.json          # 8-template adaptive rules (single source)
│   └── matching-rules.md       # PDF→template matching rules
├── scripts/
│   ├── extract_pdf.py          # Step 1: PDF extraction (with image filtering)
│   ├── translate.py            # CN→EN bilingual translation module
│   ├── generate_config.py      # Step 2: AI template matching
│   ├── build_preview.py        # Step 3: Interactive preview
│   └── build_site.py           # Step 5: Final site build (with bilingual output)
└── assets/
    └── frontend/               # Original code (modified)
        ├── index.html          # Entry (loads data.js)
        ├── index.js            # Components + slide engine + protection
        ├── index.css           # Styles + responsive + anti-print
        ├── preview.html        # Interactive preview page
        ├── preview-slide.html  # Single slide preview renderer
        └── data.js.template    # Data placeholder
```

## 8 Templates

| Template | Use Case |
|----------|----------|
| `cover` | Title page with fullscreen background |
| `text-center` | Philosophy, quotes, transitions |
| `split` | Text + image with optional swatches/tags |
| `image-full` | Fullscreen image with text overlay |
| `image-grid` | Multiple images in grid/scroll layout |
| `image-draw` | Analysis diagrams with glassmorphism panel |
| `dark-text-image` | Dark theme for artist/exhibition content |
| `about` | Company intro with scrolling image grid |

## Content Protection

All output HTML includes:
- Anti-text-selection (CSS)
- Anti-image-drag (CSS + JS)
- Anti-right-click (JS)
- Anti-Ctrl+C/S/P/A (JS)
- Anti-print (`@media print { display: none }`)

Normal browsing unaffected: keyboard navigation, scroll, touch swipe.

## Responsive Design

- **Mobile (<768px)**: Split stacks vertically, image-grid becomes single column, navigation dots move to bottom
- **Tablet (768-1023px)**: Adjusted proportions
- **Desktop (≥1024px)**: Full layout as designed

Touch gestures supported: swipe up/down to navigate slides.

## LLM Matching

Template matching uses a hybrid approach:
1. **Rule engine** handles obvious cases (cover, text-only, etc.)
2. **Agent vision analysis** handles ambiguous cases
3. **User confirmation** is mandatory before generation

No external API keys needed — uses agent's built-in vision capability.
