#!/usr/bin/env python3
"""Generates the static /unscramble/<letters>/ pages.

Why these exist: GSC shows us ranking around position 8 for one-off
letter-string searches ("unscramble etsbrmion", "unscramble tmseorn") with no
page built for them -- about 96% of /tools/word-unscrambler/'s impressions are
anonymised long-tail queries of exactly that shape. These pages answer those
searches directly instead of handing the visitor an empty text box.

The universe is deliberately NOT every possible letter combination. In this
genre a rack is always a real word, so the candidate set is the distinct
sorted-letter keys of common six- and seven-letter words (15,172 of them).

Two limits, and they do different jobs. MIN_WORDS is a QUALITY floor: the tail
of that list is genuinely thin -- the last key, VOODOO, spells three words --
and shipping those is how a site gets classified as thin content. Only 3,360
keys clear 120 words, so the full universe must never be built. PAGE_LIMIT is
a RISK limit on top of that, raised only when the previous tranche is seen to
index.

    python3 build/unscramble.py        # run from the repo root

Pages link ONE external stylesheet rather than inlining the site CSS: inlined,
300 pages would carry 8.6 MB of duplicate CSS and waste crawl budget.
"""
import os, re, json
from collections import defaultdict
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE_LIMIT = 2000         # phase 2 (18 Nov): 300 indexed within 3 days, so the
                          # constraint was never discovery. Raise on evidence only.
MIN_WORDS  = 120          # a page below this is thin, and thin is how a site gets
                          # hurt. The tail of the candidate list is genuinely bad --
                          # the 15,172nd key (VOODOO) spells three words. NEVER
                          # build the whole universe; 3,360 keys clear this bar.
RELATED    = 6
PER_PAGE   = 250          # hub pagination: 2,000 links on one page is 162 KB and
                          # no use to a reader or a crawler

SCORE = {'A':1,'B':3,'C':3,'D':2,'E':1,'F':4,'G':2,'H':4,'I':1,'J':8,'K':5,'L':1,'M':3,
         'N':1,'O':1,'P':3,'Q':10,'R':1,'S':1,'T':1,'U':1,'V':4,'W':4,'X':8,'Y':4,'Z':10}

home = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
SITE_CSS = re.search(r'<style>(.*?)</style>', home, re.S).group(1)
NAV  = re.search(r'<nav class="nav navstatic">.*?</nav>',
                 open(os.path.join(ROOT, 'tools/index.html'), encoding='utf-8').read(), re.S).group(0)
FOOT = re.search(r'<footer class="sitefoot">.*?</footer>', home, re.S).group(0)

PAGE_CSS = """
/* ── /unscramble/ pages ─────────────────────────────── */
.navstatic{position:static;}
.navstatic .navbar{background:var(--white); border-color:rgba(14,58,80,.08);}
.unwrap{max-width:1080px; margin:0 auto; padding:clamp(24px,4vw,52px) var(--gutter) 56px;}
.crumbs{font-size:13px; color:var(--ink-faint); margin:0 0 14px; font-weight:500;}
.crumbs a{color:var(--ink-soft); text-decoration:underline; text-decoration-color:rgba(14,58,80,.35);
  text-underline-offset:3px; display:inline-block; padding:4px 0;}
.unwrap h1{font-family:var(--display); font-weight:800; font-size:clamp(30px,5.4vw,50px);
  letter-spacing:-.038em; line-height:1; margin:0; color:var(--ink); text-wrap:balance;}
.unwrap .sub{margin:12px 0 0; color:var(--ink-soft); font-size:clamp(15px,1.8vw,18px); max-width:52ch;}
.panel{margin-top:26px; background:var(--white); border-radius:22px; padding:clamp(18px,3vw,28px);
  box-shadow:inset 0 0 0 1px rgba(14,58,80,.08), 0 8px 22px rgba(14,58,80,.08);}
.grp{margin-top:22px;}
.grp:first-child{margin-top:0;}
.grp h2{font-family:var(--display); font-weight:800; font-size:clamp(17px,2.4vw,21px); letter-spacing:-.02em;
  margin:0 0 12px; color:var(--ink); display:flex; align-items:baseline; gap:9px;}
.grp h2 span{font-family:var(--body); font-size:13px; font-weight:600; color:var(--ink-faint);}
.ws{display:flex; flex-wrap:wrap; gap:7px; margin:0; padding:0; list-style:none;}
.ws li{font-family:var(--display); font-weight:800; font-size:15px; letter-spacing:.11em; color:#5B3310;
  background:linear-gradient(180deg,#F6C98B,#E4A458); border-radius:9px; padding:9px 12px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.5);}
.ws li.rare{background:var(--page); color:#4B6C7A; box-shadow:inset 0 0 0 1px rgba(14,58,80,.10);}
.ws li.top{background:linear-gradient(180deg,#5AD9EC,var(--tq)); color:#06323A;}
.best{display:flex; flex-wrap:wrap; align-items:baseline; gap:10px; margin:0; color:var(--ink-soft); font-size:15px;}
.best b{font-family:var(--display); font-weight:800; font-size:19px; letter-spacing:.12em; color:var(--ink);}
.unprose{margin-top:40px; max-width:var(--measure);}
.unprose h2{font-family:var(--display); font-weight:800; font-size:clamp(19px,2.6vw,24px);
  letter-spacing:-.025em; margin:26px 0 9px; color:var(--ink);}
.unprose p{margin:0 0 13px; color:var(--ink-read); font-size:16px; line-height:1.68;}
.unprose a{color:#0C6E92; font-weight:600; text-decoration:underline; text-underline-offset:3px;}
.near{display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 0; padding:0; list-style:none;}
.near a{display:inline-block; background:var(--white); border-radius:10px; padding:9px 13px;
  font-family:var(--display); font-weight:800; font-size:14px; letter-spacing:.09em; color:var(--ink);
  text-decoration:none; box-shadow:inset 0 0 0 1px rgba(14,58,80,.10);}
.near a:hover{box-shadow:inset 0 0 0 2px var(--tq);}
.backtool{display:inline-flex; margin-top:26px; font-family:var(--display); font-weight:800; font-size:15px;
  color:#fff; text-decoration:none; background:linear-gradient(180deg,#D64A28,#BE3F22); border-radius:999px;
  padding:14px 26px; box-shadow:0 4px 0 #9E3319;}
.hubletters{display:grid; grid-template-columns:repeat(auto-fill,minmax(132px,1fr)); gap:8px; margin:0; padding:0; list-style:none;}
.hubletters a{display:block; background:var(--white); border-radius:12px; padding:12px 14px; text-decoration:none;
  box-shadow:inset 0 0 0 1px rgba(14,58,80,.08);}
.hubletters a:hover{box-shadow:inset 0 0 0 2px var(--tq);}
.hubletters b{display:block; font-family:var(--display); font-weight:800; font-size:15px; letter-spacing:.1em; color:var(--ink);}
.hubletters span{display:block; margin-top:3px; font-size:12.5px; color:var(--ink-faint); font-weight:600;}
@media (max-width:600px){ .ws li{font-size:14px; padding:8px 11px;} }
"""

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#E9F6FE">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Wordmere">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://wordmere.com/img/social-card.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://wordmere.com/img/social-card.jpg">
<link rel="icon" href="/img/favicon-32.png" sizes="32x32">
<link rel="icon" href="/img/favicon-16.png" sizes="16x16">
<link rel="apple-touch-icon" href="/img/icon-180.png">
<link rel="preload" as="font" type="font/woff2" crossorigin href="/fonts/3y9K6as8bTXq_nANBjzKo3IeZx8z6up5BeSl9D4dj_x9PpZBMlGIInHWVyNJ.woff2">
<link rel="stylesheet" href="/fonts/fonts.css">
<link rel="stylesheet" href="/unscramble/style.css?v=1">
<script type="application/ld+json">{schema}</script>
</head>
<body>
<div class="shell">
  {nav}
  <main class="unwrap">
"""
TAIL = """  </main>
  {foot}
</div>
</body>
</html>
"""


def load():
    words, common = [], set()
    for line in open(os.path.join(ROOT, 'tools/words.txt'), encoding='utf-8'):
        w = line.strip()
        if not w:
            continue
        if w.endswith('*'):
            w = w[:-1]; common.add(w)
        words.append(w)
    return words, common


def build_index(words):
    amap = defaultdict(list)
    for w in words:
        if 3 <= len(w) <= 8:
            amap[''.join(sorted(w))].append(w)
    return amap


def subwords(key, amap):
    """Every dictionary word spellable from `key`, via sorted-subset lookup."""
    seen, out = set(), []
    for r in range(3, len(key) + 1):
        for sub in combinations(key, r):
            sk = ''.join(sub)
            if sk in seen:
                continue
            seen.add(sk)
            out.extend(amap.get(sk, ()))
    return out


def pick(common, amap):
    """Candidate keys = sorted letters of common 6-7 letter words, richest first."""
    cand = defaultdict(list)
    for w in common:
        if 6 <= len(w) <= 7:
            cand[''.join(sorted(w))].append(w)
    rows = []
    for k, bases in cand.items():
        hits = subwords(k, amap)
        rows.append((k, sorted(bases), hits, sum(1 for w in hits if w in common)))
    rows.sort(key=lambda r: (-r[3], -len(r[2]), r[0]))
    rich = [r for r in rows if len(r[2]) >= MIN_WORDS]
    print(f'  {len(rows):,} candidate keys, {len(rich):,} clear the {MIN_WORDS}-word floor')
    return rich


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render(key, bases, hits, common, neighbours):
    letters = key.upper()
    spaced  = ' '.join(letters)
    slug    = key.lower()      # paths and URLs are lowercase; GitHub Pages is case-sensitive
    url     = f'https://wordmere.com/unscramble/{slug}/'
    exact   = sorted(w for w in hits if len(w) == len(key))
    head    = bases[0]
    n       = len(hits)
    ncommon = sum(1 for w in hits if w in common)

    # Every anagram of a rack scores the same, so ties are common. Break them
    # towards a word people recognise -- naming ESPARTO over SEAPORT is correct
    # arithmetic and a useless answer.
    best = max(hits, key=lambda w: (sum(SCORE.get(c, 0) for c in w),
                                    w in common, len(w), [-ord(c) for c in w]))
    bestscore = sum(SCORE.get(c, 0) for c in best)

    title = f'Unscramble {head} — {n} Words From These Letters'
    if len(title) > 60:
        title = f'Unscramble {head} — All {n} Words'
    desc = (f'Every word the letters in {head} ({spaced}) can spell — all {n} of them, '
            f'grouped longest first, with the {ncommon} everyday words marked. No sign-up.')
    if len(desc) > 160:
        desc = f'All {n} words from the letters in {head} ({spaced}), longest first, with {ncommon} everyday words marked.'

    schema = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Wordmere", "item": "https://wordmere.com/"},
            {"@type": "ListItem", "position": 2, "name": "Word tools", "item": "https://wordmere.com/tools/"},
            {"@type": "ListItem", "position": 3, "name": f"Unscramble {head}", "item": url}]}, ensure_ascii=False)

    # the full-length words are shown in their own section above, so they are
    # kept out of the by-length groups -- otherwise every page lists them twice
    by = defaultdict(list)
    for w in hits:
        if len(w) == len(key) and exact:
            continue
        by[len(w)].append(w)

    body = [f'''    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Wordmere</a> › <a href="/tools/">Word tools</a> › <span aria-current="page">Unscramble {head}</span></nav>
    <h1>Unscramble {head}</h1>
    <p class="sub">Every word the letters <strong>{spaced}</strong> can spell — {n} of them, {ncommon} everyday words and the rest less common. Longest first.</p>
    <div class="panel">''']

    if exact:
        body.append(f'''      <div class="grp"><h2>Uses all {len(key)} letters <span>{len(exact)} {"word" if len(exact)==1 else "words"}</span></h2>
      <ul class="ws">''' + ''.join(
            f'<li class="top">{w}</li>' if w in common else f'<li class="top rare">{w}</li>' for w in exact) + '</ul></div>')

    body.append(f'''      <div class="grp"><h2>Highest-scoring play</h2>
      <p class="best"><b>{best}</b> scores {bestscore} on a Scrabble board before any bonus squares.</p></div>''')

    for L in sorted(by, reverse=True):
        lst = sorted(by[L], key=lambda w: (w not in common, w))
        body.append(f'''      <div class="grp"><h2>{L}-letter words <span>{len(lst)}</span></h2>
      <ul class="ws">''' + ''.join(
            f'<li>{w}</li>' if w in common else f'<li class="rare" title="Less common word">{w}</li>' for w in lst) + '</ul></div>')

    body.append('    </div>')

    body.append(f'''    <div class="unprose">
      <h2>What is on this page</h2>
      <p>These are all {n} words in our dictionary that the letters of <strong>{head}</strong> can spell, using each letter no more times than it appears. They are grouped longest first, because in most word games length is what scores. The {ncommon} everyday words are shown on amber tiles; the paler ones are real dictionary entries that most people would not reach for.</p>
      <h2>A different set of letters</h2>
      <p>This page is fixed to one rack. If you are holding something else, the <a href="/tools/word-unscrambler/">word unscrambler</a> does the same job for any letters you type, and the <a href="/tools/anagram-solver/">anagram solver</a> finds only the words that use every letter exactly once.</p>
      <h2>Nearby racks</h2>
      <ul class="near">''' + ''.join(
        f'<li><a href="/unscramble/{nk.lower()}/">{nb}</a></li>' for nk, nb in neighbours) + f'''</ul>
      <p><a class="backtool" href="/tools/word-unscrambler/">Unscramble your own letters</a></p>
    </div>''')

    return (HEAD.format(title=esc(title), desc=esc(desc), url=url, schema=schema, nav=NAV)
            + '\n'.join(body) + '\n' + TAIL.format(foot=FOOT))


def main():
    words, common = load()
    amap = build_index(words)
    rows = pick(common, amap)
    chosen = rows[:PAGE_LIMIT]
    print(f'  building the richest {len(chosen):,} '
          f'({len(chosen[-1][2])} words on the thinnest)')

    os.makedirs(os.path.join(ROOT, 'unscramble'), exist_ok=True)
    open(os.path.join(ROOT, 'unscramble/style.css'), 'w', encoding='utf-8').write(SITE_CSS + PAGE_CSS)

    total = 0
    for i, (key, bases, hits, nc) in enumerate(chosen):
        nb = [(chosen[(i + d) % len(chosen)][0], chosen[(i + d) % len(chosen)][1][0])
              for d in range(1, RELATED + 1)]
        html = render(key, bases, hits, common, nb)
        d = os.path.join(ROOT, 'unscramble', key.lower())
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(html)
        total += len(html)

    # hub, paginated. Nothing is an orphan: every page is also reachable from
    # the six-neighbour ring, and every one is in the sitemap.
    pages = [chosen[i:i + PER_PAGE] for i in range(0, len(chosen), PER_PAGE)]
    for pno, group in enumerate(pages, start=1):
        path = 'unscramble' if pno == 1 else f'unscramble/page/{pno}'
        url = ('https://wordmere.com/unscramble/' if pno == 1
               else f'https://wordmere.com/unscramble/page/{pno}/')
        cards = ''.join(
            f'<li><a href="/unscramble/{k.lower()}/"><b>{b[0]}</b><span>{len(h)} words</span></a></li>'
            for k, b, h, _ in group)
        crumb_tail = 'Unscramble' if pno == 1 else f'Unscramble, page {pno}'
        hub_schema = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Wordmere", "item": "https://wordmere.com/"},
                {"@type": "ListItem", "position": 2, "name": "Word tools", "item": "https://wordmere.com/tools/"},
                {"@type": "ListItem", "position": 3, "name": crumb_tail, "item": url}]}, ensure_ascii=False)
        pager = '<ul class="near">'
        if pno > 1:
            prev = '/unscramble/' if pno == 2 else f'/unscramble/page/{pno-1}/'
            pager += f'<li><a href="{prev}">← Previous</a></li>'
        for n in range(1, len(pages) + 1):
            href = '/unscramble/' if n == 1 else f'/unscramble/page/{n}/'
            pager += (f'<li><a href="{href}"><b>{n}</b></a></li>' if n != pno
                      else f'<li><a href="{href}" aria-current="page"><b>{n}</b></a></li>')
        if pno < len(pages):
            pager += f'<li><a href="/unscramble/page/{pno+1}/">Next →</a></li>'
        pager += '</ul>'
        heading = ('Unscramble letters' if pno == 1
                   else f'Unscramble letters — page {pno}')
        title = ('Unscramble Letters — Every Word, Rack by Rack' if pno == 1
                 else f'Unscramble Letters — Racks, Page {pno} of {len(pages)}')
        desc = (f'Ready-made word lists for {len(chosen):,} common letter racks. Pick a rack '
                f'and see every word it spells, grouped by length.' if pno == 1 else
                f'Page {pno} of {len(pages)}: more ready-made racks, each with every word '
                f'those letters spell, grouped longest first.')
        hub = (HEAD.format(title=esc(title), desc=esc(desc), url=url, schema=hub_schema, nav=NAV)
            + f'''    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Wordmere</a> › <a href="/tools/">Word tools</a> › <span aria-current="page">{crumb_tail}</span></nav>
    <h1>{heading}</h1>
    <p class="sub">Ready-made lists for {len(chosen):,} of the letter racks word games use most. Each page shows every word that rack spells, longest first.</p>
    <div class="panel"><div class="grp"><h2>Racks <span>{len(group)} of {len(chosen):,}</span></h2>
    <ul class="hubletters">{cards}</ul></div></div>
    <div class="unprose">
      {pager}
      <h2>Why these are already written out</h2>
      <p>Most people reaching for an unscrambler are holding one specific set of letters and want the answer, not a text box. These pages are the answer for the racks that come up most often. For anything else, the <a href="/tools/word-unscrambler/">word unscrambler</a> takes whatever you type.</p>
      <p><a class="backtool" href="/tools/word-unscrambler/">Unscramble your own letters</a></p>
    </div>'''
            + '\n' + TAIL.format(foot=FOOT))
        os.makedirs(os.path.join(ROOT, path), exist_ok=True)
        open(os.path.join(ROOT, path, 'index.html'), 'w', encoding='utf-8').write(hub)
    print(f'  hub paginated into {len(pages)} pages of up to {PER_PAGE}')

    # its own sitemap, so indexation of this tranche can be measured on its own
    urls = ''.join(
        f'  <url><loc>https://wordmere.com/unscramble/{k.lower()}/</loc><lastmod>2026-11-18</lastmod>'
        f'<changefreq>monthly</changefreq><priority>0.5</priority></url>\n' for k, _, _, _ in chosen)
    hubs = ''.join(
        f'  <url><loc>https://wordmere.com/unscramble/{"" if p == 1 else f"page/{p}/"}</loc>'
        f'<lastmod>2026-11-18</lastmod><changefreq>weekly</changefreq><priority>0.6</priority></url>\n'
        for p in range(1, len(pages) + 1))
    open(os.path.join(ROOT, 'sitemap-unscramble.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + hubs + urls + '</urlset>\n')

    css = os.path.getsize(os.path.join(ROOT, 'unscramble/style.css'))
    print(f'  {len(chosen)} pages + hub, {total/1024/1024:.1f} MB of HTML')
    print(f'  one shared stylesheet: {css/1024:.0f} KB (inlining it would have cost {css*len(chosen)/1024/1024:.1f} MB)')
    print(f'  sitemap-unscramble.xml: {len(chosen)+1} URLs')


if __name__ == '__main__':
    main()
