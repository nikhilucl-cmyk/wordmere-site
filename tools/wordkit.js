/* Shared engine for the Wordmere word tools.
   One dictionary (104,562 words, 3-8 letters, public domain) loaded once
   and cached by the browser across every tool page. */
(function (w) {
  var queue = [], DICT = null, byLen = {}, SET = null, COMMON = new Set();
  var SCORE = {A:1,B:3,C:3,D:2,E:1,F:4,G:2,H:4,I:1,J:8,K:5,L:1,M:3,N:1,O:1,P:3,Q:10,R:1,S:1,T:1,U:1,V:4,W:4,X:8,Y:4,Z:10};

  fetch('/tools/words.txt?v=2').then(function (r) { return r.text(); }).then(function (t) {
    /* A trailing * marks a common word: one with a real dictionary
       definition in the game, or a plain inflection of one. */
    DICT = t.split('\n').filter(Boolean).map(function (d) {
      if (d.charAt(d.length - 1) === '*') { d = d.slice(0, -1); COMMON.add(d); }
      return d;
    });
    SET = new Set(DICT);
    for (var i = 0; i < DICT.length; i++) { var d = DICT[i]; (byLen[d.length] = byLen[d.length] || []).push(d); }
    var q = queue; queue = null; q.forEach(function (f) { f(); });
  }).catch(function () { var q = queue || []; queue = null; q.forEach(function (f) { f(new Error('load')); }); });

  function counts(s) { var c = {}; for (var i = 0; i < s.length; i++) c[s[i]] = (c[s[i]] || 0) + 1; return c; }

  /* Can `word` be spelled from the letter counts in `have`, using up to
     `blanks` wildcard tiles for letters we don't hold? */
  function makeable(word, have, blanks) {
    var need = {}, short = 0; blanks = blanks || 0;
    for (var i = 0; i < word.length; i++) {
      var ch = word[i]; need[ch] = (need[ch] || 0) + 1;
      if (need[ch] > (have[ch] || 0)) { short++; if (short > blanks) return false; }
    }
    return true;
  }

  /* Scrabble-style score: real tiles score, blank-filled letters score 0.
     Uses real tiles first so the score is the best available. */
  function score(word, have) {
    var left = {}, k, s = 0;
    for (k in have) left[k] = have[k];
    for (var i = 0; i < word.length; i++) {
      var ch = word[i];
      if (left[ch] > 0) { left[ch]--; s += SCORE[ch] || 0; }
    }
    return s;
  }

  function clean(v, extra) { return (v || '').toUpperCase().replace(extra ? /[^A-Z?]/g : /[^A-Z]/g, ''); }

  function group(words, title) {
    var by = {}, out = '';
    words.forEach(function (x) { var L = (x.w || x).length; (by[L] = by[L] || []).push(x); });
    /* Within each length, common words first; original order kept inside each class. */
    Object.keys(by).forEach(function (L) {
      var c = [], r = [];
      by[L].forEach(function (x) { (COMMON.has(x.w || x) ? c : r).push(x); });
      by[L] = c.concat(r);
    });
    Object.keys(by).map(Number).sort(function (a, b) { return b - a; }).forEach(function (L) {
      var list = by[L];
      out += '<div class="group"><h2>' + L + '-letter words <span>' + list.length + '</span></h2><ul class="words">';
      list.forEach(function (x) {
        var word = x.w || x, cls = [];
        if (x.top) cls.push('top');
        if (!COMMON.has(word)) cls.push('rare');
        out += '<li' + (cls.length ? ' class="' + cls.join(' ') + '"' : '') + (COMMON.has(word) ? '' : ' title="Less common word"') + '>'
             + word + (x.s != null ? '<em>' + x.s + '</em>' : '') + '</li>';
      });
      out += '</ul></div>';
    });
    return out;
  }

  w.WK = {
    onReady: function (f) { if (DICT) f(); else if (queue) queue.push(f); else f(new Error('load')); },
    get dict() { return DICT; }, get byLen() { return byLen; },
    has: function (x) { return SET ? SET.has(x) : false; },
    isCommon: function (x) { return COMMON.has(x); },
    counts: counts, makeable: makeable, score: score, clean: clean, group: group, SCORE: SCORE
  };
})(window);
