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
 slug='android-dev-launcher-leak',
 date='2026-11-10',
 updated='2026-11-10',
 title='We shipped a barcode scanner in a word game',
 h1='We shipped a barcode scanner in a word game',
 sub='For fifteen builds our Android app carried a barcode reader, two unused font families and a GraphQL client. We had written the line that was meant to keep them out.',
 desc='Fifteen Android builds shipped the Expo dev launcher despite an exclude rule, because the Gradle plugin joined the whole exclude list into one argument.',
 body="""
      <p>Our download was 77 MB. It is now 47 MB, and nothing was removed that any player could see.</p>

      <p>About five of those megabytes were a development tool that should never have been in a store build at all. It had been there for fifteen consecutive releases. We had written the configuration line that excludes it, we could point at that line, and the line did nothing whatsoever.</p>

      <h2>What was actually in the download</h2>

      <p>The thing shipping was Expo's dev launcher — the in-app menu you use while developing, which has no business in a release. It does not travel light. It brought Jetpack Compose, an Apollo GraphQL client, two font families, and Google's ML Kit barcode scanning models.</p>

      <p>It also registered an initialiser that ran at every launch. So every player opening a word game was, briefly, starting up a barcode reader.</p>

      <p>I want to be clear that this is not an exotic failure. We had done the documented thing. There is an <code>exclude</code> list in the Gradle configuration, the dev launcher was on it, and we had shipped fifteen builds in the comfortable belief that this was handled.</p>

      <h2>The exclude line that did nothing</h2>

      <p>Expo's Gradle plugin passes that exclude list to a command-line tool. The helper it uses to build the command takes a key and a list of values, and it joins the list into <em>one</em> argument.</p>

      <p>So a list of four package names arrived at the CLI as a single package name with spaces in it. Nothing matches a package called "a b c d", so nothing was excluded, and no error was raised — an exclude list that matches nothing is indistinguishable from an exclude list that had nothing to do.</p>

      <p>The fix is four lines in a patch against that package: split on whitespace. We spent considerably longer being sure that was really the cause than fixing it, because the first three theories were wrong. It looked like a Gradle ordering problem, then a stale daemon, then a build-variant mix-up. It was none of those.</p>

      <div class="pull"><p>A configuration that silently matches nothing looks exactly like a configuration that is working. That is the whole problem with exclusions.</p></div>

      <h2>Why our build script never caught it</h2>

      <p>We did have a check. The release script grepped the compiled dex for the dev launcher's class names, found nothing, and reported the build clean.</p>

      <p>It found nothing because R8 had renamed those classes. Our minifier was hiding the thing our check was looking for, every single time, and the check reported success for fifteen builds.</p>

      <p>What works is grepping the built artefact for strings that <em>survive</em> minification — the barcode library's native name, a bundled font file name, the initialiser's manifest entry. Those are resources and manifest entries, not classes, so nothing renames them. The release script now hard-fails on any of them, which means this particular mistake cannot ship again even if the exclude breaks a second time.</p>

      <h2>The other twenty-five megabytes</h2>

      <p>The dev launcher was the embarrassing find, not the biggest one.</p>

      <p>Our world-card artwork shipped four image layers for each of ninety-five worlds, and the component only ever draws one of them. The other three had been designed for a parallax effect that was cut long before launch. That was the single largest item on the list.</p>

      <p>Then the fonts. A theme file imported from a font package's top-level barrel, which pulls every weight of every family in it. Fifty-five font files shipped; nine were used.</p>

      <p>On iOS the JavaScript bundle carried nearly five megabytes of Hermes debug information, because the build was not told where to write a source map, so it kept the debug data inline instead. And a handful of images were shipping at 1024 px to be drawn at 72 pt.</p>

      <p>None of these is clever. They are all the same shape: something was configured once, the reason for it went away, and nothing in the pipeline measures the result.</p>

      <h2>What we did not take out</h2>

      <p>We left an ad network in place that costs a couple of megabytes and earns a small single-digit share of revenue on one platform. On paper it is the easiest remaining win. In practice removing a bidder changes the auction for the bidders that stay, and we were not confident enough about the second-order effect to trade it for two megabytes.</p>

      <p>We also left a set of unused social-SDK components alone. The patch to strip them was written and then parked, because the gain was about a megabyte and the change touched the login and sharing paths, which are exactly the paths you do not want to debug remotely after a release.</p>

      <p>Thirty megabytes was enough. The last five would have cost more than they were worth.</p>

      <h2>Is it worth doing at all?</h2>

      <p>Google's own rough guidance is that install conversion moves about a percentage point for every six megabytes. If that holds for us, thirty megabytes is a meaningful change to how many people who tap install actually get the game. We have not been able to measure it cleanly, because the size change shipped in a build that also changed other things, which is a mistake we keep making and keep writing down.</p>

      <p>What I am confident about is narrower and duller: a word game should not contain a barcode scanner, and we could not have told you it did.</p>

      <h2>Grep the artefact, not the config</h2>

      <p>Every check we had was reading our intentions. The exclude list said the right thing. The build script looked for the right class. Both were describing what we meant rather than what came out.</p>

      <p>Unzip the thing you are about to upload and look inside it. Search for strings that minification cannot touch. If you cannot explain why a file is in there, that is the finding — you do not need a size budget or a tool, just the willingness to open the box.</p>"""),
dict(
 slug='daily-puzzle-omissions',
 date='2026-11-10',
 updated='2026-11-10',
 title='Our daily puzzle left out words for 347 days',
 h1='Our daily puzzle left out words for 347 days',
 sub='A player swipes a word that is plainly there on the wheel, the game says no, and something breaks between you. We had been doing that on almost every day of the year.',
 desc='Our daily puzzle omitted at least one obvious word on 347 days out of 365. The generator kept the twelve commonest words rather than all the good ones.',
 body="""
      <p>The message said the daily was awful, that loads of common words were not part of it. That is the kind of complaint that is easy to wave off, because every word game gets it constantly and it is usually wrong. People swipe words that are not words.</p>

      <p>This time there was a screen recording, and on it the rack does not move. The player swipes <code>PLAY</code>. Nothing. <code>PRAY</code>. Nothing. <code>RELY</code>. Nothing. Three ordinary words, all spellable from the letters on screen, all rejected.</p>

      <h2>Twenty-one words, twelve kept</h2>

      <p>The daily is built from a wheel of letters. A generator works out which words that wheel can spell, and the rack — the row of blanks you are filling in — is the list it decides to ask for.</p>

      <p>That generator was taking the twelve commonest words and stopping. The day in the recording had a wheel spelling twenty-one perfectly ordinary four-to-six-letter words. Nine of them were simply not asked for, and swiping any of the nine got you a rejection.</p>

      <p>From the player's side there is no way to tell that apart from a broken game. The dictionary looks wrong. In a sense it was.</p>

      <h2>A floor that cut the wrong words</h2>

      <p>Two of the missing words had a second, separate problem. The generator also applied a frequency floor, dropping anything below a commonness threshold, and <code>PAYER</code> and <code>REPAY</code> both fell under it.</p>

      <p>A frequency floor is a reasonable idea. It is there to stop the puzzle demanding words nobody says. But commonness scores are built from written corpora, and they are unreliable in exactly the band a word game lives in — ordinary, short, slightly dull words that people use constantly and write down rarely. The floor was tuned to keep obscurity out and was quietly taking everyday words with it.</p>

      <div class="pull"><p>A word you omit is not a gap in a list. It is a swipe the player makes, and a rejection they get back, and a reason to stop believing the game.</p></div>

      <h2>How often: nearly always</h2>

      <p>Having found it on one day, the obvious question was how many days. We had a year of generated puzzles sitting in the repository, so this was a script rather than an investigation.</p>

      <p>Three hundred and forty-seven days out of three hundred and sixty-five left off at least one obvious word. Two hundred and seventy-nine left off three or more.</p>

      <p>I had assumed we would find a bad week. It was the whole year, and it had been shipping daily the entire time.</p>

      <p>Nobody caught it because each individual day looks fine. You open the puzzle, you solve the twelve words it asks for, and you never learn about the nine it did not. The failure is only visible to a player who tries a word that should work — which is to say, the more fluent the player, the worse the game looked.</p>

      <h2>The rule we replaced it with</h2>

      <p>The new rule has no quota in it at all. The rack is <em>exactly</em> the set of obvious words the wheel spells, in the length range the daily uses. Not the top twelve of them. All of them.</p>

      <p>That inverts which thing gets rejected. Previously, if a wheel spelled too many good words, we trimmed the words. Now, if a wheel spells a set we cannot ask for in full, we throw away the wheel and pick a different one. There are plenty of wheels; there is only one first impression of a daily puzzle.</p>

      <p>Concretely: a wheel is usable only if its obvious set lands between nine and twelve words with at least two long ones. Everything else is discarded at generation time. The whole year was rebuilt against the new rule — about a hundred wheels, with the puzzle identifiers kept stable so nobody's streak broke — and an audit script now has to report zero omissions before the content can be regenerated at all. There is a test pinning it.</p>

      <h2>Why this is the opposite of our last dictionary problem</h2>

      <p>We wrote earlier about a <a href="/blog/word-list-problem/">dictionary that accepted nonsense</a> — our own tool confidently recommending a word that is not a word. This is the mirror image, and it is the more damaging of the two.</p>

      <p>Accepting a junk word costs a player a moment of confusion and a small amount of trust in the word list. Rejecting a real word costs you the player's belief that the game is working, and they are not wrong to lose it. One failure makes the game look generous and sloppy. The other makes it look broken.</p>

      <p>If you are building the same thing and have to choose which way to err, err towards accepting. It is the cheaper mistake by a wide margin.</p>

      <h2>What the rule costs us</h2>

      <p>Throwing away wheels that spell too much means the pool of usable wheels is a lot smaller than it was, and it will eventually bind — a year is fine, several years of unique dailies is a different problem that we have not solved.</p>

      <p>The rule also does nothing about a separate category of complaint. Our word bank tiers some genuinely odd words as "obvious" — a handful of archaic or technical entries that our frequency data rates far higher than any person would. Those now get <em>included</em>, correctly by the rule and wrongly by any human standard, and the daily asks for them. That is a problem in the word bank's tiering, not in this rule, and fixing it there is the right place rather than adding a second exception list here.</p>

      <p>And the daily still refuses three-letter words by design. A player swiping <code>LAY</code> gets a rejection, exactly like the one that started all this. The difference is that it now says so explicitly rather than failing silently, which is the least we can do while the rule stands.</p>

      <h2>Count the words you did not ask for</h2>

      <p>The generalisable bit is a one-line audit, and I would run it against any generated puzzle content.</p>

      <p>For every puzzle you ship, compute the set of valid answers the player can plausibly find, subtract the set you actually ask for, and look at the size of the difference. If it is not zero, those are rejections waiting to happen, and your players will find them long before your dashboards do.</p>"""),
dict(
 slug='ios-app-switcher-no-event',
 date='2026-11-10',
 updated='2026-11-10',
 title='There is no event for swiping an app away',
 h1='There is no event for swiping an app away',
 sub='We had a metric meaning "the app vanished during a video". It took three analyses to work out that it meant at least three different things.',
 desc='On iOS a swipe from the app switcher goes to inactive, never background, so it leaves no trace at all. Our crash metric was three behaviours under one name.',
 body="""
      <p>Of the rewarded videos our players started one week, well under half ended with the app still running. The rest were followed by a cold launch. We had an event for it, and the event was called <code>rewarded_ad_lost</code>.</p>

      <p>The name was doing a lot of work it had not earned.</p>

      <h2>First reading: we are crashing</h2>

      <p>The obvious interpretation is that the app is dying under the ad. The timing supported it — most of the losses happened within thirty seconds of the video opening, with a median around ten. We had a plausible mechanism too: the game renders a 3-D scene behind the UI, and that scene kept rendering underneath every full-screen ad, because the hook that pauses it only reacted to a real background transition.</p>

      <p>A memory-hungry renderer running under a video player on a phone is a good story. We wrote a fix, which pauses the scene whenever an ad goes up.</p>

      <p>The fix was worth shipping. The story was wrong.</p>

      <h2>Second reading: people are leaving on purpose</h2>

      <p>Crashlytics had nothing. Not a reduced number of reports — nothing at all, for a failure supposedly affecting a large share of our ad views.</p>

      <p>That is explicable: if the operating system kills your process for using too much memory, that is not a crash and no crash reporter will see it. But it meant the crash theory had no independent evidence, so we went back to the raw event stream and looked at what the sessions actually did.</p>

      <p>Most of the lost videos were followed by a background transition and a relaunch within a minute. A large share of those had our own explicit backgrounding event attached. That is not a process being killed. That is a person leaving the app, waiting out the video they did not want to watch, and coming back.</p>

      <p>So we rewrote the conclusion: around a third of full-screen ads were being escaped by players quitting out of them.</p>

      <h2>The correction</h2>

      <p>When this went to the founder, his reply was that he did not think all of these would be crashes. He was right, and more usefully he was right about a subset I had been confident about.</p>

      <p>I had split the losses into "left on purpose" and "hard deaths", putting anything with no leave signal in the second bucket. More than a hundred interstitial losses had no leave signal at all, and I had called those real crashes.</p>

      <p>They were not. On iOS, swiping an app away from the app switcher does not produce a background transition. The app goes to <code>inactive</code> and is then terminated. <code>inactive</code> is the state you also get for a phone call, a notification pulled down, or Control Centre — it is not a lifecycle event you would normally log, and we were not logging it.</p>

      <p>So a deliberate force-quit and an out-of-memory kill look identical in our data. Both are: last event, then nothing, then a cold start.</p>

      <div class="pull"><p>Absence of a leave signal is not evidence of a crash. On iOS it is the expected shape of the most deliberate exit a player can make.</p></div>

      <p>What settled it was looking at who those sessions belonged to. Almost all of the supposed hard deaths came from players who also quit ads in ways that <em>did</em> leave a signal. People who had never once quit an ad produced almost none of them. A behaviour that clusters in the players who demonstrably do that behaviour is that behaviour, not a crash that happens to prefer them.</p>

      <h2>Third reading, and the one that stuck</h2>

      <p>A later analysis moved it again, and this is the version we now believe.</p>

      <p>On the newest iPhones the pattern is much tighter than "a person decides to skip". The app leaves the foreground a median of about three seconds after the video opens — too fast to be a decision about content nobody has seen yet — then cold-starts a few seconds later, and most of the time the player immediately taps the same video again. Those players come back the next day at a <em>higher</em> rate than average, which is not what people who are sick of your ads do.</p>

      <p>That is not skipping. That is the player force-quitting an app that has gone unresponsive behind an ad that never appeared, and then trying again because they wanted the reward. The share doing it had been climbing with every build since the summer.</p>

      <p>Three readings, three different mechanisms, one event name.</p>

      <h2>What we still cannot separate</h2>

      <p>We have not closed this. The data still cannot distinguish a force-quit from a memory kill, because iOS genuinely does not tell you, and we should be honest that the third reading rests on timing and on return behaviour rather than on a signal that says what happened.</p>

      <p>Two things would fix it and we have shipped neither. Logging the <code>inactive</code> transition itself would at least mark the sessions where the app was alive at the moment it disappeared. MetricKit reports memory-limit terminations after the fact, which is the only first-party way to confirm the kills. Until one of those is in, "the app went away" remains a category rather than a cause.</p>

      <p>The scene-pause fix stayed in, incidentally. It is a reasonable thing to do for battery and heat regardless of whether it fixes anything else, and we removed the stability claim from the release notes once we knew it was not one.</p>

      <h2>Two signals that will mislead you</h2>

      <p>If you are instrumenting this on iOS, two specific traps cost us time.</p>

      <p>Firebase's <code>user_engagement</code> event looks like a session-boundary signal and is not. It fires on every screen change, so a session full of them tells you nothing about backgrounding.</p>

      <p>And the generic uncaught-exception event that crash reporting SDKs expose effectively never appears for real devices in our data. If you are watching it as a safety net, you are watching a line that stays at zero through every category of failure described above.</p>

      <h2>Name the event for what you saw</h2>

      <p>The mistake was upstream of all the analysis, and it was the name.</p>

      <p><code>rewarded_ad_lost</code> encodes a conclusion. Everyone who read it, including me, started from "we lost the app" and went looking for the cause of a loss. Had it been called something flatter — we started a video and never observed it ending — the first question would have been what else could produce that, which is the question that actually took three attempts to ask.</p>

      <p>Name events after the observation. Keep the interpretation in the analysis, where it can be wrong out loud and corrected, instead of baking it into a string that every future reader will inherit.</p>"""),
dict(
 slug='xcode-27-ios-27-launch',
 date='2026-11-10',
 updated='2026-11-10',
 title='A new Xcode shipped an app that could not launch',
 h1='A new Xcode shipped an app that could not launch',
 sub='The first build we made with the new Xcode died at launch on every device running the new iOS. Nothing of ours ran, so nothing of ours reported it, and it read as churn.',
 desc='Our first Xcode 27 build crashed at launch on every iOS 27 device. No code of ours ran, so it reached neither analytics nor crash reporting. It read as churn.',
 body="""
      <p>We found it on a phone in the house. Someone updated to the new iOS, opened the game, and it closed itself. Reinstalling did not help.</p>

      <p>Our dashboards showed nothing wrong, and they were not broken. They were telling the truth about a population that no longer included anyone this was happening to.</p>

      <h2>A trap before any of our code</h2>

      <p>The phone had analytics sharing turned off, so there was no report from it. We reproduced it on a simulator running the same OS version and got a crash log within a minute.</p>

      <p>The process died on a <code>SIGTRAP</code> inside a system function whose name says exactly what it is for: the runtime check for an app that has not adopted the scene lifecycle. The new iOS refuses to run an app that is linked against its SDK and still uses the old, pre-scene application lifecycle. It does not warn. It traps, at launch, before any application code executes.</p>

      <p>That last part is the whole story. Not one line of ours ran. No analytics initialisation, no crash reporter, no remote config fetch. From our side the device simply stopped existing.</p>

      <h2>Why a working app broke without us touching it</h2>

      <p>Nothing about our lifecycle code had changed. What changed was the machine that built it.</p>

      <p>The build in question was the first store build we had made with the new major version of Xcode. A new Xcode means a new SDK, and linking against a new SDK is how the operating system decides which generation of rules to hold you to. Everything we had shipped before was built against the previous SDK and was exempt — so players on the new iOS running our *older* release were completely fine, and players who had taken our newest update were locked out.</p>

      <p>Updating the app was the thing that broke it. Staying behind was the safe choice. That is an unpleasant inversion to discover from a phone on your kitchen table.</p>

      <div class="pull"><p>The compiler upgrade was the change. Nothing in the diff for that release had anything to do with it, which is why nothing in the diff was ever going to explain it.</p></div>

      <h2>The cohort that looked like it left</h2>

      <p>Work out who this hit and the shape is nasty. Every player who had our newest build and then updated their phone disappeared from our data on the day they updated, permanently, with no event marking the transition.</p>

      <p>In every retention report, those people are churn. They look exactly like players who got bored. The only way to tell the difference is to go looking at retention split by OS version and build, which nobody does routinely because it is a strange thing to suspect.</p>

      <p>We have written before about a <a href="/blog/crash-free-rate-denominator/">crash-free rate that was measuring the wrong population</a>. This is the same disease with the symptom inverted. There, phantom sessions were dragging a number down. Here, the affected sessions vanished entirely and every number looked healthy. A metric that only sees the people your code reaches cannot report on the people it does not.</p>

      <h2>What the fix actually is</h2>

      <p>Adopting the scene lifecycle on a React Native app is a config plugin plus a small Swift file. You declare a scene manifest in the app's property list, and you add a scene delegate that creates the window and starts React Native inside the callback for a scene connecting, rather than in the old application-did-finish-launching path. The application delegate keeps the things that genuinely belong to the process — analytics and attribution initialisation — and deep links get forwarded through to the new entry point.</p>

      <p>It is about an hour of work once you know. Our plugin is unit-tested against the real generated delegate file rather than a fixture we wrote ourselves, which matters because the generated file changes between framework versions and a fixture would quietly stop representing it.</p>

      <h2>The fix build that shipped without the fix</h2>

      <p>This is the part worth the post.</p>

      <p>We wrote the plugin, built, and sent it out. It still died. The plugin had not run, because the app configuration edit that registers it had not landed properly, and nothing anywhere in our pipeline checks that a config plugin actually took effect. The build succeeded. The archive validated. The app was byte-for-byte as broken as before.</p>

      <p>Config plugins are code that edits generated native projects during a build you do not watch. They can silently not apply. So the release script now opens the built app, reads the property list, and refuses to continue if the scene manifest is not there.</p>

      <p>That is the same lesson as several other things that have bitten us: assert against the artefact, not against the source that was supposed to produce it.</p>

      <h2>Getting word to people whose app will not start</h2>

      <p>There is a genuinely hard problem underneath the bug. The affected players could not be reached by remote config, because remote config is fetched by our code and our code never ran. There is no in-app message surface in an app that cannot launch.</p>

      <p>Push notifications were the only channel left, since those are handled by the system before the app starts, and we used them — targeted at the specific broken build — to tell people an update was waiting. It worked for the minority who had granted notification permission. For everyone else there was no mechanism at all; they got the fix whenever they happened to update.</p>

      <p>If you take one operational thing from this: the population you most need to reach in an emergency is the one your own tooling is least able to reach, and push permission is the only lever that still works when the app itself is dead.</p>

      <h2>Install the new simulator on day one</h2>

      <p>The preventable version of this is cheap and we were not doing it.</p>

      <p>When a new major OS and a new major Xcode appear, install the matching simulator runtime and launch your existing app on it before you ship anything built with the new toolchain. Not a test suite — just open the app and see it draw a screen. The crash reproduced on the first try on a simulator that took ten minutes to download.</p>

      <p>A new Xcode major is not a build-tooling upgrade. It is an opt-in to a new set of operating system rules, applied the moment the build is linked, and the first thing it can take away from you is launch.</p>"""),
dict(
 slug='notification-ask-timing',
 date='2026-11-10',
 updated='2026-11-10',
 title='We asked for notifications earlier and got fewer',
 h1='We asked for notifications earlier and got fewer',
 sub='Our permission ask sat behind a level about half of new players never reach. Moving it earlier is the obvious fix. We shipped it, and it halved the number who said yes.',
 desc='We moved our notification permission ask earlier so more players would see it. Many more saw it, far fewer granted it, and grants per install roughly halved.',
 body="""
      <p>Notifications are how you get a lapsed player back. If you never got permission, there is no mechanism — no email, no address, nothing. For a free game it is close to the only re-engagement channel that exists.</p>

      <p>Ours was gated behind reaching level six.</p>

      <h2>The gate sat exactly on the cliff</h2>

      <p>Separately, we had worked out that first-session depth is the strongest early predictor we have. Players who get past about half a dozen levels in their first sitting come back at roughly double the rate of players who stop short of that, and the effect keeps climbing with depth.</p>

      <p>The uncomfortable corollary is that around half of new players never reach six levels at all. They are the ones most likely to drift away, and they are therefore the ones we would most want to be able to reach later.</p>

      <p>And the ask was gated at six. The people who most needed a recovery channel were precisely the people never offered one. Written down like that it is not a subtle problem, and the fix is not subtle either: move the ask earlier.</p>

      <h2>What we changed</h2>

      <p>We moved it to level three, behind a remote-config key so it could be reverted without a release. Everything else stayed the same — the same soft prompt, the same wording, the same flow into the system dialog.</p>

      <p>The expectation was straightforward. Many more people would see the ask. Some fraction of those would say yes. The fraction might be a bit lower, because they were less invested, but the much larger denominator would more than cover it.</p>

      <p>Exactly half of that happened.</p>

      <h2>More asks, fewer grants</h2>

      <p>Far more people saw it. Of those, nearly three quarters declined the soft prompt — a much worse rate than at level six.</p>

      <p>The part that mattered: grants per install roughly halved. Not "grew more slowly". We ended up with about half as many players reachable by notification as before the change, having shown the ask to several times as many people.</p>

      <p>The conversion of the system dialog itself did not move at all. Everyone who got as far as Apple's actual permission alert said yes at the same rate as before. The entire loss was in the soft prompt, on players who had been in the game for about ninety seconds.</p>

      <div class="pull"><p>We did not convert fewer people because fewer saw the ask. We converted fewer because showing the ask to an uninvested player is how you spend it.</p></div>

      <h2>One shot, and the soft prompt spends it</h2>

      <p>Here is the mechanism we had not taken seriously.</p>

      <p>A soft prompt — your own screen, asking whether the player would like reminders, before you trigger the real system dialog — is the standard pattern, and the reason for it is sound: the system dialog can only be shown once, ever, so you use your own screen to avoid burning it on a no.</p>

      <p>But our soft prompt was also effectively one-shot. A player who declined it was not asked again. Of several hundred players who declined that soft prompt, exactly one ever went on to see the system dialog.</p>

      <p>So the soft prompt was not protecting the permission. It was consuming it, on our own terms, at a moment we had chosen badly. We had built a mechanism to avoid spending a scarce resource too early and then spent the resource with it.</p>

      <h2>The number we had been quoting was the wrong one</h2>

      <p>Worse, we had been reporting this well for months without noticing.</p>

      <p>The opt-in figure in our own reporting was the conversion of the system dialog — of people who reached Apple's alert, what share tapped Allow. That number was healthy and it was real. It was also conditional on three earlier steps, every one of which lost people.</p>

      <p>Measured the way that actually matters — of everyone who installed the game, how many are reachable by notification — the true figure was a small fraction of the one we had been quoting. Roughly a fifth of it.</p>

      <p>Neither number is wrong. One answers "is our permission alert well-timed", the other answers "can we reach our players", and we had been using the first to feel good about the second.</p>

      <h2>We could not see the top of the funnel</h2>

      <p>One reason this ran as long as it did: the event that fires when the soft prompt is shown was firing zero times.</p>

      <p>It had been added to one of the two code paths that can trigger the ask. The other path — the one most players actually hit — consumed the prompt without logging it. So for months we had grant counts and dialog counts and no idea how many people had been asked, which is the denominator the whole question turns on.</p>

      <p>It is an unglamorous class of bug and I suspect it is extremely common. If an event's count is exactly zero, that is not a quiet signal. It is a broken one.</p>

      <h2>Where this reasoning breaks</h2>

      <p>We reverted to level six, and I want to be careful about what that decision does and does not prove.</p>

      <p>We tested the old prompt, earlier. We did not test a <em>better</em> prompt earlier. Our soft prompt at the time said very little about why anyone would want notifications, and asking a stranger ninety seconds into a game for a vague benefit is a weak offer at any level. It is entirely possible that a benefit-led prompt — tied to a streak the player can see they are about to start, or a daily reward that is visibly waiting — converts fine at level three. We have not run that, so the honest conclusion is narrower than "ask later".</p>

      <p>It is also one game and one audience. Puzzle games are not social apps; a player with no friends in the game has less obvious reason to want a push, and the result may not transfer.</p>

      <p>And the original problem is still there, untouched. Half of our new players still leave with no way for us to reach them. Reverting the gate restored the grant rate; it did nothing at all about the people behind the cliff. The real fix is to get more players past six levels, which is a content problem, and much harder than moving a number in a config file.</p>

      <h2>Ask at investment, not at reach</h2>

      <p>The thing I would carry to another product is that permission asks are not an impressions game, even though every instinct says they are.</p>

      <p>Reach and conversion are not independent here. The earlier you ask, the more people see it and the worse they convert, and because the ask is one-shot, a bad ask is not a neutral outcome — it permanently removes that player from the pool. Showing it to twice as many of the wrong people does not get you more grants. It gets you fewer.</p>

      <p>Before moving any permission prompt, work out what the player has at stake at that moment. If the honest answer is nothing yet, you are not widening the funnel. You are spending it.</p>"""),
dict(
 slug='idle-animation-loops',
 date='2026-11-06',
 updated='2026-11-06',
 title='One animation loop costs the same as ten',
 h1='One animation loop costs the same as ten',
 sub='Left on a desk, our game kept redrawing sixty times a second. We switched off one of the eight animations running on that screen and measured again. Nothing moved.',
 desc='Our idle game screen drew 60 frames a second. Switching off one of its eight animation loops saved nothing — the cost is per screen, not per animation.',
 body="""
      <p>Leave Wordmere open on a table and walk away. Nothing moves that you would really notice. A letter chip swells slightly and settles. A disc breathes. A flame flickers on the streak counter. The screen looks still.</p>

      <p>It was drawing sixty frames a second, indefinitely, and spending about a third of a CPU core to do it.</p>

      <p>That is the sort of thing that surfaces as a one-star review about battery on a four-year-old Android phone and surfaces nowhere else. So in October we sat down to measure it properly, expecting to come away with a ranked list of expensive animations to go and fix. We got something more useful and a lot less convenient.</p>

      <h2>Eight loops, and switching one off changed nothing</h2>

      <p>First we counted the infinite loops on the two screens people actually sit on. A level has the letter-chip breath, the disc breathe, an idle nudge that starts after six seconds and then runs forever, and a rescue cell that spins and pops once you have stalled. Three more appear only in certain states: a halo on the plane, the ads-free slot, the piggy pill. The home screen has two, the streak flame and the daily tile's flip and glow.</p>

      <p>Then we switched them off one at a time and measured every configuration.</p>

      <p>Switching off a single loop while any other was still running saved approximately nothing. Not a small amount — an amount we could not separate from the noise in the measurement. Switch all of them off and the screen dropped to zero frames per second and two to five per cent of a core. Switch any one of them back on, it genuinely did not matter which, and we were back to drawing on every vsync at twenty-five to thirty-five per cent.</p>

      <p>I had assumed the cost would be roughly proportional to the number of animations running. It is not proportional at all. It is a step, and the step is at one.</p>

      <h2>Why the saving is not additive</h2>

      <p>This is obvious once you have seen it, which is the most irritating kind of obvious.</p>

      <p>A frame is a whole-screen unit of work. Once anything has invalidated the view for this vsync, the pipeline does its pass — layout, draw, upload, composite — more or less regardless of how much of the screen actually changed. The second animation is joining a frame that was going to be drawn anyway, so it is close to free. The first one is not, because the first one is what turns the frame on.</p>

      <p>So "how expensive is this animation" is the wrong question to profile. The expensive thing is not any particular animation. It is the existence of any animation at all, and one loop makes that decision on behalf of the entire screen.</p>

      <p>Which is why per-component optimisation cannot help you here. You can make every animation on the screen twice as efficient and save nothing worth measuring, because you have not changed the number of frames.</p>

      <div class="pull"><p>The cost is not in the animation. It is in the decision to draw a frame at all — and a single loop makes that decision for everything else on the screen.</p></div>

      <h2>The measurement I had to throw away</h2>

      <p>A study we had run a few weeks earlier, looking at a video backdrop, reported the home screen holding 72 to 76 frames a second. Two things are wrong with that sentence and I wrote it.</p>

      <p>The capture windows labelled "Home" were not the home screen. They were level 2. Wrong screen, confidently labelled.</p>

      <p>The other problem is worse, because it was visible on the page. A 60 Hz display cannot show you 76 frames a second. That number should have stopped me cold, and instead it sat in a table for a month looking like data. It was an artefact of how we were counting frames; the real figure was about sixty.</p>

      <p>What caught it in the end was the new study producing clean zeros. Zero is a hard number to arrive at by accident, and once we had one we could see that the earlier table had never been measuring what it claimed.</p>

      <h2>Kill switches beat rebuilds</h2>

      <p>None of this would have been practical with a normal build loop. Eight loops is a lot of combinations, and if each one costs you a twenty-minute native build you will measure three of them and reason your way to the rest. Reasoning your way to the rest is exactly how we got the 76 fps table.</p>

      <p>So we built two bits of throwaway tooling first. A deep link that toggles individual loops at runtime, roughly <code>wordmere://qa-idle?off=wheel,flame</code>, and a script that injects a fresh JavaScript bundle into an already-built APK. Together those turned a configuration change from a rebuild into about thirty seconds.</p>

      <p>While we were in there we found four animated components still sitting in the tree that nothing imports any more. They cost exactly nothing, because they never render. We had been carrying them for months and would have happily profiled them.</p>

      <h2>Settling, not deleting</h2>

      <p>The blunt fix is to delete animations. That is a product decision wearing a performance costume, and the breathing chips are part of how the game feels to play. We did not want to pay for battery with character.</p>

      <p>What shipped instead is a screen-wide idle rule. Every loop rests fifteen seconds after the last touch. The hint nudge pulses three times rather than forever. The flame burns for four seconds. The daily tile flips once instead of on a cycle. Touch anything and the whole screen wakes up.</p>

      <p>On the emulator a level now sits around fifty frames a second while you are playing, falls to zero fifteen seconds after you stop, and returns to sixty-two the instant you tap. The home screen reaches zero about four seconds in, once the flame has finished. Both platforms behave the same way.</p>

      <p>One detail worth knowing if you use Reanimated: <code>withRepeat</code> already respects the system Reduce Motion setting by default. Every player who had that switch turned on had been getting the idle behaviour free the entire time. We had shipped a battery feature by accident and filed it under accessibility.</p>

      <h2>What this does not fix</h2>

      <p>The figures above are emulator figures, on API 35. The shape of the result holds — all-or-nothing is a property of how frames work, not of that machine — but do not expect the percentages to match a real handset.</p>

      <p>It does nothing at all for anyone actively playing, and that is on purpose. During play the screen should animate. We only fixed the case where the game is open and nobody is touching it, which happens more than you would think: a level left on screen while someone answers the door, the home screen while they decide whether to keep going.</p>

      <p>It also leaves two things alone. The video backdrop is a separate problem that we measured separately. And the music costs three to five per cent of a core on its own, which no amount of frame work touches.</p>

      <p>Finally, an honest deduction from our own result: animations built as a burst followed by a hold were already cheap, because a hold draws no frames. Some of what we "fixed" was not costing much to begin with. The win came from the loops that never stopped, not from the ones that paused.</p>

      <h2>Measure the screen, not the component</h2>

      <p>If you are profiling a UI with several animations running, measure configurations rather than components. The question "which of these is the expensive one" may simply have no answer, and you can lose a week looking for it.</p>

      <p>The question that does have an answer is how many frames the screen draws when nobody is touching it, and what the smallest change is that takes that number to zero.</p>

      <p>Zero, not fewer. Fewer frames is a different and much worse outcome, because it costs you the same wake-ups and gives you a visibly choppier animation. Either the screen is alive or it is asleep.</p>"""),
dict(
 slug='crash-free-rate-denominator',
 date='2026-11-04',
 title='Your crash-free rate is lying to you',
 h1='Your crash-free rate is lying to you',
 sub='One Monday our Android crash-free rate fell 8.8 points. The crash was real and the stack trace was real, but almost none of it was happening to anyone with a phone.',
 desc='Our Android crash-free rate fell 8.8 points overnight. 108 of 130 crashes came from x86_64 emulator installs, and our analytics never saw one of them.',
 body="""
      <p>One Monday in October our Android crash-free rate fell 8.8 points overnight, to 88.87%. One issue accounted for nearly all of it: 108 of the 130 crashes we logged that week.</p>

      <p>I spent the first hour of that morning certain we had shipped a launch crash. We hadn't. Almost none of those crashes were happening to anyone holding a phone.</p>

      <h2>What the stack trace said</h2>

      <p>The error was a <code>SoLoaderDSONotFoundError</code> — "couldn't find DSO to load: libc++_shared.so" — thrown during startup, in <code>MainApplication</code>, before the app had drawn anything. A missing native library at launch is about as bad as a crash gets. It's unrecoverable, it's instant, and the user sees a dead icon.</p>

      <p>It was also entirely real. The trace was not corrupted, the symbolication was fine, and the devices reporting it were listed as OnePlus 8 Pros running Android 11. If you stopped reading there, as I nearly did, you would start bisecting releases.</p>

      <h2>Four things that didn't add up</h2>

      <p>The first was the native library folder. The crash report named <code>lib/x86_64</code> — an Intel chip. A real OnePlus 8 Pro is ARM. Whatever was running our app was not the phone the report named.</p>

      <p>The second was the package manifest. The installs carried every language split we ship and no CPU-architecture split at all, which is not a shape the Play Store produces. That's what an XAPK-style sideload looks like, or an emulator on a PC with a device model typed into it.</p>

      <p>Third, the device spread was far too clean. 77% called themselves OnePlus 8 Pro and 23% Huawei, and <strong>100% of them were on Android 11</strong>. Real populations are never 100% anything.</p>

      <p>And 53% of the crashes happened with the app in the background. People do not launch a word game and immediately background it, over and over, half the time.</p>

      <p>None of those four is conclusive on its own. Together they describe a machine, not a person.</p>

      <div class="pull"><p>The crash was real. The stack trace was real. The users were not, and nothing in the crash dashboard is designed to tell you that.</p></div>

      <h2>Our two dashboards disagreed and we believed the wrong one</h2>

      <p>Here's the part I'd not thought about before that morning. The crash happens in <code>onCreate</code>, before our analytics SDK finishes starting. So these sessions never reach analytics at all.</p>

      <p>Which means the crash reporter counted them and the analytics product didn't. Two tools, same week, different populations — and the discrepancy wasn't an integration bug to go and fix, it was the answer. The gap between those two numbers <em>was</em> the fake installs.</p>

      <p>I'd always treated a mismatch between analytics and crash reporting as something to reconcile. It's better read as a signal in its own right.</p>

      <h2>What the number should have been</h2>

      <p>Take that one issue out and crash-free users for the week was about 96.7%, not 88.87%. The real-device crashes behind that figure were a thin, unglamorous list: a view-manager <code>ClassCastException</code> on some older builds, a handful of Hermes segfaults, a couple of <code>libc</code> aborts, and then single instances of four unrelated things.</p>

      <p>That's a normal week. It needed a morning of ordinary bug-fixing, not an incident.</p>

      <p>The difference between those two numbers is the difference between "stop everything" and "carry on" — and the metric that was supposed to tell us which one we were in had been computed over a population that included software pretending to be phones.</p>

      <h2>The fix I nearly shipped was worse than the bug</h2>

      <p>My first instinct was to exclude the OnePlus 8 Pro from our device catalogue so the noise would stop.</p>

      <p>That would have been a genuinely bad call, and I'm glad I slept on it. The OnePlus 8 Pro is a real phone that real people own. Filtering the model name would have hidden every future crash suffered by anyone who actually owns one, in order to tidy up a chart. The thing worth filtering on is the architecture — <code>x86_64</code> where we ship ARM — not the name the device claims.</p>

      <p>It's a small distinction and it would have been an expensive one to get wrong, because the damage wouldn't have shown up as a bug. It would have shown up as an absence, months later, which is the kind of mistake you never find.</p>

      <h2>Three weeks later, by Google</h2>

      <p>In the middle of the month the same family of error came back on a newer build — this time <code>libreactnative.so</code>, 33 events across four devices. Same cause, different culprit: Google's own pre-launch report and Test Lab, running our app on <code>Sdk_gphone64_x86_64</code> emulators.</p>

      <p>Our app bundle ships arm64 and armv7 only. SoLoader goes looking for <code>lib/x86_64</code>, doesn't find it, and dies at launch. Every time Google tests our app for us, it files a crash against us for not supporting a chip no phone in our install base has.</p>

      <p>I find that funnier than I should. It is also the clearest possible demonstration that a crash in your dashboard is not evidence that a person had a bad time.</p>

      <h2>What we actually changed</h2>

      <p>Less than you'd think. We did not add an x86_64 slice to the bundle — it would grow the download for every real user to satisfy a test harness and some sideloads, and that trade is not worth making.</p>

      <p>What changed was the reading. Before trusting a movement in crash-free rate we now check the architecture and the split manifest, and analytics models beginning <code>sdk_gphone</code> are excluded outright. The number on the dashboard is still wrong; we just no longer act on it without looking underneath.</p>

      <p>One thing still open, and I don't have a clean answer: Play Console computes its own user-perceived crash rate against a bad-behaviour threshold, and I don't know whether these installs count toward it. If they do, emulator traffic can push a healthy app over a distribution threshold. That's worth knowing and I haven't finished chasing it.</p>

      <h2>Any health metric has a denominator</h2>

      <p>Crash-free rate is a percentage, and the argument above is entirely about what went into the bottom half of it.</p>

      <p>Every health metric you watch has this property — error rate, conversion, uptime, p99 latency. Each one is computed over a population that somebody defined, usually long before you got there, usually as "everything we could see". Bots, emulators, test harnesses, scrapers and sideloads all land in "everything we could see", and none of them can have a bad experience, because there is nobody there to have it.</p>

      <p>So when a number you trust moves sharply and the cause isn't obvious, it's worth one look at who is in the denominator before you go looking for what you broke. We lost most of a day to not doing that. The check took twenty minutes once somebody thought to run it.</p>

      <div class="tryit">
        <p>The game this all happened to is free, and it runs on ARM like everything else.</p>
        <a href="/">Play Wordmere</a>
      </div>

      <p class="endnote">We build <a href="/">Wordmere</a>, a cosy word game where the words you find assemble a small world around you. We publish the shapes of our numbers rather than the numbers themselves; the ratios here are real, the absolute levels are ours to keep. These posts are the things that went wrong on the way.</p>"""),
dict(
 slug='retention-magic-number',
 date='2026-10-28',
 updated='2026-11-03',
 title='Our retention magic number was a mirage',
 h1='Our retention magic number was a mirage',
 sub="Players who cleared six levels in their first session came back at roughly double the rate. So we made more players clear six levels. Retention didn't move at all.",
 desc='Six levels in session one doubled our day-one retention. We shipped a release that moved that number by a third, and retention stayed flat. What we got wrong.',
 body="""
      <p>We found our magic number in August. Six levels.</p>

      <p>Plot how likely a new player is to come back the next day against how many levels they cleared in their very first session, and the chart is almost too tidy. Flat and low up to about five. Somewhere between five and six it roughly doubles. Then it keeps climbing.</p>
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
      <p>About half of our new players were finishing their first session down in the flat part. The brief writes itself.</p>

      <h2>So we built it</h2>

      <p>We went at first-session depth head on. The opening levels were made quicker to read and quicker to clear, we pulled out the interruptions that fired before the threshold, and the moment a brand-new player finds their first word got rebuilt so that what the game is asking of you can't be missed.</p>

      <p>It worked. That's the annoying part. In one release, the share of new players clearing six or more levels on their first day went up by about a third.</p>

      <p>Day-one retention didn't move. Not slightly — it sat exactly where it had been sitting for two months, and it is sitting there now.</p>

      <div class="pull"><p>The threshold was real. It was never a cause. We moved the symptom and the illness didn't notice.</p></div>

      <h2>The number was describing them, not steering them</h2>

      <p>A player who clears six levels in one sitting has told you something about themselves before your level design gets a vote. They were in the mood, they had twenty minutes, and they had nothing better to do with them. Depth was a <em>measurement</em> of that, and the intent is what comes back tomorrow — not the depth.</p>

      <p>Make the levels faster and you move the measurement. You haven't been anywhere near the thing it was measuring.</p>

      <p>Written down now it looks obvious, which is the thing about this particular trap. It is the oldest one in product analytics and it still catches everybody, because the correlation is strong, the threshold is sharp, and shipping against a proxy feels identical to shipping against the real thing right up until the results come in. "Players who do X retain better" is not a finding. It is an invitation to ask the actual question, which is: and what happens if we <em>make</em> them do X?</p>

      <p>There's a cheap way to ask that before you build anything. Go back through your own release history, find a change that already moved the proxy, and check whether the outcome followed. We had one of those. We didn't look.</p>

      <h2>Two kinds of churn, and we fixed the wrong one</h2>

      <p>The deeper mistake was treating early churn as one thing.</p>

      <p>It's two, with opposite causes, and the bigger one is invisible if you go in looking for difficulty — which we did, because difficulty is the thing a level designer knows how to fix.</p>

      <p><strong>The early group isn't stuck.</strong> They leave around twenty seconds into a level. Nobody is defeated at twenty seconds. Almost everyone who starts the first level finishes it, so the first level isn't hard. And they leave with their hints unspent — they don't exhaust the help we gave them and give up, they never reach for it once. There's also a slice of installs that opens the app, registers a screen view and never starts a level at all, which is the single largest hole in our funnel and the one I think about most.</p>

      <p>None of that is difficulty. It's cold start. You can't fix it by making the puzzle easier, because they were not trying to solve the puzzle.</p>

      <p><strong>The second group is genuinely stuck</strong>, and they're much further in, at the point where the content first asks something real of you. Their median time on the last level they ever touch roughly doubles, and a third of them spend over two minutes on it before they go. That's difficulty churn. It responds to difficulty work. It is also a good deal smaller than the first group.</p>

      <p>So we spent a release tuning the opening for a population that wasn't failing it.</p>

      <h2>One number that actually had a shape</h2>

      <p>Out of everything we pulled, one measurement behaved differently enough to be worth something.</p>

      <p>Take the first time a player is ever offered a rewarded video — in our case a rescue, which fires automatically when they stall rather than being hunted for — and compare how often it's actually watched, by ordinal. The first one is far worse than the second. The second is worse than the third. It recovers from there, and keeps recovering.</p>

      <p>The shape is the finding, not the level. A flat line would mean players simply dislike video ads, and the fix would be to show fewer of them. A line that starts low and climbs means the first one is a <em>surprise</em>, and the fix is something you do once per player: say what's about to happen before it happens, and then never again.</p>

      <p>That's a far cheaper intervention than rebuilding an ad strategy, and we'd never have found it in the average.</p>

      <h2>Reasons we might still be wrong about that</h2>

      <p>This reading is correlational too, and having just been caught by one correlation we are trying hard not to do the same trick twice in one quarter. Players who were already on their way out may tap and close, which would produce the same curve from the opposite direction.</p>

      <p>What argues against it: it's the only placement in the game that fires unprompted on a single tap; its completion rate is anomalously low against other placements running on the same ad stack; and the monotonic recovery by ordinal is hard to explain if the cause is the kind of player rather than the moment.</p>

      <p>The high ordinals are badly survivorship-biased, obviously. A player on their eleventh rescue has self-selected as somebody who tolerates rescues. The first-attempt row is the clean one, because every player appears in it exactly once, and that row is what the whole argument rests on.</p>

      <p>So it's being tested rather than believed. If the test comes back flat we'll write that up too.</p>

      <h2>What I'd tell someone else</h2>

      <ul>
        <li><strong>A threshold in a correlation describes your users. It isn't a lever on them.</strong> Before you build against one, go and find a release that already moved it and check whether the outcome moved as well. That takes an afternoon and it would have saved us a release.</li>
        <li><strong>Split your churn before you diagnose it.</strong> Ours looked like one curve and turned out to be two populations with opposite causes, and the larger one was invisible because it leaves before it does anything we had thought to measure.</li>
      </ul>

      <p>And prefer findings that have a shape to them. "This number is bad" only tells you to improve it. "This number is bad and then recovers" tells you what <em>kind</em> of fix it needs, which is worth a great deal more and costs one extra group-by.</p>

      <p>We kept the six-level work, for the record. The opening is better than it was, new players get further into it, and that's worth having on its own terms. It just wasn't the retention fix, and I'd like to be able to say we only needed the data to tell us that once.</p>

      <div class="tryit">
        <p>The game all of this is about is free, and the opening is the part we have rebuilt the most.</p>
        <a href="/">Play Wordmere</a>
      </div>

      <p class="endnote">We build <a href="/">Wordmere</a>, a cosy word game where the words you find assemble a small world around you. We publish the shapes of our numbers rather than the numbers themselves; the ratios and thresholds here are real, the absolute levels are ours to keep. These posts are the things that went wrong on the way.</p>"""),
dict(
 slug='word-search-answer-keys',
 date='2026-10-28',
 updated='2026-11-03',
 title='Word search generators print wrong answer keys',
 h1='Word search generators print wrong answer keys',
 sub='We switched off one check in our puzzle maker and ran it twenty thousand times. Thirty-seven per cent of the grids hid a word somewhere the answer key never mentioned.',
 desc='A word search is a grid and a separate answer key, built by different code. Here is the bug that makes them disagree, how often it fires, and the cheap fix.',
 body="""
      <p>A word search is two things, not one. There's a grid of letters, and there's an answer key claiming where each word is hidden. Different code produces each of them, and when the two disagree, the person who gets told they're wrong is a child with a pencil.</p>

      <p>Here's how they come to disagree.</p>

      <h2>The naive generator is almost right</h2>

      <p>Everyone writes the same one. Sort the words longest first. For each, find every position and direction where it fits without contradicting a letter already on the grid, prefer the positions that overlap something (crossings make a tighter, better-looking puzzle), place it, record where it went. When every word is down, fill the empty cells with random letters. Print the grid, print the key.</p>

      <p>That's our generator too, and it is correct right up to the last step, where the random letters get a vote.</p>

      <p>Say the puzzle contains <code>CAT</code>, placed across on row four. The key says row four. Three rows down, by pure chance, the filler has produced a <strong>C</strong>, an <strong>A</strong> and a <strong>T</strong> on a diagonal. There are now two CATs in the grid and exactly one of them is in the key. A child circles the other one, checks the answers, and your software tells them they are wrong.</p>

      <h2>How often? More often than I'd have guessed</h2>

      <p>We can put a number on this, because the check that prevents it is one loop in our engine and the loop can be switched off. So I switched it off.</p>

      <p>Twenty thousand puzzles, eight to fifteen words each, every word three to six letters, all eight directions enabled. <strong>37.1% contained at least one word readable somewhere the answer key did not claim.</strong></p>

      <p>I would have said five per cent. Broken down by word length, the picture gets sharper:</p>

      <ul>
        <li>Three letters: <strong>12.7%</strong> forged, out of 77,252 placements.</li>
        <li>Four letters: <strong>0.94%</strong>, out of 14,037.</li>
        <li>Five and six letters: <strong>zero</strong>, out of 137,475.</li>
      </ul>

      <p>So the whole bug lives in short words, which is precisely why it is so easy to ship. Your test list is OTTER, BADGER, HERON, WILLOW, and you will never once see it. The first person to make an animal puzzle for a five-year-old — CAT, DOG, COW, OWL, FOX — gets a one-in-three chance of a lying answer key.</p>

      <p>The arithmetic isn't mysterious once you look at it. A three-letter word needs three cells to line up. A fifteen-by-fifteen grid read in eight directions holds a few thousand three-cell runs, and every one of them is a lottery ticket. Buy enough tickets and eventually you win something you didn't want.</p>

      <div class="pull"><p>The change that made our puzzles look better also made them more likely to be wrong, and nothing about it looked like it touched correctness.</p></div>

      <h2>The pretty version is the buggy version</h2>

      <p>Our filler letters aren't drawn uniformly from A to Z. They're drawn from the letters of the words being hidden.</p>

      <p>That is purely a looks decision. A uniform fill scatters J, Q and Z across a grid of farmyard animals and they read as signposts — you can find the hidden words by looking for the patches that are suspiciously boring. Drawing the padding from the puzzle's own letters kills that completely. It's the kind of change you make on a Friday afternoon and feel quite good about.</p>

      <p>It also biases every single filler cell towards exactly the letters your target words are made of.</p>

      <p>Same twenty thousand puzzles, same seeds, uniform A–Z filler instead: <strong>20.6%</strong>. The pretty version is roughly twice as likely to lie. And for longer words it is the difference between never and sometimes — in a separate run restricted to five- and six-letter words, the uniform fill produced not one forgery in twelve thousand puzzles, while the blended fill produced them in about one puzzle in fifty.</p>

      <p>That's the part I'd carry away from the whole exercise. A change made entirely for appearance moved a correctness property in the wrong direction, and I can't construct the code review that would have caught it.</p>

      <h2>Fixing it</h2>

      <p>After filling, for every word in the key, find every position in the grid where it reads. All eight directions, not just the ones the puzzle is using, because a backwards word is still a word a child can circle. Any hit that isn't the position in the key is a forgery. Take one of its cells that is filler rather than part of a placed word, change the letter, look again.</p>

      <p>Repeat until clean, with a bound.</p>

      <p>The bound matters more than it looks, because changing a letter to clear one forgery can create another — so this is a loop and not a pass. In practice it settles in a handful of iterations. The guard is there so that a pathological word list can't hang somebody's browser tab.</p>

      <p>Run with the repair back on, the same twenty thousand puzzles produce <strong>zero</strong> forgeries.</p>

      <h2>The case the repair can't touch</h2>

      <p>Occasionally a forged copy contains no filler at all. Every one of its cells belongs to a word you deliberately placed, which means two of your own words have spelled a third between them, and there is nothing to change. The repair gives up, the whole layout is discarded, and we lay the puzzle out again from scratch, growing the grid if we have to.</p>

      <p>In those twenty thousand puzzles, that escape hatch never fired once. It's insurance, not a workhorse, and if you were trimming code you would be tempted to delete it — I nearly did. The reason it stays is that its absence is not a wrong answer. Its absence is an infinite loop.</p>

      <h2>What we deliberately don't check</h2>

      <p>We only check the words in the key. The grid is full of accidental other words — there's a RAT and an ARE and a TEN in very nearly every puzzle we produce — and we don't care, because the key has never claimed them. Nobody circles a word that isn't on the list.</p>

      <p>A stricter generator would run a dictionary over the finished grid and refuse any real word anywhere. We decided against that, partly on principle and mostly on weight: the puzzle makers load no dictionary at all, the words come from the person making the puzzle, and pulling a few hundred kilobytes of word list onto a page that never reads it costs about twenty Lighthouse points to solve a problem nobody has.</p>

      <p>The narrow failure is the one that matters. The key says a word is <em>here</em>, and it is also <em>there</em>. That is the only case where the software tells a correct person they are wrong.</p>

      <h2>Where else this hides</h2>

      <p>Any generator that emits both a thing and a description of that thing has this bug available to it. The grid and the key. The build and the manifest. The migration and the schema dump — that one has bitten me twice.</p>

      <p>Two code paths, one claim, and nobody checking that they still agree.</p>

      <p>The check is almost always cheaper than the generator that needed it, which is the only reason I'd push this on anybody. Read your own output back, and confirm it says what you said it says. Ours runs on every build, over a fixed set of word lists and forty random ones, and it is the reason this post has numbers in it rather than an apology.</p>

      <div class="tryit">
        <p>The puzzle maker is free, runs entirely in your browser, and the answer keys are checked before you ever see them.</p>
        <a href="/tools/word-search-maker/">Make a word search</a>
      </div>

      <p class="endnote">We build <a href="/">Wordmere</a>, a cosy word game where the words you find assemble a small world around you. The same engine lays out our <a href="/tools/crossword-maker/">crossword maker</a>, which has <a href="/blog/crossword-adjacency-rules/">a different way of going wrong</a>. These posts are the things that went wrong on the way.</p>"""),
dict(
 slug='crossword-adjacency-rules',
 date='2026-10-28',
 updated='2026-11-03',
 title='The two rules that make a crossword a crossword',
 h1='The two rules that make a crossword a crossword',
 sub='Take either rule out of our generator and the grids still look fine. They are not fine: 78% and 98% of them hide a run of letters that nobody wrote a clue for.',
 desc='A crossword generator is easy to write and hard to write correctly. The gap is two adjacency rules, and here is what the grids look like without each of them.',
 body="""
      <p>A crossword generator is easy to write and hard to write correctly, and the gap between those two is two rules that aren't obvious until you print one out and hand it to somebody.</p>

      <p>The easy part takes an afternoon. I know, because it took me one. Take the longest word and lay it across. For each remaining word, look for a letter it shares with something already on the grid and place it at ninety degrees through that letter. Score the candidates — more crossings is better, growing the bounding box less is better — take the best, repeat. The result looks like a crossword.</p>

      <p>Then you print it, hand it to somebody, and they get stuck on a row that reads <code>RIVEROTTER</code>.</p>

      <h2>Rule one: a word may not run straight into another word</h2>

      <p>The cell immediately before a word's first letter, and the cell immediately after its last, must both be empty.</p>

      <p>I assumed I got this for free, on the grounds that every placement in a generator like ours has to cross something, and a crossing is perpendicular. That's wrong, and here's why. RIVER is sitting across, ending at column nine. OTTER comes along, crosses some down word, and the arithmetic puts its first letter at column ten on the same row. Both words are legal. Both cross something. The row now reads RIVEROTTER, and the solver has to work out that it is two answers in a trench coat.</p>

      <p>With the rule removed, <strong>77.9% of three thousand generated grids contained at least one run of two or more letters that nobody had written a clue for</strong> — 4,197 such runs in total. Real output, not invented examples: <code>RIVEROTTER</code>, <code>PEPPERICED</code>, <code>OTTERSCALA</code>, <code>PEPPERL</code>, <code>REEDH</code>.</p>

      <h2>Rule two: a letter that isn't a crossing may not touch a neighbour side-on</h2>

      <p>This is the subtle one, and it's the rule people leave out.</p>

      <p>Take OTTER running across. Every one of its five letters has a cell above it and a cell below it. If the cell above the first T happens to be occupied by a letter belonging to some other word, then that column now contains a run of two letters — the T and whatever is sitting on top of it — and that run is not an answer. It isn't numbered. It isn't in the clue list. It is just there, and the solver can't tell it apart from a real entry.</p>

      <p>The exception is the entire point of the rule. At a crossing, touching is exactly what's supposed to happen. So the check has two branches, and they are opposites:</p>

      <ul>
        <li>If the cell we're about to write is <strong>already occupied</strong>, this is a crossing. The letter must match the one that's there, and the perpendicular neighbours are somebody else's problem — they belong to the word we are crossing.</li>
        <li>If the cell is <strong>empty</strong>, this is a new letter of ours, and both of its perpendicular neighbours must be empty too.</li>
      </ul>

      <p>Those two branches are the difference between a crossword and a letter jumble.</p>

      <p>With the rule removed, <strong>98.0% of grids contained an unclued run</strong> — 19,119 of them across three thousand grids, which is about six per puzzle. The output is a blizzard of two-letter debris: <code>TS</code>, <code>MC</code>, <code>GL</code>, <code>PI</code>, <code>EE</code>. Each one is a place where two answers brushed past each other.</p>

      <p>With both rules in place: zero unclued runs in three thousand grids.</p>

      <div class="pull"><p>Both rules are local — one cell and its neighbours. Both of the failures they prevent are global. That mismatch is why you cannot test this inside the generator.</p></div>

      <h2>Why you don't notice</h2>

      <p>Because you look at the grid with all the answers in it, and your eye follows the words you intended to put there. The spurious runs are invisible to the person who placed the words and glaring to the person trying to solve them.</p>

      <p>Everybody has shipped a bug they were structurally unable to see. This is the cleanest example I have got.</p>

      <p>Which is why the check can't live in the generator's head. It has to be a pass over the finished grid: walk every maximal run of two or more letters, across and down, and assert that each one is a word somebody wrote a clue for, that it is numbered, and that it appears in the lists. That single assertion is what separates a crossword from a jumble, and it runs on every build.</p>

      <h2>The corner you paint yourself into</h2>

      <p>One more, since you'll hit it about ten minutes after fixing the first two. Greedy placement with a deterministic choice is a disaster: the first few words decide the shape of everything that follows, and the locally best opening move is very often the one that leaves nowhere to go.</p>

      <p>We try forty different orderings of the same word list, break near-ties in the scoring at random, and keep whichever grid fits the most words into the smallest bounding box. Forty is not a researched number. It's where the improvement stopped being visible and the tab still felt instant.</p>

      <p>And a word that genuinely cannot cross anything — give the generator AAA, BBB and CCC and only one of them can be placed — is reported back as unplaced rather than quietly dropped. Silently losing a word is the other way a puzzle maker lies to you.</p>

      <h2>What this grid isn't</h2>

      <p>These two rules make a grid <em>legal</em>. They don't make it <em>good</em>.</p>

      <p>A newspaper crossword has properties ours doesn't: rotational symmetry, no unchecked letters (every square belongs to both an across answer and a down answer), a minimum entry length, a single connected block of squares. We enforce none of that. What we produce is the free-form criss-cross grid you'd print for a classroom or a party — every entry crosses at least one other, nothing reads that shouldn't, and the overall shape is whatever the words gave us.</p>

      <p>Getting a symmetric, fully-checked grid needs a different algorithm entirely: start from a pattern of black squares and fill it, backtracking when you fail, with a dictionary to fill it from. That is a much larger program, and on a free tool where the words are supplied by the person making the puzzle it would solve a problem nobody brought us. I would quite like to build it anyway.</p>

      <h2>Local rule, global failure</h2>

      <p>Both rules here are decisions about a single cell and its immediate neighbours. Both of the failures they prevent are properties of the finished grid that no individual placement is responsible for.</p>

      <p>When that's the shape of a problem, you need the rule in two places. Put it where the decision is made, so the generator can't produce the bad thing. Put the proof where the artefact is finished, so you find out when the rule was wrong. Neither one is enough on its own — a generator whose rules you trust but whose output you have never read back is a well-commented guess.</p>

      <div class="tryit">
        <p>The crossword maker is free and runs in your browser. Type your words and clues, and it will tell you if one of them could not be placed.</p>
        <a href="/tools/crossword-maker/">Make a crossword</a>
      </div>

      <p class="endnote">We build <a href="/">Wordmere</a>, a cosy word game where the words you find assemble a small world around you. The companion to this one is <a href="/blog/word-search-answer-keys/">the bug that makes word search answer keys wrong</a>, which comes from the same engine and the same lesson. These posts are the things that went wrong on the way.</p>"""),
dict(
 slug='word-list-problem',
 date='2026-10-10',
 updated='2026-11-03',
 title='Why your word game’s dictionary is lying to you',
 h1='Why your word game’s dictionary is lying to you',
 sub='Our Scrabble helper once told a player that REQUIZ was their best move. Here is why every open word list will do that to you, and the cheap fix.',
 desc='Open word lists accept words no human would play. Why a word game needs two dictionaries, not one, and the cheap signal we used to tell them apart.',
 body="""
      <p>If you are building anything that suggests words to a person — a Scrabble helper, an unscrambler, a hint system, a bot opponent — you will reach for a word list early. There are good free ones. You will wire it in, it will work, and then it will embarrass you.</p>

      <p>Ours embarrassed us like this. We built a <a href="/tools/scrabble-word-finder/">Scrabble word finder</a>, fed it a rack, and it confidently announced the highest-scoring play: <strong>REQUIZ</strong>.</p>

      <p>REQUIZ is in the list. It is not a word anybody has ever played.</p>

      <h2>Open word lists answer a different question</h2>

      <p>We used the public-domain <code>dwyl/english-words</code> list, filtered to three to eight letters, which left 104,562 words. Lists like it are built by union: take several sources, merge them, deduplicate. That is the right way to build a list that answers <em>is this string a word?</em> — and the wrong way to build one that answers <em>would a person recognise this?</em></p>

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

      <p>There was an argument about this, and the objection is a fair one: a definitions file is not a frequency list, and using the presence of a gloss as a stand-in for "ordinary people know this word" is only roughly true. It went in anyway, because the alternative on the table was curating a hundred thousand words by hand, and the alternative we actually wanted was a licence we don't have.</p>

      <p>In the shipped tools, common words sort first and rare ones are still shown, greyed and labelled. The Scrabble finder's recommended best play is drawn only from the common set. REQUIZ is still in there if you go looking for it. It is just no longer what we tell you to do.</p>

      <h2>Where the proxy fails</h2>

      <p>NASTIER and QUIRES land in the rare bucket. They are perfectly good words. The proxy has false negatives, and we shipped it anyway, because the two failure modes are not equally bad:</p>

      <ul>
        <li>A real word shown in grey, slightly lower down the page. The player shrugs.</li>
        <li>A confident recommendation of a word that does not exist in any usable sense. The player stops believing anything the tool says.</li>
      </ul>

      <p>The honest fix is a tournament word list — TWL or Collins — which is maintained precisely to answer "is this playable". Those are licensed, which is why a free tool on the open web generally isn't using one, including ours. If you are building something commercial, licensing one is the move. If you are not, a definitions source is a surprisingly good stand-in.</p>

      <h2>Pick your failure mode on purpose</h2>

      <p>None of this is really about word lists. It is about choosing your failure mode deliberately, rather than inheriting whichever one your data source happened to come with.</p>

      <p>Any time you ship a list — of words, of suggestions, of autocompletions, of anything a person will read as your recommendation — ask which direction you would rather be wrong in, and then go and check whether your source was built with that same preference. Usually it wasn't. Usually nobody checked.</p>

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
