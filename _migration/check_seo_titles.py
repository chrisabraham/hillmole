"""Check seo_meta.tsv: one row per published entry, the row's title_starts
matches the entry's own title (catches a wrong mt_id), titles 50-60 chars,
descriptions 140-160, no pipes, dashes or hyphens, no site or author name."""
import csv, glob, re, unicodedata
posts = {}
for f in glob.glob('_posts/*.html'):
    fm = open(f, encoding='utf-8').read().split('\n---\n', 1)[0]
    posts[re.search(r'^mt_id: (\d+)', fm, re.M).group(1)] = re.search(r'^title: "(.*)"$', fm, re.M).group(1).replace('\\"', '"')
key = lambda s: re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', s.lower()).replace('’', "'"))
rows = list(csv.DictReader(open('_migration/seo_meta.tsv', encoding='utf-8'), delimiter='\t'))
problems, seen = [], set()
for r in rows:
    i, t, d = r['mt_id'], r['seo_title'], r['seo_description']
    if i in seen: problems.append(f'{i}: duplicate row')
    seen.add(i)
    if i not in posts: problems.append(f'{i}: no such entry'); continue
    if not key(posts[i]).startswith(key(r['title_starts'])):
        problems.append(f'{i}: row is for [{r["title_starts"]}] but entry is [{posts[i]}]')
    if not 50 <= len(t) <= 60: problems.append(f'{i}: title {len(t)} chars')
    if not 140 <= len(d) <= 160: problems.append(f'{i}: description {len(d)} chars')
    for s in (t, d):
        if re.search(r'[|\-—–]', s): problems.append(f'{i}: pipe/dash/hyphen: {s}')
        if 'Hill Mole' in s or 'Chris Abraham' in s: problems.append(f'{i}: site name: {s}')
missing = sorted(set(posts) - seen, key=int)
print(f'{len(rows)} rows; {len(missing)} entries without one {missing[:10]}; {len(problems)} problems')
for p in problems: print('  ', p)
