# Drawsie

Step-by-step drawing tutorials for kids and beginners — cute animals in 6–10 easy steps, following the red guide lines.

**Live site:** https://drawise.github.io/ (GitHub Pages, served from the `docs/` folder on `main`)

## How it works

- The website is fully static: everything lives under `docs/` and GitHub Pages serves it as-is. Push to `main` = live.
- Tutorials are produced as **cumulative vector step data** (SVG), never AI-generated step images, so the character is pixel-identical across panels. One step dataset renders:
  - the single-sheet PNG (website / Pinterest / printables),
  - the interactive step player (future app),
  - the SVG source.
- Generators live in the project workspace (`make_sheet*.py`); each tutorial's rendered assets live in their own folder, `docs/assets/<subject>/`, with one page per tutorial in `docs/tutorials/`.

## Structure

```
docs/
  index.html                 homepage + tutorial gallery
  tutorials/                 one page per tutorial
  assets/
    style.css                shared styles
    favicon.svg
    <tutorial-slug>/         one folder per tutorial (variants of the same
                               animal, e.g. cat-facing-left/, are separate
                               peer folders — never nested):
      sheet.png                printable sheet
      final.png                finished-drawing thumbnail
      steps.js                 draw-along player step data
  robots.txt
  sitemap.xml
```

## Discovery

Visitors find tutorials three ways, all powered by `tutorials.json`:

- **Search** — the homepage search box matches titles and tags (including kid synonyms like "kitty"), filtered instantly in the browser.
- **Browse** — category and difficulty chips filter the gallery; every tutorial page ends with "Draw these next" cards (same category first).
- **Search engines / Pinterest** — one page per tutorial with HowTo structured data, plus a generated sitemap.

## Adding a tutorial

`tutorials.json` is the source of truth — the gallery, chips, related cards, and sitemap are generated, never hand-edited.

1. Produce the step data + sheet PNG (production pipeline).
2. Create `docs/assets/<tutorial-slug>/` (a new peer folder for every tutorial, including variants of an animal already covered) with the sheet (`sheet.png`), the finished-drawing thumbnail (`final.png`), and the player data (`steps.js`, defining `window.DRAWSIE_STEPS`).
3. Copy `tools/tutorial-template.html` to `docs/tutorials/how-to-draw-<slug>.html` and fill in the placeholders.
4. Add one entry to `tutorials.json`.
5. Run `python3 tools/build.py` (validates everything, regenerates the listings), then commit and push.
