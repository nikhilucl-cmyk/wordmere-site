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
  .fig{margin:26px 0; padding:18px 20px 14px; background:var(--white); border-radius:18px;
    box-shadow:inset 0 0 0 1px rgba(14,58,80,.08), 0 6px 18px rgba(14,58,80,.06);}
  .fig svg{display:block; width:100%; height:auto;}
  .figcap{margin:10px 0 0; font-size:14px; color:var(--ink-faint); line-height:1.5;}
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
 slug='retention-magic-number',
 date='2026-10-28',
 title='Our retention magic number was a mirage',
 h1='Our retention magic number was a mirage',
 sub='Players who cleared six levels in their first session came back at roughly double the rate. So we made more players clear six levels. Retention did not move at all.',
 desc='Six levels in session one doubled our day-one retention. We shipped a release that moved that number by a third, and retention stayed flat. What we got wrong.',
 body="""
      <p>Every product eventually finds a magic number. Ours was six levels.</p>

      <p>Plot how likely a new player is to come back the next day against how many levels they cleared in their very first session, and the chart is almost too tidy. It is flat and low up to about five. Somewhere between five and six it roughly doubles. It keeps climbing after that.</p>

      <figure class="fig">
        <svg viewBox="0 0 660 300" role="img" aria-labelledby="figt figd">
          <title id="figt">Day-one retention by first-session depth, indexed to the shallowest group</title>
          <desc id="figd">Retention is lowest for players who clear one to five levels in their first
            session, roughly doubles at six to nine, and reaches about three times the baseline at twenty
            or more. The vertical axis is a multiple of that baseline; absolute figures are not shown.</desc>
          <g font-family="var(--body)" font-size="13" fill="var(--ink-faint)">
            <line x1="100" y1="181" x2="620" y2="181" stroke="rgba(14,58,80,.10)"/>
            <line x1="100" y1="113" x2="620" y2="113" stroke="rgba(14,58,80,.10)"/>
            <line x1="100" y1="44"  x2="620" y2="44"  stroke="rgba(14,58,80,.10)"/>
            <line x1="100" y1="250" x2="620" y2="250" stroke="rgba(14,58,80,.28)"/>
            <text x="86" y="186" text-anchor="end">&#215;1</text>
            <text x="86" y="118" text-anchor="end">&#215;2</text>
            <text x="86" y="49"  text-anchor="end">&#215;3</text>
            <line x1="192" y1="30" x2="192" y2="250" stroke="var(--sun-deep)" stroke-width="1.5"
                  stroke-dasharray="5 5" opacity=".55"/>
            <text x="200" y="42" fill="var(--sun-deep)" font-weight="600">the jump</text>
            <polyline points="110,181 273,113 437,85 600,51" fill="none" stroke="var(--sea)"
                      stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <g fill="var(--white)" stroke="var(--sea)" stroke-width="3">
              <circle cx="110" cy="181" r="6"/><circle cx="273" cy="113" r="6"/>
              <circle cx="437" cy="85" r="6"/><circle cx="600" cy="51" r="6"/>
            </g>
            <g text-anchor="middle" font-weight="600" fill="var(--ink-soft)">
              <text x="110" y="274">1&#8211;5</text><text x="273" y="274">6&#8211;9</text>
              <text x="437" y="274">15&#8211;19</text><text x="600" y="274">20+</text>
            </g>
            <text x="360" y="296" text-anchor="middle">levels cleared in the first session</text>
          </g>
        </svg>
        <figcaption class="figcap">Day-one retention by how far a player got in their very first session,
          as a multiple of the shallowest group. We publish shapes rather than levels, so the axis is a
          ratio &#8212; but the ratio is real and the step between five and six is where it happens.</figcaption>
      </figure>

      <p>About half of our new players were finishing their first session in the flat part of that curve. The brief writes itself: get more of them past five.</p>

      <h2>So we did</h2>

      <p>We went at first-session depth directly. The opening levels were made quicker to read and quicker to clear. Interruptions before the threshold were taken out. The moment a brand-new player finds their first word was redesigned so that the thing the game is asking of them cannot be missed.</p>

      <p>It worked, in the sense that it did what it was supposed to do. In one release, the share of new players clearing six or more levels on their first day went up by about a third.</p>

      <p>Day-one retention did not move. Not slightly &#8212; it sat exactly where it had been sitting for two months, and it is sitting there still.</p>

      <div class="pull"><p>The threshold was real. It was never a cause. We moved the symptom and the illness did not notice.</p></div>

      <h2>Why the number lied</h2>

      <p>A player who clears six levels in one sitting has told you something about themselves before your level design gets a vote. They were in the mood. The game landed. They had twenty minutes and nothing better to do with them. Depth was a <em>measurement</em> of that intent, and intent is what comes back tomorrow.</p>

      <p>Make the levels faster and you move the measurement. You have not been anywhere near the thing it was measuring.</p>

      <p>This is the oldest trap in product analytics and it still catches everybody, because the correlation is strong, the threshold is sharp, and shipping against a proxy feels exactly like shipping against the real thing. &#8220;Players who do X retain better&#8221; is never a finding. It is an invitation to ask the actual question, which is: and if we <em>make</em> them do X?</p>

      <p>The cheap way to ask it, before you build anything: find a change you have already shipped that moved the proxy, and check whether the outcome followed. If no such change exists in your history, you do not know yet, and that is worth saying out loud before a quarter of roadmap gets built on top of it.</p>

      <h2>What the churn actually looked like</h2>

      <p>The deeper mistake was treating early churn as one thing. It is two, with opposite causes, and the bigger one is invisible if you go looking for difficulty.</p>

      <p><strong>The early group is not stuck.</strong> They leave around twenty seconds into a level. Nobody is defeated at twenty seconds. Almost everyone who starts the first level finishes it, so the first level is not hard. And they leave with their hints unspent &#8212; they do not exhaust the help we gave them and give up, they never reach for it once. There is also a slice of installs, the single largest hole in our funnel, that opens the app, registers a screen view, and never starts a level at all.</p>

      <p>None of that is difficulty. It is cold start. You cannot fix it by making the puzzle easier, because they were not trying to solve the puzzle.</p>

      <p><strong>The second group is genuinely stuck</strong>, and they are much further in, at the point where the content first asks something real of you. Their median time on the last level they ever touch roughly doubles, and a third of them spend over two minutes on it before they go. That is difficulty churn, it responds to difficulty work, and it is a good deal smaller than the first group.</p>

      <p>We spent a release tuning the opening for a population that was not failing it.</p>

      <h2>The one number with a shape worth acting on</h2>

      <p>Out of everything we looked at, one measurement behaved differently.</p>

      <p>Take the first time a player is ever offered a rewarded video &#8212; in our case a rescue, triggered automatically when they stall rather than hunted for &#8212; and compare how often it is actually watched, by ordinal. The first one is far worse than the second. The second is worse than the third. It recovers from there, and keeps recovering.</p>

      <p>The shape is the finding, not the level. A flat line would mean players simply dislike video ads, and the fix would be to show fewer of them. A line that starts low and climbs means the first one is a <em>surprise</em>, and the fix is something you do once per player: say what is about to happen before it happens, and never again.</p>

      <p>That is a much cheaper intervention than rebuilding your ad strategy, and we would not have known to reach for it from the average.</p>

      <h2>The part where we hold it loosely</h2>

      <p>This reading is correlational too, and having just been caught by one correlation we are trying not to repeat the trick. Players who were already on their way out may tap and close, which would produce the same curve from the opposite direction.</p>

      <p>What argues against that: it is the only placement in the game that fires unprompted on a single tap; its completion rate is anomalously low against other placements running on the same ad stack; and the monotonic recovery by ordinal is hard to explain if the cause is the kind of player rather than the moment. The high ordinals are badly survivorship-biased &#8212; a player on their eleventh rescue has self-selected as someone who tolerates rescues. The first-attempt row is the clean one, because every player appears in it exactly once.</p>

      <p>So it is being tested rather than believed, and the test is a confirmation step, not a formality.</p>

      <h2>The generalisable bit</h2>

      <ul>
        <li><strong>A threshold in a correlation describes your users. It is not a lever on them.</strong> Before building against one, find a release that already moved it and check whether the outcome moved too.</li>
        <li><strong>Split your churn before you diagnose it.</strong> Ours looked like one curve and was two populations with opposite causes. The larger one was invisible because it leaves before it does anything you thought to measure.</li>
        <li><strong>Prefer findings with a shape.</strong> &#8220;This number is bad&#8221; tells you to improve it. &#8220;This number is bad and then recovers&#8221; tells you what <em>kind</em> of fix it is. The second is worth far more and costs one extra group-by.</li>
      </ul>

      <p>We kept the six-level work, for the record. The opening is better than it was, new players get further into it, and that is worth having on its own terms. It simply was not the retention fix, and we should not have needed the data to tell us twice.</p>

      <div class="tryit">
        <p>The game all of this is about is free, and the opening is the part we have rebuilt the most.</p>
        <a href="/">Play Wordmere</a>
      </div>

      <p class="endnote">We build <a href="/">Wordmere</a>, a cosy word game where the words you find assemble a small world around you. We publish the shapes of our numbers rather than the numbers themselves; the ratios and thresholds here are real, the absolute levels are ours to keep. These posts are the things that went wrong on the way.</p>"""),
dict(
 slug='word-search-answer-keys',
 date='2026-10-28',
 title='Word search generators print wrong answer keys',
 h1='Word search generators print wrong answer keys',
 sub='We switched off one check in our puzzle maker and ran it twenty thousand times. Thirty-seven per cent of the grids hid a word somewhere the answer key never mentioned.',
 desc='A word search is a grid and a separate answer key, built by different code. Here is the bug that makes them disagree, how often it fires, and the cheap fix.',
 body="""
      <p>A word search is two artefacts, not one. There is a grid of letters, and there is an answer key that claims where each word is hidden. They are produced by different code, and when they disagree the person who gets told they are wrong is a child with a pencil.</p>

      <p>Here is how they come to disagree.</p>

      <h2>The naive generator is almost right</h2>

      <p>Everyone writes the same one. Sort the words longest first. For each, find every position and direction where it fits without contradicting a letter already on the grid, prefer the positions that overlap something (crossings make a tighter, better-looking puzzle), place it, record where it went. When every word is down, fill the empty cells with random letters. Print the grid, print the key.</p>

      <p>That is our generator too, and it is correct right up to the last step, where the random letters get a vote.</p>

      <p>Say the puzzle contains <code>CAT</code>, placed across on row four. The key says row four. Three rows down, by pure chance, the filler has produced a <strong>C</strong>, an <strong>A</strong> and a <strong>T</strong> on a diagonal. There are now two CATs in the grid and exactly one of them is in the key. A child circles the other one, checks the answers, and your software tells them they are wrong.</p>

      <h2>It is not a rare bug</h2>

      <p>We can put a number on it, because the check that prevents it is one loop in our engine and the loop can be switched off.</p>

      <p>With it off: twenty thousand puzzles, eight to fifteen words each, every word three to six letters, all eight directions enabled. <strong>37.1% contained at least one word readable somewhere the answer key did not claim.</strong></p>

      <p>Broken down by word length, the picture gets sharper:</p>

      <ul>
        <li>Three letters: <strong>12.7%</strong> forged, out of 77,252 placements.</li>
        <li>Four letters: <strong>0.94%</strong>, out of 14,037.</li>
        <li>Five and six letters: <strong>zero</strong>, out of 137,475.</li>
      </ul>

      <p>The whole bug lives in short words, which is precisely why it is so easy to ship. Your test list is OTTER, BADGER, HERON, WILLOW, and you will never see it. The first person to make an animal puzzle for a five-year-old &#8212; CAT, DOG, COW, OWL, FOX &#8212; gets a one-in-three chance of a lying answer key.</p>

      <p>The arithmetic is not mysterious. A three-letter word needs three cells to line up. A fifteen-by-fifteen grid read in eight directions contains a few thousand three-cell runs, and every one of them is a lottery ticket. Buy enough tickets and you win something you did not want.</p>

      <div class="pull"><p>The change that made our puzzles look better also made them more likely to be wrong, and nothing about it looked like it touched correctness.</p></div>

      <h2>The cosmetic choice that doubles it</h2>

      <p>Our filler letters are not drawn uniformly from A to Z. They are drawn from the letters of the words being hidden.</p>

      <p>That is purely a looks decision. A uniform fill scatters J, Q and Z across a grid of farmyard animals, and they read as signposts &#8212; you can find the hidden words by looking for the patches that are suspiciously boring. Drawing the padding from the puzzle&#8217;s own letters fixes that completely.</p>

      <p>It also biases every single filler cell towards exactly the letters your target words are made of.</p>

      <p>Same twenty thousand puzzles, same seeds, uniform A&#8211;Z filler instead: <strong>20.6%</strong>. So the pretty version is roughly twice as likely to lie. And for longer words it is the difference between never and sometimes &#8212; in a separate run restricted to five- and six-letter words, the uniform fill produced not one forgery in twelve thousand puzzles, while the blended fill produced them in about one puzzle in fifty.</p>

      <p>That is the part worth carrying away. A change made entirely for appearance moved a correctness property, in the wrong direction, with no code review on earth likely to catch it.</p>

      <h2>The fix is cheap</h2>

      <p>After filling, for every word in the key, find every position in the grid where it reads &#8212; in all eight directions, not just the ones the puzzle is using, because a backwards word is still a word a child can circle. Any hit that is not the position in the key is a forgery. Take one of its cells that is filler rather than part of a placed word, change the letter, and look again.</p>

      <p>Repeat until clean, with a bound. The bound matters: changing a letter to clear one forgery can create another, so this is a loop and not a pass. In practice it settles in a handful of iterations. The guard exists so that a pathological word list cannot hang the browser tab.</p>

      <p>Run with the repair on, the same twenty thousand puzzles produce <strong>zero</strong> forgeries.</p>

      <h2>What the repair cannot do</h2>

      <p>Occasionally a forged copy contains no filler at all &#8212; every one of its cells belongs to some word you deliberately placed, which means two of your own words have spelled a third between them. There is nothing to change. The repair gives up, the whole layout is discarded, and we lay the puzzle out again from scratch, growing the grid if we have to.</p>

      <p>In those twenty thousand puzzles, that escape hatch never fired once. It is insurance, not a workhorse, and if you were trimming code you would be tempted to delete it. The reason it stays is that its absence is not a wrong answer. Its absence is an infinite loop.</p>

      <h2>The part where we tell you it is not perfect</h2>

      <p>We only check the words in the key. The grid is full of accidental other words &#8212; there is a RAT and an ARE and a TEN in very nearly every puzzle we produce &#8212; and we do not care, because the key has never claimed them. Nobody circles a word that is not on the list.</p>

      <p>A stricter generator would run a dictionary over the finished grid and refuse any real word anywhere. We deliberately do not. The puzzle makers load no dictionary at all; the words come from the person making the puzzle, and pulling a few hundred kilobytes of word list onto a page that never reads it costs about twenty Lighthouse points to solve a problem nobody has.</p>

      <p>The narrow failure is the one that matters: the key says a word is <em>here</em>, and it is also <em>there</em>. That is the only case where the software tells a correct person they are wrong.</p>

      <h2>The generalisable bit</h2>

      <p>Any generator that emits both an artefact and a description of that artefact has this bug available to it. The grid and the key. The build and the manifest. The image and its alt text. The migration and the schema dump. Two code paths, one claim, and nobody checking that they still agree.</p>

      <p>The check is almost always cheaper than the generator that needed it. Read your own output back, and confirm it says what you said it says. Ours runs on every build, over a fixed set of word lists and forty random ones, and it is the reason this post has numbers in it rather than an apology.</p>

      <div class="tryit">
        <p>The puzzle maker is free, runs entirely in your browser, and the answer keys are checked before you ever see them.</p>
        <a href="/tools/word-search-maker/">Make a word search</a>
      </div>

      <p class="endnote">We build <a href="/">Wordmere</a>, a cosy word game where the words you find assemble a small world around you. The same engine lays out our <a href="/tools/crossword-maker/">crossword maker</a>, which has <a href="/blog/crossword-adjacency-rules/">a different way of going wrong</a>. These posts are the things that went wrong on the way.</p>"""),
dict(
 slug='crossword-adjacency-rules',
 date='2026-10-28',
 title='The two rules that make a crossword a crossword',
 h1='The two rules that make a crossword a crossword',
 sub='Take either one out of our generator and the grids still look fine. Seventy-eight per cent and ninety-eight per cent of them respectively contain a run of letters nobody wrote a clue for.',
 desc='A crossword generator is easy to write and hard to write correctly. The gap is two adjacency rules, and here is what the grids look like without each of them.',
 body="""
      <p>A crossword generator is easy to write and hard to write correctly, and the gap between the two is two rules that are not obvious until you print one out.</p>

      <p>The easy part takes an afternoon. Take the longest word and lay it across. For each remaining word, look for a letter it shares with something already on the grid and place it at ninety degrees through that letter. Score the candidates &#8212; more crossings is better, and growing the bounding box less is better &#8212; take the best, repeat. The result looks like a crossword.</p>

      <p>Then you print it, hand it to somebody, and they get stuck on a row that reads <code>RIVEROTTER</code>.</p>

      <h2>Rule one: a word may not run straight into another word</h2>

      <p>The cell immediately before a word&#8217;s first letter, and the cell immediately after its last, must both be empty.</p>

      <p>It is easy to assume you get this for free, because every placement in a generator like ours has to cross something, and a crossing is perpendicular. But consider RIVER sitting across, ending at column nine. Now OTTER comes along, crosses some down word, and the arithmetic puts its first letter at column ten on the same row. Both words are legal. Both cross something. The row now reads RIVEROTTER, and the solver has to work out that it is two answers wearing a trench coat.</p>

      <p>With the rule removed, <strong>77.9% of three thousand generated grids contained at least one run of two or more letters that nobody had written a clue for</strong> &#8212; 4,197 such runs in total. A sample of the actual output: <code>RIVEROTTER</code>, <code>PEPPERICED</code>, <code>OTTERSCALA</code>, <code>PEPPERL</code>, <code>REEDH</code>.</p>

      <h2>Rule two: a letter that is not a crossing may not touch a neighbour side-on</h2>

      <p>This is the subtler one, and it is the rule people leave out.</p>

      <p>Take OTTER running across. Every one of its five letters has a cell above it and a cell below it. If the cell above the first T happens to be occupied by a letter belonging to some other word, then that column now contains a run of two letters &#8212; the T and whatever is on top of it &#8212; and that run is not an answer. It is not numbered. It is not in the clue list. It is just there, and the solver cannot tell it apart from a real entry.</p>

      <p>The exception is the entire point of the rule. At a crossing, touching is exactly what is supposed to happen. So the check has two branches, and they are opposites:</p>

      <ul>
        <li>If the cell we are about to write is <strong>already occupied</strong>, this is a crossing. The letter must match the one that is there, and the perpendicular neighbours are somebody else&#8217;s problem &#8212; they belong to the word we are crossing.</li>
        <li>If the cell is <strong>empty</strong>, this is a new letter of ours, and both of its perpendicular neighbours must be empty too.</li>
      </ul>

      <p>Those two branches are the difference between a crossword and a letter jumble.</p>

      <p>With the rule removed, <strong>98.0% of grids contained an unclued run</strong> &#8212; 19,119 of them across three thousand grids, which is about six per puzzle. The output is a blizzard of two-letter debris: <code>TS</code>, <code>MC</code>, <code>GL</code>, <code>PI</code>, <code>EE</code>. Each one is a place where two answers brushed past each other.</p>

      <p>With both rules in place: zero unclued runs in three thousand grids.</p>

      <div class="pull"><p>Both rules are local &#8212; one cell and its neighbours. Both of the failures they prevent are global. That mismatch is why you cannot test this inside the generator.</p></div>

      <h2>Why you do not notice</h2>

      <p>Because you look at the grid with all the answers in it, and your eye follows the words you intended to put there. The spurious runs are invisible to the person who placed the words and glaring to the person trying to solve them. We have all shipped a bug we were structurally unable to see.</p>

      <p>So the check cannot live in the generator&#8217;s head. It has to be a pass over the finished grid: walk every maximal run of two or more letters, across and down, and assert that each one is a word somebody wrote a clue for, that it is numbered, and that it appears in the lists. That single assertion is what separates a crossword from a jumble, and it is the one we run on every build.</p>

      <h2>The corner you paint yourself into</h2>

      <p>A related trap, since you will hit it immediately after fixing the first two. Greedy placement with a deterministic choice is a disaster: the first few words decide the shape of everything that follows, and the locally best opening move is very often the one that leaves nowhere to go.</p>

      <p>We try forty different orderings of the same word list, break near-ties in the scoring at random, and keep whichever grid fits the most words in the smallest bounding box. And a word that genuinely cannot cross anything &#8212; give the generator AAA, BBB and CCC and only one of them can be placed &#8212; is reported back as unplaced rather than quietly dropped. Silently losing a word is the other way a puzzle maker lies to you.</p>

      <h2>The part where we tell you it is not perfect</h2>

      <p>These two rules make a grid <em>legal</em>. They do not make it <em>good</em>.</p>

      <p>A newspaper crossword has properties ours does not: rotational symmetry, no unchecked letters (every square belongs to both an across answer and a down answer), a minimum entry length, and a single connected block of squares. We enforce none of that. What we produce is the free-form criss-cross grid you would print for a classroom or a party &#8212; every entry crosses at least one other, nothing reads that should not, and the overall shape is whatever the words gave us.</p>

      <p>Getting a symmetric, fully-checked grid needs a different algorithm entirely: start from a pattern of black squares and fill it, backtracking when you fail, with a dictionary to fill it from. That is a much larger program, and on a free tool where the words are supplied by the person making the puzzle it would solve a problem nobody brought us.</p>

      <h2>The generalisable bit</h2>

      <p>Both rules here are decisions about a single cell and its immediate neighbours. Both of the failures they prevent are properties of the finished grid that no individual placement is responsible for. Local rule, global failure &#8212; and when that is the shape of a problem, you need the rule in two places.</p>

      <p>Put the rule where the decision is made, so the generator cannot produce the bad thing. Put the proof where the artefact is finished, so you find out when the rule was wrong. Neither is sufficient on its own. A generator whose rules you trust but whose output you have never read back is a well-commented guess.</p>

      <div class="tryit">
        <p>The crossword maker is free and runs in your browser. Type your words and clues, and it will tell you if one of them could not be placed.</p>
        <a href="/tools/crossword-maker/">Make a crossword</a>
      </div>

      <p class="endnote">We build <a href="/">Wordmere</a>, a cosy word game where the words you find assemble a small world around you. The companion to this one is <a href="/blog/word-search-answer-keys/">the bug that makes word search answer keys wrong</a>, which comes from the same engine and the same lesson. These posts are the things that went wrong on the way.</p>"""),
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
      <h2>What this is</h2>
      <p>No roadmap, no release notes, no announcements. Each of these is one specific thing that went
        wrong while we were building a word game, written up properly: what broke, how often, what we
        did about it, and what the fix still does not handle.</p>
      <p>The <a href="/tools/">word tools</a> are free and the <a href="/">game</a> is the thing all of
        this is in aid of.</p>
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
