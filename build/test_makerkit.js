/* Tests for tools/makerkit.js.  Run from the repo root:  node build/test_makerkit.js
   The puzzle makers are the only tools whose output can be silently wrong —
   a word search whose answer key doesn't match, or a crossword with a run of
   letters nobody wrote a clue for — so both invariants are checked here. */
const MK = require('../tools/makerkit.js').MK;

let pass = 0, fail = 0;
function ok(cond, what) { cond ? pass++ : (fail++, console.log('  FAIL  ' + what)); }

/* ── parsing ─────────────────────────────────────────────────────── */
{
  const p = MK.parseWords('cat\nOTTER, badger; fox\nbadger\nan');
  ok(p.words.join(' ') === 'CAT OTTER BADGER FOX', 'parseWords splits, uppercases, dedupes: ' + p.words);
  ok(p.short.join('') === 'AN', 'parseWords sets aside words under three letters');
  const q = MK.parseWords('elephantine', 8);
  ok(q.words.length === 0 && q.long[0] === 'ELEPHANTINE', 'parseWords honours a max length');

  const c = MK.parseClued('ORBIT: what a moon does\nCOMET - icy visitor\nMARS, the red one\nPLUTO');
  ok(c.entries.length === 4, 'parseClued reads four entries');
  ok(c.entries[0].clue === 'what a moon does', 'parseClued splits on a colon');
  ok(c.entries[1].clue === 'icy visitor', 'parseClued splits on a spaced hyphen');
  ok(c.entries[2].clue === 'the red one', 'parseClued splits on a comma');
  ok(c.noclue.join('') === 'PLUTO', 'parseClued reports entries with no clue');
}

/* ── word search ─────────────────────────────────────────────────── */
function checkSearch(words, opts) {
  const res = MK.wordsearch(words, opts);
  const { size, grid } = res;
  ok(grid.length === size * size, 'grid is ' + size + '×' + size);
  ok(grid.every(ch => /^[A-Z]$/.test(ch)), 'every cell holds one A-Z letter');
  ok(res.unplaced.length === 0, 'every word placed (' + res.unplaced + ')');

  res.placed.forEach(p => {
    let read = '';
    for (let k = 0; k < p.word.length; k++) read += grid[(p.r + p.dr * k) * size + (p.c + p.dc * k)];
    ok(read === p.word, 'answer key matches the grid for ' + p.word + ' (read ' + read + ')');
    ok(p.r >= 0 && p.c >= 0 && p.r < size && p.c < size, p.word + ' starts inside the grid');
    const er = p.r + p.dr * (p.word.length - 1), ec = p.c + p.dc * (p.word.length - 1);
    ok(er >= 0 && ec >= 0 && er < size && ec < size, p.word + ' ends inside the grid');
    ok(MK.occurrences(grid, size, p.word) === 1, p.word + ' appears exactly once — no filler forgery');
  });

  const dirsUsed = new Set(res.placed.map(p => p.dr + ':' + p.dc));
  const allowed = new Set(MK.DIRS.slice(0, opts.dirs || 4).map(d => d[0] + ':' + d[1]));
  ok([...dirsUsed].every(d => allowed.has(d)), 'only the requested directions were used');
  return res;
}

checkSearch(['OTTER', 'BADGER', 'HERON', 'WILLOW', 'RIVER', 'MEADOW', 'PEBBLE', 'MOSS'], { dirs: 4, seed: 1 });
checkSearch(['CAT', 'DOG', 'COW'], { dirs: 2, seed: 7 });
checkSearch(['EXTRAORDINARY', 'QUIZZICAL', 'JUXTAPOSE'], { dirs: 8, seed: 3 });

/* Same seed, same grid — so "Make puzzle" is reproducible when it needs to be. */
{
  const a = MK.wordsearch(['ALPHA', 'BRAVO', 'DELTA'], { dirs: 8, seed: 42 });
  const b = MK.wordsearch(['ALPHA', 'BRAVO', 'DELTA'], { dirs: 8, seed: 42 });
  ok(a.grid.join('') === b.grid.join(''), 'the same seed produces the same grid');
}

/* A word longer than the requested grid forces the grid to grow. */
{
  const r = MK.wordsearch(['CONSTITUTIONAL'], { dirs: 8, size: 6, seed: 5 });
  ok(r.size >= 14 && !r.unplaced.length, 'grid grows to fit a word longer than the size asked for');
}

/* ── crossword ───────────────────────────────────────────────────── */

/* Every maximal run of two or more letters must be a word somebody clued.
   This is the invariant that separates a crossword from a letter jumble. */
function checkCross(entries) {
  const res = MK.crossword(entries);
  const { cells, rows, cols } = res;
  const clued = new Set([...res.across, ...res.down].map(e => e.n + ':' + (e.dr ? 'D' : 'A')));
  const placedWords = new Set([...res.across, ...res.down].map(e => e.word));

  [...res.across, ...res.down].forEach(e => {
    let read = '';
    for (let k = 0; k < e.word.length; k++) {
      const cell = cells[e.r + e.dr * k] && cells[e.r + e.dr * k][e.c + e.dc * k];
      read += cell ? cell.ch : '.';
    }
    ok(read === e.word, 'grid reads ' + e.word + ' at its clue number (got ' + read + ')');
    ok(typeof e.n === 'number' && e.n > 0, e.word + ' got a clue number');
  });

  let runs = 0;
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      if (!cells[y][x]) continue;
      [[0, 1], [1, 0]].forEach(([dr, dc]) => {
        if (cells[y - dr] && cells[y - dr][x - dc]) return;          /* not a run start */
        let run = '', k = 0;
        while (cells[y + dr * k] && cells[y + dr * k][x + dc * k]) run += cells[y + dr * k][x + dc * k].ch, k++;
        if (run.length < 2) return;
        runs++;
        ok(placedWords.has(run), 'run "' + run + '" at ' + y + ',' + x + ' is a word that was clued');
        ok(clued.has(cells[y][x].n + ':' + (dr ? 'D' : 'A')), 'run "' + run + '" is numbered and listed');
      });
    }
  }
  ok(runs === res.across.length + res.down.length, 'no run is missing from the clue lists');
  ok(res.across.every((e, i, a) => !i || a[i - 1].n <= e.n), 'across clues run in numerical order');
  ok(res.down.every((e, i, a) => !i || a[i - 1].n <= e.n), 'down clues run in numerical order');
  return res;
}

const clue = ws => ws.map(w => ({ word: w, clue: 'clue for ' + w }));

checkCross(clue(['OTTER', 'RIVER', 'WILLOW', 'MEADOW', 'HERON', 'REED', 'STONE', 'MOSS']));
checkCross(clue(['PYTHON', 'RUBY', 'RUST', 'SWIFT', 'KOTLIN', 'SCALA', 'ELIXIR']));
checkCross(clue(['AAA', 'BBB', 'CCC']));             /* nothing can cross — all but one unplaced */
checkCross(clue(['SOLO']));

{
  const r = MK.crossword(clue(['AAA', 'BBB', 'CCC']));
  ok(r.across.length + r.down.length + r.unplaced.length === 3, 'words that cannot cross are reported, not dropped');
  ok(r.unplaced.length === 2, 'two of three uncrossable words are unplaced');
}
{
  const r = MK.crossword([]);
  ok(r.rows === 0 && r.across.length === 0, 'an empty list makes an empty crossword, not a crash');
}

/* ── fuzz: random lists, both makers, invariants must hold every time ── */
{
  const bank = ('APPLE BREAD CHEESE DINNER EGG FLOUR GRAPE HONEY ICING JAM KETTLE LEMON MANGO NUTMEG OLIVE PEPPER QUICHE '
    + 'RICE SUGAR TOMATO ONION VANILLA WALNUT YEAST ZEST BUTTER CREAM DOUGH FENNEL GARLIC').split(' ');
  let rng = 12345;
  const rnd = () => (rng = (rng * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  for (let i = 0; i < 40; i++) {
    const n = 3 + ((rnd() * 12) | 0);
    const pick = bank.slice().sort(() => rnd() - 0.5).slice(0, n);
    const dirs = [2, 4, 8][(rnd() * 3) | 0];
    const res = MK.wordsearch(pick, { dirs, seed: (rnd() * 1e9) | 0 });
    const bad = res.placed.filter(p => MK.occurrences(res.grid, res.size, p.word) !== 1);
    ok(!bad.length && !res.unplaced.length, 'fuzz search #' + i + ' (' + n + ' words, ' + dirs + ' dirs)');
    checkCross(clue(pick));
  }
}

console.log((fail ? 'FAILED  ' : 'ok      ') + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
