# wordmere.com

The marketing site for Wordmere, the word game. Static HTML, no build step for
most of it, **served by GitHub Pages from this repo's `main` branch, path `/`**
(legacy branch build, CNAME `wordmere.com`, HTTPS enforced). DNS stays on
GoDaddy nameservers pointing at GitHub's 185.199.108-111.153.

**Pushing to `main` publishes to the live web within about a minute.** There is
no staging site. Cloudflare Pages was proposed in Sept 2026 and parked — if
anyone tells you the site moved, check `gh api repos/nikhilucl-cmyk/wordmere-site/pages`
before believing it.

## Never break these

**Five frozen URLs.** Apple, Google Play, AdMob and Meta all point at these.
They must keep returning 200 and must keep their exact paths:

    /  /privacy/  /terms/  /support/  /data-deletion/  /app-ads.txt

**`/app-ads.txt` is ad revenue.** AdMob polls it. A 404 or a malformed line
means buyers drop bids. There is exactly ONE copy, at the repo root — never
create a second one anywhere.

**Two verification files at the root must never be deleted.** Both are
re-fetched by machines on a schedule, and deleting either silently breaks
verification:

    google490fd72aa106894a.html      Google Search Console ownership
    ab5c06ff4b8d21f81392b956dc7af0ed.txt   IndexNow key (Bing and friends)

## More than one Claude session works in this folder

Sessions share this one working copy. The way that bites is not simultaneous
edits — it is one session committing another's half-finished work.

- **`git pull` before you edit.**
- **Stage named files. Never `git add -A` or `git add .`** — you cannot tell
  whose uncommitted work you are sweeping up, and the next push puts it live.
- **Commit and push in the same breath.** Do not leave work sitting
  uncommitted in a shared folder.
- Check `git status` before committing. Anything there you did not write
  belongs to someone else — leave it alone and say so.

### Who owns what

| Area | Owner |
|---|---|
| The website — pages, design, SEO, tools, Search Console, IndexNow | The website session |
| `app-ads.txt` | The ad-stack session, which owns the mediation partners |

If you need a change outside your area, message the other session rather than
editing. Both areas live in this repo, so a wrong assumption ships instantly.

## Generated files — do not hand-edit

The ten tool pages under `/tools/<slug>/index.html` are generated:

    python3 build/tools.py          # run from the repo root

Their content, form fields and copy live in `build/tools.py`; the shared
shell (head, nav, footer, script harness) lives in `build/tool_template.html`.
Hand-edits to `tools/*/index.html` are overwritten on the next build.

The generator reads the site's CSS out of `index.html` and the nav/footer out
of `tools/index.html`, so a change to those propagates to every tool page the
next time you run it. **After editing `index.html`, re-run the generator** or
the tool pages keep the old chrome.

Everything else — `index.html`, the legal pages, `404.html`, `tools/index.html` —
is hand-maintained.

The word tools share `tools/words.txt` (the dictionary, with a trailing `*`
marking common words) and `tools/wordkit.js` (the engine). Both are requested
with a `?v=N` cache-buster. **If you change the dictionary format, bump that
version in `tools/wordkit.js` and `build/tool_template.html`** — otherwise
browsers mix a cached old dictionary with new code and every word silently
looks "rare".

The two puzzle makers (`word-search-maker`, `crossword-maker`) load **no
dictionary at all** — their words come from the person making the puzzle. They
use `tools/makerkit.js` instead, and a tool opts out of the dictionary with
`needs_dict=False` in its `SPEC`, which drops the `words.txt` preload and the
`wordkit.js` tag from that page. Keep it that way: pulling 274 KB of gzipped
dictionary onto a page that never reads it costs about 20 Lighthouse points.

**`tools/makerkit.js` has tests. Run them after any change to it:**

    node build/test_makerkit.js

They check the two invariants that can silently produce a wrong puzzle: every
word in a word search reads out of the grid exactly once at the position the
answer key claims (random filler letters can otherwise spell a second copy),
and every run of two or more letters in a crossword is a word somebody wrote a
clue for. Both makers retry their layout when those fail, so a regression
shows up as a hang or a dropped word rather than an obvious break.

## Adding a page

1. Create it, matching the existing head block: title, meta description,
   canonical, Open Graph, favicons, self-hosted fonts from `/fonts/`.
2. Add it to `sitemap.xml`.
3. Link it from somewhere real — the nav, the footer, or a related page. The
   site has no orphans and it should stay that way.
4. Push. The IndexNow workflow (`.github/workflows/indexnow.yml`) fires after
   the Pages build and tells Bing about every sitemap URL automatically.

## Checking your work before you push

    # every frozen URL still answers
    for u in / /privacy/ /terms/ /support/ /data-deletion/ /app-ads.txt; do
      curl -s -o /dev/null -w "$u %{http_code}\n" "https://wordmere.com$u"; done

    # app-ads.txt is well formed: 3-4 comma fields per record, no duplicates
    grep -vE "^\s*(#|$)" app-ads.txt | awk -F, 'NF<3||NF>4{print "BAD: "$0}'
    grep -vE "^\s*(#|$)" app-ads.txt | tr -d ' ' | tr 'A-Z' 'a-z' \
      | awk -F, '{print $1","$2","$3}' | sort | uniq -d

    # real Lighthouse scores, mobile (the site holds 98-100 across the board)
    npx -y lighthouse@12 https://wordmere.com/ --form-factor=mobile \
      --only-categories=performance,seo,accessibility,best-practices --quiet \
      --chrome-flags="--headless=new"

Hand-rolled contrast or overflow checks miss things Lighthouse catches —
heading order, links distinguishable by colour alone, layout shift. Run it.
