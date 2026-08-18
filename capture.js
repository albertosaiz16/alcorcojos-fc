/* Alcorcojos FC — captura diaria.
 * Pegar en la consola de Chrome estando logueado en fantasy.marca.com.
 * Rellena CONFIG antes del primer uso.
 */
(async () => {
  const CONFIG = {
    owner: 'TU_USUARIO_GITHUB',
    repo: 'alcorcojos-fc',
    token: 'github_pat_XXXX',
  };

  const cfg = JSON.parse(
    document.documentElement.innerHTML.match(/var _FG_cfg = (\{.*?\});\n/s)[1]);

  const H = {
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'x-auth': cfg.auth,
    'x-requested-with': 'XMLHttpRequest',
  };

  const FILTERS = 'post=players&filters%5Bposition%5D=0'
    + '&filters%5Bvalue_from%5D=0&filters%5Bvalue_to%5D=81300000'
    + '&filters%5Bclause_from%5D=0&filters%5Bclause_to%5D=95800000'
    + '&filters%5Bteam%5D=0&filters%5Binjured%5D=0&filters%5Bfavs%5D=0'
    + '&filters%5Bowner%5D=0&filters%5Bbenched%5D=0'
    + '&filters%5Bstealable%5D=0&order=0&name=&parentElement=%23fg-content';

  // Quitamos datos personales antes de que nada salga del navegador.
  const ctx = JSON.parse(JSON.stringify(cfg.context || {}));
  if (ctx.user) ctx.user = { id: ctx.user.id };

  const out = {
    ts: new Date().toISOString(),
    market_date: cfg.market_date,
    context: ctx,
    chunks: [],
    pages: {},
  };

  const balance = await fetch('https://fantasy.marca.com/ajax/balance',
    { headers: { 'x-auth': cfg.auth, 'x-requested-with': 'XMLHttpRequest' } });
  out.balance = (await balance.json()).data;
  console.log('saldo', out.balance.current);

  for (let off = 0; off < 3000; off += 50) {
    const r = await fetch('https://fantasy.marca.com/ajax/sw/players', {
      method: 'POST', headers: H, credentials: 'include',
      referrer: 'https://fantasy.marca.com/search',
      body: FILTERS + '&offset=' + off,
    });
    const t = await r.text();
    if (t.length < 200) break;
    out.chunks.push({ offset: off, html: t });
    await new Promise(s => setTimeout(s, 300));
  }
  console.log('chunks', out.chunks.length);

  for (const [k, u] of Object.entries(
    { equipo: '/team', mercado: '/market', clasificacion: '/standings' })) {
    out.pages[k] = await (await fetch('https://fantasy.marca.com' + u)).text();
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

  // Si el fichero ya existe hoy, GitHub exige el sha para sobrescribirlo.
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
