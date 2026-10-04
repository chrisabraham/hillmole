# Hill Mole

Chris Abraham's serialized novel, written at [hillmole.com](https://hillmole.com) from May 2005 through June 2022. It ran on Movable Type 3.33 until the CGI broke; this is the same site as static Jekyll on GitHub Pages.

## Writing a new entry

Add a Markdown file to `_posts/` named `YYYY-MM-DD-slug.md`:

```markdown
---
title: A new chapter
date: 2026-10-05 09:00:00 -0500
---

The text goes here.
```

Push to `main` and GitHub Pages publishes it at `/archives/2026/10/a-new-chapter.html`, the same URL shape as the old entries. It joins the prev/next chain, the front page, the archives list, and all three feeds automatically.

## What's where

- `_posts/`: the 309 published entries from Movable Type, one `.html` file each. The body is exactly what MT published (encoding repairs only, logged during migration). Each has an explicit `permalink` matching its original URL. **Don't edit these by hand.**
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
