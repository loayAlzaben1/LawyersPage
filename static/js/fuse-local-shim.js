// Minimal local Fuse-like shim v1
// Provides a Fuse-like constructor with search(list) returning array of { item, score }
// This is intentionally tiny and approximate: it performs tokenized substring matching
// and returns simple scores (lower is better). It is not a full substitute for Fuse.js
// but works as a reliable local fallback for fuzzy-ish search.
(function(global){
  function tokenize(s){ return (s||'').toString().trim().toLowerCase().split(/\s+/).filter(Boolean); }
  function scoreMatch(qTokens, text){
    if(!qTokens || !qTokens.length) return 0;
    var t = (text||'').toString().toLowerCase();
    var score = 0; // lower is better
    qTokens.forEach(function(tok){
      if(t.indexOf(tok) === 0) score += 0; // best
      else if(t.indexOf(tok) !== -1) score += 1; // okay
      else score += 5; // no match
    });
    return score + Math.max(0, (t.length - qTokens.join(' ').length) / 100);
  }

  function LocalFuse(list, opts){
    this.list = list || [];
    this.keys = (opts && opts.keys) || ['title','desc'];
  }
  LocalFuse.prototype.search = function(query, options){
    var q = (query||'').toString().trim().toLowerCase();
    if(!q) return [];
    var qTokens = tokenize(q);
    var results = [];
    for(var i=0;i<this.list.length;i++){
      var it = this.list[i];
      var text = '';
      for(var k=0;k<this.keys.length;k++){ var key = this.keys[k]; text += ' ' + (it[key]||''); }
      var sc = scoreMatch(qTokens, text);
      // filter out very bad matches
      if(sc < 6){ results.push({ item: this.list[i], score: sc }); }
    }
    results.sort(function(a,b){ return a.score - b.score; });
    return results;
  };

  // Expose under Fuse name if real Fuse is not present
  if(!global.Fuse){ global.Fuse = LocalFuse; global.__FUSE_LOCAL_SHIM = true; }
})(window);
