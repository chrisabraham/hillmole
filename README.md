# Hill Mole

Chris Abraham's serialized novel, written at [hillmole.com](https://hillmole.com) from May 2005 through June 2022. It ran on Movable Type 3.33 until the CGI broke; this is the same site as static Jekyll on GitHub Pages.

## Writing a new entry

Add a Markdown file to `_posts/` named `YYYY-MM-DD-slug.md`:

```markdown
---
title: A new chapter
date: 2026-10-05 09:00:00 -0500
seo_title: What this entry is about, in 50 to 60 characters
description: What happens or is argued in it, 140 to 160 characters, plainly, the way a searcher would put it.
---

The text goes here.
```

Push to `main` and GitHub Pages publishes it at `/archives/2026/10/a-new-chapter.html`, the same URL shape as the old entries. It joins the prev/next chain, the front page, the archives list, and all three feeds automatically.

## What's where

- `_posts/`: the 309 published entries from Movable Type, one `.html` file each, with an explicit `permalink` matching the original URL. Bodies are what MT published, plus deliberate changes, every one listed in `_migration/typography-changes.log`: encoding repairs; spelling and grammar fixes from `_migration/corrections.tsv` (one row per fix; delete a row to undo it); and `_migration/typography.py` (no hyperlinks in the prose except the 2006 `[Listen]` podcast links; `--` to closed-up em dash; `...` to `…`; curly quotes). They're generated, so **don't edit these by hand**; change the generator and re-run it.
- New entries: write plain text. No links in the prose; use `—` (closed up), `…` and curly quotes, or plain `--`, `...` and straight quotes, which you can convert later.
- `_mtarchives/`: stubs for MT's monthly, weekly, daily and category archive URLs, plus redirects for pages MT left behind after entries moved. Generated; covers 2005–2022.
- `archives/N.xml`: MT's per-entry TrackBack feeds, kept so their URLs answer. The spam pings in them were removed.
- `index.rdf` (RSS 1.0), `index.xml` (RSS 2.0) and `atom.xml` (Atom, via jekyll-feed): the three feed URLs the old site published.
- `images/`, `podcast/` and the root `.gif` files: copied from the old webroot, paths unchanged.
- `attic/`: the original MT templates, `mt.cgi` and config, database credentials removed. A museum piece; excluded from the build, nothing in it runs.
- `_migration/`: the scripts that did the port (`extract.py` reads the MT MySQL dump, `build_site.py` writes this repo). They read from a local copy of the old server backup, which is never committed.

## Building locally

```sh
bundle install
bundle exec jekyll serve
```

The Gemfile pins the `github-pages` gem, so local builds match production. Plugins are limited to the GitHub Pages whitelist.

## Search and discovery

- Every entry has a hand-written SEO title (50–60 characters) and meta description (140–160) saying what the page is about, kept in `_migration/seo_meta.tsv` and checked by `python3 _migration/check_seo_titles.py`. No pipes, dashes, hyphens, or site/author name on entry pages; the main pages carry the name. For a new entry, add `seo_title:` and `description:` to its front matter; without them it falls back to its title plus its opening words.
- JSON-LD on every page: the site is a `WebSite`, the novel a `Book`, each entry a `BlogPosting` + `Chapter` with its chapter number, plus breadcrumbs; the home page adds the 2006 `PodcastSeries`.
- `sitemap.xml` (jekyll-sitemap) and `robots.txt`. Only the home page, the entries and `archives.html` are indexable. MT's monthly, weekly, daily and category archives repeat entry text, so they're `noindex, follow` (crawlable, not indexed) and left out of the sitemap.
- `/llms.txt` (and the same content at `/llm.txt`) lists every entry; `/llms-full.txt` holds the full text.
- IndexNow: `.github/workflows/indexnow.yml` pings Bing, Yandex and the rest with new or changed entries after each push. The key is `indexnow_key` in `_config.yml` and the matching `<key>.txt` at the root.
- While `url` isn't `https://hillmole.com`, every page says `noindex` and IndexNow does nothing, so the github.io preview stays out of search.

## Going live on hillmole.com

1. In `_config.yml`: `url: "https://hillmole.com"` and `baseurl: ""`. Add a `CNAME` file containing `hillmole.com`.
2. Set the custom domain in the repo's Pages settings, point DNS at GitHub Pages, then enforce HTTPS.
3. Run the IndexNow workflow once by hand with "Submit every URL" checked.
4. Submit `https://hillmole.com/sitemap.xml` in Google Search Console (the site's verification file is still in place) and Bing Webmaster Tools.

The full step-by-step, with DNS records and the post-switch check, is in [`_migration/CUTOVER.md`](_migration/CUTOVER.md).
