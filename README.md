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
    <subject>/               one folder per tutorial:
      sheet.png                printable sheet
      final.png                finished-drawing thumbnail
      steps.js                 draw-along player step data
  robots.txt
  sitemap.xml
```

## Adding a tutorial

1. Produce the step data + sheet PNG (production pipeline).
2. Create `docs/assets/<subject>/` with the sheet (`sheet.png`), the finished-drawing thumbnail (`final.png`), and the player data (`steps.js`).
3. Add `docs/tutorials/how-to-draw-<subject>.html` (copy the cat page, update title/steps/HowTo JSON-LD).
4. Link it from the gallery in `docs/index.html` and add the URL to `docs/sitemap.xml`.
5. Commit and push.
