"""Genera el dashboard estático en docs/."""
import json
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alcorcojos FC</title>
<style>
:root{--bg:#0f1115;--card:#171a21;--line:#252a34;--txt:#e6e8ec;--dim:#8b94a3;
--up:#3fb950;--down:#f85149;--warn:#d29922;--acc:#58a6ff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);
font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{padding:20px 16px 12px;border-bottom:1px solid var(--line)}
h1{margin:0;font-size:19px;font-weight:600}
.sub{color:var(--dim);font-size:13px;margin-top:2px}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px 60px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
gap:10px;margin:16px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:12px 14px}
.kpi .l{color:var(--dim);font-size:12px}
.kpi .v{font-size:21px;font-weight:600;margin-top:2px}
nav{display:flex;gap:6px;overflow-x:auto;margin:18px 0 14px;
padding-bottom:4px}
nav button{background:var(--card);color:var(--dim);border:1px solid var(--line);
border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer;
white-space:nowrap}
nav button.on{color:var(--txt);border-color:var(--acc)}
section{display:none}section.on{display:block}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:var(--dim);font-weight:500;padding:8px 10px;
border-bottom:1px solid var(--line);font-size:12px;white-space:nowrap}
td{padding:9px 10px;border-bottom:1px solid var(--line)}
tr:hover td{background:#1c2029}
.num{text-align:right;font-variant-numeric:tabular-nums}
.up{color:var(--up)}.down{color:var(--down)}
.tag{font-size:11px;padding:2px 7px;border-radius:5px;background:#252a34;
color:var(--dim)}
.tag.injury{background:#3d1418;color:#ff7b72}
.tag.doubt{background:#3a2d0b;color:#e3b341}
.tag.red{background:#3d1418;color:#ff7b72}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.md{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:4px 20px 20px}
.md h2{font-size:15px;margin:22px 0 6px;color:var(--acc)}
.md p,.md li{font-size:14px;color:#d3d7de}
.warn{background:#3a2d0b;border:1px solid #6b5115;border-radius:8px;
padding:10px 14px;font-size:13px;margin:12px 0}
footer{color:var(--dim);font-size:12px;padding:24px 16px;text-align:center}
</style></head><body>
<header><div class="wrap" style="padding-bottom:0">
<h1>Alcorcojos FC</h1><div class="sub" id="sub"></div>
</div></header>
<div class="wrap">
<div class="kpis" id="kpis"></div>
<nav id="nav"></nav>
<div id="views"></div>
</div>
<footer>Generado automáticamente · datos de fantasy.marca.com</footer>
<script id="payload" type="application/json">__DATA__</script>
<script id="analysis" type="text/plain">__ANALYSIS__</script>
<script>
const D = JSON.parse(document.getElementById('payload').textContent);
const A = document.getElementById('analysis').textContent;
const eur = n => n == null ? '—' :
  new Intl.NumberFormat('es-ES').format(Math.round(n)) + ' \\u20ac';
const pct = n => n == null || isNaN(n) ? '—' : (n*100).toFixed(1) + '%';
const sign = n => n > 0 ? 'up' : n < 0 ? 'down' : '';
const arrow = n => n > 0 ? '\\u2191' : n < 0 ? '\\u2193' : '';
const tag = s => s && s !== 'ok'
  ? `<span class="tag ${s}">${s}</span>` : '';

document.getElementById('sub').textContent =
  `Mercado del ${D.meta.market_date} \\u00b7 temporada ${D.meta.temporada}` +
  ` \\u00b7 saldo ${eur(D.meta.saldo)}`;

const kpis = [
  ['Saldo', eur(D.meta.saldo)],
  ['Valor plantilla', eur(D.plantilla.resumen.valor_total)],
  ['Variación hoy', arrow(D.plantilla.resumen.delta_total) + ' ' +
    eur(Math.abs(D.plantilla.resumen.delta_total))],
  ['Riesgo cláusula', eur(D.plantilla.resumen.riesgo_clausula)],
  ['Libres', D.universo.libres + ' / ' + D.universo.total],
  ['Lesionados', D.universo.lesionados + ' + ' + D.universo.dudas + ' dudas']
];
document.getElementById('kpis').innerHTML = kpis.map(([l,v]) =>
  `<div class="kpi"><div class="l">${l}</div><div class="v">${v}</div></div>`
).join('');

function table(rows, cols) {
  if (!rows.length) return '<p style="color:var(--dim)">Sin datos.</p>';
  const head = cols.map(c => `<th class="${c.n?'num':''}">${c.h}</th>`).join('');
  const body = rows.map(r =>
    '<tr>' + cols.map(c =>
      `<td class="${c.n?'num':''} ${c.c?c.c(r):''}">${c.f(r)}</td>`
    ).join('') + '</tr>').join('');
  return `<div class="scroll"><table><thead><tr>${head}</tr></thead>
    <tbody>${body}</tbody></table></div>`;
}

const P = r => `${r.nombre} <span class="tag">${r.posicion}</span> ${tag(r.estado)}`;

const VIEWS = {
  'Análisis': () => `<div class="md" id="md"></div>`,

  'Mi plantilla': () => table(D.plantilla.jugadores, [
    {h:'Jugador', f:P},
    {h:'Valor', n:1, f:r=>eur(r.valor)},
    {h:'Hoy', n:1, f:r=>arrow(r.delta_valor)+' '+eur(Math.abs(r.delta_valor)),
      c:r=>sign(r.delta_valor)},
    {h:'Cláusula', n:1, f:r=>eur(r.clausula)},
    {h:'Pts', n:1, f:r=>r.puntos},
    {h:'Media', n:1, f:r=>r.media}
  ]),

  'Cláusulas': () => `<div class="warn">La cláusula es siempre 1,5\\u00d7 el
    valor (suelo 1.000.000 \\u20ac). Sin jornadas jugadas, el orden por
    rendimiento aún no es informativo.</div>` +
    table(D.clausulas.candidatos, [
    {h:'Jugador', f:P},
    {h:'Dueño', f:r=>r.dueno||'—'},
    {h:'Valor', n:1, f:r=>eur(r.valor)},
    {h:'Cláusula', n:1, f:r=>eur(r.clausula)},
    {h:'Sobrecoste', n:1, f:r=>r.sobrecoste.toFixed(2)+'\\u00d7'},
    {h:'Pagable', n:1, f:r=>r.asequible?'Sí':'No', c:r=>r.asequible?'up':'down'},
    {h:'Pts', n:1, f:r=>r.puntos}
  ]),

  'Mercado': () => table(D.mercado.pujas, [
    {h:'Jugador', f:P},
    {h:'Valor', n:1, f:r=>eur(r.valor)},
    {h:'Salida', n:1, f:r=>eur(r.precio_salida)},
    {h:'Dto.', n:1, f:r=>pct(r.descuento), c:r=>sign(r.descuento)},
    {h:'Pagable', n:1, f:r=>r.asequible?'Sí':'No', c:r=>r.asequible?'up':'down'},
    {h:'Libre', n:1, f:r=>r.libre?'Sí':'No'},
    {h:'Pts', n:1, f:r=>r.puntos}
  ]),

  'Suben': () => table(D.variaciones.suben, [
    {h:'Jugador', f:P},
    {h:'Valor', n:1, f:r=>eur(r.valor)},
    {h:'Variación', n:1, f:r=>'+'+eur(r.delta_valor), c:()=>'up'},
    {h:'%', n:1, f:r=>pct(r.delta_pct), c:()=>'up'},
    {h:'Dueño', f:r=>r.dueno||'libre'}
  ]),

  'Bajan': () => table(D.variaciones.bajan, [
    {h:'Jugador', f:P},
    {h:'Valor', n:1, f:r=>eur(r.valor)},
    {h:'Variación', n:1, f:r=>eur(r.delta_valor), c:()=>'down'},
    {h:'%', n:1, f:r=>pct(r.delta_pct), c:()=>'down'},
    {h:'Dueño', f:r=>r.dueno||'libre'}
  ]),

  'Liga': () => table(D.liga, [
    {h:'#', n:1, f:r=>r.posicion},
    {h:'Mánager', f:r=>r.nombre},
    {h:'Puntos', n:1, f:r=>r.puntos},
    {h:'Jugadores', n:1, f:r=>r.n_jugadores},
    {h:'Valor plantilla', n:1, f:r=>eur(r.valor_plantilla)}
  ])
};

const nav = document.getElementById('nav');
const views = document.getElementById('views');
Object.keys(VIEWS).forEach((k, i) => {
  const b = document.createElement('button');
  b.textContent = k; b.className = i === 0 ? 'on' : '';
  const s = document.createElement('section');
  s.className = i === 0 ? 'on' : ''; s.innerHTML = VIEWS[k]();
  b.onclick = () => {
    [...nav.children].forEach(x => x.classList.remove('on'));
    [...views.children].forEach(x => x.classList.remove('on'));
    b.classList.add('on'); s.classList.add('on');
  };
  nav.appendChild(b); views.appendChild(s);
});

const md = document.getElementById('md');
if (md) md.innerHTML = A
  .replace(/^## (.+)$/gm, '<h2>$1</h2>')
  .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
  .replace(/^- (.+)$/gm, '<li>$1</li>')
  .split('\\n\\n').map(b => b.startsWith('<') ? b : `<p>${b}</p>`).join('');
</script></body></html>
"""


def build(payload, analisis, out_dir="docs"):
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    html = (TEMPLATE
            .replace("__DATA__", json.dumps(payload, ensure_ascii=False,
                                            default=str))
            .replace("__ANALYSIS__", analisis))
    (out / "index.html").write_text(html, encoding="utf-8")
    return out / "index.html"
