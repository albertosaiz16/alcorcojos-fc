(async () => {
  const CONFIG = {
    owner: 'albertosaiz16',
    repo: 'alcorcojos-fc',
    token: 'github_pat_XXXX',
    minJugadores: 500,   // sube esto si el universo crece; si baja, algo corta
  };

  const cfg = JSON.parse(
    document.documentElement.innerHTML.match(/var _FG_cfg = (\{.*?\});\n/s)[1]);

  const H = {
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'x-auth': cfg.auth,
    'x-requested-with': 'XMLHttpRequest',
  };

  // Sin topes de valor ni de clausula: cualquier limite numerico caduca.
  const FILTERS = 'post=players&filters%5Bposition%5D=0'
    + '&filters%5Bteam%5D=0&filters%5Binjured%5D=0&filters%5Bfavs%5D=0'
    + '&filters%5Bowner%5D=0&filters%5Bbenched%5D=0'
    + '&filters%5Bstealable%5D=0&order=0&name=&parentElement=%23fg-content';

  /* Quita nombre y email de cualquier HTML antes de que salga del navegador.
   * Cubre _FG_cfg.user, _FG_cfg.context.user y la variable suelta _FG_user. */
  const anonimizar = (html) => html
    .replace(/"email"\s*:\s*"[^"]*"/g, '"email":null')
    .replace(/"name"\s*:\s*"saizalbert"/g, '"name":"__ME__"')
    .replace(/saizalbert/g, '__ME__');

  const ctx = JSON.parse(JSON.stringify(cfg.context || {}));
  if (ctx.user) ctx.user = { id: ctx.user.id };

  const out = {
    ts: new Date().toISOString(),
    market_date: cfg.market_date,
    context: ctx,
    // Flags del juego que afectan a la decision y no estaban en el payload.
    features: {
      captain: !!cfg.FEATURE_CAPTAIN_ENABLED,
      league_captain: !!cfg.LEAGUE_CAPTAIN_ENABLED,
      market_lock: cfg.market_lock,
    },
    chunks: [],
    pages: {},
    probes: {},
  };

  const balance = await fetch('https://fantasy.marca.com/ajax/balance',
    { headers: { 'x-auth': cfg.auth, 'x-requested-with': 'XMLHttpRequest' } });
  out.balance = (await balance.json()).data;
  console.log('saldo', out.balance.current);

  let nJugadores = 0;
  for (let off = 0; off < 3000; off += 50) {
    const r = await fetch('https://fantasy.marca.com/ajax/sw/players', {
      method: 'POST', headers: H, credentials: 'include',
      referrer: 'https://fantasy.marca.com/search',
      body: FILTERS + '&offset=' + off,
    });
    const t = await r.text();
    if (t.length < 200) break;
    // anonimizar() tambien limpia esto: /ajax/sw/players puede traer el
    // nombre/email del propietario dentro del objeto del jugador.
    out.chunks.push({ offset: off, html: anonimizar(t) });
    try { nJugadores += JSON.parse(t).data.players.length; } catch (e) { /* */ }
    await new Promise(s => setTimeout(s, 300));
  }
  console.log('chunks', out.chunks.length, '| jugadores', nJugadores);
  if (nJugadores < CONFIG.minJugadores) {
    console.warn(`AVISO: solo ${nJugadores} jugadores (esperados >= `
      + `${CONFIG.minJugadores}). Revisa los filtros antes de fiarte del brief.`);
  }
  out.n_jugadores = nJugadores;

  const PAGES = {
    equipo: '/team',
    mercado: '/market',
    clasificacion: '/standings',
    buscador: '/search',
  };
  for (const [k, u] of Object.entries(PAGES)) {
    const html = await (await fetch('https://fantasy.marca.com' + u)).text();
    out.pages[k] = anonimizar(html);
  }

  /* Sondas. No se de que endpoint salen el diccionario de equipos y la
   * jornada; estas son las candidatas. Mira que devuelve cada una la primera
   * vez que ejecutes esto y quedate con la que funcione. */
  for (const [k, u] of Object.entries({
    equipos: '/ajax/teams',
    jornada: '/ajax/gameweek',
    calendario: '/ajax/calendar',
  })) {
    try {
      const r = await fetch('https://fantasy.marca.com' + u, { headers: H });
      const t = await r.text();
      out.probes[k] = { status: r.status, muestra: t.slice(0, 400) };
      console.log('sonda', k, r.status, t.slice(0, 120));
    } catch (e) {
      out.probes[k] = { error: String(e) };
    }
  }

  if (JSON.stringify(out).includes('@')) {
    console.warn('AVISO: quedan arrobas en el payload. Revisa anonimizar().');
  }

  const gz = new Blob([JSON.stringify(out)]).stream()
    .pipeThrough(new CompressionStream('gzip'));
  const buf = await new Response(gz).arrayBuffer();
  let bin = '';
  new Uint8Array(buf).forEach(b => { bin += String.fromCharCode(b); });
  const b64 = btoa(bin);

  const path = `data/raw/${cfg.market_date}.json.gz`;
  const api = `https://api.github.com/repos/${CONFIG.owner}/${CONFIG.repo}`
    + `/contents/${path}`;
  const auth = {
    Authorization: 'Bearer ' + CONFIG.token,
    Accept: 'application/vnd.github+json',
  };

  let sha;
  const prev = await fetch(api, { headers: auth });
  if (prev.ok) sha = (await prev.json()).sha;

  const put = await fetch(api, {
    method: 'PUT', headers: auth,
    body: JSON.stringify({
      message: `captura ${cfg.market_date}`,
      content: b64,
      ...(sha ? { sha } : {}),
    }),
  });

  console.log(put.ok
    ? `SUBIDO ${path} (${(b64.length / 1365).toFixed(0)} KB)`
    : `ERROR ${put.status}: ${await put.text()}`);
})();