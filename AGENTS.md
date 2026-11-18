# AGENTS.md — Drawsie site rules for LLM agents

This repo is the Drawsie website (step-by-step drawing tutorials for kids,
students, and parents), served by GitHub Pages from the `docs/` folder on
`main`. Push to `main` = live. Read this file before changing anything.

## REQUIRED on every page: Google Tag Manager

Every HTML page in `docs/` MUST include the Google Tag Manager container
**GTM-WP3XNK83** so traffic can be tracked. No page ships without it.

In `<head>`, as high as possible:

```html
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WP3XNK83');</script>
<!-- End Google Tag Manager -->
```

Immediately after the opening `<body>` tag:

```html
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WP3XNK83"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
```

When you create or edit any page, verify both blocks are present (search the
file for `GTM-WP3XNK83` — it must appear exactly twice per page).

## Commit identity

- Commit author/committer is plain **"Muse"** with the project-local email
  `muse@drawise.local`. NEVER put the owner's name in a commit, in any form.
- Commit and push directly to `main`. No branches, no PRs.

## Adding a tutorial (the only supported workflow)

`tutorials.json` (repo root) is the source of truth for the tutorial list.
Never hand-edit the gallery, chips, related cards, or sitemap — they are
generated. To add a tutorial:

1. Create `docs/assets/<slug>/` with `sheet.png`, `final.png`, `steps.js`
   (steps.js must define `window.DRAWSIE_STEPS`).
2. Copy `tools/tutorial-template.html` to
   `docs/tutorials/how-to-draw-<slug>.html` and fill in the placeholders.
3. Add one entry to `tutorials.json` (slug, title, subject, category,
   difficulty Easy/Medium/Hard, steps, dateAdded, tags — include kid
   synonyms like "kitty" so search finds it). The page filename defaults
   to `how-to-draw-<slug>.html`; when it differs (e.g. the cat's page is
   `how-to-draw-a-cat.html`), set the entry's `page` field to the exact
   filename.
4. Run `python3 tools/build.py` — it validates everything (asset files,
   page, GTM exactly twice, manifest fields) and regenerates the homepage
   gallery + filter chips, each page's "Draw these next" cards, the
   sitemap, and `docs/assets/tutorials.json`. Fix any error it reports;
   never commit a failing build.
5. Commit everything the build touched, and push.

Content between `<!-- GALLERY:START/END -->`, `<!-- CHIPS-*:START/END -->`,
and `<!-- RELATED:START/END -->` markers is machine-generated — edits there
will be overwritten by the next build.

## Site structure

- `docs/index.html` — homepage + tutorial gallery.
- `docs/tutorials/how-to-draw-<subject>.html` — one page per tutorial, with
  HowTo JSON-LD, the draw-along player (when step data exists), and the
  printable sheet.
- `docs/assets/` — shared files at the top level (`style.css` — bump the
  `?v=` query when it changes — and `favicon.svg`), plus **one folder per
  tutorial**: `docs/assets/<tutorial-slug>/` containing exactly that
  tutorial's `sheet.png` (printable sheet), `final.png` (finished-drawing
  thumbnail), and `steps.js` (player step data).
  - The folder is per **tutorial**, not per animal. A variant of the same
    animal (different pose, direction, or scene — e.g. "cat facing left")
    is a NEW tutorial with its OWN folder, a **peer** of the existing one:
    `docs/assets/cat/` and `docs/assets/cat-facing-left/` sit side by side.
    Never nest a variant inside another tutorial's folder, and never add a
    second tutorial's files to an existing folder.
  - The folder name is the tutorial's slug: the page
    `docs/tutorials/how-to-draw-cat-facing-left.html` pairs with the folder
    `docs/assets/cat-facing-left/`.
  - Adding a tutorial = adding one new folder; never put tutorial files in
    shared folders.
- `docs/robots.txt`, `docs/sitemap.xml` — add every new page to the sitemap.

## Content rules

- Tutorials are produced as cumulative **vector** step data (SVG): each panel
  is the previous panel plus new lines, new lines in red (`#e5484d`), old
  lines in ink (`#33302c`). Never generate step images with an image model —
  it cannot keep the character consistent across panels.
- House style is the approved cute/chibi look: big head, small chubby body,
  big sparkly eyes, soft cream/pink palette, rounded lines.
- Audience is kids, students, and parents: plain, friendly language; no
  accounts, no uploads, no tracking of children beyond the site-wide GTM
  analytics above.
- Canonical host for URLs/OG tags is https://drawise.github.io/ until a
  custom domain is added.
