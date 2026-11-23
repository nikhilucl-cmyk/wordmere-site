#!/usr/bin/env python3
"""Generates the static /words/ pages -- "5 letter words starting with SA" and
its family.

Why these exist, and why they are a different bet from /unscramble/:

/unscramble/<letters>/ answers a query whose demand is spread paper-thin over
thousands of keys. Measured 23 Nov: ~300 indexed pages produced 429 impressions
in 7 days at position 9.7 and ZERO clicks. The pages rank; almost nobody is
searching any single rack.

This template is the opposite shape. "5 letter words starting with sa" is a
query real people type in volume -- it is the Wordle-era staple of every word
site -- and we currently serve none of it. /tools/five-letter-word-solver/
already pulls 2.6K impressions on the generic variants ("5 letter word finder")
alone, with no page for a single pattern.

What makes these pages worth having rather than doorway spam: every competitor
dumps an undifferentiated wall of words, most of which no one has heard of.
We mark the everyday words apart from the obscure ones, which is the whole
question a Wordle player is actually asking.

    python3 build/wordlists.py        # run from the repo root

Pages link ONE external stylesheet rather than inlining the site CSS -- see
build/unscramble.py for that arithmetic.
"""
import os, re, json
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LENGTHS     = (4, 5, 6, 7)   # 5 shipped first (the Wordle length); 4/6/7 added
                      # 23 Nov on Nikhil's instruction, ahead of indexation evidence.
MIN_WORDS   = 8       # below this the page is a stub. Unlike /unscramble/,
                      # a short list here is still the COMPLETE answer to the
                      # query -- but Google cannot tell, so hold a floor.
COMMON_CAP  = 900     # display caps. The biggest set (5-letter ending in S)
RARE_CAP    = 400     # is 3,096 words; a page must not become a scroll trap.
RELATED     = 8
PER_PAGE    = 220

# Three-letter endings are gated, and the gate is the point. 1,108 trigrams
# clear the word floor at some length, but most are not endings anyone thinks
# of as an ending -- in CANE, LANE, PANE the "ANE" is simply the rest of the
# word, and nobody searches for it. Requiring the ending to appear on at least
# this many words across all four lengths is a measured test of whether it is a
# productive ending rather than a coincidence of spelling. It keeps every real
# suffix (-ing -ers -est -ion -ous -ily -ate -ies -ier -ish -ful -ive -ent -age
# -ary) and the phonetic endings people do search (-ine -ite -ock -ble -tic),
# and it cuts the build from 2,607 pages to 330. One- and two-letter endings
# need no gate: there are few enough that all of them are searched.
SUFFIX_MIN_TOTAL = 150

ORD = {1:'1st', 2:'2nd', 3:'3rd', 4:'4th', 5:'5th', 6:'6th', 7:'7th'}

# Which solver a page should send people to. The five-letter solver takes the
# green/yellow/grey boxes a daily puzzle gives you and only ever works on five
# letters; for every other length the word finder is the tool that matches a
# wildcard pattern. Pointing a 7-letter page at the five-letter solver would be
# a dead end for the reader and a bad internal link.
def solver(n):
    return (('/tools/five-letter-word-solver/', 'five-letter word solver')
            if n == 5 else ('/tools/word-finder/', 'word finder'))

home = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
SITE_CSS = re.search(r'<style>(.*?)</style>', home, re.S).group(1)
NAV  = re.search(r'<nav class="nav navstatic">.*?</nav>',
                 open(os.path.join(ROOT, 'tools/index.html'), encoding='utf-8').read(), re.S).group(0)
FOOT = re.search(r'<footer class="sitefoot">.*?</footer>', home, re.S).group(0)

PAGE_CSS = """
/* ── /words/ pages ──────────────────────────────────── */
.navstatic{position:static;}
.navstatic .navbar{background:var(--white); border-color:rgba(14,58,80,.08);}
.unwrap{max-width:1080px; margin:0 auto; padding:clamp(24px,4vw,52px) var(--gutter) 56px;}
.crumbs{font-size:13px; color:var(--ink-faint); margin:0 0 14px; font-weight:500;}
.crumbs a{color:var(--ink-soft); text-decoration:underline; text-decoration-color:rgba(14,58,80,.35);
  text-underline-offset:3px; display:inline-block; padding:4px 0;}
.unwrap h1{font-family:var(--display); font-weight:800; font-size:clamp(28px,5vw,46px);
  letter-spacing:-.038em; line-height:1.03; margin:0; color:var(--ink); text-wrap:balance;}
.unwrap .sub{margin:12px 0 0; color:var(--ink-soft); font-size:clamp(15px,1.8vw,18px); max-width:52ch;}
.panel{margin-top:26px; background:var(--white); border-radius:22px; padding:clamp(18px,3vw,28px);
  box-shadow:inset 0 0 0 1px rgba(14,58,80,.08), 0 8px 22px rgba(14,58,80,.08);}
.grp{margin-top:22px;}
.grp:first-child{margin-top:0;}
.grp h2{font-family:var(--display); font-weight:800; font-size:clamp(17px,2.4vw,21px); letter-spacing:-.02em;
  margin:0 0 6px; color:var(--ink); display:flex; align-items:baseline; gap:9px; flex-wrap:wrap;}
.grp h2 span{font-family:var(--body); font-size:13px; font-weight:600; color:var(--ink-faint);}
.grp .hint{margin:0 0 12px; font-size:13.5px; color:var(--ink-faint); max-width:60ch;}
.ws{display:flex; flex-wrap:wrap; gap:7px; margin:0; padding:0; list-style:none;}
.ws li{font-family:var(--display); font-weight:800; font-size:15px; letter-spacing:.11em; color:#5B3310;
  background:linear-gradient(180deg,#F6C98B,#E4A458); border-radius:9px; padding:9px 12px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.5);}
.ws li.rare{background:var(--page); color:#4B6C7A; box-shadow:inset 0 0 0 1px rgba(14,58,80,.10);}
.more{margin:12px 0 0; font-size:13.5px; color:var(--ink-faint);}
.unprose{margin-top:40px; max-width:var(--measure);}
.unprose h2{font-family:var(--display); font-weight:800; font-size:clamp(19px,2.6vw,24px);
  letter-spacing:-.025em; margin:26px 0 9px; color:var(--ink);}
.unprose p{margin:0 0 13px; color:var(--ink-read); font-size:16px; line-height:1.68;}
.unprose a{color:#0C6E92; font-weight:600; text-decoration:underline; text-underline-offset:3px;}
.near{display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 0; padding:0; list-style:none;}
.near a{display:inline-block; background:var(--white); border-radius:10px; padding:9px 13px;
  font-family:var(--display); font-weight:800; font-size:14px; letter-spacing:.06em; color:var(--ink);
  text-decoration:none; box-shadow:inset 0 0 0 1px rgba(14,58,80,.10);}
.near a:hover{box-shadow:inset 0 0 0 2px var(--tq);}
.backtool{display:inline-flex; margin-top:26px; font-family:var(--display); font-weight:800; font-size:15px;
  color:#fff; text-decoration:none; background:linear-gradient(180deg,#D64A28,#BE3F22); border-radius:999px;
  padding:14px 26px; box-shadow:0 4px 0 #9E3319;}
.hubletters{display:grid; grid-template-columns:repeat(auto-fill,minmax(210px,1fr)); gap:8px; margin:0; padding:0; list-style:none;}
.hubletters a{display:block; background:var(--white); border-radius:12px; padding:12px 14px; text-decoration:none;
  box-shadow:inset 0 0 0 1px rgba(14,58,80,.08);}
.hubletters a:hover{box-shadow:inset 0 0 0 2px var(--tq);}
.hubletters b{display:block; font-family:var(--display); font-weight:800; font-size:14.5px; color:var(--ink);}
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
<link rel="icon" href="/img/favicon-32.png" sizes="32x32">
<link rel="icon" href="/img/favicon-16.png" sizes="16x16">
<link rel="apple-touch-icon" href="/img/icon-180.png">
<link rel="preload" as="font" type="font/woff2" crossorigin href="/fonts/3y9K6as8bTXq_nANBjzKo3IeZx8z6up5BeSl9D4dj_x9PpZBMlGIInHWVyNJ.woff2">
<link rel="stylesheet" href="/fonts/fonts.css">
<link rel="stylesheet" href="/words/style.css?v=1">
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


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def productive_endings(words):
    """Three-letter endings common enough across LENGTHS to be worth a page."""
    tally = defaultdict(int)
    for w in words:
        if len(w) in LENGTHS:
            tally[w[-3:]] += 1
    keep = {k for k, c in tally.items() if c >= SUFFIX_MIN_TOTAL}
    print(f'  {len(keep)} three-letter endings clear {SUFFIX_MIN_TOTAL} words '
          f'(of {len(tally)} that occur at all)')
    return keep


def make_sets(words):
    """Every (slug, heading, query-phrase, word-list) this template covers."""
    out = []
    suffixes = productive_endings(words)
    for n in LENGTHS:
        pool = [w for w in words if len(w) == n]

        # prefixes: one and two letters only. A three-letter prefix of a
        # four-letter word is almost the whole word, and nobody searches it.
        for size in (1, 2):
            g = defaultdict(list)
            for w in pool:
                g[w[:size]].append(w)
            for k, lst in g.items():
                out.append((f'{n}-letter-words-starting-with-{k.lower()}',
                            f'{n} letter words starting with {k}',
                            f'start with {k}', 'start', k, n, sorted(lst)))

        # suffixes: one and two letters, plus the three-letter endings that
        # pass the productivity gate above
        for size in (1, 2, 3):
            g = defaultdict(list)
            for w in pool:
                g[w[-size:]].append(w)
            for k, lst in g.items():
                if size == 3 and k not in suffixes:
                    continue
                out.append((f'{n}-letter-words-ending-in-{k.lower()}',
                            f'{n} letter words ending in {k}',
                            f'end in {k}', 'end', k, n, sorted(lst)))

        # positional: the Wordle shape, "5 letter words with A as the 3rd letter"
        g = defaultdict(list)
        for w in pool:
            for i, c in enumerate(w):
                g[(i + 1, c)].append(w)
        for (p, c), lst in g.items():
            if p == 1:
                continue            # that is "starting with", already built
            out.append((f'{n}-letter-words-with-{c.lower()}-as-the-{ORD[p]}-letter',
                        f'{n} letter words with {c} as the {ORD[p]} letter',
                        f'have {c} as the {ORD[p]} letter', 'pos', (p, c), n, sorted(lst)))

    return [s for s in out if len(s[6]) >= MIN_WORDS]


def render(s, common, neighbours):
    slug, heading, phrase, kind, key, n, lst = s
    url = f'https://wordmere.com/words/{slug}/'
    com = [w for w in lst if w in common]
    rare = [w for w in lst if w not in common]
    total = len(lst)

    title = heading[0].upper() + heading[1:]
    if len(title) <= 46:
        title += ' — Full List'
    desc = (f'All {total} {n}-letter words that {phrase}, with the {len(com)} everyday '
            f'words marked apart from the obscure ones. Useful for Wordle and crosswords.')
    if len(desc) > 160:
        desc = f'All {total} {n}-letter words that {phrase} — everyday words marked apart from the obscure ones.'

    schema = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Wordmere", "item": "https://wordmere.com/"},
            {"@type": "ListItem", "position": 2, "name": "Word lists", "item": "https://wordmere.com/words/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}]}, ensure_ascii=False)

    body = [f'''    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Wordmere</a> › <a href="/words/">Word lists</a> › <span aria-current="page">{esc(heading)}</span></nav>
    <h1>{esc(heading)}</h1>
    <p class="sub">There are <strong>{total}</strong> of them. {len(com)} are words you would actually use; the rest are valid but obscure.</p>
    <div class="panel">''']

    if com:
        shown = com[:COMMON_CAP]
        body.append(f'''      <div class="grp"><h2>Everyday words <span>{len(com)}</span></h2>
      <p class="hint">Words most people know. If you are guessing, start here.</p>
      <ul class="ws">''' + ''.join(f'<li>{w}</li>' for w in shown) + '</ul>'
            + (f'<p class="more">Showing the first {len(shown)} of {len(com)}.</p>' if len(shown) < len(com) else '')
            + '</div>')

    if rare:
        shown = rare[:RARE_CAP]
        body.append(f'''      <div class="grp"><h2>Valid but uncommon <span>{len(rare)}</span></h2>
      <p class="hint">Real dictionary entries that will be accepted in a word game, but that few people would reach for.</p>
      <ul class="ws">''' + ''.join(f'<li class="rare">{w}</li>' for w in shown) + '</ul>'
            + (f'<p class="more">Showing the first {len(shown)} of {len(rare)}.</p>' if len(shown) < len(rare) else '')
            + '</div>')

    body.append('    </div>')

    shref, sname = solver(n)
    if kind == 'pos':
        p, c = key
        narrow = (f'<a href="{shref}">{sname}</a> takes a pattern like '
                  f'<strong>{"?"*(p-1)}{c}{"?"*(n-p)}</strong> and narrows it further '
                  f'once you know a letter that is <em>not</em> in the answer')
    else:
        narrow = (f'<a href="{shref}">{sname}</a> combines this with the other letters you '
                  f'have already ruled in or out')

    body.append(f'''    <div class="unprose">
      <h2>What is on this page</h2>
      <p>Every {n}-letter word in our dictionary that {phrase} — {total} in all. They are split into the {len(com)} words in ordinary use and the {len(rare)} that are valid in a word game but that almost nobody says. Most word lists do not make that distinction, which is why they are so hard to use: the answer you want is usually an everyday word.</p>
      <h2>Narrowing it down</h2>
      <p>A list this long is a starting point rather than an answer. The {narrow}, and the <a href="/tools/word-unscrambler/">word unscrambler</a> works the other way round, from letters you are holding.</p>
      <h2>Related lists</h2>
      <ul class="near">''' + ''.join(
        f'<li><a href="/words/{ns}/">{esc(nh)}</a></li>' for ns, nh in neighbours) + f'''</ul>
      <p><a class="backtool" href="{shref}">Solve a {n}-letter word</a></p>
    </div>''')

    return (HEAD.format(title=esc(title), desc=esc(desc), url=url, schema=schema, nav=NAV)
            + '\n'.join(body) + '\n' + TAIL.format(foot=FOOT))


def main():
    words, common = load()
    sets = make_sets(words)
    kindord = {'start': 0, 'end': 1, 'pos': 2}
    sets.sort(key=lambda s: (s[5], kindord[s[3]], s[0]))
    print(f'  {len(sets):,} pages clear the {MIN_WORDS}-word floor')

    os.makedirs(os.path.join(ROOT, 'words'), exist_ok=True)
    open(os.path.join(ROOT, 'words/style.css'), 'w', encoding='utf-8').write(SITE_CSS + PAGE_CSS)

    total = 0
    for i, s in enumerate(sets):
        nb = [(sets[(i + d) % len(sets)][0], sets[(i + d) % len(sets)][1])
              for d in range(1, RELATED + 1)]
        html = render(s, common, nb)
        d = os.path.join(ROOT, 'words', s[0])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(html)
        total += len(html)

    pages = [sets[i:i + PER_PAGE] for i in range(0, len(sets), PER_PAGE)]
    # first hub page each length appears on, so every page can offer a jump nav
    first = {}
    for pno, group in enumerate(pages, start=1):
        for t in group:
            first.setdefault(t[5], pno)
    def lennav(cur):
        out = '<ul class="near">'
        for n in sorted(first):
            href = '/words/' if first[n] == 1 else f'/words/page/{first[n]}/'
            mark = ' aria-current="page"' if first[n] == cur else ''
            out += f'<li><a href="{href}"{mark}>{n}-letter words</a></li>'
        return out + '</ul>'
    for pno, group in enumerate(pages, start=1):
        path = 'words' if pno == 1 else f'words/page/{pno}'
        url = ('https://wordmere.com/words/' if pno == 1
               else f'https://wordmere.com/words/page/{pno}/')
        cards = ''.join(
            f'<li><a href="/words/{s[0]}/"><b>{esc(s[1])}</b><span>{len(s[6])} words</span></a></li>'
            for s in group)
        crumb_tail = 'Word lists' if pno == 1 else f'Word lists, page {pno}'
        hub_schema = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Wordmere", "item": "https://wordmere.com/"},
                {"@type": "ListItem", "position": 2, "name": crumb_tail, "item": url}]}, ensure_ascii=False)
        pager = '<ul class="near">'
        if pno > 1:
            prev = '/words/' if pno == 2 else f'/words/page/{pno-1}/'
            pager += f'<li><a href="{prev}">← Previous</a></li>'
        for k in range(1, len(pages) + 1):
            href = '/words/' if k == 1 else f'/words/page/{k}/'
            pager += (f'<li><a href="{href}"><b>{k}</b></a></li>' if k != pno
                      else f'<li><a href="{href}" aria-current="page"><b>{k}</b></a></li>')
        if pno < len(pages):
            pager += f'<li><a href="/words/page/{pno+1}/">Next →</a></li>'
        pager += '</ul>'
        lens = sorted({t[5] for t in group})
        span = (f'{lens[0]}-letter' if len(lens) == 1
                else f'{lens[0]}- to {lens[-1]}-letter')
        heading = 'Word lists' if pno == 1 else f'Word lists — {span}, page {pno}'
        title = ('Word Lists — Words by Letter Pattern' if pno == 1
                 else f'Word Lists — {span[0].upper() + span[1:]} Words, Page {pno}')
        desc = (f'{len(sets):,} ready-made word lists for four to seven letters, by starting '
                f'letters, ending letters and letter position, with everyday words marked.'
                if pno == 1 else
                f'Page {pno} of {len(pages)}: {span} word lists by pattern, with the '
                f'everyday words marked apart from the obscure ones.')
        lenjump = lennav(pno)
        hub = (HEAD.format(title=esc(title), desc=esc(desc), url=url, schema=hub_schema, nav=NAV)
            + f'''    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Wordmere</a> › <span aria-current="page">{crumb_tail}</span></nav>
    <h1>{heading}</h1>
    <p class="sub">{len(sets):,} ready-made lists for words of four to seven letters — by first letters, last letters, and which letter sits in which position. Everyday words are marked apart from the obscure ones.</p>
    <div class="panel"><div class="grp"><h2>Jump to a length</h2>{lenjump}</div>
    <div class="grp"><h2>{span} lists <span>{len(group)} of {len(sets):,}</span></h2>
    <ul class="hubletters">{cards}</ul></div></div>
    <div class="unprose">
      {pager}
      <h2>Why these are written out</h2>
      <p>Someone stuck on a puzzle usually knows one or two letters and where they sit. These lists are that answer, already written down. For anything more specific, the <a href="/tools/word-finder/">word finder</a> matches a wildcard pattern at any length, and the <a href="/tools/five-letter-word-solver/">five-letter word solver</a> also takes the letters a daily puzzle has ruled out.</p>
      <p><a class="backtool" href="/tools/word-finder/">Find a word by pattern</a></p>
    </div>'''
            + '\n' + TAIL.format(foot=FOOT))
        os.makedirs(os.path.join(ROOT, path), exist_ok=True)
        open(os.path.join(ROOT, path, 'index.html'), 'w', encoding='utf-8').write(hub)
    print(f'  hub paginated into {len(pages)} pages of up to {PER_PAGE}')

    urls = ''.join(
        f'  <url><loc>https://wordmere.com/words/{s[0]}/</loc><lastmod>2026-11-23</lastmod>'
        f'<changefreq>monthly</changefreq><priority>0.5</priority></url>\n' for s in sets)
    hubs = ''.join(
        f'  <url><loc>https://wordmere.com/words/{"" if p == 1 else f"page/{p}/"}</loc>'
        f'<lastmod>2026-11-23</lastmod><changefreq>weekly</changefreq><priority>0.6</priority></url>\n'
        for p in range(1, len(pages) + 1))
    open(os.path.join(ROOT, 'sitemap-words.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + hubs + urls + '</urlset>\n')

    css = os.path.getsize(os.path.join(ROOT, 'words/style.css'))
    print(f'  {len(sets)} pages + hub, {total/1024/1024:.1f} MB of HTML')
    print(f'  one shared stylesheet: {css/1024:.0f} KB')
    print(f'  sitemap-words.xml: {len(sets)+len(pages)} URLs')


if __name__ == '__main__':
    main()
