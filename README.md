# Alcorcojos FC

Sistema de apoyo a la decisión para Fantasy Marca (LaLiga, puntuación
Sofascore). Captura diaria de mercado, pipeline determinista de métricas y
dashboard estático.

## Arquitectura

```
Chrome (capture.js)  ó  iPhone (atajo + capture-ios.js)
  └─ PUT GitHub Contents API
       └─ data/raw/YYYY-MM-DD.json.gz        [crudo, inmutable]

push → GitHub Action
  ├─ pipeline/run.py       métricas → docs/data.json + data/brief.json
  ├─ claude-code-action    lee el brief → docs/analisis.md
  ├─ pipeline/render.py    data.json + analisis.md → docs/index.html
  └─ commit

GitHub Pages → dashboard
```

Dos etapas separadas a propósito. La primera es determinista y
backtesteable; la segunda solo redacta. Claude nunca calcula: recibe un
brief ya cerrado y `verificar_numeros()` comprueba después que no se haya
inventado ninguna cifra.

El crudo no se modifica nunca. Cualquier cambio de parser o de modelo se
reprocesa sobre todo el histórico acumulado.

## Uso diario

**Ordenador:** abrir fantasy.marca.com en Chrome con sesión iniciada y pegar
`capture.js` en la consola.

**iPhone:** abrir fantasy.marca.com en Safari → Compartir → atajo
"Capturar Fantasy".

## Puesta en marcha

1. Repo `alcorcojos-fc` en GitHub. Settings → Pages → Source: GitHub Actions
2. Fine-grained PAT con `Contents: Read and write` solo sobre este repo.
   Pegarlo en el `CONFIG` de `capture.js` y `capture-ios.js`
3. `npm i -g @anthropic-ai/claude-code && claude setup-token`.
   El `sk-ant-oat01-...` resultante va como secret `CLAUDE_CODE_OAUTH_TOKEN`.
   Usa tu suscripción, no facturación por API
4. Instalar la app de GitHub de Claude: https://github.com/apps/claude

### Atajo de iPhone

Atajos → nuevo atajo → acción **Ejecutar JavaScript en la página web** →
pegar `capture-ios.js` → en los ajustes del atajo, activar **Mostrar en la
hoja de compartir** y aceptar páginas web de Safari.

## Datos

`ajax/sw/players` devuelve por jugador: valor, valor previo, cláusula,
propietario, estado (lesión / duda / sanción), puntos, media, racha de
jornadas y próximo rival. 516 jugadores en 11 páginas de 50.

Reglas confirmadas empíricamente:

- Cláusula = 1,5 × valor, con suelo de 1.000.000 €
- Puntuación derivada del rating Sofascore: lineal a 5 pts por unidad en la
  franja 6,0–7,9, aplanada por encima de 8,0, suelo en −4
- Bonus de gol aditivos y fuera de esa tabla: PT 6, DF 5, MC 4, DL 3

## Pendiente

- Mapeo `id_equipo` → nombre
- Enriquecimiento con `soccerdata` (Sofascore: torneo 8, temporada 77559)
- Modelo de dos etapas: P(juega ≥8 min) × distribución sobre bandas de rating
- Optimizador de fichajes y alineación (PuLP)
