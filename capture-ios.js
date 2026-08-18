/* Alcorcojos FC — captura desde iPhone.
 *
 * Va dentro de la acción "Ejecutar JavaScript en la página web" de Atajos.
 * Se lanza desde la hoja de Compartir de Safari, estando en
 * fantasy.marca.com con la sesión iniciada.
 *
 * A diferencia de capture.js, aquí no se descarga ningún fichero: el JSON
 * comprimido viaja directo a GitHub y la función completion() devuelve el
 * resultado a Atajos para que te lo enseñe.
 *
 * Rellena CONFIG antes de guardarlo.
 */
(async () => {
  const CONFIG = {
    owner: 'TU_USUARIO_GITHUB',
    repo: 'alcorcojos-fc',
    token: 'github_pat_XXXX',
  };

  try {
    const html = document.documentElement.innerHTML;
    const match = html.match(/var _FG_cfg = (\{.*?\});\n/s);
    if (!match) {
      return completion('No estás en fantasy.marca.com o falta la sesión.');
    }
    const cfg = JSON.parse(match[1]);

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

    const ctx = JSON.parse(JSON.stringify(cfg.context || {}));
    if (ctx.user) ctx.user = { id: ctx.user.id };

    const out = {
      ts: new Date().toISOString(),
      market_date: cfg.market_date,
      context: ctx,
      chunks: [],
      pages: {},
      origen: 'ios',
    };

    const bal = await fetch('https://fantasy.marca.com/ajax/balance', {
      headers: { 'x-auth': cfg.auth, 'x-requested-with': 'XMLHttpRequest' },
    });
    out.balance = (await bal.json()).data;

    for (let off = 0; off < 3000; off += 50) {
      const r = await fetch('https://fantasy.marca.com/ajax/sw/players', {
        method: 'POST', headers: H, credentials: 'include',
        body: FILTERS + '&offset=' + off,
      });
      const t = await r.text();
      if (t.length < 200) break;
      out.chunks.push({ offset: off, html: t });
    }

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

    let sha;
    const prev = await fetch(api, { headers: auth });
    if (prev.ok) sha = (await prev.json()).sha;

    const put = await fetch(api, {
      method: 'PUT', headers: auth,
      body: JSON.stringify({
        message: `captura ${cfg.market_date} (ios)`,
        content: b64,
        ...(sha ? { sha } : {}),
      }),
    });

    if (!put.ok) return completion(`Error GitHub ${put.status}`);
    return completion(
      `${cfg.market_date} · ${out.chunks.length * 50} jugadores · `
      + `${(b64.length / 1365).toFixed(0)} KB subidos`);
  } catch (e) {
    return completion('Fallo: ' + e.message);
  }
})();
