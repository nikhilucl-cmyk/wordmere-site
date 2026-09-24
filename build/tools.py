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
  ('scrabble-word-finder', 'Scrabble word finder', 'Highest-scoring words from your rack'),
  ('words-with-letters',   'Words with letters',   'Words that contain the letters you choose'),
  ('five-letter-word-solver','Five-letter word solver','Narrow 5-letter words by what you know'),
  ('random-word-generator', 'Random word generator','Pick random words, any length'),
  ('word-scrambler',        'Word scrambler',       'Scramble a list of words for a puzzle'),
]

TOOL_CSS = """<style>
  .navstatic{position:static;}
  .navstatic .navbar{background:var(--white); border-color:rgba(14,58,80,.08);}
  .toolwrap{max-width:1080px; margin:0 auto; padding:clamp(24px,4vw,52px) var(--gutter) 56px;}
  .crumbs{font-size:13px; color:var(--ink-faint); margin:0 0 14px; font-weight:500;}
  .crumbs a{color:var(--ink-soft); text-decoration:underline; text-decoration-color:rgba(14,58,80,.35); text-underline-offset:3px;}
  .toolwrap h1{font-family:var(--display); font-weight:800; font-size:clamp(30px,5.4vw,50px); letter-spacing:-.038em; line-height:1; margin:0; color:var(--ink); text-wrap:balance;}
  .toolwrap .sub{margin:12px 0 0; color:var(--ink-soft); font-size:clamp(15px,1.8vw,18px); max-width:60ch;}
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
  .prose{margin-top:46px; max-width:66ch;}
  .prose h2{font-family:var(--display); font-weight:800; font-size:clamp(21px,3vw,28px); letter-spacing:-.028em; margin:30px 0 10px; color:var(--ink);}
  .prose p{margin:0 0 14px; color:var(--ink-soft); font-size:16px;}
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
 title='Scrabble Word Finder — Highest-Scoring Words From Your Rack',
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
 title='Words With Letters — Find Words Containing Any Letters You Choose',
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

SPEC['word-scrambler'] = dict(
 cta='Scramble',
 title='Word Scrambler — Make a Jumbled Word Puzzle',
 desc='Free word scrambler. Paste a list of words and get them jumbled, ready for a worksheet, a quiz or a party game. Includes an answer key.',
 sub='Paste your words, one per line or separated by commas. You get each one jumbled, with the answer beside it — ready to paste into a worksheet or a quiz.',
 form=ta('words','Your words','ORANGE\nMEADOW\nLIGHTHOUSE\nPUZZLE','One word per line, or separated by commas'),
 hint='Letters only. Anything longer than two letters gets scrambled; the answer key is shown next to each one.',
 js=r"""
  var raw=(val('words')||'').toUpperCase().split(/[^A-Z]+/).filter(function(w){ return w.length>0; });
  if(!raw.length) return fail('Paste at least one word.');
  if(raw.length>200) return fail('That is more than 200 words — trim the list a little.');
  var short=raw.filter(function(w){ return w.length<3; });
  function scramble(w){
    var a=w.split(''), best=w, tries=0;
    while(tries++<30){
      for(var i=a.length-1;i>0;i--){ var j=(Math.random()*(i+1))|0, t=a[i]; a[i]=a[j]; a[j]=t; }
      best=a.join('');
      if(best!==w) return best;
    }
    return best;
  }
  var rows=raw.map(function(w){
    return w.length<3 ? {w:w, s:w, skip:true} : {w:w, s:scramble(w)};
  });
  var html='<div class="group"><h2>Scrambled <span>'+rows.length+'</span></h2><ul class="pairs">'
    + rows.map(function(r){ return '<li class="pair"><b>'+r.s+'</b><span>'+(r.skip?'too short':r.w)+'</span></li>'; }).join('')
    + '</ul></div>';
  out(html, rows.length+' word'+(rows.length===1?'':'s')+' scrambled'+(short.length?' — '+short.length+' left alone (under three letters)':''));""",
 prose="""
      <h2>Making a worksheet</h2>
      <p>Paste a spelling list, a set of topic words or the names of everyone at a party. Each word comes back jumbled with the answer next to it, so you can copy the scrambled column into a handout and keep the answers for yourself. Words of one or two letters are left alone — there's nothing to scramble.</p>
      <h2>Every jumble is different</h2>
      <p>The letters are shuffled fresh each time, and the tool won't hand back a "scramble" that is identical to the original word. Press Search again if a particular jumble looks too easy — short words with repeated letters sometimes land close to the real thing.</p>
      <h2>The other direction</h2>
      <p>This tool makes puzzles. To solve one, the <a href="/tools/word-unscrambler/">word unscrambler</a> finds every word your letters can make, and the <a href="/tools/anagram-solver/">anagram solver</a> finds the ones that use every letter exactly once.</p>""")

TEMPLATE = open(os.path.join(ROOT, 'build/tool_template.html'), encoding='utf-8').read()

def related(slug):
    cards = [f'<a class="rel" href="/tools/{s}/"><b>{n}</b><span>{d}</span></a>' for s, n, d in TOOLS if s != slug][:3]
    cards.append('<a class="rel" href="/"><b>Wordmere</b><span>The cosy word game this dictionary comes from.</span></a>')
    return '\n        '.join(cards)

def build(slug, name):
    s = SPEC[slug]
    url = f'https://wordmere.com/tools/{slug}/'
    schema = {"@context": "https://schema.org", "@graph": [
      {"@type": "WebApplication", "name": name, "url": url, "applicationCategory": "UtilitiesApplication",
       "operatingSystem": "Any", "browserRequirements": "Requires JavaScript", "description": s['desc'],
       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
       "publisher": {"@type": "Organization", "name": "Wordmere", "url": "https://wordmere.com/"}},
      {"@type": "BreadcrumbList", "itemListElement": [
       {"@type": "ListItem", "position": 1, "name": "Wordmere", "item": "https://wordmere.com/"},
       {"@type": "ListItem", "position": 2, "name": "Word tools", "item": "https://wordmere.com/tools/"},
       {"@type": "ListItem", "position": 3, "name": name, "item": url}]}]}
    page = TEMPLATE
    for k, v in {
        'TITLE': s['title'], 'DESC': s['desc'], 'URL': url, 'NAME': name, 'SUB': s['sub'],
        'SCHEMA': json.dumps(schema, ensure_ascii=False), 'STYLE': STYLE, 'TOOLCSS': TOOL_CSS,
        'NAV': NAV, 'FOOT': FOOT, 'FORM': s['form'], 'HINT': f'<p class="hint">{s["hint"]}</p>' if s.get('hint') else '',
        'PROSE': s['prose'], 'TM': f'<p class="tm">{s["tm"]}</p>' if s.get('tm') else '',
        'RELATED': related(slug), 'SOLVE': s['js'], 'CTA': s.get('cta', 'Search'),
    }.items():
        page = page.replace('{{' + k + '}}', v)
    assert '{{' not in page, re.findall(r'\{\{\w+\}\}', page)
    os.makedirs(os.path.join(ROOT, 'tools', slug), exist_ok=True)
    open(os.path.join(ROOT, 'tools', slug, 'index.html'), 'w', encoding='utf-8').write(page)
    return len(page)

if __name__ == '__main__':
    for slug, name, _ in TOOLS:
        print(f'  /tools/{slug}/  {build(slug, name)//1024} KB')
