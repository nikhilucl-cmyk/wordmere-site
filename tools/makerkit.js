/* Shared engine for the Wordmere puzzle makers.
   Unlike wordkit.js this loads no dictionary — the words come from the
   person making the puzzle. Pure functions, so the layout code can be
   unit-tested in node (see build/test_makerkit.js). */
(function (root) {
  'use strict';

  /* ── input ──────────────────────────────────────────────────────── */

  /* One word per line or comma-separated. Keeps A-Z only, uppercases,
     drops duplicates, and reports what it threw away so the page can
     say so instead of silently losing a word. */
  function parseWords(raw, maxLen) {
    var seen = {}, ok = [], short = [], long = [];
    (raw || '').split(/[\n,;]+/).forEach(function (line) {
      var w = line.toUpperCase().replace(/[^A-Z]/g, '');
      if (!w) return;
      if (w.length < 3) { short.push(w); return; }
      if (maxLen && w.length > maxLen) { long.push(w); return; }
      if (seen[w]) return;
      seen[w] = 1; ok.push(w);
    });
    return { words: ok, short: short, long: long };
  }

  /* "WORD: clue" / "WORD - clue" / "WORD, clue" per line. */
  function parseClued(raw, maxLen) {
    var seen = {}, ok = [], short = [], long = [], noclue = [];
    (raw || '').split(/\n+/).forEach(function (line) {
      if (!line.trim()) return;
      var m = line.match(/^\s*([^:,–—-]+?)\s*(?:[:,–—]|\s-\s)\s*(.+?)\s*$/);
      var word = (m ? m[1] : line).toUpperCase().replace(/[^A-Z]/g, '');
      var clue = m ? m[2].trim() : '';
      if (!word) return;
      if (word.length < 3) { short.push(word); return; }
      if (maxLen && word.length > maxLen) { long.push(word); return; }
      if (seen[word]) return;
      seen[word] = 1;
      if (!clue) noclue.push(word);
      ok.push({ word: word, clue: clue });
    });
    return { entries: ok, short: short, long: long, noclue: noclue };
  }

  /* ── word search ────────────────────────────────────────────────── */

  /* Ordered so the first two are across/down, the first four add the two
     downward diagonals, and all eight add every backwards direction. */
  var DIRS = [[0, 1], [1, 0], [1, 1], [-1, 1], [0, -1], [-1, 0], [-1, -1], [1, -1]];

  function mulberry(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      var t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  function placeAll(words, size, ndirs, rnd) {
    var grid = new Array(size * size).fill(''), placed = [], unplaced = [];
    var dirs = DIRS.slice(0, ndirs);
    words.forEach(function (w) {
      var n = w.length, spots = [], best = -1;
      for (var d = 0; d < dirs.length; d++) {
        var dr = dirs[d][0], dc = dirs[d][1];
        for (var r = 0; r < size; r++) {
          for (var c = 0; c < size; c++) {
            var er = r + dr * (n - 1), ec = c + dc * (n - 1);
            if (er < 0 || er >= size || ec < 0 || ec >= size) continue;
            var over = 0, ok = true;
            for (var k = 0; k < n; k++) {
              var cell = grid[(r + dr * k) * size + (c + dc * k)];
              if (!cell) continue;
              if (cell === w[k]) over++; else { ok = false; break; }
            }
            if (!ok) continue;
            spots.push({ r: r, c: c, dr: dr, dc: dc, over: over });
            if (over > best) best = over;
          }
        }
      }
      if (!spots.length) { unplaced.push(w); return; }
      /* Crossings make a tighter, better-looking puzzle, so favour them —
         but not always, or every grid from the same list looks identical. */
      var pool = rnd() < 0.8 ? spots.filter(function (s) { return s.over === best; }) : spots;
      var s = pool[(rnd() * pool.length) | 0];
      for (var i = 0; i < n; i++) grid[(s.r + s.dr * i) * size + (s.c + s.dc * i)] = w[i];
      placed.push({ word: w, r: s.r, c: s.c, dr: s.dr, dc: s.dc });
    });
    return { grid: grid, placed: placed, unplaced: unplaced };
  }

  /* Everywhere `word` reads out of the grid, in any of the eight
     directions. Used to keep filler letters from forging a second copy
     of a word the answer key claims is somewhere else. */
  function findAll(grid, size, word) {
    var n = word.length, hits = [];
    for (var d = 0; d < 8; d++) {
      var dr = DIRS[d][0], dc = DIRS[d][1];
      for (var r = 0; r < size; r++) {
        for (var c = 0; c < size; c++) {
          var er = r + dr * (n - 1), ec = c + dc * (n - 1);
          if (er < 0 || er >= size || ec < 0 || ec >= size) continue;
          var ok = true;
          for (var k = 0; k < n && ok; k++) ok = grid[(r + dr * k) * size + (c + dc * k)] === word[k];
          if (ok) hits.push({ r: r, c: c, dr: dr, dc: dc });
        }
      }
    }
    return hits;
  }

  function occurrences(grid, size, word) { return findAll(grid, size, word).length; }

  function wordsearch(words, opts) {
    opts = opts || {};
    var ndirs = opts.dirs || 4, rnd = mulberry(opts.seed == null ? (Math.random() * 1e9) | 0 : opts.seed);
    var longest = words.reduce(function (m, w) { return Math.max(m, w.length); }, 0);
    var letters = words.join('').length;
    var floor = Math.max(longest, Math.ceil(Math.sqrt(letters * 1.8)), 8);
    var size = opts.size || floor;
    if (size < longest) size = longest;
    if (size > 26) size = 26;

    /* Fill from the puzzle's own letters so the padding blends in; a
       uniform A-Z fill makes J, Q and Z stand out like signposts. A very
       short list doesn't supply enough variety on its own, so top it up. */
    var pool = (words.join('') + (letters < 40 ? 'AEIOUAEIOURSTLNCDHM' : '')).split('');
    if (!pool.length) pool = 'AEIOURSTLN'.split('');

    /* One complete puzzle: place the words, pad the gaps, then repair any
       padding that accidentally spelled a target word a second time. */
    function build(sz) {
      var byLen = words.slice().sort(function (a, b) { return (b.length - a.length) || (rnd() - 0.5); });
      var got = placeAll(byLen, sz, ndirs, rnd);
      var marked = new Array(sz * sz).fill(false);
      got.placed.forEach(function (p) {
        for (var k = 0; k < p.word.length; k++) marked[(p.r + p.dr * k) * sz + (p.c + p.dc * k)] = true;
      });
      for (var i = 0; i < sz * sz; i++) if (!marked[i]) got.grid[i] = pool[(rnd() * pool.length) | 0];

      var spot = function (p) { return p.r + ',' + p.c + ',' + p.dr + ',' + p.dc; };
      var intended = {};
      got.placed.forEach(function (p) { intended[spot(p)] = 1; });
      var stuck = 0;
      for (var guard = 0; guard < 600; guard++) {
        var bad = null;
        for (var wi = 0; wi < got.placed.length && !bad; wi++) {
          var word = got.placed[wi].word, hits = findAll(got.grid, sz, word);
          for (var h = 0; h < hits.length; h++) {
            if (!intended[spot(hits[h])]) { bad = { at: hits[h], word: word }; break; }
          }
        }
        if (!bad) break;
        var loose = [];
        for (var k2 = 0; k2 < bad.word.length; k2++) {
          var idx = (bad.at.r + bad.at.dr * k2) * sz + (bad.at.c + bad.at.dc * k2);
          if (!marked[idx]) loose.push(idx);
        }
        /* No padding to change means two placed words spell it between them
           (or it reads the same backwards). Only a fresh layout fixes that. */
        if (!loose.length) { stuck = 1; break; }
        var cell = loose[(rnd() * loose.length) | 0], was = got.grid[cell], t = 0;
        do { got.grid[cell] = pool[(rnd() * pool.length) | 0]; } while (got.grid[cell] === was && ++t < 25);
      }
      return { size: sz, grid: got.grid, placed: got.placed, unplaced: got.unplaced, solved: marked, stuck: stuck };
    }

    /* Retry, then grow the grid, until every word fits and the answer key
       is the only place each word can be read. */
    var best = null;
    for (var grow = 0; grow <= 4 && size + grow <= 26; grow++) {
      for (var t = 0; t < 14; t++) {
        var got = build(size + grow);
        var worse = best && (got.unplaced.length > best.unplaced.length
          || (got.unplaced.length === best.unplaced.length && got.stuck && !best.stuck));
        if (!best || !worse) best = got;
        if (!got.unplaced.length && !got.stuck) return best;
      }
    }
    return best;
  }

  /* ── crossword ──────────────────────────────────────────────────── */

  function key(r, c) { return r + ',' + c; }

  /* Score a candidate placement, or -1 if it would break the grid.
     Two rules keep the puzzle legal: a word may not run straight into
     another word, and a letter that isn't a crossing may not sit
     shoulder-to-shoulder with a neighbour — both create words nobody
     wrote a clue for. */
  function fits(G, word, r, c, dr, dc) {
    var n = word.length, cross = 0;
    if (G[key(r - dr, c - dc)]) return -1;
    if (G[key(r + dr * n, c + dc * n)]) return -1;
    for (var k = 0; k < n; k++) {
      var rr = r + dr * k, cc = c + dc * k, cur = G[key(rr, cc)];
      if (cur) {
        if (cur !== word[k]) return -1;
        cross++;
      } else if (G[key(rr + dc, cc + dr)] || G[key(rr - dc, cc - dr)]) {
        return -1;
      }
    }
    return cross;
  }

  /* One greedy pass: place the longest word, then hang each remaining word
     off a letter that is already on the grid. */
  function layout(list, rnd) {
    var G = {}, placed = [], unplaced = [];
    function put(e, r, c, dr, dc) {
      for (var k = 0; k < e.word.length; k++) G[key(r + dr * k, c + dc * k)] = e.word[k];
      placed.push({ word: e.word, clue: e.clue, r: r, c: c, dr: dr, dc: dc });
    }
    put(list[0], 0, 0, 0, 1);

    for (var i = 1; i < list.length; i++) {
      var e = list[i], w = e.word, cand = [], top = -Infinity;
      for (var p = 0; p < placed.length; p++) {
        var P = placed[p], pd = P.dr === 0;            /* pd: P runs across */
        for (var a = 0; a < w.length; a++) {
          for (var b = 0; b < P.word.length; b++) {
            if (w[a] !== P.word[b]) continue;
            var dr = pd ? 1 : 0, dc = pd ? 0 : 1;       /* cross it at 90° */
            var r = pd ? P.r - a : P.r + b;
            var c = pd ? P.c + b : P.c - a;
            var cross = fits(G, w, r, c, dr, dc);
            if (cross < 1) continue;
            /* More crossings first; then the placement that grows the
               bounding box least, so the finished grid stays compact. */
            var span = bounds(G, r, c, r + dr * (w.length - 1), c + dc * (w.length - 1));
            var score = cross * 100 - (span.rows + span.cols);
            if (score > top) top = score;
            cand.push({ r: r, c: c, dr: dr, dc: dc, score: score });
          }
        }
      }
      if (!cand.length) { unplaced.push(e); continue; }
      /* Break ties at random — a single deterministic choice early on is
         what paints the grid into a corner for everything after it. */
      var pool = cand.filter(function (x) { return x.score >= top - 2; });
      var pick = pool[(rnd() * pool.length) | 0];
      put(e, pick.r, pick.c, pick.dr, pick.dc);
    }
    var bb = bounds(G);
    return { G: G, placed: placed, unplaced: unplaced, bb: bb, area: bb.rows * bb.cols };
  }

  function crossword(entries, opts) {
    opts = opts || {};
    var rnd = mulberry(opts.seed == null ? (Math.random() * 1e9) | 0 : opts.seed);
    var byLen = entries.slice().sort(function (a, b) { return b.word.length - a.word.length; });
    if (!byLen.length) return { cells: [], rows: 0, cols: 0, across: [], down: [], unplaced: [] };

    /* Which word goes down first decides most of the grid, so try a few
       orders and keep whichever fits the most words in the least space. */
    var best = null;
    for (var t = 0; t < 40; t++) {
      var order = t === 0 ? byLen
        : byLen.slice().sort(function (a, b) { return (b.word.length - a.word.length) || (rnd() - 0.5); });
      if (t > 20) order = byLen.slice().sort(function () { return rnd() - 0.5; });
      var got = layout(order, rnd);
      if (!best || got.placed.length > best.placed.length
        || (got.placed.length === best.placed.length && got.area < best.area)) best = got;
      if (!best.unplaced.length && t >= 8) break;
    }

    var G = best.G, rows = best.bb.rows, cols = best.bb.cols, r0 = best.bb.r0, c0 = best.bb.c0;
    var cells = [];
    for (var y = 0; y < rows; y++) {
      cells.push([]);
      for (var x = 0; x < cols; x++) cells[y].push(G[key(y + r0, x + c0)] ? { ch: G[key(y + r0, x + c0)] } : null);
    }

    /* Number every cell that begins a run, reading rows then columns —
       the same order a printed crossword uses. */
    var at = {}, num = 0;
    for (y = 0; y < rows; y++) {
      for (x = 0; x < cols; x++) {
        if (!cells[y][x]) continue;
        var startA = (x === 0 || !cells[y][x - 1]) && x + 1 < cols && cells[y][x + 1];
        var startD = (y === 0 || !cells[y - 1][x]) && y + 1 < rows && cells[y + 1][x];
        if (startA || startD) { cells[y][x].n = ++num; at[key(y, x)] = num; }
      }
    }

    var across = [], down = [];
    best.placed.forEach(function (P) {
      var y = P.r - r0, x = P.c - c0;
      (P.dr ? down : across).push({ n: at[key(y, x)], word: P.word, clue: P.clue, r: y, c: x, dr: P.dr, dc: P.dc });
    });
    var byNum = function (a, b) { return a.n - b.n; };
    return { cells: cells, rows: rows, cols: cols, across: across.sort(byNum), down: down.sort(byNum), unplaced: best.unplaced };
  }

  /* Bounding box of everything placed, optionally including a candidate. */
  function bounds(G, r1, c1, r2, c2) {
    var lo = Infinity, hi = -Infinity, lc = Infinity, hc = -Infinity;
    for (var k in G) {
      var p = k.split(','), r = +p[0], c = +p[1];
      if (r < lo) lo = r; if (r > hi) hi = r;
      if (c < lc) lc = c; if (c > hc) hc = c;
    }
    if (r1 != null) {
      lo = Math.min(lo, r1, r2); hi = Math.max(hi, r1, r2);
      lc = Math.min(lc, c1, c2); hc = Math.max(hc, c1, c2);
    }
    return { r0: lo, c0: lc, rows: hi - lo + 1, cols: hc - lc + 1 };
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* One document-level listener, so output redrawn on every run still
     has a working Print button without rebinding anything. */
  if (root.document) root.document.addEventListener('click', function (e) {
    var t = e.target;
    while (t && t !== root.document) {
      if (t.hasAttribute && t.hasAttribute('data-print')) { e.preventDefault(); root.print(); return; }
      t = t.parentNode;
    }
  });

  var DIRNAME = {
    '0,1': 'left to right', '1,0': 'top to bottom',
    '1,1': 'diagonally down and to the right', '-1,1': 'diagonally up and to the right',
    '0,-1': 'backwards, right to left', '-1,0': 'upwards, bottom to top',
    '-1,-1': 'diagonally up and to the left', '1,-1': 'diagonally down and to the left'
  };
  function dirName(dr, dc) { return DIRNAME[dr + ',' + dc] || ''; }

  root.MK = {
    parseWords: parseWords, parseClued: parseClued, esc: esc, dirName: dirName,
    wordsearch: wordsearch, crossword: crossword,
    occurrences: occurrences, findAll: findAll, DIRS: DIRS
  };
})(typeof module !== 'undefined' && module.exports ? module.exports : window);
