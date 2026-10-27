#!/usr/bin/env python3
"""Generates /blog/ and every /blog/<slug>/index.html from one template.
Run from the repo root:  python3 build/blog.py

Shares the site's chrome with build/tools.py — the CSS comes out of
index.html and the nav/footer out of tools/index.html, so a change there
propagates here on the next build. Posts are prose: no form, no engine,
nothing to load. Each one is a real write-up of something we hit building
Wordmere; if a post can't name a specific thing that went wrong, it
doesn't belong here."""
import re, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://wordmere.com'

home = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
STYLE = home[home.index('<style>'):home.index('</style>') + 8]
NAV = re.search(r'<nav class="nav navstatic">.*?</nav>', open(os.path.join(ROOT, 'tools/index.html'), encoding='utf-8').read(), re.S).group(0)
FOOT = re.search(r'<footer class="sitefoot">.*?</footer>', home, re.S).group(0)
TEMPLATE = open(os.path.join(ROOT, 'build/post_template.html'), encoding='utf-8').read()

AUTHOR = 'The Wordmere team'

BLOG_CSS = """<style>
  .navstatic{position:static;}
  .navstatic .navbar{background:var(--white); border-color:rgba(14,58,80,.08);}
  .postwrap{max-width:1080px; margin:0 auto; padding:clamp(24px,4vw,52px) var(--gutter) 56px;}
  .crumbs{font-size:13px; color:var(--ink-faint); margin:0 0 14px; font-weight:500;}
  .crumbs a{color:var(--ink-soft); text-decoration:underline; text-decoration-color:rgba(14,58,80,.35); text-underline-offset:3px;}
  .postwrap h1{font-family:var(--display); font-weight:800; font-size:clamp(30px,5.4vw,50px); letter-spacing:-.038em;
    line-height:1.04; margin:0; color:var(--ink); text-wrap:balance; max-width:20ch;}
  .postwrap .sub{margin:14px 0 0; color:var(--ink-soft); font-size:clamp(16px,2vw,19px); max-width:58ch;}
  .meta{margin:18px 0 0; font-size:13.5px; color:var(--ink-faint); font-weight:600;}
  .meta time{font-variant-numeric:tabular-nums;}
  .article{margin-top:clamp(28px,4vw,44px); max-width:68ch;}
  .article h2{font-family:var(--display); font-weight:800; font-size:clamp(21px,3vw,28px); letter-spacing:-.028em;
    margin:38px 0 12px; color:var(--ink); text-wrap:balance;}
  .article p{margin:0 0 16px; color:var(--ink-soft); font-size:17px; line-height:1.65;}
  .article strong{color:var(--ink); font-weight:700;}
  .article a{color:#0C6E92; font-weight:600; text-decoration:underline; text-underline-offset:3px;}
  .article ul{margin:0 0 16px; padding:0 0 0 2px; list-style:none; display:grid; gap:10px;}
  .article ul li{position:relative; padding-left:22px; color:var(--ink-soft); font-size:17px; line-height:1.6;}
  .article ul li::before{content:""; position:absolute; left:2px; top:11px; width:7px; height:7px; border-radius:50%;
    background:var(--tq);}
  .article code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:14.5px; background:var(--mist);
    color:var(--ink); padding:2px 6px; border-radius:6px; word-break:break-word;}
  .pull{margin:26px 0; padding:20px 24px; background:var(--white); border-radius:18px;
    box-shadow:inset 0 0 0 1px rgba(14,58,80,.08), 0 6px 18px rgba(14,58,80,.06);}
  .pull p{margin:0; font-family:var(--display); font-weight:700; font-size:clamp(17px,2.2vw,20px); line-height:1.45;
    color:var(--ink); letter-spacing:-.015em;}
  .tryit{margin:30px 0; display:flex; flex-wrap:wrap; gap:12px; align-items:center; padding:18px 22px;
    background:linear-gradient(120deg,#FFF3DC,#FFFBF2); border-radius:18px; box-shadow:inset 0 0 0 1px rgba(192,106,18,.22);}
  .tryit p{margin:0; flex:1 1 240px; font-size:15.5px; color:#5A3300; font-weight:600;}
  .tryit a{flex:0 0 auto; font-family:var(--display); font-weight:800; font-size:15px; color:#fff; text-decoration:none;
    background:linear-gradient(180deg,#D64A28,#BE3F22); border-radius:999px; padding:13px 24px; box-shadow:0 4px 0 #9E3319;}
  .endnote{margin-top:40px; padding-top:22px; border-top:1px solid var(--line-soft); font-size:15px; color:var(--ink-faint);}
  .endnote a{color:#0C6E92; font-weight:600; text-decoration:underline; text-underline-offset:3px;}
  .postlist{margin-top:34px; display:grid; gap:16px;}
  .postcard{display:block; text-decoration:none; color:inherit; background:var(--white); border-radius:20px;
    padding:clamp(20px,3vw,28px); box-shadow:inset 0 0 0 1px rgba(14,58,80,.08), 0 6px 18px rgba(14,58,80,.06);}
  a.postcard:hover{box-shadow:inset 0 0 0 2px var(--tq), 0 10px 24px rgba(14,58,80,.12);}
  .postcard h2{font-family:var(--display); font-weight:800; font-size:clamp(19px,2.6vw,24px); letter-spacing:-.025em;
    margin:0; color:var(--ink); text-wrap:balance;}
  .postcard p{margin:9px 0 0; color:var(--ink-soft); font-size:15.5px;}
  .postcard .when{display:block; margin-top:12px; font-size:13px; color:var(--ink-faint); font-weight:600;}
  .upnext{margin-top:44px; max-width:68ch;}
  .upnext h2{font-family:var(--display); font-weight:800; font-size:clamp(19px,2.6vw,23px); letter-spacing:-.02em;
    margin:0 0 12px; color:var(--ink);}
  .upnext p{margin:0 0 14px; color:var(--ink-soft); font-size:16px;}
  @media (max-width:600px){
    .postwrap h1{font-size:clamp(27px,8vw,36px);}
    .article p,.article ul li{font-size:16.5px;}
    .tryit a{width:100%; text-align:center;}
  }
</style>"""

# ── posts ────────────────────────────────────────────────────────────
# Newest first. `body` is the article only; the shell adds everything else.

POSTS = [
dict(
 slug='word-list-problem',
 date='2026-10-10',
 title='Why your word game’s dictionary is lying to you',
 h1='Why your word game’s dictionary is lying to you',
 sub='Our Scrabble helper once told a player that REQUIZ was their best move. Here is why every open word list will do that to you, and the cheap fix.',
 desc='Open word lists accept words no human would play. Why a word game needs two dictionaries, not one, and the cheap signal we used to tell them apart.',
 body="""
      <p>If you are building anything that suggests words to a person — a Scrabble helper, an unscrambler, a hint system, a bot opponent — you will reach for a word list early. There are good free ones. You will wire it in, it will work, and then it will embarrass you.</p>

      <p>Ours embarrassed us like this. We built a <a href="/tools/scrabble-word-finder/">Scrabble word finder</a>, fed it a rack, and it confidently announced the highest-scoring play: <strong>REQUIZ</strong>.</p>

      <p>REQUIZ is in the list. It is not a word anybody has ever played.</p>

      <h2>Open word lists answer a different question</h2>

      <p>We used the public-domain <code>dwyl/english-words</code> list, filtered to three to eight letters, which left 104,562 words. Lists like it are built by union: take several sources, merge them, deduplicate. That is the right way to build a list that answers <em>is this a string a word?</em> — and it is the wrong way to build one that answers <em>would a person recognise this?</em></p>

      <p>What comes along for the ride is obsolete spellings, dialect forms, abbreviations that lost their full stops, proper nouns that leaked through lowercasing, and inflections of words nobody inflects. None of that is a bug in the list. The list is doing its job. The bug is ours, for asking it the wrong question.</p>

      <div class="pull"><p>A word game needs two dictionaries, not one. Most of them ship with one, and that is the whole problem.</p></div>

      <h2>Accepting and suggesting are not the same job</h2>

      <p>There are two moments where a word game consults a dictionary, and they want opposite things.</p>

      <ul>
        <li><strong>Validation</strong> — the player has found something and you decide whether it counts. Here you want to be <em>permissive</em>. A player who finds a real word and is told it isn't one will put your game down, and they will be right to.</li>
        <li><strong>Suggestion</strong> — you are proposing a word to the player, as a hint, a best play, or a solver result. Here you want to be <em>conservative</em>. A suggestion the player has never heard of doesn't read as erudition. It reads as the software being broken.</li>
      </ul>

      <p>Use one list for both and you have to pick a side. Pick permissive and your helper recommends REQUIZ. Pick conservative and you reject words your player legitimately knows. Neither is acceptable, and the whole argument disappears the moment you stop treating it as one list.</p>

      <h2>What we actually did</h2>

      <p>We kept the permissive list for validation, and built a second, smaller set for suggestion — not by hand-curating 104,562 words, but by borrowing a signal we already had.</p>

      <p>Wordmere ships definitions for the words it teaches, sourced from WordNet. A word having a real dictionary definition in our game data turns out to be a decent proxy for <em>a person would recognise this</em>. So we marked every word with a definition, plus plain inflections of those words, as common. That came to <strong>29,355 of 104,562 — about 28%</strong>.</p>

      <p>In the shipped tools, common words sort first and rare ones are still shown, greyed and labelled. The Scrabble finder's recommended best play is drawn only from the common set. REQUIZ is still there if you go looking. It is no longer what we tell you to do.</p>

      <h2>The part where we tell you it isn't perfect</h2>

      <p>NASTIER and QUIRES land in the rare bucket. They are perfectly good words. The proxy has false negatives, and we shipped it anyway, because the two failure modes are not equally bad:</p>

      <ul>
        <li>A real word shown in grey, slightly lower down the page. The player shrugs.</li>
        <li>A confident recommendation of a word that does not exist in any usable sense. The player stops believing anything the tool says.</li>
      </ul>

      <p>The honest fix is a tournament word list — TWL or Collins — which is maintained precisely to answer "is this playable". Those are licensed, which is why a free tool on the open web generally isn't using one, including ours. If you are building something commercial, licensing one is the move. If you are not, a definitions source is a surprisingly good stand-in.</p>

      <h2>The generalisable bit</h2>

      <p>None of this is really about word lists. It is about choosing your failure mode on purpose rather than inheriting whichever one your data source happened to have.</p>

      <p>Any time you ship a list — of words, of suggestions, of autocompletions, of anything a person will read as your recommendation — ask which direction you would rather be wrong in, and then ask whether your source was built with that same preference. Usually it wasn't. Usually nobody checked.</p>

      <div class="tryit">
        <p>Everything above is live. The tools run in your browser, there's nothing to sign up for, and the rare words are the ones in grey.</p>
        <a href="/tools/">Try the word tools</a>
      </div>

      <p class="endnote">We build <a href="/">Wordmere</a>, a cosy word game where the words you find assemble a small world around you. These posts are the things that went wrong on the way.</p>"""),
]

# ── build ────────────────────────────────────────────────────────────

MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']

def pretty(d):
    y, m, dd = d.split('-')
    return f'{int(dd)} {MONTHS[int(m) - 1]} {y}'

def shell(path, title, desc, schema, crumbs, body, ogtype='article'):
    page = TEMPLATE
    for k, v in {
        'TITLE': title, 'DESC': desc, 'URL': SITE + path, 'OGTYPE': ogtype,
        'SCHEMA': json.dumps(schema, ensure_ascii=False), 'STYLE': STYLE, 'BLOGCSS': BLOG_CSS,
        'NAV': NAV, 'FOOT': FOOT, 'CRUMBS': crumbs, 'BODY': body,
    }.items():
        page = page.replace('{{' + k + '}}', v)
    assert '{{' not in page, re.findall(r'\{\{\w+\}\}', page)
    out = os.path.join(ROOT, path.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(page)
    return len(page)

def build_post(p):
    path = f"/blog/{p['slug']}/"
    schema = {"@context": "https://schema.org", "@graph": [
      {"@type": "BlogPosting", "headline": p['title'], "description": p['desc'],
       "url": SITE + path, "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + path},
       "datePublished": p['date'], "dateModified": p.get('updated', p['date']),
       "author": {"@type": "Organization", "name": "Wordmere", "url": SITE + '/'},
       "publisher": {"@type": "Organization", "name": "Wordmere", "url": SITE + '/'},
       "image": SITE + '/img/social-card.jpg', "inLanguage": "en"},
      {"@type": "BreadcrumbList", "itemListElement": [
       {"@type": "ListItem", "position": 1, "name": "Wordmere", "item": SITE + '/'},
       {"@type": "ListItem", "position": 2, "name": "Notes", "item": SITE + '/blog/'},
       {"@type": "ListItem", "position": 3, "name": p['title'], "item": SITE + path}]}]}
    crumbs = f'<a href="/">Wordmere</a> › <a href="/blog/">Notes</a> › <span aria-current="page">{p["title"]}</span>'
    body = (f'    <article class="post">\n'
            f'      <h1>{p["h1"]}</h1>\n'
            f'      <p class="sub">{p["sub"]}</p>\n'
            f'      <p class="meta"><time datetime="{p["date"]}">{pretty(p["date"])}</time> · {AUTHOR}</p>\n'
            f'      <div class="article">{p["body"]}\n      </div>\n'
            f'    </article>')
    return shell(path, p['title'] + ' — Wordmere', p['desc'], schema, crumbs, body)

def build_index():
    desc = ('Notes from building Wordmere: word lists, puzzle generators, retention, and the bugs '
            'that only show up once real people are playing.')
    schema = {"@context": "https://schema.org", "@graph": [
      {"@type": "Blog", "name": "Wordmere Notes", "url": SITE + '/blog/', "description": desc,
       "publisher": {"@type": "Organization", "name": "Wordmere", "url": SITE + '/'},
       "blogPost": [{"@type": "BlogPosting", "headline": p['title'], "url": f"{SITE}/blog/{p['slug']}/",
                     "datePublished": p['date'], "description": p['desc']} for p in POSTS]},
      {"@type": "BreadcrumbList", "itemListElement": [
       {"@type": "ListItem", "position": 1, "name": "Wordmere", "item": SITE + '/'},
       {"@type": "ListItem", "position": 2, "name": "Notes", "item": SITE + '/blog/'}]}]}
    cards = '\n'.join(
      f'      <a class="postcard" href="/blog/{p["slug"]}/">\n'
      f'        <h2>{p["title"]}</h2>\n'
      f'        <p>{p["sub"]}</p>\n'
      f'        <span class="when"><time datetime="{p["date"]}">{pretty(p["date"])}</time></span>\n'
      f'      </a>' for p in POSTS)
    body = f"""    <h1>Notes</h1>
    <p class="sub">What we learned building a word game, written down properly. Word lists, puzzle
      generators, retention, and the bugs that only show up once real people are playing.</p>

    <div class="postlist">
{cards}
    </div>

    <div class="upnext">
      <h2>What else is coming</h2>
      <p>The bug that makes word search generators print wrong answer keys. The two rules that stop a
        crossword turning into a letter jumble. And what the retention data actually says about why
        players stop — which is not what we assumed.</p>
      <p>In the meantime, the <a href="/tools/">word tools</a> are free and the
        <a href="/">game</a> is the thing all of this is in aid of.</p>
    </div>"""
    crumbs = '<a href="/">Wordmere</a> › <span aria-current="page">Notes</span>'
    return shell('/blog/', 'Notes — Building a Word Game | Wordmere', desc, schema, crumbs, body, ogtype='website')


def assert_no_class_collisions():
    """The home page's CSS is inlined into every blog page, so any class we
    define that index.html also defines gets silently restyled — .soon is a
    pill badge there and turned a whole section into uppercase chips. Compare
    the selectors we DEFINE against the ones it defines, and fail the build.
    Chrome we deliberately re-skin is allowlisted."""
    css = home[home.index('<style>'):home.index('</style>')]
    theirs = set(re.findall(r'\.([a-zA-Z][\w-]*)', css))
    ours = set(re.findall(r'\.([a-zA-Z][\w-]*)', BLOG_CSS))
    # The nav and footer markup is lifted from the other pages and is meant
    # to take the home page's styling; we only adjust it.
    allowed = {'navbar', 'navstatic', 'fh', 'sitefoot', 'footcols', 'brand', 'top'}
    clash = sorted(ours & theirs - allowed)
    assert not clash, ('blog CSS redefines classes index.html already styles: '
                       + ', '.join('.' + c for c in clash))

if __name__ == '__main__':
    assert_no_class_collisions()
    print(f'  /blog/  {build_index() // 1024} KB')
    for p in POSTS:
        print(f"  /blog/{p['slug']}/  {build_post(p) // 1024} KB")
