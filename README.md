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

## Search and discovery

- `<title>` is at most 60 characters and the meta description at most 160, cut at word boundaries (`_includes/seo.html`, `_includes/fit.html`). The entry title on the page is never changed. To override either for one entry, set `seo_title` or `description` in its front matter.
- JSON-LD on every page: the site is a `WebSite`, the novel a `Book`, each entry a `BlogPosting` + `Chapter` with its chapter number, plus breadcrumbs; the home page adds the 2006 `PodcastSeries`.
- `sitemap.xml` (jekyll-sitemap) and `robots.txt`. MT's daily and weekly archives repeat the monthly pages, so they're `noindex, follow` and left out of the sitemap.
- `/llms.txt` (and the same content at `/llm.txt`) lists every entry; `/llms-full.txt` holds the full text.
- IndexNow: `.github/workflows/indexnow.yml` pings Bing, Yandex and the rest with new or changed entries after each push. The key is `indexnow_key` in `_config.yml` and the matching `<key>.txt` at the root.
- While `url` isn't `https://hillmole.com`, every page says `noindex` and IndexNow does nothing, so the github.io preview stays out of search.

## Going live on hillmole.com

1. In `_config.yml`: `url: "https://hillmole.com"` and `baseurl: ""`. Add a `CNAME` file containing `hillmole.com`.
2. Set the custom domain in the repo's Pages settings, point DNS at GitHub Pages, then enforce HTTPS.
3. Run the IndexNow workflow once by hand with "Submit every URL" checked.
4. Submit `https://hillmole.com/sitemap.xml` in Google Search Console (the site's verification file is still in place) and Bing Webmaster Tools.
