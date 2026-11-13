#!/usr/bin/env python3
"""Generates every /tools/<slug>/index.html from one template.
Run from the repo root:  python3 build/tools.py
Nav, footer, styles and the shared engine (tools/wordkit.js) are common;
each tool supplies its form, its solver and its own explanatory copy."""
import re, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IOS = 'https://apps.apple.com/app/id6782536688'

home = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
STYLE = home[home.index('<style>'):home.index('</style>') + 8]
NAV = re.search(r'<nav class="nav navstatic">.*?</nav>', open(os.path.join(ROOT, 'tools/index.html'), encoding='utf-8').read(), re.S).group(0)
FOOT = re.search(r'<footer class="sitefoot">.*?</footer>', home, re.S).group(0)

TOOLS = [
  ('word-unscrambler',     'Word unscrambler',     'Every word from your letters'),
  ('anagram-solver',       'Anagram solver',       'Words that use every letter'),
  ('word-finder',          'Word finder',          'Search by pattern, start, end or length'),
  ('scrabble-word-finder', 'Scrabble word finder', 'Highest-scoring plays from your rack, blanks included'),
  ('words-with-letters',   'Words with letters',   'Words that contain the letters you choose'),
  ('five-letter-word-solver','Five-letter word solver','Narrow 5-letter words by what you know'),
  ('random-word-generator', 'Random word generator','Pick random words, any length'),
  ('word-scrambler',        'Word scramble maker',  'Jumble a word list into a puzzle, with an answer key'),
  ('word-search-maker',     'Word search maker',    'Build a printable word search from your own words'),
  ('crossword-maker',       'Crossword maker',      'Turn your words and clues into a printable crossword'),
  ('multi-word-anagram-solver','Multi-word anagram solver','Anagrams that take two or three words'),
  ('word-ladder-solver',    'Word ladder solver',   'The shortest chain from one word to another'),
  ('cryptogram-maker',      'Cryptogram maker',     'Turn a quote into a printable letter-swap puzzle'),
]

TOOL_CSS = """<style>
  .navstatic{position:static;}
  .navstatic .navbar{background:var(--white); border-color:rgba(14,58,80,.08);}
  .toolwrap{max-width:1080px; margin:0 auto; padding:clamp(24px,4vw,52px) var(--gutter) 56px;}
  .crumbs{font-size:13px; color:var(--ink-faint); margin:0 0 14px; font-weight:500;}
  .crumbs a{color:var(--ink-soft); text-decoration:underline; text-decoration-color:rgba(14,58,80,.35); text-underline-offset:3px; display:inline-block; padding:4px 0;}
  .toolwrap h1{font-family:var(--display); font-weight:800; font-size:clamp(30px,5.4vw,50px); letter-spacing:-.038em; line-height:1; margin:0; color:var(--ink); text-wrap:balance;}
  .toolwrap .sub{margin:12px 0 0; color:var(--ink-soft); font-size:clamp(15px,1.8vw,18px); max-width:52ch;}
  .panel{margin-top:26px; background:var(--white); border-radius:22px; padding:clamp(18px,3vw,28px); box-shadow:inset 0 0 0 1px rgba(14,58,80,.08), 0 8px 22px rgba(14,58,80,.08);}
  .field{display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end;}
  .field label{display:block; font:700 11px/1 var(--body); letter-spacing:.16em; text-transform:uppercase; color:var(--ink-faint); margin-bottom:8px;}
  .field .grow{flex:1 1 220px; min-width:0;}
  .field .mid{flex:1 1 150px; min-width:0;}
  input[type=text]{width:100%; font-family:var(--display); font-weight:800; font-size:clamp(19px,2.6vw,26px); letter-spacing:.12em; text-transform:uppercase; color:var(--ink); background:var(--page); border:2px solid transparent; border-radius:14px; padding:14px 16px; outline:none; box-shadow:inset 0 2px 5px rgba(14,58,80,.10);}
  input[type=text]::placeholder{color:#5E7E8C; letter-spacing:.02em; text-transform:none; font-weight:600; font-family:var(--body);}
  input[type=text]:focus{border-color:var(--tq); box-shadow:inset 0 2px 5px rgba(14,58,80,.10), 0 0 0 4px rgba(47,196,220,.22);}
  select{width:100%; font-family:var(--body); font-weight:600; font-size:15px; color:var(--ink); background:var(--page); border:2px solid transparent; border-radius:14px; padding:15px 14px; outline:none; box-shadow:inset 0 2px 5px rgba(14,58,80,.10);}
  select:focus{border-color:var(--tq); box-shadow:0 0 0 4px rgba(47,196,220,.22);}
  textarea{width:100%; font-family:var(--body); font-weight:600; font-size:16px; line-height:1.5; color:var(--ink);
    background:var(--page); border:2px solid transparent; border-radius:14px; padding:13px 15px; outline:none; resize:vertical;
    box-shadow:inset 0 2px 5px rgba(14,58,80,.10);}
  textarea::placeholder{color:#5E7E8C; font-weight:500;}
  textarea:focus{border-color:var(--tq); box-shadow:inset 0 2px 5px rgba(14,58,80,.10), 0 0 0 4px rgba(47,196,220,.22);}
  .pairs{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:10px; margin:0; padding:0; list-style:none;}
  .pair{display:flex; align-items:baseline; gap:10px; background:var(--white); border-radius:12px; padding:11px 14px;
    box-shadow:inset 0 0 0 1px rgba(14,58,80,.10);}
  .pair b{font-family:var(--display); font-weight:800; font-size:17px; letter-spacing:.14em; color:var(--ink);}
  .pair span{margin-left:auto; font-size:13px; color:#3E6270; font-weight:600;}
  .solve{font-family:var(--display); font-weight:800; font-size:17px; color:#06323A; border:0; border-radius:14px; padding:16px 30px; cursor:pointer; background:linear-gradient(180deg,#5AD9EC,var(--tq)); box-shadow:inset 0 2px 0 rgba(255,255,255,.45), 0 5px 0 var(--tq-deep);}
  .solve:disabled{opacity:.55; cursor:progress;}
  .hint{margin:12px 0 0; color:var(--ink-faint); font-size:13.5px;}
  .err{margin:12px 0 0; color:#B23624; font-size:14px; font-weight:600;}
  .status{margin:14px 0 0; color:var(--ink-faint); font-size:14px; font-weight:500;}
  #out{min-height:520px;}
  .best{margin-top:22px; display:flex; flex-wrap:wrap; align-items:center; gap:12px; background:linear-gradient(120deg,#FFF3DC,#FFFBF2); border-radius:16px; padding:16px 18px; box-shadow:inset 0 0 0 1px rgba(192,106,18,.25);}
  .best b{font-family:var(--display); font-weight:800; font-size:22px; letter-spacing:.06em; color:#5A2D00;}
  .best span{color:#6B4A1F; font-size:14px; font-weight:600;}
  .group{margin-top:26px;}
  .group h2{font-family:var(--display); font-weight:800; font-size:19px; letter-spacing:-.02em; margin:0 0 12px; color:var(--ink);}
  .group h2 span{color:var(--ink-faint); font-weight:600; font-size:14px; font-family:var(--body); letter-spacing:0;}
  .words{display:flex; flex-wrap:wrap; gap:8px; margin:0; padding:0; list-style:none;}
  .words li{font-family:var(--display); font-weight:800; font-size:15px; letter-spacing:.04em; color:var(--ink); background:var(--white); padding:9px 13px; border-radius:10px; box-shadow:inset 0 0 0 1px rgba(14,58,80,.10);}
  .words li em{font-style:normal; font-family:var(--body); font-weight:700; font-size:11px; letter-spacing:0; color:#0C6E92; margin-left:7px; vertical-align:2px;}
  .words li.top{background:linear-gradient(176deg,#FFC066,#EE9932 62%,#DE8117); color:#4A2200; box-shadow:inset 0 1px 0 rgba(255,255,255,.5), 0 3px 0 var(--sun-deep);}
  .words li.top em{color:#4A2200;}
  .words li.rare{color:#3E6270; background:var(--page); box-shadow:inset 0 0 0 1px rgba(14,58,80,.07); font-weight:700;}
  .words li.top.rare{background:linear-gradient(176deg,#FFE3B8,#FAD29A); color:#5A3300; box-shadow:inset 0 0 0 1px rgba(192,106,18,.25);}
  .more{margin:10px 0 0; color:var(--ink-faint); font-size:13.5px;}
  .prose{margin-top:46px; max-width:var(--measure);}
  .prose h2{font-family:var(--display); font-weight:800; font-size:clamp(21px,3vw,28px); letter-spacing:-.028em; margin:30px 0 10px; color:var(--ink);}
  .prose p{margin:0 0 14px; color:var(--ink-read); font-size:16px; line-height:1.68;}
  .prose a{color:#0C6E92; font-weight:600; text-decoration:underline; text-underline-offset:3px;}
  .prose code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:14px; background:var(--mist); color:var(--ink); padding:2px 6px; border-radius:6px;}
  .tm{margin-top:18px; font-size:13px; color:var(--ink-faint);}
  .related{margin-top:40px; display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px;}
  .prose a.rel,.rel{display:block; text-decoration:none; color:inherit; background:var(--white); border-radius:16px; padding:18px 20px; box-shadow:inset 0 0 0 1px rgba(14,58,80,.08), 0 4px 12px rgba(14,58,80,.06);}
  .rel b{display:block; font-family:var(--display); font-weight:800; font-size:16px; color:var(--ink); letter-spacing:-.015em;}
  .rel span{display:block; margin-top:4px; font-size:13.5px; color:var(--ink-soft);}
  .prose a.backhome,.backhome{display:inline-flex; margin-top:30px; font-family:var(--display); font-weight:800; font-size:15px; color:#fff; text-decoration:none; background:linear-gradient(180deg,#D64A28,#BE3F22); border-radius:999px; padding:14px 26px; box-shadow:0 4px 0 #9E3319;}
  @media (min-width:900px){ .field{flex-wrap:nowrap;} .words li{font-size:16px; padding:10px 15px;} .group h2{font-size:21px;} }
  @media (max-width:600px){
    #out{min-height:760px;}
    .field{gap:12px;} .field .grow,.field .mid,.field > div{flex:1 1 100%;}
    .solve{width:100%;}
    input[type=text]{font-size:21px; letter-spacing:.09em; padding:13px 14px;}
    .panel{border-radius:18px; padding:16px;}
    .toolwrap h1{font-size:clamp(28px,8.4vw,38px);}
    .words li{font-size:14px; padding:8px 11px;} .group h2{font-size:17px;} .prose h2{font-size:20px;}
    .backhome{width:100%; justify-content:center;}
  }
</style>"""

LEN = '<div><label for="len">Length</label><select id="len" name="len"><option value="0">Any</option><option>3</option><option>4</option><option>5</option><option>6</option><option>7</option><option>8</option></select></div>'
def inp(i, label, val='', ph='', mx=12):
    return (f'<div class="grow"><label for="{i}">{label}</label><input type="text" id="{i}" name="{i}" value="{val}" '
            f'placeholder="{ph}" maxlength="{mx}" autocomplete="off" autocapitalize="characters" spellcheck="false" aria-describedby="err"></div>')
def mid(i, label, val='', ph='', mx=8):
    return inp(i, label, val, ph, mx).replace('class="grow"', 'class="mid"')

def ta(i, label, val='', ph='', rows=4):
    return (f'<div class="grow"><label for="{i}">{label}</label><textarea id="{i}" name="{i}" rows="{rows}" '
            f'placeholder="{ph}" spellcheck="false" aria-describedby="err">{val}</textarea></div>')

def tinp(i, label, val='', ph='', mx=48, cls='grow'):
    """A plain sentence-case text field — the uppercase letter-tile styling
    that suits a rack of letters is wrong for a puzzle title."""
    return (f'<div class="{cls} plain"><label for="{i}">{label}</label><input type="text" id="{i}" name="{i}" '
            f'value="{val}" placeholder="{ph}" maxlength="{mx}" autocomplete="off" aria-describedby="err"></div>')

def wide(block):
    """Force a control onto its own full-width row inside .field."""
    return block.replace('class="grow"', 'class="wide"', 1)

def sel(i, label, options, width='mid'):
    opts = ''.join(f'<option value="{v}"{" selected" if s else ""}>{t}</option>' for v, t, s in options)
    return f'<div class="{width}"><label for="{i}">{label}</label><select id="{i}" name="{i}">{opts}</select></div>'

SPEC = {}

SPEC['word-unscrambler'] = dict(
 cta='Unscramble',
 title='Word Unscrambler — Every Word From Your Letters',
 desc='Free word unscrambler. Enter your letters and get every word you can make from them, sorted by length. 104,562 words, works on any word game, no sign-up.',
 sub="Put in the letters you're holding. You'll get back every word they can make, longest first. Works for any word game, not just ours.",
 form=inp('letters','Your letters','STONE','e.g. STONE') + LEN,
 js=r"""
  var raw=WK.clean(val('letters'));
  if(!raw) return fail('Enter some letters first.');
  if(raw.length<3) return fail('Enter at least three letters.');
  setv('letters',raw);
  var have=WK.counts(raw), L=+val('len')||0, hits=[];
  for(var n=Math.min(8,raw.length); n>=3; n--){ if(L&&n!==L) continue; (WK.byLen[n]||[]).forEach(function(w){ if(WK.makeable(w,have,0)) hits.push({w:w, top:n>=Math.min(raw.length,7)}); }); }
  done(hits, hits.length+' words from '+raw);""",
 prose="""
      <h2>How it works</h2>
      <p>Type up to twelve letters and the tool checks them against 104,562 English words between three and eight letters long. A word only appears if your letters can actually spell it — each letter is used no more times than you have it. Results are grouped by length, because in most word games the long ones are worth the most.</p>
      <h2>Using it on a letter-wheel puzzle</h2>
      <p>Enter every letter on the wheel, repeats included. Set the length to the number of blanks in the row you're stuck on and the answer usually jumps out. If you're playing <a href="/">Wordmere</a>, a hint reveals a letter for free.</p>
      <h2>Unscrambler or anagram solver?</h2>
      <p>The unscrambler finds words that use <em>some</em> of your letters. If you need a word that uses <em>every</em> letter exactly once, the <a href="/tools/anagram-solver/">anagram solver</a> is the one you want.</p>""")

SPEC['anagram-solver'] = dict(
 cta='Solve',
 title='Anagram Solver — Words That Use Every Letter',
 desc='Free anagram solver. Enter a word or a set of letters and find every English word that uses all of them exactly once, plus the words one letter shorter.',
 sub='Type a word or a jumble of letters. You get every word that uses all of them exactly once — a true anagram — and the words that are one letter short.',
 form=inp('letters','Letters or word','LISTEN','e.g. LISTEN', 8),
 js=r"""
  var raw=WK.clean(val('letters'));
  if(!raw) return fail('Enter a word or some letters first.');
  if(raw.length<3) return fail('Enter at least three letters.');
  if(raw.length>8) return fail('Anagrams are checked up to eight letters.');
  setv('letters',raw);
  var key=raw.split('').sort().join(''), have=WK.counts(raw), exact=[], near=[];
  (WK.byLen[raw.length]||[]).forEach(function(w){ if(w.split('').sort().join('')===key) exact.push({w:w, top:true}); });
  (WK.byLen[raw.length-1]||[]).forEach(function(w){ if(WK.makeable(w,have,0)) near.push({w:w}); });
  var html='';
  html += exact.length ? '<div class="group"><h2>Exact anagrams <span>'+exact.length+'</span></h2><ul class="words">'+exact.map(function(x){return '<li class="top'+(WK.isCommon(x.w)?'':' rare')+'">'+x.w+'</li>';}).join('')+'</ul></div>'
                       : '<p class="status">No word uses all of '+raw+'.</p>';
  if(near.length) html += '<div class="group"><h2>One letter shorter <span>'+near.length+'</span></h2><ul class="words">'+near.map(function(x){return '<li'+(WK.isCommon(x.w)?'':' class="rare"')+'>'+x.w+'</li>';}).join('')+'</ul></div>';
  out(html, exact.length+' exact anagram'+(exact.length===1?'':'s')+' of '+raw);""",
 prose="""
      <h2>What counts as an anagram</h2>
      <p>An anagram rearranges every letter of the original exactly once — nothing added, nothing left over. <code>LISTEN</code> becomes <code>SILENT</code>, <code>ENLIST</code> and <code>TINSEL</code>. The tool sorts the letters of your word and finds every dictionary word with the same sorted letters, which is why it's instant.</p>
      <h2>Why it also shows words one letter shorter</h2>
      <p>Plenty of letter sets have no perfect anagram at all. The second group shows words that use all but one of your letters — often the answer when a puzzle has one letter that doesn't belong, or when you've mistyped.</p>
      <h2>Crosswords and cryptic clues</h2>
      <p>Anagram clues are a staple of cryptic crosswords, flagged by words like "mixed", "broken" or "confused". Enter the letters the clue gives you here. For puzzles where you know some letters' positions, use the <a href="/tools/word-finder/">word finder</a> instead.</p>""")

SPEC['word-finder'] = dict(
 title='Word Finder — Search Words by Pattern, Start, End or Length',
 desc='Free word finder. Search English words by pattern with wildcards, by the letters they start or end with, by letters they contain, or by length.',
 sub='Know part of a word? Search by pattern with wildcards, by how it starts or ends, by letters it must contain, or by length — or any mix of them.',
 form=mid('pattern','Pattern','','e.g. C?T or S__RE') + mid('starts','Starts with','ST','e.g. ST',6) + mid('ends','Ends with','','e.g. ING',6) + mid('has','Contains','','e.g. Q',6) + LEN,
 hint='Use <code>?</code> or <code>_</code> for any single letter in a pattern. Leave fields empty to ignore them.',
 js=r"""
  var pat=(val('pattern')||'').toUpperCase().replace(/_/g,'?').replace(/[^A-Z?]/g,''),
      st=WK.clean(val('starts')), en=WK.clean(val('ends')), has=WK.clean(val('has')), L=+val('len')||0;
  setv('pattern',pat); setv('starts',st); setv('ends',en); setv('has',has);
  if(!pat&&!st&&!en&&!has&&!L) return fail('Fill in at least one search field.');
  if(pat && L && pat.length!==L) return fail('The pattern is '+pat.length+' letters but the length is set to '+L+'.');
  var re = pat ? new RegExp('^'+pat.replace(/\?/g,'.')+'$') : null, need=WK.counts(has), hits=[];
  var lens = pat ? [pat.length] : (L ? [L] : [8,7,6,5,4,3]);
  lens.forEach(function(n){ (WK.byLen[n]||[]).forEach(function(w){
    if(re && !re.test(w)) return; if(st && w.indexOf(st)!==0) return;
    if(en && w.slice(-en.length)!==en) return;
    if(has){ var c=WK.counts(w); for(var k in need) if((c[k]||0)<need[k]) return; }
    hits.push({w:w});
  }); });
  var shown=hits, extra='';
  if(hits.length>1500){ shown=hits.slice(0,1500); extra='<p class="more">Showing the first 1,500 of '+hits.length.toLocaleString()+' matches. Narrow the search to see the rest.</p>'; }
  out(WK.group(shown)+extra, hits.length.toLocaleString()+' matching word'+(hits.length===1?'':'s'));""",
 prose="""
      <h2>Searching by pattern</h2>
      <p>Type the letters you know in their positions and a <code>?</code> or <code>_</code> for each one you don't. <code>C?T</code> finds CAT, COT and CUT; <code>S__RE</code> finds SHARE, SNORE and STORE. The pattern also fixes the length, so there's no need to set it separately.</p>
      <h2>Starts with, ends with, contains</h2>
      <p>Use these on their own or together. <code>ST</code> in "Starts with" and <code>ING</code> in "Ends with" gives you every word shaped like STING or STRING. "Contains" respects repeats — <code>EE</code> only matches words with at least two E's.</p>
      <h2>Lists like "5-letter words starting with S"</h2>
      <p>Set the length to 5 and put S in "Starts with". It works the same way for any length from three to eight letters and any starting or ending letters. For words built only from letters you're holding, use the <a href="/tools/word-unscrambler/">word unscrambler</a>.</p>""")

SPEC['scrabble-word-finder'] = dict(
 cta='Find plays',
 title='Scrabble Word Finder With Blanks — Best Plays Ranked',
 desc='Free Scrabble word finder. Enter your rack, including blank tiles, and see every playable word ranked by score, with letters on the board included.',
 sub='Enter the tiles on your rack — use ? for a blank. Add a letter from the board if you want to build through it. Every word comes back ranked by score.',
 form=inp('rack','Your rack','QUIZERS','e.g. RETAINS or AE?RT',7) + mid('board','Letter on board','','optional',3) + LEN,
 hint='Use <code>?</code> for a blank tile (up to two). Blanks score zero. Standard letter values; board premium squares aren\'t included.',
 js=r"""
  var rackRaw=(val('rack')||'').toUpperCase().replace(/[^A-Z?]/g,''), board=WK.clean(val('board')), L=+val('len')||0;
  setv('rack',rackRaw); setv('board',board);
  if(!rackRaw) return fail('Enter the tiles on your rack.');
  var blanks=(rackRaw.match(/\?/g)||[]).length, rack=rackRaw.replace(/\?/g,'');
  if(blanks>2) return fail('A standard set has only two blank tiles.');
  if(rackRaw.length>7) return fail('A rack holds seven tiles.');
  if(rack.length+blanks+board.length<2) return fail('Enter at least two tiles.');
  var pool=rack+board, have=WK.counts(pool), hits=[], bNeed=WK.counts(board), maxL=Math.min(8, rackRaw.length+board.length);
  for(var n=maxL; n>=2; n--){ if(L&&n!==L) continue; (WK.byLen[n]||[]).forEach(function(w){
    if(!WK.makeable(w,have,blanks)) return;
    if(board){ var c=WK.counts(w); for(var k in bNeed) if((c[k]||0)<bNeed[k]) return; }
    var s=WK.score(w,have), bingo=(w.length-board.length)>=7;
    hits.push({w:w, s:s+(bingo?50:0), bingo:bingo});
  }); }
  hits.sort(function(a,b){ return b.s-a.s || b.w.length-a.w.length; });
  var common=hits.filter(function(h){ return WK.isCommon(h.w); }), top=common[0]||hits[0], html='';
  if(top) html+='<div class="best"><b>'+top.w+'</b><span>Best play: '+top.s+' points'+(top.bingo?' including the 50-point bonus for using all seven tiles':'')+'</span></div>';
  if(hits.length && common.length<hits.length) html+='<p class="hint">Lighter words are less common. They\'re in our dictionary but may not be accepted by an official word list.</p>';
  common.slice(0,10).forEach(function(h){ h.top=true; });
  html+=WK.group(hits);
  out(html, hits.length.toLocaleString()+' playable word'+(hits.length===1?'':'s')+' from '+rackRaw+(board?' + '+board:''));""",
 prose="""
      <h2>How the scores are worked out</h2>
      <p>Each word is scored with the standard tile values — E and A are 1, K is 5, J and X are 8, Q and Z are 10. A blank tile can stand for any letter but scores nothing, and the tool always uses your real tiles first so the score shown is the best you can get. Premium squares depend on where you play, so they aren't added.</p>
      <h2>Bingos</h2>
      <p>Playing all seven tiles from your rack in one turn earns a 50-point bonus, and it's included in the score here. Seven-letter words using common letters like <code>RETAINS</code> are worth learning for exactly this reason.</p>
      <h2>Building through a letter on the board</h2>
      <p>Put a letter that's already on the board in the second box and every result will include it. To see every word from your letters regardless of score, the <a href="/tools/word-unscrambler/">word unscrambler</a> lists them by length.</p>""",
 tm='Scrabble® is a registered trademark of Hasbro, Inc. in the USA and Canada, and of J.W. Spear &amp; Sons Limited, a Mattel company, elsewhere. Wordmere is not affiliated with or endorsed by either. Word validity here follows the Wordmere dictionary, not an official tournament word list.')

SPEC['words-with-letters'] = dict(
 title='Words With Letters — Find Words Containing Your Letters',
 desc='Free tool to find words containing the letters you choose, in any position and any order. Search words with Q and Z, words with two Es, and more.',
 sub='Choose the letters a word has to include. You get every word that contains all of them, in any order and any position — and it can have other letters too.',
 form=inp('has','Letters it must contain','QZ','e.g. QZ or XYZ',8) + LEN,
 js=r"""
  var has=WK.clean(val('has')), L=+val('len')||0;
  if(!has) return fail('Enter at least one letter.');
  setv('has',has);
  var need=WK.counts(has), hits=[];
  for(var n=8;n>=3;n--){ if(L&&n!==L) continue; if(n<has.length) continue; (WK.byLen[n]||[]).forEach(function(w){ var c=WK.counts(w); for(var k in need) if((c[k]||0)<need[k]) return; hits.push({w:w}); }); }
  var shown=hits, extra='';
  if(hits.length>1500){ shown=hits.slice(0,1500); extra='<p class="more">Showing the first 1,500 of '+hits.length.toLocaleString()+'. Add a letter or pick a length to narrow it.</p>'; }
  out(WK.group(shown)+extra, hits.length.toLocaleString()+' word'+(hits.length===1?'':'s')+' containing '+has.split('').join(', '));""",
 prose="""
      <h2>How this is different from an unscrambler</h2>
      <p>An unscrambler only uses the letters you give it. This does the opposite: the letters you enter are a minimum, and a word can have any other letters around them. <code>QZ</code> finds QUIZ and QUARTZ; <code>XYZ</code> finds every word that has an X, a Y and a Z somewhere in it.</p>
      <h2>Repeated letters</h2>
      <p>Enter a letter twice to require it twice. <code>EE</code> matches words like FREEZE and KEEPER but not TREND. It works for any letter, so <code>SS</code> or <code>OO</code> behave the same way.</p>
      <h2>Awkward letters</h2>
      <p>Stuck holding a Q, a J or an X? Put it here, set the length you have room for, and pick from what comes back. If you also know where in the word a letter sits, the <a href="/tools/word-finder/">word finder</a> takes a pattern.</p>""")


SPEC['five-letter-word-solver'] = dict(
 cta='Narrow it down',
 title='Five-Letter Word Solver — Narrow Down the Answer',
 desc='Free five-letter word solver for daily letter puzzles. Enter the letters you have placed, the ones in the word but misplaced, and the ones ruled out.',
 sub='For daily five-letter puzzles. Put the letters you have placed in their slots, the letters you know are in the word somewhere, and the letters you have ruled out.',
 form=(mid('greens','Placed letters','?????','?????',5)
       + mid('yellows','In the word, wrong spot','','e.g. AR',5)
       + mid('greys','Ruled out','','e.g. SLNT',15)),
 hint='In <b>Placed letters</b>, type the word with <code>?</code> for each slot you have not solved — <code>C?A?E</code>. Leave the other boxes empty until you know something.',
 js=r"""
  var g=(val('greens')||'').toUpperCase().replace(/[^A-Z?]/g,'').slice(0,5),
      y=WK.clean(val('yellows')), x=WK.clean(val('greys'));
  if(!g) g='?????';
  while(g.length<5) g+='?';
  setv('greens',g); setv('yellows',y); setv('greys',x);
  var placed=g.replace(/\?/g,'');
  for(var i=0;i<y.length;i++) if(x.indexOf(y[i])>-1) return fail(y[i]+' is in both "in the word" and "ruled out" — it can only be one.');
  for(var i=0;i<placed.length;i++) if(x.indexOf(placed[i])>-1) return fail(placed[i]+' is placed but also ruled out — it can only be one.');
  var re=new RegExp('^'+g.replace(/\?/g,'.')+'$'), hits=[];
  (WK.byLen[5]||[]).forEach(function(w){
    if(!re.test(w)) return;
    for(var i=0;i<y.length;i++){ if(w.indexOf(y[i])<0) return; }
    for(var i=0;i<x.length;i++){ if(w.indexOf(x[i])>-1) return; }
    hits.push({w:w});
  });
  var known=(placed?placed.length+' placed':'')+(y?(placed?', ':'')+y.length+' misplaced':'')+(x?((placed||y)?', ':'')+x.length+' ruled out':'');
  done(hits, hits.length.toLocaleString()+' possible word'+(hits.length===1?'':'s')+(known?' \u2014 '+known:''));""",
 prose="""
      <h2>How to narrow it down</h2>
      <p>Most daily five-letter puzzles tell you three things after each guess: letters in the right slot, letters in the word but in the wrong slot, and letters not in the word at all. Put each kind in its own box here and the list shrinks fast. Common words are listed first, which usually matters — daily puzzles rarely pick obscure answers.</p>
      <h2>A worked example</h2>
      <p>Say you opened with <code>CRANE</code> and got the C and E in place, the R somewhere else, and A and N ruled out. Enter <code>C???E</code> in placed letters, <code>R</code> in the second box and <code>AN</code> in the third. What's left is a short list you can read at a glance.</p>
      <h2>If nothing comes back</h2>
      <p>Check you haven't put the same letter in two boxes — the tool will tell you if you have. A letter can be placed, misplaced or ruled out, never two at once. Note also that a letter appearing twice in the puzzle behaves differently in different games, so treat the ruled-out box with care when you have a repeat. For other lengths, use the <a href="/tools/word-finder/">word finder</a>.</p>""")

SPEC['random-word-generator'] = dict(
 cta='Generate',
 title='Random Word Generator — Any Length, Common or Obscure',
 desc='Free random word generator. Pick how many words you want and how long they should be, from a dictionary of 104,562 English words. No sign-up.',
 sub='Random English words, as many as you need. Useful for games, writing prompts, passwords you can actually say out loud, or naming things.',
 form=(sel('count','How many',[('1','1',False),('5','5',True),('10','10',False),('25','25',False),('50','50',False),('100','100',False)])
       + LEN
       + sel('pool','Word type',[('common','Defined words',True),('all','All words, incl. obscure',False)])
       + mid('starts','Starts with','','optional',4)),
 js=r"""
  var n=+val('count')||5, L=+val('len')||0, pool=val('pool'), st=WK.clean(val('starts'));
  setv('starts',st);
  var source=[];
  (L?[L]:[3,4,5,6,7,8]).forEach(function(k){ (WK.byLen[k]||[]).forEach(function(w){
    if(pool==='common' && !WK.isCommon(w)) return;
    if(st && w.indexOf(st)!==0) return;
    source.push(w); }); });
  if(!source.length) return fail('Nothing matches that. Try "include rare words", a different length, or fewer starting letters.');
  var picked=[], used={};
  for(var i=0; i<n*40 && picked.length<Math.min(n,source.length); i++){
    var w=source[(Math.random()*source.length)|0];
    if(used[w]) continue; used[w]=1; picked.push({w:w, top:true});
  }
  out('<div class="group"><h2>Your words <span>'+picked.length+'</span></h2><ul class="words">'
      + picked.map(function(p){ return '<li class="top'+(WK.isCommon(p.w)?'':' rare')+'">'+p.w+'</li>'; }).join('')
      + '</ul></div>',
      picked.length+' of '+source.length.toLocaleString()+' matching words — press Search again for a new set');""",
 prose="""
      <h2>Everyday words or the whole dictionary</h2>
      <p>"Defined words" draws from the 29,355 that carry a real dictionary definition — the ones a person can read aloud without blinking. It is not a hand-picked list, so the odd proper noun or technical term slips through. "All words" opens up the full 104,562, including the obscure corners that only exist in word-game dictionaries.</p>
      <h2>What people use it for</h2>
      <p>Party games where everyone needs a word to act out or draw. Writing prompts when a blank page is winning. Picking a name for a project. Building a passphrase out of several short words, which is easier to remember and harder to guess than a mangled single word.</p>
      <h2>Press again for a fresh set</h2>
      <p>Every press gives a new selection, and no word repeats within one set. If you want words that fit a shape rather than random ones, the <a href="/tools/word-finder/">word finder</a> searches by pattern, and the <a href="/tools/word-unscrambler/">unscrambler</a> works from letters you already hold.</p>""")

SCRAMBLE_CSS = """<style>
  /* The scramble maker produces two things: a worksheet with blanks to write
     on, and the answer key. They must print on separate sheets.
     #out reserves space so the first render does not shift the page: enough
     for a short list, far less than the 620px the grid makers need. */
  #out{min-height:320px;}
  @media (max-width:600px){ #out{min-height:420px;} }
  .pzbar{display:flex; flex-wrap:wrap; align-items:center; gap:12px; margin-top:22px;}
  .ghost{font-family:var(--display); font-weight:800; font-size:15px; color:#0A4A63; background:var(--page);
    border:0; border-radius:12px; padding:13px 20px; cursor:pointer; box-shadow:inset 0 0 0 2px rgba(14,58,80,.18);}
  .ghost:hover{box-shadow:inset 0 0 0 2px var(--tq);}
  .pznote{font-size:13.5px; color:var(--ink-faint); font-weight:600;}
  .pzsec{margin-top:24px;}
  .pzhead{font-family:var(--display); font-weight:800; font-size:clamp(19px,3vw,25px); letter-spacing:-.02em;
    margin:0 0 14px; color:var(--ink); text-wrap:balance;}
  .plain input[type=text]{font-family:var(--body); font-weight:600; font-size:16px; letter-spacing:.01em; text-transform:none;}
  .plain input[type=text]::placeholder{font-weight:500;}
  .field .wide{flex:1 1 100%; min-width:0;}
  .scrw{list-style:none; margin:0; padding:0; display:grid; gap:11px;}
  .scrw li{display:flex; align-items:baseline; gap:14px; background:var(--white); border-radius:12px;
    padding:12px 15px; box-shadow:inset 0 0 0 1px rgba(14,58,80,.10);}
  .scrw b{font-family:var(--display); font-weight:800; font-size:17px; letter-spacing:.14em; color:var(--ink); flex:0 0 auto;}
  .scrw i{flex:1 1 auto; border-bottom:1.5px dotted rgba(14,58,80,.38); min-height:1.1em;}
  .scrw em{font-style:normal; margin-left:auto; font-size:13px; color:var(--ink-faint); font-weight:600;}
  @media print{
    @page{margin:16mm;}
    body{background:#fff; color:#000;}
    .nav,.sitefoot,.crumbs,.prose,form,.pzbar,.toolwrap h1,.toolwrap .sub{display:none !important;}
    .toolwrap{max-width:none; padding:0;}
    .panel{background:#fff; box-shadow:none; border-radius:0; padding:0;}
    .pzhead{color:#000;}
    .scrw li{background:none; box-shadow:none; padding:6px 0; border-bottom:1px solid #ddd; border-radius:0;}
    .scrw b,.scrw em{color:#000;}
    .scrw i{border-bottom-color:#999;}
    .pzsec{break-inside:avoid;}
    .keysec{break-before:page;}
  }
</style>"""

SPEC['word-scrambler'] = dict(
 cta='Scramble',
 needs_dict=False,
 extra_css=SCRAMBLE_CSS,
 title='Word Scramble Maker — Free Jumbled Word Generator',
 desc='Free word scramble maker. Paste any word list and get a printable worksheet of jumbled words with lines to write on, and the answer key on its own sheet.',
 sub='Paste your words, one per line or separated by commas. You get a printable worksheet of jumbles with a line to write on, and the answer key on a separate sheet.',
 form=wide(ta('words','Your words','ORANGE\nMEADOW\nLIGHTHOUSE\nPUZZLE','One word per line, or separated by commas'))
      + tinp('title','Worksheet title (optional)','','e.g. Friday spellings', 48, 'mid'),
 hint='Letters only. Anything under three letters is left alone — there is nothing to scramble.',
 js=r"""
  var raw=(val('words')||'').toUpperCase().split(/[^A-Z]+/).filter(function(w){ return w.length>0; });
  if(!raw.length) return fail('Paste at least one word.');
  if(raw.length>200) return fail('That is more than 200 words — trim the list a little.');
  var title=(val('title')||'').trim();
  var short=raw.filter(function(w){ return w.length<3; });

  /* A jumble that comes back as the original word is not a puzzle, and for a
     two-letter word there is only one other arrangement, so those are left. */
  function scramble(w){
    var a=w.split(''), tries=0, best=w;
    while(tries++<40){
      for(var i=a.length-1;i>0;i--){ var j=(Math.random()*(i+1))|0, t=a[i]; a[i]=a[j]; a[j]=t; }
      best=a.join('');
      if(best!==w) return best;
    }
    return best;
  }
  var rows=raw.map(function(w){
    return w.length<3 ? {w:w, s:w, skip:true} : {w:w, s:scramble(w)};
  });

  function esc(x){ return String(x).replace(/[&<>"]/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  var sheet='<ol class="scrw">'+rows.map(function(r){
      return '<li><b>'+r.s+'</b><i></i>'+(r.skip?'<em>too short to scramble</em>':'')+'</li>'; }).join('')+'</ol>';
  var key='<ol class="scrw">'+rows.map(function(r){
      return '<li><b>'+r.s+'</b><em>'+r.w+'</em></li>'; }).join('')+'</ol>';

  var html='<div class="pzbar"><button type="button" class="ghost" data-print>Print or save as PDF</button>'
      +'<span class="pznote">'+rows.length+' word'+(rows.length===1?'':'s')
      +(short.length?' · '+short.length+' left alone':'')+'</span></div>'
    +'<section class="pzsec">'+(title?'<h2 class="pzhead">'+esc(title)+'</h2>':'<h2 class="pzhead">Unscramble the words</h2>')
      +sheet+'</section>'
    +'<section class="pzsec keysec"><h2 class="pzhead">Answer key'+(title?' — '+esc(title):'')+'</h2>'
      +key+'</section>';

  out(html, 'Press Scramble again for a different set of jumbles.');""",
 prose="""
      <h2>Making a worksheet</h2>
      <p>Paste a spelling list, a set of topic words or the names of everyone coming to a party. You get two sheets: the worksheet, which shows each word jumbled with a line to write the answer on, and the answer key, which pairs each jumble with the word it came from. Press <em>Print or save as PDF</em> and the key starts on a fresh page, so you can hand out the first sheet without the answers showing through.</p>
      <h2>What makes a scramble hard</h2>
      <p>Almost entirely length. Three and four-letter words are solved at a glance; seven letters and up are a real puzzle, because the number of arrangements grows faster than anyone's ability to check them. Repeated letters make a word easier, not harder — <code>LETTER</code> has far fewer distinct jumbles than a word with six different letters, so the eye lands on it sooner. If a list feels too easy, add length before you add words.</p>
      <h2>Every jumble is different</h2>
      <p>The letters are shuffled fresh each time and the tool will not hand back a "scramble" that is identical to the original. Press the button again if a particular jumble looks too generous — short words with repeated letters sometimes land close to the real thing. Words under three letters are left alone and marked, because there is nothing useful to do with them.</p>
      <h2>Jumble, letter scramble, word mix-up</h2>
      <p>The same worksheet goes by a few names. Teachers tend to say word scramble or spelling scramble; puzzle books call it a jumble, after the newspaper feature; children's activity sheets often say letter scramble or mixed-up words. They are all this: a word with its letters shuffled and a blank to write the real one in.</p>
      <h2>In a classroom</h2>
      <p>The useful property is that it takes a list you already have and makes a task out of it, in about ten seconds. This week's spelling words, the vocabulary from a topic, the irregular verbs — paste the list, print two sheets, done. Because difficulty tracks length, one list can be split into an easier and a harder sheet without writing anything new: short words on one, long words on the other.</p>
      <h2>The other direction</h2>
      <p>This tool makes puzzles. To solve one, the <a href="/tools/word-unscrambler/">word unscrambler</a> finds every word a set of letters can make, and the <a href="/tools/anagram-solver/">anagram solver</a> finds the ones that use every letter exactly once. If you want a grid rather than a list, the <a href="/tools/word-search-maker/">word search maker</a> hides the same words in a letter square.</p>""")

MAKER_CSS = """<style>
  /* The two puzzle makers: a square letter grid that has to survive a
     phone, a laptop and a sheet of A4 without being re-laid-out. */
  .field .wide{flex:1 1 100%; min-width:0;}
  @media (min-width:900px){ .field{flex-wrap:wrap;} }
  .plain input[type=text]{font-family:var(--body); font-weight:600; font-size:16px; letter-spacing:.01em; text-transform:none;}
  .plain input[type=text]::placeholder{font-weight:500;}
  #out{min-height:620px;}
  .pzbar{display:flex; flex-wrap:wrap; align-items:center; gap:12px; margin-top:22px;}
  .ghost{font-family:var(--display); font-weight:800; font-size:15px; color:#0A4A63; background:var(--page);
    border:0; border-radius:12px; padding:13px 20px; cursor:pointer; box-shadow:inset 0 0 0 2px rgba(14,58,80,.18);}
  .ghost:hover{box-shadow:inset 0 0 0 2px var(--tq);}
  .pznote{font-size:13.5px; color:var(--ink-faint); font-weight:600;}
  .pzsec{margin-top:24px;}
  .pzhead{font-family:var(--display); font-weight:800; font-size:clamp(19px,3vw,25px); letter-spacing:-.02em;
    margin:0 0 14px; color:var(--ink); text-wrap:balance;}
  .pzgrid{container-type:inline-size; max-width:620px; margin:0 auto;}
  .pz{table-layout:fixed; border-collapse:collapse; width:100%;}
  .pz td{padding:0; border:1px solid rgba(14,58,80,.18); background:var(--white);}
  .pz td span{display:flex; align-items:center; justify-content:center; aspect-ratio:1/1; position:relative;
    font-family:var(--display); font-weight:700; font-size:14px; line-height:1; color:var(--ink);}
  .pzgrid .pz td span{font-size:calc(58cqi / var(--n));}
  .pz.key td span{color:#7593A1; font-weight:600;}
  .pz.key td span.hit{color:#06323A; font-weight:800; background:#BDEEF6; box-shadow:inset 0 0 0 1px rgba(16,112,127,.35);}
  .cw td.blk{background:var(--mist); border-color:rgba(14,58,80,.10);}
  .cw td span i{position:absolute; top:4%; left:7%; font-style:normal; font-family:var(--body); font-weight:700;
    font-size:.52em; color:#3E6270; line-height:1;}
  .cw.key td span{color:#06323A;}
  .findh,.cluesh{font-family:var(--display); font-weight:800; font-size:17px; letter-spacing:-.015em; margin:22px 0 10px; color:var(--ink);}
  .findlist{display:flex; flex-wrap:wrap; gap:8px; margin:0; padding:0; list-style:none;}
  .findlist li{font-family:var(--display); font-weight:700; font-size:14.5px; letter-spacing:.05em; color:var(--ink);
    background:var(--page); padding:8px 12px; border-radius:9px;}
  .clues{display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:clamp(16px,3vw,30px); margin-top:8px;}
  .cluelist{margin:0; padding:0; list-style:none; display:grid; gap:9px;}
  .cluelist li{display:flex; gap:9px; font-size:15px; color:var(--ink-soft); line-height:1.45;}
  .cluelist b{flex:0 0 auto; min-width:1.4em; font-family:var(--display); font-weight:800; color:var(--ink);}
  .cluelist em{font-style:normal; color:var(--ink-faint); font-weight:600;}
  .vh{position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); clip-path:inset(50%); white-space:nowrap;}
  @media (max-width:600px){ #out{min-height:520px;} .ghost{width:100%;} .pznote{width:100%;} }

  @media print{
    @page{margin:14mm;}
    body{background:#fff; color:#000;}
    .nav,.sitefoot,.crumbs,.prose,form,.pzbar,.toolwrap h1,.toolwrap .sub{display:none !important;}
    .pzhead,.findh,.cluesh,.cluelist li,.cluelist b,.cluelist em,.findlist li{color:#000;}
    .toolwrap{max-width:none; padding:0;}
    .panel{background:#fff; box-shadow:none; border-radius:0; padding:0;}
    #out{min-height:0;}
    .pzgrid{max-width:min(100%, calc(var(--n) * 11mm));}
    .pz td{border-color:#111;}
    .pz td span,.pz.key td span{color:#000;}
    .pz.key td span.hit{background:#D9D9D9; box-shadow:none; color:#000;}
    .cw td.blk{background:#fff; border-color:transparent;}
    .cw.key td.blk{background:#fff;}
    .pzsec{break-inside:avoid;}
    .keysec{break-before:page;}
    .findlist li{background:none; box-shadow:inset 0 0 0 1px #999;}
  }
</style>"""

WS_DEFAULT = 'OTTER\nWILLOW\nHERON\nRIVER\nMEADOW\nPEBBLE\nREEDS\nMOSS'
CW_DEFAULT = ('OTTER: river swimmer with a taste for fish\n'
              'WILLOW: tree that leans over the water\n'
              'HERON: long-legged fisher, stands very still\n'
              'MEADOW: open grassy ground\n'
              'PEBBLE: small smooth stone\n'
              'REEDS: tall stems at the water\'s edge\n'
              'MOSS: soft green cover on a damp log')

SPEC['word-search-maker'] = dict(
 cta='Make puzzle',
 needs_dict=False,
 extra_css=MAKER_CSS,
 title='Word Search Maker — Create a Printable Word Search',
 desc='Free word search maker. Create your own printable word search from any list, pick the size and difficulty, print it or save as PDF. No sign-up, no watermark.',
 sub='Paste a spelling list, a set of topic words, or the names of everyone coming to the party. You get a grid, a word list and a matching answer key, ready to print.',
 form=(wide(ta('words', 'Your words — one per line', WS_DEFAULT, 'OTTER\nWILLOW\nHERON', 6))
       + tinp('title', 'Puzzle title (optional)', 'Riverbank words', 'Week 3 spellings')
       + sel('size', 'Grid size', [('0', 'Fit to the words', True), ('10', '10 × 10', False), ('12', '12 × 12', False),
                                   ('15', '15 × 15', False), ('18', '18 × 18', False), ('22', '22 × 22', False)])
       + sel('dirs', 'Difficulty', [('2', 'Easy — across and down', False),
                                    ('4', 'Medium — adds diagonals', True),
                                    ('8', 'Hard — adds backwards', False)])),
 hint='Three letters or more. Spaces and punctuation are stripped, so <code>ICE CREAM</code> becomes <code>ICECREAM</code>.',
 js=r"""
  var p=MK.parseWords(val('words'),22);
  if(!p.words.length) return fail('Add some words first — one per line, three letters or more.');
  if(p.words.length>44) return fail('That is more than a grid can hold. Keep it to 44 words or fewer.');
  var res=MK.wordsearch(p.words,{dirs:+val('dirs')||4, size:+val('size')||0});
  var title=(val('title')||'').trim();

  function grid(key){
    var h='<div class="pzgrid" style="--n:'+res.size+'" role="img" aria-label="'
         +(key?'Answer key. ':'')+'Word search grid, '+res.size+' by '+res.size+' letters.">'
         +'<table class="pz'+(key?' key':'')+'" role="presentation"><tbody>';
    for(var r=0;r<res.size;r++){
      h+='<tr>';
      for(var c=0;c<res.size;c++){ var i=r*res.size+c;
        h+='<td><span'+(key&&res.solved[i]?' class="hit"':'')+'>'+res.grid[i]+'</span></td>'; }
      h+='</tr>';
    }
    return h+'</tbody></table></div>';
  }

  var found=res.placed.map(function(x){return x.word;}).sort();
  var html='<div class="pzbar"><button type="button" class="ghost" data-print>Print or save as PDF</button>'
      +'<span class="pznote">'+res.size+' × '+res.size+' grid · '+found.length+' word'+(found.length===1?'':'s')+'</span></div>'
    +'<section class="pzsec">'+(title?'<h2 class="pzhead">'+MK.esc(title)+'</h2>':'')+grid(false)
      +'<h3 class="findh">Find these words</h3><ul class="findlist">'
      +found.map(function(w){return '<li>'+w+'</li>';}).join('')+'</ul></section>'
    +'<section class="pzsec keysec"><h2 class="pzhead">Answer key'+(title?' — '+MK.esc(title):'')+'</h2>'+grid(true)
      +'<ul class="vh">'+res.placed.map(function(p){
          return '<li>'+p.word+' starts at row '+(p.r+1)+', column '+(p.c+1)+', reading '+MK.dirName(p.dr,p.dc)+'.</li>';
        }).join('')+'</ul></section>';

  var note=[];
  if(p.short.length) note.push(p.short.length+' entr'+(p.short.length===1?'y was':'ies were')+' under three letters and left out');
  if(p.long.length) note.push(p.long.length+' too long for a grid ('+p.long.join(', ')+')');
  if(res.unplaced.length) note.push("couldn't fit "+res.unplaced.join(', ')+' — try a bigger grid');
  out(html, note.length ? note.join('; ')+'.' : 'Press Make puzzle again for a different layout.');""",
 prose="""
      <h2>What the difficulty setting changes</h2>
      <p>Easy hides words left-to-right and top-to-bottom only, which is right for children who are still reading in one direction. Medium adds the two downward diagonals. Hard adds every backwards direction, so a word can run right-to-left or bottom-to-top — eight directions in all. The grid size stays the same; only the hiding places change.</p>
      <h2>Find-a-word, word sleuth, letter soup</h2>
      <p>The same puzzle goes by different names depending on where you went to school. It's a find-a-word in Australia and New Zealand, a word sleuth in South Africa, and a <em>sopa de letras</em> — letter soup — across the Spanish-speaking world. Some people call it a word hunt. They are all this: a grid of letters with words hidden in it, and this maker builds any of them.</p>

      <h2>How many words to use</h2>
      <p>Ten to fifteen words is the sweet spot for a single sheet. Fewer than about eight and the grid is mostly filler, which makes the puzzle feel thin and oddly harder — there is less structure for the eye to catch on. More than about twenty and either the grid grows past a comfortable page, or the words cross so often that the square turns into a thicket. Word length matters as much as count: ten long words need a far bigger grid than ten short ones, because each one has to fit end to end in a straight line.</p>
      <h2>Printing it</h2>
      <p>Press <em>Print or save as PDF</em> and the page strips itself back to the puzzle — no navigation, no form, no colour to drain your cartridge. The answer key prints on its own sheet, so you can hand out the first page and keep the second. In the print dialog, choose <em>Save as PDF</em> as the destination if you want a file to email instead.</p>
      <h2>Getting a tighter grid</h2>
      <p>Leave the size on <em>Fit to the words</em> and the grid is only as big as it needs to be — it grows on its own if a word won't fit. Words share letters where they cross, so a list with a lot of common letters packs in more tightly. If a word is reported as not fitting, it is longer than one side of the grid; pick a larger size and it will go in.</p>
      <h2>Two things this will not do</h2>
      <p>It will not hide a word twice. If the random filler letters happen to spell one of your words somewhere else, the grid is redrawn until they don't — otherwise the answer key would point at the wrong place. And it won't keep your list: nothing is uploaded or stored, so copy it somewhere if you want it next week.</p>
      <h2>Making the other kind of puzzle</h2>
      <p>The <a href="/tools/crossword-maker/">crossword maker</a> takes the same list plus a clue for each word. The <a href="/tools/word-scrambler/">word scrambler</a> jumbles a list for a quick warm-up sheet, and the <a href="/tools/word-unscrambler/">word unscrambler</a> is for solving one.</p>""")

SPEC['crossword-maker'] = dict(
 cta='Make crossword',
 needs_dict=False,
 extra_css=MAKER_CSS,
 title='Crossword Maker — Make a Printable Crossword Puzzle',
 desc='Free crossword maker. Enter your own words and clues, and get a numbered crossword grid with Across and Down lists plus an answer key, ready to print.',
 sub='Give it a word and a clue on each line. It works out where the words cross, numbers the grid, and prints with the answers on a separate sheet.',
 form=(wide(ta('entries', 'One per line — WORD: clue', CW_DEFAULT, 'OTTER: river swimmer', 7))
       + tinp('title', 'Puzzle title (optional)', 'Riverbank crossword', 'Chapter 4 review')),
 hint='Separate the word from its clue with a colon, a comma or a dash. A line with no clue still goes in the grid.',
 js=r"""
  var p=MK.parseClued(val('entries'),18);
  if(!p.entries.length) return fail('Add some entries first — one word per line, three letters or more.');
  if(p.entries.length>34) return fail('That is more than this will lay out. Keep it to 34 entries or fewer.');
  var res=MK.crossword(p.entries);
  var title=(val('title')||'').trim();

  function grid(key){
    var h='<div class="pzgrid" style="--n:'+res.cols+'" role="img" aria-label="'
         +(key?'Completed crossword grid. ':'Empty crossword grid. ')+res.rows+' rows by '+res.cols+' columns.">'
         +'<table class="pz cw'+(key?' key':'')+'" role="presentation"><tbody>';
    for(var y=0;y<res.rows;y++){
      h+='<tr>';
      for(var x=0;x<res.cols;x++){
        var cell=res.cells[y][x];
        h+= cell ? '<td class="open"><span>'+(cell.n?'<i>'+cell.n+'</i>':'')+(key?cell.ch:'')+'</span></td>'
                 : '<td class="blk"><span></span></td>';
      }
      h+='</tr>';
    }
    return h+'</tbody></table></div>';
  }
  function clues(list,heading){
    if(!list.length) return '';
    return '<div><h3 class="cluesh">'+heading+'</h3><ul class="cluelist">'
      + list.map(function(e){
          return '<li><b>'+e.n+'</b><span>'+(e.clue?MK.esc(e.clue):'<em>no clue given</em>')+' <em>('+e.word.length+')</em></span></li>';
        }).join('')
      + '</ul></div>';
  }

  var n=res.across.length+res.down.length;
  var html='<div class="pzbar"><button type="button" class="ghost" data-print>Print or save as PDF</button>'
      +'<span class="pznote">'+res.rows+' × '+res.cols+' grid · '+n+' entr'+(n===1?'y':'ies')+'</span></div>'
    +'<section class="pzsec">'+(title?'<h2 class="pzhead">'+MK.esc(title)+'</h2>':'')+grid(false)
      +'<div class="clues">'+clues(res.across,'Across')+clues(res.down,'Down')+'</div></section>'
    +'<section class="pzsec keysec"><h2 class="pzhead">Answer key'+(title?' — '+MK.esc(title):'')+'</h2>'+grid(true)
      +'<ul class="vh">'+res.across.concat(res.down).map(function(e){
          return '<li>'+e.n+' '+(e.dr?'Down':'Across')+': '+e.word+'.</li>';
        }).join('')+'</ul></section>';

  var note=[];
  if(p.short.length) note.push(p.short.length+' entr'+(p.short.length===1?'y was':'ies were')+' under three letters and left out');
  if(p.long.length) note.push(p.long.join(', ')+' too long to lay out');
  if(p.noclue.length) note.push(p.noclue.length+' entr'+(p.noclue.length===1?'y has':'ies have')+' no clue yet');
  if(res.unplaced.length) note.push('no crossing point for '+res.unplaced.map(function(e){return e.word;}).join(', '));
  out(html, note.length ? note.join('; ')+'.' : 'Every word crossed. Press Make crossword again for a different layout.');""",
 prose="""
      <h2>How to write the list</h2>
      <p>One entry per line, the word first, then the clue: <code>OTTER: river swimmer</code>. A comma or a dash works just as well as a colon. Spaces inside an answer are removed, so <code>ICE AGE</code> becomes one seven-letter entry. A line with no clue still goes into the grid and is listed as having no clue yet, which is useful when you are building the grid first and writing the clues afterwards.</p>
      <h2>Why a word sometimes doesn't go in</h2>
      <p>Every entry has to cross an entry that is already placed, sharing a letter at the crossing square. If a word has no letter in common with anything else on the grid, there is nowhere legal to put it and it is reported rather than quietly dropped. Adding one more word that shares a letter with it usually pulls it in. Lists that share plenty of vowels interlock most easily.</p>
      <h2>The rule that keeps it a crossword</h2>
      <p>Two entries may only touch at a crossing square. Words never run straight into one another, and a letter that isn't a crossing never sits shoulder-to-shoulder with a neighbour — otherwise the grid would read out words nobody wrote a clue for. That constraint is why the finished grid is a little sparser than you might expect, and why every run of letters in it appears in the Across or Down list.</p>
      <h2>Printing and the answer key</h2>
      <p>Press <em>Print or save as PDF</em>. The puzzle and its clues print on the first sheet and the filled grid on a second, so the answers never show through on the handout. Choose <em>Save as PDF</em> in the print dialog if you want a file instead of paper. Nothing is uploaded — the grid is worked out in your browser, so your clues stay on your machine.</p>
      <h2>Related tools</h2>
      <p>The <a href="/tools/word-search-maker/">word search maker</a> takes the same word list without clues. If you're solving rather than setting, the <a href="/tools/word-finder/">word finder</a> matches a pattern like <code>C??SS</code>, and the <a href="/tools/anagram-solver/">anagram solver</a> handles the anagram clues.</p>""")


ANAG_CSS = """<style>
  /* Multi-word results are phrases, not single words: they need to wrap as
     units so a two-word answer never breaks across a line. */
  .phr{display:flex; flex-wrap:wrap; gap:8px; margin:0; padding:0; list-style:none;}
  .phr li{display:flex; align-items:baseline; gap:7px; background:var(--page); border-radius:11px; padding:9px 13px;
    box-shadow:inset 0 0 0 1px rgba(14,58,80,.08);}
  .phr li b{font-family:var(--display); font-weight:800; font-size:15.5px; letter-spacing:.09em; color:var(--ink);}
  .phr li i{font-style:normal; font-weight:700; color:var(--ink-faint); font-size:12px;}
  .phr li.rare b{color:#4B6C7A;}
</style>"""

SPEC['multi-word-anagram-solver'] = dict(
 cta='Find anagrams',
 extra_css=ANAG_CSS,
 title='Multi-Word Anagram Solver — Phrase Anagrams',
 desc='Free multi-word anagram solver. Enter a name, word or phrase and find the two- and three-word anagrams its letters can spell. 104,562 words, no sign-up.',
 sub='Enter a word, a name or a phrase. This finds the anagrams that need more than one word — the ones a single-word solver will never show you.',
 form=inp('letters','Letters, word or phrase','DORMITORY','e.g. DORMITORY', 18)
      + sel('pool','Dictionary', [('common','Everyday words',True),('all','Every word (obscure too)',False)]),
 hint='Spaces and punctuation are ignored, so you can paste a whole phrase. Six to eighteen letters.',
 js=r"""
  var raw=WK.clean(val('letters'));
  if(!raw) return fail('Enter a word, a name or a phrase first.');
  if(raw.length<6) return fail('Enter at least six letters — there is nothing to split into two words below that.');
  if(raw.length>18) return fail('Eighteen letters is the limit. Trim the phrase a little.');
  var co = val('pool') !== 'all';

  /* One sorted-letters index of the dictionary, built on first use and kept
     for the rest of the visit. Looking a remainder up in it is what makes
     the two-word search instant instead of quadratic. */
  var MAPS = window.__wmAmap || (window.__wmAmap = {});
  function amap(common){
    var k = common ? 'c' : 'a';
    if(MAPS[k]) return MAPS[k];
    var m = {}, d = WK.dict;
    for(var i=0;i<d.length;i++){
      var w = d[i];
      if(common && !WK.isCommon(w)) continue;
      var key = w.split('').sort().join('');
      (m[key] = m[key] || []).push(w);
    }
    return MAPS[k] = m;
  }
  function keyOf(c){
    var ks = Object.keys(c).sort(), s = '';
    for(var i=0;i<ks.length;i++){ for(var n=0;n<c[ks[i]];n++) s += ks[i]; }
    return s;
  }
  function take(have, w){
    var r = {}, k;
    for(k in have) r[k] = have[k];
    for(var i=0;i<w.length;i++){
      var ch = w.charAt(i);
      if(!r[ch]) return null;
      r[ch]--; if(!r[ch]) delete r[ch];
    }
    return r;
  }
  function size(c){ var n=0, k; for(k in c) n += c[k]; return n; }

  var M = amap(co), have = WK.counts(raw), n = raw.length, d = WK.dict;

  var one = (M[raw.split('').sort().join('')] || []).slice();

  var cands = [];
  for(var i=0;i<d.length;i++){
    var w = d[i];
    if(w.length < 3 || w.length > n-3) continue;
    if(co && !WK.isCommon(w)) continue;
    if(WK.makeable(w, have, 0)) cands.push(w);
  }
  cands.sort(function(a,b){ return b.length - a.length || (a < b ? -1 : 1); });

  var two = [], three = [], seen = {}, CAP = 400, t0 = Date.now();

  for(i=0;i<cands.length;i++){
    var rem = take(have, cands[i]);
    var part = M[keyOf(rem)];
    if(!part) continue;
    for(var j=0;j<part.length;j++){
      var k2 = [cands[i], part[j]].sort().join(' ');
      if(!seen[k2]){ seen[k2] = 1; two.push(k2); }
    }
  }

  /* Three words is the expensive half, so it runs second, stops at CAP
     results and gives up after a second rather than freezing the tab. */
  outer:
  for(i=0;i<cands.length;i++){
    var r1 = take(have, cands[i]);
    if(size(r1) < 6) continue;
    for(var j2=i;j2<cands.length;j2++){
      var r2 = take(r1, cands[j2]);
      if(r2 === null || size(r2) < 3) continue;
      var p3 = M[keyOf(r2)];
      if(p3){
        for(var m3=0;m3<p3.length;m3++){
          var k3 = [cands[i], cands[j2], p3[m3]].sort().join(' ');
          if(!seen[k3]){ seen[k3] = 1; three.push(k3); }
        }
      }
      if(three.length >= CAP) break outer;
    }
    if(Date.now() - t0 > 1000) break;
  }

  /* Balanced splits read best, so the longest shortest-word wins. */
  function rank(a,b){
    var A=a.split(' '), B=b.split(' ');
    function lo(x){ var v=99; for(var i=0;i<x.length;i++) v=Math.min(v,x[i].length); return v; }
    function hi(x){ var v=0;  for(var i=0;i<x.length;i++) v=Math.max(v,x[i].length); return v; }
    return lo(B)-lo(A) || hi(B)-hi(A) || (a<b?-1:1);
  }
  two.sort(rank); three.sort(rank);

  function phrases(list, limit){
    return '<ul class="phr">' + list.slice(0, limit).map(function(p){
      var ws = p.split(' '), rare = false;
      for(var i=0;i<ws.length;i++){ if(!WK.isCommon(ws[i])) rare = true; }
      return '<li' + (rare ? ' class="rare" title="Includes a less common word"' : '') + '>'
           + ws.map(function(w){ return '<b>' + w + '</b>'; }).join('<i>+</i>') + '</li>';
    }).join('') + '</ul>';
  }

  var html = '';
  if(one.length)
    html += '<div class="group"><h2>One word <span>' + one.length + '</span></h2><ul class="words">'
          + one.map(function(w){ return '<li class="top' + (WK.isCommon(w)?'':' rare') + '">' + w + '</li>'; }).join('')
          + '</ul></div>';
  if(two.length)
    html += '<div class="group"><h2>Two words <span>' + two.length + '</span></h2>' + phrases(two, 250) + '</div>';
  if(three.length)
    html += '<div class="group"><h2>Three words <span>' + three.length + (three.length >= CAP ? '+' : '') + '</span></h2>'
          + phrases(three, 150) + '</div>';

  if(!html){
    return out('<p class="status">Nothing splits ' + raw + ' into whole words.'
      + (co ? ' Try the full dictionary — it includes obscure words this one leaves out.' : ' Try a different set of letters.')
      + '</p>', '');
  }
  var total = one.length + two.length + three.length;
  out(html, total + ' anagram' + (total===1?'':'s') + ' of ' + raw
      + (three.length >= CAP ? ' — showing the first ' + CAP + ' three-word splits' : ''));""",
 prose="""
      <h2>Why one word is often not enough</h2>
      <p><code>DORMITORY</code> has no single-word anagram. Split it in two and it becomes <code>DIRTY ROOM</code>. That is the whole reason this tool exists: an ordinary <a href="/tools/anagram-solver/">anagram solver</a> looks for one word that uses all your letters, and for most inputs there isn't one. Here the letters get divided between two or three words instead, and every one of them has to be a real dictionary word with nothing left over.</p>
      <h2>Everyday words or the whole list</h2>
      <p>Leave the dictionary on everyday words and you get answers you'd actually say out loud. Switch to every word and the search opens up to all 104,562 entries, including obscure ones and names — more results, most of them unusable. Start narrow. Widen it only when nothing comes back.</p>
      <h2>Reading the results</h2>
      <p>Two-word answers come first and the list is complete — every valid split is there. Three-word answers are capped, because the number of ways to cut a long phrase into three grows fast; you get the first few hundred, sorted so the ones built from longer words appear at the top. Anything containing a less common word is dimmed slightly.</p>
      <h2>Names, phrases and cryptic clues</h2>
      <p>Paste a name with the spaces in and they're ignored, so <code>CLINT EASTWOOD</code> is treated as fourteen letters. This is the kind of anagram a cryptic crossword setter uses for a long clue, and the kind people make out of their own names. For a clue where you know some letter positions, the <a href="/tools/word-finder/">word finder</a> is the better tool.</p>""")


CRYP_CSS = """<style>
  /* A cryptogram has to be legible on a phone and writable on paper, so the
     letter cells are a clamped square with the cipher letter underneath. */
  #out{min-height:460px;}
  .crypbody{display:flex; flex-wrap:wrap; gap:15px 19px; margin:0;}
  .crypw{display:flex; gap:4px;}
  .cgrp{display:flex; flex-direction:column; align-items:center; gap:4px;}
  .cbox{width:clamp(21px,4.1vw,27px); height:clamp(27px,5vw,33px); border-radius:6px; background:var(--white);
    box-shadow:inset 0 0 0 1px rgba(14,58,80,.22); display:flex; align-items:center; justify-content:center;
    font-family:var(--display); font-weight:800; font-size:clamp(13px,2.5vw,16px); color:#06323A;}
  .cbox.given{background:#BDEEF6; box-shadow:inset 0 0 0 1px rgba(16,112,127,.35);}
  .cbox.solid{background:none; box-shadow:none; color:var(--ink);}
  .cltr{font-family:var(--display); font-weight:700; font-size:clamp(10px,2.1vw,12.5px); color:#3E6270; letter-spacing:.07em;}
  .cgrp.mark .cbox{box-shadow:none; background:none; color:var(--ink-soft); font-weight:700;}
  .cgrp.mark .cltr{visibility:hidden;}
  .subtab{display:flex; flex-wrap:wrap; gap:7px; margin:0; padding:0; list-style:none;}
  .subtab li{display:flex; flex-direction:column-reverse; align-items:center; gap:4px;}
  .crypkey{display:flex; flex-wrap:wrap; gap:6px; margin:0; padding:0; list-style:none;}
  .crypkey li{font-family:var(--display); font-weight:700; font-size:14px; letter-spacing:.04em; color:var(--ink);
    background:var(--page); border-radius:8px; padding:7px 10px;}
  .cryptext{font-size:clamp(16px,2.2vw,19px); line-height:1.55; color:var(--ink); font-weight:600; margin:0; max-width:62ch;}
  @media print{
    .cbox{box-shadow:inset 0 0 0 1px #111 !important; background:#fff !important; color:#000 !important;}
    .cbox.given{background:#D9D9D9 !important;}
    .cbox.solid{box-shadow:none !important;}
    .cltr{color:#000 !important;}
    .cgrp.mark .cbox{box-shadow:none !important; color:#000 !important;}
    .crypkey li{background:none; box-shadow:inset 0 0 0 1px #999; color:#000;}
    .cryptext{color:#000;}
  }
</style>"""

CRYP_DEFAULT = 'The quick brown fox jumps over the lazy dog.'

SPEC['cryptogram-maker'] = dict(
 cta='Make cryptogram',
 needs_dict=False,
 extra_css=MAKER_CSS + CRYP_CSS,
 title='Cryptogram Maker — Printable Cryptogram Puzzles',
 desc='Free cryptogram maker. Turn any quote into a printable letter-substitution puzzle, choose how many letters to give away, and print the answer key.',
 sub='Type a quote, a saying or a message. Every letter is swapped for a different one, and you get a printable puzzle with a solving grid and a separate answer key.',
 form=wide(ta('text','Your quote or message', CRYP_DEFAULT, 'Type or paste the sentence to encipher', 3))
      + tinp('title','Puzzle title (optional)','','e.g. Monday warm-up', 48, 'mid')
      + sel('give','Letters given away', [('0','None — hardest',False),('2','Two letters',True),('4','Four letters',False),('v','All the vowels',False)]),
 hint='Punctuation and spaces stay as they are — only letters get swapped. No letter is ever enciphered as itself.',
 js=r"""
  var text=(val('text')||'').replace(/\s+/g,' ').trim();
  if(!text) return fail('Type a quote or a message first.');
  if(text.length>320) return fail('That is '+text.length+' characters. Keep it under 320 so the puzzle fits a page.');
  var letters=text.toUpperCase().replace(/[^A-Z]/g,'');
  if(letters.length<12) return fail('Use at least twelve letters, or there is not enough to solve.');
  var title=(val('title')||'').trim(), give=val('give');
  var AL='ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

  /* A cryptogram where some letter stands for itself is a broken puzzle, so
     the permutation has to be a derangement — no fixed points anywhere. */
  function derange(){
    var p=AL.slice(), i, j, t;
    for(var attempt=0; attempt<80; attempt++){
      for(i=p.length-1;i>0;i--){ j=(Math.random()*(i+1))|0; t=p[i]; p[i]=p[j]; p[j]=t; }
      var ok=true;
      for(i=0;i<26;i++){ if(p[i]===AL[i]){ ok=false; break; } }
      if(ok) return p;
    }
    for(i=0;i<26;i++){ if(p[i]===AL[i]){ j=(i+1)%26; t=p[i]; p[i]=p[j]; p[j]=t; } }
    return p;
  }
  var perm=derange(), enc={}, dec={};
  for(var i=0;i<26;i++){ enc[AL[i]]=perm[i]; dec[perm[i]]=AL[i]; }

  /* Only letters that actually appear can be given away — revealing a Z that
     is not in the text tells the solver nothing. */
  var used={}, order=[];
  for(i=0;i<letters.length;i++){ var c=letters.charAt(i); if(!used[c]){ used[c]=1; order.push(c); } }
  var given={}, want = give==='v' ? 0 : (+give||0);
  if(give==='v'){ 'AEIOU'.split('').forEach(function(v){ if(used[v]) given[v]=1; }); }
  else if(want>0){
    var bag=order.slice();
    for(i=bag.length-1;i>0;i--){ var j2=(Math.random()*(i+1))|0, t2=bag[i]; bag[i]=bag[j2]; bag[j2]=t2; }
    bag.slice(0, Math.min(want, bag.length)).forEach(function(c){ given[c]=1; });
  }

  function cell(ch, reveal){
    if(!/[A-Z]/.test(ch))
      return '<span class="cgrp mark"><span class="cbox">'+MK.esc(ch)+'</span><span class="cltr">·</span></span>';
    var shown = reveal ? ch : (given[ch] ? ch : '');
    return '<span class="cgrp"><span class="cbox'+(reveal?' solid':(given[ch]?' given':''))+'">'+shown+'</span>'
         + '<span class="cltr">'+enc[ch]+'</span></span>';
  }
  function body(reveal){
    return '<div class="crypbody">' + text.toUpperCase().split(' ').filter(Boolean).map(function(word){
      return '<span class="crypw">' + word.split('').map(function(ch){ return cell(ch, reveal); }).join('') + '</span>';
    }).join('') + '</div>';
  }

  /* The working grid: every cipher letter the solver will meet, with a blank
     to write the plain letter above it. */
  var seenC={}, cipherLetters=[];
  for(i=0;i<letters.length;i++){ var e=enc[letters.charAt(i)]; if(!seenC[e]){ seenC[e]=1; cipherLetters.push(e); } }
  cipherLetters.sort();
  var grid='<ul class="subtab">'+cipherLetters.map(function(cl){
      var plain=dec[cl];
      return '<li><span class="cltr">'+cl+'</span><span class="cbox'+(given[plain]?' given':'')+'">'+(given[plain]?plain:'')+'</span></li>';
    }).join('')+'</ul>';

  var gnote = give==='v' ? Object.keys(given).length+' vowels given'
            : (Object.keys(given).length ? Object.keys(given).length+' letter'+(Object.keys(given).length===1?'':'s')+' given' : 'nothing given away');

  var html='<div class="pzbar"><button type="button" class="ghost" data-print>Print or save as PDF</button>'
      +'<span class="pznote">'+letters.length+' letters · '+cipherLetters.length+' of 26 in play · '+gnote+'</span></div>'
    +'<section class="pzsec">'+(title?'<h2 class="pzhead">'+MK.esc(title)+'</h2>':'<h2 class="pzhead">Cryptogram</h2>')
      +body(false)
      +'<h3 class="findh">Your solving grid</h3>'+grid+'</section>'
    +'<section class="pzsec keysec"><h2 class="pzhead">Answer key'+(title?' — '+MK.esc(title):'')+'</h2>'
      +'<p class="cryptext">'+MK.esc(text)+'</p>'
      +'<h3 class="findh">The cipher</h3><ul class="crypkey">'
      +cipherLetters.map(function(cl){ return '<li>'+cl+' = '+dec[cl]+'</li>'; }).join('')
      +'</ul></section>';

  out(html, 'Press Make cryptogram again for a fresh cipher.');""",
 prose="""
      <h2>What a cryptogram is</h2>
      <p>Every letter of the alphabet is swapped for a different one, consistently, for the whole message. If E became Q in one word it is Q in every word. Spaces and punctuation are left alone, which is what makes the puzzle solvable — word lengths, apostrophes and the shape of short words are most of the evidence you have.</p>
      <h2>No letter stands for itself</h2>
      <p>The cipher is built as a derangement: a shuffle of the alphabet with no letter left in its own place. That matters more than it sounds. A puzzle where T happens to encipher to T has a free answer sitting in it, and an experienced solver will spot it. Press the button again and you get an entirely new cipher for the same text.</p>
      <h2>Choosing how much to give away</h2>
      <p>Giving nothing away is the proper version and it is genuinely hard for a first-timer. Two letters is a reasonable classroom setting. Four is gentle. Giving all the vowels turns it into a different and much easier puzzle — close to a fill-in-the-blanks — which is about right for younger children or a warm-up.</p>
      <h2>Where to start solving</h2>
      <p>Count the letters. The most frequent one in ordinary English prose is usually E, then T, A and O. A one-letter word is A or I. A three-letter word that keeps appearing is very often THE, and that single guess cracks three letters at once. Apostrophes are a gift: the letter after one is nearly always S, T or a vowel in a contraction.</p>
      <h2>Printing it</h2>
      <p>Press <em>Print or save as PDF</em>. The puzzle and its solving grid come out on the first sheet, the answer key on a second, so you can hand out the first page without the answers showing through. Nothing leaves your browser — the cipher is generated on your machine, so your quote stays on it.</p>
      <h2>The other makers</h2>
      <p>The <a href="/tools/word-search-maker/">word search maker</a> and the <a href="/tools/crossword-maker/">crossword maker</a> build their puzzles from your own word list, and the <a href="/tools/word-scrambler/">word scramble maker</a> jumbles a list of words one at a time.</p>""")


LAD_CSS = """<style>
  /* The ladder reads top to bottom with the letter that changed on each rung
     picked out, because that is the only thing a solver is looking for. */
  .lad{list-style:none; margin:0; padding:0; display:grid; gap:7px; justify-items:center;}
  .lad li{display:flex; gap:6px;}
  .lad li span{display:flex; align-items:center; justify-content:center; width:clamp(32px,6.6vw,42px); aspect-ratio:1/1;
    background:var(--white); border-radius:10px; font-family:var(--display); font-weight:800;
    font-size:clamp(15px,2.9vw,20px); letter-spacing:.02em; color:var(--ink); box-shadow:inset 0 0 0 1px rgba(14,58,80,.12);}
  .lad li span.chg{background:linear-gradient(180deg,#5AD9EC,var(--tq)); color:#06323A;
    box-shadow:inset 0 2px 0 rgba(255,255,255,.45);}
  .lad li.rare span{color:#4B6C7A;}
  .ladfoot{margin:16px 0 0; color:var(--ink-faint); font-size:13.5px; text-align:center;}
</style>"""

SPEC['word-ladder-solver'] = dict(
 cta='Build the ladder',
 extra_css=LAD_CSS,
 title='Word Ladder Solver — Shortest Chain Between Words',
 desc='Free word ladder solver. Enter two words of the same length and get the shortest chain between them, changing one letter at a time, every rung a real word.',
 sub='Give it two words the same length. It finds the shortest chain from one to the other, changing a single letter at each step, with every rung a real word.',
 form=mid('start','Start word','COLD','e.g. COLD') + mid('end','End word','WARM','e.g. WARM')
      + sel('pool','Dictionary', [('common','Everyday words',True),('all','Every word (obscure too)',False)]),
 hint='Three to eight letters, and both words the same length. Each step changes exactly one letter — no adding, removing or rearranging.',
 js=r"""
  var a=WK.clean(val('start')), b=WK.clean(val('end'));
  if(!a || !b) return fail('Enter a start word and an end word.');
  setv('start',a); setv('end',b);
  if(a.length !== b.length)
    return fail('Both words need the same length — '+a+' has '+a.length+' letters, '+b+' has '+b.length+'.');
  if(a.length < 3 || a.length > 8) return fail('Word ladders here run from three to eight letters.');
  if(a === b) return fail('Those are the same word. Pick two different ones.');
  var co = val('pool') !== 'all';
  if(!WK.has(a)) return fail(a+' is not in the dictionary.');
  if(!WK.has(b)) return fail(b+' is not in the dictionary.');
  if(co && !WK.isCommon(a)) return fail(a+' is an unusual word. Switch to every word to use it as a rung.');
  if(co && !WK.isCommon(b)) return fail(b+' is an unusual word. Switch to every word to use it as a rung.');

  /* Words of one length, bucketed by each position blanked out. Two words are
     one letter apart exactly when they share a bucket, so the graph is built
     once per length and reused for every search in the visit. */
  var CACHE = window.__wmLadder || (window.__wmLadder = {});
  function graph(L, common){
    var k = L + (common ? 'c' : 'a');
    if(CACHE[k]) return CACHE[k];
    var pool = (WK.byLen[L] || []).filter(function(w){ return !common || WK.isCommon(w); });
    var bk = {};
    for(var i=0;i<pool.length;i++){
      var w = pool[i];
      for(var p=0;p<L;p++){
        var key = w.substring(0,p) + '_' + w.substring(p+1);
        (bk[key] = bk[key] || []).push(w);
      }
    }
    return CACHE[k] = { n: pool.length, bk: bk };
  }

  var L = a.length, G = graph(L, co);
  var prev = {}, q = [a], qi = 0;
  prev[a] = null;
  while(qi < q.length){
    var w = q[qi++];
    if(w === b) break;
    for(var p=0;p<L;p++){
      var nbs = G.bk[w.substring(0,p) + '_' + w.substring(p+1)];
      if(!nbs) continue;
      for(var i=0;i<nbs.length;i++){
        var nb = nbs[i];
        if(prev[nb] === undefined){ prev[nb] = w; q.push(nb); }
      }
    }
  }

  if(prev[b] === undefined){
    return out('<p class="status">There is no ladder from '+a+' to '+b+'.'
      + (co ? ' Every rung has to be an everyday word — switching to every word opens up far more stepping stones.'
            : ' Some words simply sit in their own corner of the dictionary with nothing one letter away.')
      + '</p>', '');
  }

  var path = [], cur = b;
  while(cur !== null && cur !== undefined){ path.push(cur); cur = prev[cur]; }
  path.reverse();

  var rungs = path.map(function(w, i){
    var before = i ? path[i-1] : null, cells = '';
    for(var k=0;k<w.length;k++){
      var changed = before && before.charAt(k) !== w.charAt(k);
      cells += '<span' + (changed ? ' class="chg"' : '') + '>' + w.charAt(k) + '</span>';
    }
    return '<li' + (WK.isCommon(w) ? '' : ' class="rare" title="Less common word"') + '>' + cells + '</li>';
  }).join('');

  var steps = path.length - 1;
  var html = '<div class="group"><h2>' + a + ' to ' + b
           + ' <span>' + steps + ' step' + (steps===1?'':'s') + '</span></h2>'
           + '<ol class="lad">' + rungs + '</ol>'
           + '<p class="ladfoot">No shorter ladder exists'
           + (co ? ' using everyday words.' : ' in the dictionary.') + '</p></div>';
  out(html, steps + ' step' + (steps===1?'':'s') + ', ' + path.length + ' rungs, searched '
      + G.n.toLocaleString() + ' ' + L + '-letter words.');""",
 prose="""
      <h2>The rules of a word ladder</h2>
      <p>Change one letter at a time. Every step has to land on a real word, and the letters stay where they are — no adding, removing or shuffling. <code>COLD</code> to <code>WARM</code> is the famous one, and it takes four steps: <code>COLD</code>, <code>CORD</code>, <code>CARD</code>, <code>WARD</code>, <code>WARM</code>. The puzzle was invented by Lewis Carroll, who called it Doublets and set them as a weekly column in 1879.</p>
      <h2>What "shortest" means here</h2>
      <p>The tool treats the dictionary as a map: every word of your length is a place, and two places are connected if they differ by one letter. It then walks outwards from your start word a step at a time, so the first route it reaches the end by is necessarily the shortest one. If it says six steps, there is no five-step ladder. There may well be other six-step ladders — this shows one of them.</p>
      <h2>When there is no ladder at all</h2>
      <p>Plenty of pairs have none. Some words have no neighbours whatsoever — change any single letter and you get a non-word — so they sit alone and no ladder can reach them. Others belong to a cluster that simply never connects to the one you're aiming at. The everyday-words setting makes this far more likely, because it throws away the obscure words that often form the bridge. Switch to every word and a surprising number of dead ends open up.</p>
      <h2>Setting one as a puzzle</h2>
      <p>Pick two words that are related but opposite — <code>HEAD</code> and <code>TAIL</code>, <code>BLACK</code> and <code>WHITE</code>, <code>WHEAT</code> and <code>BREAD</code> — and check the ladder here first so you know it exists and how long it runs. Give your solvers the two ends and the number of rungs. Four- and five-letter words make the best puzzles: three-letter ladders are over too quickly, and anything above six tends to need words nobody uses.</p>
      <h2>Related tools</h2>
      <p>The <a href="/tools/word-finder/">word finder</a> matches a pattern like <code>C?LD</code>, which is the manual version of what each rung of this search does. For rearranging letters rather than replacing them, try the <a href="/tools/anagram-solver/">anagram solver</a> or the <a href="/tools/multi-word-anagram-solver/">multi-word anagram solver</a>.</p>""")

PRELOAD = '<link rel="preload" as="fetch" href="/tools/words.txt?v=2" crossorigin>\n'
ENGINE_DICT = '<script src="/tools/wordkit.js?v=2"></script>'
ENGINE_MAKER = '<script src="/tools/makerkit.js?v=1"></script>'
BOOT_DICT = """  WK.onReady(function(e){
    if(e){ status.textContent='The dictionary could not load. Refresh the page to try again.'; return; }
    go.disabled=false; status.textContent='104,562 words ready.'; solve();
  });"""
BOOT_PLAIN = """  go.disabled=false; solve();"""

TEMPLATE = open(os.path.join(ROOT, 'build/tool_template.html'), encoding='utf-8').read()

def related(slug):
    i = [t[0] for t in TOOLS].index(slug)
    ring = [TOOLS[(i + k) % len(TOOLS)] for k in range(1, 4)]
    cards = [f'<a class="rel" href="/tools/{s}/"><b>{n}</b><span>{d}</span></a>' for s, n, d in ring]
    cards.append('<a class="rel" href="/"><b>Wordmere</b><span>The cosy word game this dictionary comes from.</span></a>')
    return '\n        '.join(cards)

def build(slug, name):
    s = SPEC[slug]
    url = f'https://wordmere.com/tools/{slug}/'
    schema = {"@context": "https://schema.org", "@graph": [
      {"@type": "WebApplication", "name": name, "url": url,
       "applicationCategory": "EducationalApplication" if slug.endswith("-maker") else "UtilitiesApplication",
       "operatingSystem": "Any", "browserRequirements": "Requires JavaScript", "description": s['desc'],
       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
       "publisher": {"@type": "Organization", "name": "Wordmere", "url": "https://wordmere.com/"}},
      {"@type": "BreadcrumbList", "itemListElement": [
       {"@type": "ListItem", "position": 1, "name": "Wordmere", "item": "https://wordmere.com/"},
       {"@type": "ListItem", "position": 2, "name": "Word tools", "item": "https://wordmere.com/tools/"},
       {"@type": "ListItem", "position": 3, "name": name, "item": url}]}]}
    dictionary = s.get('needs_dict', True)
    page = TEMPLATE
    for k, v in {
        'TITLE': s['title'], 'DESC': s['desc'], 'URL': url, 'NAME': name, 'SUB': s['sub'],
        'SCHEMA': json.dumps(schema, ensure_ascii=False), 'STYLE': STYLE, 'TOOLCSS': TOOL_CSS,
        'EXTRACSS': s.get('extra_css', ''),
        'NAV': NAV, 'FOOT': FOOT, 'FORM': s['form'], 'HINT': f'<p class="hint">{s["hint"]}</p>' if s.get('hint') else '',
        'PROSE': s['prose'], 'TM': f'<p class="tm">{s["tm"]}</p>' if s.get('tm') else '',
        'RELATED': related(slug), 'SOLVE': s['js'], 'CTA': s.get('cta', 'Search'),
        'PRELOAD': PRELOAD if dictionary else '',
        'ENGINE': ENGINE_DICT if dictionary else ENGINE_MAKER,
        'GUARD': '    if(!WK.dict) return;' if dictionary else '',
        'BOOT': BOOT_DICT if dictionary else BOOT_PLAIN,
        'LOADING': 'Loading the dictionary…' if dictionary else 'Building your puzzle…',
    }.items():
        page = page.replace('{{' + k + '}}', v)
    assert '{{' not in page, re.findall(r'\{\{\w+\}\}', page)
    os.makedirs(os.path.join(ROOT, 'tools', slug), exist_ok=True)
    open(os.path.join(ROOT, 'tools', slug, 'index.html'), 'w', encoding='utf-8').write(page)
    return len(page)

if __name__ == '__main__':
    for slug, name, _ in TOOLS:
        print(f'  /tools/{slug}/  {build(slug, name)//1024} KB')
