# Moving hillmole.com to GitHub Pages

The goal: Google sees the same site, at the same URLs, just faster and fixed. No 404s, no lost Search Console history, no window where the site is down or marked `noindex`.

Every old URL is already in place (`python3 _migration/check_live.py https://chrisabraham.github.io/hillmole` checks all 953). What's left is DNS, and doing it in this order.

## Why the order matters

hillmole.com's DNS is hosted by the old web host (TotalChoice: `dns3`/`dns4.totalchoicehosting.com`). Cancel the hosting and DNS disappears with it. So DNS moves first, to the registrar or Cloudflare, while still pointing at the old server. Then the site flips. Then, weeks later, the old host goes.

## 1. A day or two before: move DNS, change nothing visible

At the new DNS host (registrar or Cloudflare, DNS only, no proxy), recreate these records **exactly as they are now**, TTL 300:

| Name | Type | Value | Why |
|---|---|---|---|
| `hillmole.com` | A | `198.38.77.135` | the old site, for now |
| `www` | CNAME | `hillmole.com` | |
| `hillmole.com` | TXT | `google-site-verification=X4wVLk892UTtlvJQ-6isfSVh6_oIGW75H8-Zc-yQzXU` | **keeps Search Console verified. Do not skip.** |

Mail: `mole@hillmole.com` only holds 2006 mail (saved in the backup). If it's retired, skip the MX/SPF/DKIM records and add a null MX instead (`hillmole.com MX 0 .`) so nobody can spoof the domain. Skip all the cPanel records (`cpanel`, `webmail`, `_caldav`, `_acme-challenge`, `_cpanel-dcv-test-record`, …).

Then switch the domain's nameservers at the registrar to the new DNS host. Wait until `dig +short NS hillmole.com` shows the new nameservers and `dig +short TXT hillmole.com` shows the Google record. The site is unchanged throughout.

## 2. Verify the domain with GitHub (prevents takeover)

GitHub → Settings (your account) → Pages → Verified domains → Add `hillmole.com`. It gives a TXT record (`_github-pages-challenge-chrisabraham`); add it at the new DNS host and click Verify.

## 3. Go live (about an hour, at a quiet time)

1. Merge the **Go live on hillmole.com** pull request. It sets `url: https://hillmole.com`, `baseurl: ""` and adds the `CNAME` file. That one merge removes the preview `noindex`, points every canonical, the sitemap, the feeds and `robots.txt` at hillmole.com, and switches IndexNow on.
2. At the DNS host, replace the A record and add the rest:

   | Name | Type | Value |
   |---|---|---|
   | `hillmole.com` | A | `185.199.108.153` |
   | `hillmole.com` | A | `185.199.109.153` |
   | `hillmole.com` | A | `185.199.110.153` |
   | `hillmole.com` | A | `185.199.111.153` |
   | `hillmole.com` | AAAA | `2606:50c0:8000::153` |
   | `hillmole.com` | AAAA | `2606:50c0:8001::153` |
   | `hillmole.com` | AAAA | `2606:50c0:8002::153` |
   | `hillmole.com` | AAAA | `2606:50c0:8003::153` |
   | `www` | CNAME | `chrisabraham.github.io` |

3. Repo → Settings → Pages: the custom domain should read `hillmole.com`. Wait for "DNS check successful" and the certificate (minutes to an hour), then tick **Enforce HTTPS**.
4. Run `python3 _migration/check_live.py`. It must end with `ALL GOOD`: every old URL answers, http and www redirect to https://hillmole.com, no `noindex`, canonicals on hillmole.com.

## 4. Same day: tell the search engines

- **Google Search Console** (hillmole.com property, already verified):
  - Sitemaps → submit `https://hillmole.com/sitemap.xml` (resubmit if it's listed).
  - URL Inspection → Request indexing for: the home page, `/archives.html`, `/about.html`, `/book.html`, the first entry, the latest entry. (There's a daily quota; these are the ones that matter.)
  - Don't use the Change of Address tool: the domain isn't changing.
- **Bing Webmaster Tools**: add the site by importing from Search Console; submit the sitemap.
- **IndexNow**: GitHub → Actions → IndexNow → Run workflow, tick "Submit every URL". After this it runs by itself on every new entry.

## 5. The following weeks

- Search Console → Pages: "Not found (404)" should stay near zero; "Crawled, currently not indexed" should shrink as the revised entries get recrawled.
- Keep the old hosting (now only the old server, no DNS) for two weeks, then cancel it.

## What actually lifts a site out of "archive"

The migration keeps everything Google already credits. What changes how Google treats the site is activity and links:

- **New entries.** A site that hasn't changed since 2022 gets crawled like an archive. New chapters, even short ones, on any regular rhythm, change that. Each push pings IndexNow automatically.
- **Links in from your other profiles.** Put hillmole.com on chrisabraham.com, your Substack (about page and occasional posts), LinkedIn (Featured), X bio, GitHub profile README, and your Amazon author page, and in the Kindle book's front or back matter. These are the same profiles the site's schema names as you, so the links confirm to Google that the author of Hill Mole is you.
- **The podcast.** Narrated chapters on the site with a fresh podcast feed give Google and Apple a reason to come back.
