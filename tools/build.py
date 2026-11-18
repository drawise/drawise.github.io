#!/usr/bin/env python3
"""Drawise site builder.

Reads tutorials.json (repo root) and regenerates everything that depends on
the tutorial list, so adding a tutorial never means hand-editing listings:

  * homepage gallery cards      (docs/index.html, between GALLERY markers)
  * homepage filter chips       (docs/index.html, between CHIPS markers)
  * related-tutorials cards     (each docs/tutorials/*.html, RELATED markers)
  * docs/sitemap.xml
  * docs/assets/tutorials.json  (public index, also used by the future app)

It also validates every tutorial before writing anything: asset folder with
sheet.png/final.png/steps.js present, tutorial page present, GTM container
present exactly twice on the page, manifest fields complete. Exits non-zero
on any problem.

Run from the repo root:  python3 tools/build.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SITE = "https://drawise.github.io"
DIFF_ORDER = ["Easy", "Medium", "Hard"]


def fail(errors):
    print("BUILD FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)


def replace_region(text, name, content):
    pat = re.compile(r"(<!-- " + name + r":START -->).*?(<!-- " + name + r":END -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"marker region {name} not found")
    return pat.sub(lambda m: m.group(1) + "\n" + content + "\n" + m.group(2), text, count=1)


def page_file(t):
    return t.get("page", f"how-to-draw-{t['slug']}.html")


def card(t, cat_name, prefix):
    search = " ".join([t["title"], t["subject"]] + t.get("tags", [])).lower()
    return (
        f'      <a class="tcard" href="{prefix}tutorials/{page_file(t)}" '
        f'data-category="{t["category"]}" data-difficulty="{t["difficulty"].lower()}" data-search="{search}">\n'
        f'        <div class="thumb"><img src="{prefix}assets/{t["slug"]}/final.png" alt="Cute {t["subject"].lower()} drawing" loading="lazy"></div>\n'
        f'        <div class="meta">\n'
        f'          <h3>{t["title"]}</h3>\n'
        f'          <p>{t["steps"]} steps · {t["difficulty"]} · {cat_name}</p>\n'
        f'          <span class="badge">Start drawing</span>\n'
        f'        </div>\n'
        f'      </a>'
    )


def related_card(t, cat_name):
    # tutorial pages link to sibling pages, so no "tutorials/" prefix
    c = card(t, cat_name, "../")
    return c.replace("../tutorials/", "", 1)


def main():
    with open(os.path.join(ROOT, "tutorials.json")) as f:
        manifest = json.load(f)
    cats = {c["slug"]: c["name"] for c in manifest["categories"]}
    tuts = manifest["tutorials"]

    # ---- validate -------------------------------------------------------
    errors = []
    seen = set()
    for t in tuts:
        for field in ("slug", "title", "subject", "category", "difficulty", "steps", "dateAdded"):
            if field not in t:
                errors.append(f"{t.get('slug', '?')}: missing field {field}")
        slug = t.get("slug")
        if slug in seen:
            errors.append(f"duplicate slug {slug}")
        seen.add(slug)
        if t.get("category") not in cats:
            errors.append(f"{slug}: unknown category {t.get('category')}")
        if t.get("difficulty") not in DIFF_ORDER:
            errors.append(f"{slug}: difficulty must be one of {DIFF_ORDER}")
        for fn in ("sheet.png", "final.png", "steps.js"):
            p = os.path.join(DOCS, "assets", slug or "", fn)
            if not os.path.exists(p):
                errors.append(f"{slug}: missing docs/assets/{slug}/{fn}")
        page = os.path.join(DOCS, "tutorials", page_file(t))
        if not os.path.exists(page):
            errors.append(f"{slug}: missing tutorial page {page}")
        else:
            html = open(page).read()
            n = html.count("GTM-WP3XNK83")
            if n != 2:
                errors.append(f"{slug}: GTM-WP3XNK83 appears {n}x on page (must be exactly 2)")
            steps_js = open(os.path.join(DOCS, "assets", slug, "steps.js")).read()
            if "DRAWISE_STEPS" not in steps_js:
                errors.append(f"{slug}: steps.js must define window.DRAWISE_STEPS")
    if errors:
        fail(errors)

    # ---- homepage: gallery + chips --------------------------------------
    index_path = os.path.join(DOCS, "index.html")
    index = open(index_path).read()
    cards = "\n".join(card(t, cats[t["category"]], "") for t in tuts)
    index = replace_region(index, "GALLERY", cards)

    used_cats = [c for c in manifest["categories"] if any(t["category"] == c["slug"] for t in tuts)]
    cat_chips = ['<button type="button" class="chip on" data-group="cat" data-value="all">All drawings</button>']
    for c in used_cats:
        cat_chips.append(f'<button type="button" class="chip" data-group="cat" data-value="{c["slug"]}">{c["name"]}</button>')
    index = replace_region(index, "CHIPS-CAT", "        " + "\n        ".join(cat_chips))

    used_diffs = [d for d in DIFF_ORDER if any(t["difficulty"] == d for t in tuts)]
    diff_chips = ['<button type="button" class="chip on" data-group="diff" data-value="all">Any level</button>']
    for d in used_diffs:
        diff_chips.append(f'<button type="button" class="chip" data-group="diff" data-value="{d.lower()}">{d}</button>')
    index = replace_region(index, "CHIPS-DIFF", "        " + "\n        ".join(diff_chips))
    open(index_path, "w").write(index)

    # ---- tutorial pages: related cards -----------------------------------
    for t in tuts:
        page = os.path.join(DOCS, "tutorials", page_file(t))
        html = open(page).read()
        others = [o for o in tuts if o["slug"] != t["slug"]]
        others.sort(key=lambda o: o["dateAdded"], reverse=True)   # newest first
        others.sort(key=lambda o: o["category"] != t["category"])  # same category first (stable)
        rel = others[:3]
        if rel:
            content = "\n".join(related_card(o, cats[o["category"]]) for o in rel)
        else:
            content = '      <p class="sub" style="grid-column:1/-1">More tutorials are on the way — check back soon!</p>'
        html = replace_region(html, "RELATED", content)
        open(page, "w").write(html)

    # ---- sitemap ----------------------------------------------------------
    latest = max(t["dateAdded"] for t in tuts)
    urls = [f"  <url>\n    <loc>{SITE}/</loc>\n    <lastmod>{latest}</lastmod>\n  </url>"]
    for t in sorted(tuts, key=lambda x: x["slug"]):
        urls.append(
            f"  <url>\n    <loc>{SITE}/tutorials/{page_file(t)}</loc>\n"
            f"    <lastmod>{t['dateAdded']}</lastmod>\n  </url>"
        )
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(urls) + "\n</urlset>\n")
    open(os.path.join(DOCS, "sitemap.xml"), "w").write(sitemap)

    # ---- public index ------------------------------------------------------
    public = {"tutorials": []}
    for t in tuts:
        public["tutorials"].append({
            "slug": t["slug"], "title": t["title"], "subject": t["subject"],
            "category": t["category"], "difficulty": t["difficulty"],
            "steps": t["steps"], "tags": t.get("tags", []),
            "page": f"tutorials/{page_file(t)}",
            "sheet": f"assets/{t['slug']}/sheet.png",
            "thumb": f"assets/{t['slug']}/final.png",
            "stepsData": f"assets/{t['slug']}/steps.js",
        })
    with open(os.path.join(DOCS, "assets", "tutorials.json"), "w") as f:
        json.dump(public, f, indent=2)
        f.write("\n")

    print(f"OK: {len(tuts)} tutorial(s); gallery, chips, related, sitemap, index regenerated.")


if __name__ == "__main__":
    main()
