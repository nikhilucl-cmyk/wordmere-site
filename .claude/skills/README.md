# Vendored agent skills

Third-party Claude Code skills, copied into the repo so every session picks them
up without a setup step. Nothing here is ours and nothing here is published —
these files are tooling for the agent, not part of the website.

**Do not hand-edit these folders.** They are verbatim upstream copies. To change
one, update it from upstream and re-copy; local edits are lost on the next refresh.

## What is here

| Folder | Upstream | Commit | Licence | What it does |
|---|---|---|---|---|
| `taste-skill` | `Leonxlnx/taste-skill` | `f6b7657` | MIT | Frontend design via art direction and reference images; checks its work in a real browser |
| `anatomy` | `wheresryan22/anatomy` | `1482e84` | MIT | Interactive isometric SVG figures that explain how something works |
| `hallmark` | `Nutlope/hallmark` | `04977e1` | MIT | Design skill for new pages; ~50 themes. Won't touch an existing design unless named |
| `diagram-design` | `cathrynlavery/diagram-design` | `f6db0de` | MIT | ~45 editorial diagram types as self-contained HTML/SVG |
| `impeccable` | `pbakaus/impeccable` | `b4bff16` | Apache-2.0 | Design vocabulary: `polish`, `bolder`, `critique`, `audit` |
| `ponytail*` | `DietrichGebert/ponytail` | `96608e0` | MIT | Smallest-change-that-works discipline, plus review/audit/debt reports |
| `graphify` | `Graphify-Labs/graphify` | `52cb282` | Apache-2.0 | Codebase → queryable knowledge graph |

`ponytail` ships six skills: `ponytail`, `-review`, `-audit`, `-debt`, `-gain`, `-help`.

Vendored 2026-11-13. Upstream moves fast, so these are a snapshot, not a subscription.

## graphify needs one extra step

Unlike the others, graphify is not self-contained. The `SKILL.md` here drives a
Python CLI that is **not** in this repo, so in a fresh container run:

    pip install --break-system-packages graphifyy

Without it the skill loads but cannot build a graph. (Its installer also writes a
short `~/.claude/CLAUDE.md` registering the `/graphify` trigger — three lines,
harmless, and outside this repo.)

## Two things to know when using these

**The design skills overlap.** `taste-skill` and `impeccable` both trigger on
"design / redesign / polish / review a page", so a bare request is ambiguous.
Name the one you want. `hallmark` stays out of the way unless named.

**`anatomy/examples/` is load-bearing**, not sample output — its `SKILL.md`
tells the agent to open the nearest example before starting. It is also most of
the 27 MB. Don't prune it.

## Size

About 83 MB, against ~1.5 MB for the site itself. Almost all of it is
`taste-skill/assets` (38 MB of reference images, the point of that skill) and
`anatomy/examples` (25 MB). Worth knowing before adding more.

## Not yet verified

Whether GitHub Pages serves dot-directories on this site. `robots.txt` is
`Allow: /`, so if `.claude/` were reachable it would be crawlable. It is not in
`sitemap.xml`, so the IndexNow workflow will not announce it. Check
`https://wordmere.com/.claude/skills/README.md` after this reaches `main`; if it
returns 200, add a `Disallow: /.claude/` line to `robots.txt`.
