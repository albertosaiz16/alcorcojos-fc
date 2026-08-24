**Aviso de fiabilidad:** el brief de hoy trae un problema señalado en `validaciones`: "la plantilla tiene 13 jugadores, no 15". Las cifras de plantilla de hoy pueden no ser fiables en ese punto. Además, `medias_fiables` es `false` (solo 2 jornadas disputadas): ninguna media ni ranking por rendimiento en este análisis debe tomarse como fiable; se citan puntos brutos donde aporten información.

## Titular
El mercado cierra en 16,1 horas y, entre los 12 candidatos que tengo delante (de 49 en total), Odysseas Vlachodimos (PT, 12 puntos en sus 2 jornadas, 23.753.000 €) es el más sólido.

## Decisión
- **Portero de refuerzo: no hace falta fichar hoy.** Augusto Batalla (PT, nuestro) llega "injury" al partido ante el FC Barcelona, pero ya tenemos segundo portero en plantilla, Alejandro Iturbe (sin jornadas con nota todavía). No se justifica pagar por Vlachodimos (23.753.000 €) solo por esta baja, aunque cierre en 16,1 horas.
- **Alineación:** tres bajas por lesión antes de sus próximos partidos — Augusto Batalla (PT) ante FC Barcelona fuera, Luis Rioja (MC) ante Betis en casa, Kike García (DL) ante Real Sociedad fuera. Los tres, fuera de la convocatoria mientras el estado siga "injury".
- **Capitán:** `capitan_activo` es `true`, toca elegir. `medias_fiables` es `false`, así que no se puede ordenar por `media` ni `media_por_millon`, y el brief no trae dato de probabilidad de gol. Entre los delanteros en estado "ok" con partido esta jornada: Lucas Cepeda suma 6 puntos en sus 2 jornadas con nota y visita a Racing de Santander, el rival de menor valor medio de plantilla entre los cruces de los nuestros (7.755.217 €); Alemão suma 5 puntos en su único partido pero visita al FC Barcelona, el rival más caro del calendario. Con la reserva de que la muestra es de 1-2 jornadas, Lucas Cepeda es el candidato más razonable.
- Nada más exige acción hoy: en `clausulas_top` no hay ganga aprovechable — los 10 candidatos están al mínimo legal de 1.000.000 €, la lista está ordenada por coste y no por calidad (`ordenado_por` lo dice explícitamente) y ninguno es nuestro.

## Ventana de mercado
Los 12 candidatos que tengo delante (de 49 en el mercado) cierran todos en 16,1 horas (mismo `cierre_ts`). Puntos brutos, no medias:
- Jon Pacheco (DF) — 361.000 € — descuento 22,37% — sin jornadas con nota
- Enzo Bardeli (MC) — 1.586.000 € — descuento 11,94% — 2 puntos en 1 jornada
- Diego López (MC) — 362.000 € — descuento 10,62% — "injury", sin jornadas con nota
- Óscar Valentín (MC) — 6.584.000 € — descuento 2,33% — 7 puntos en 2 jornadas
- Odysseas Vlachodimos (PT) — 23.753.000 € — descuento 2,08% — 12 puntos en 2 jornadas
- Aïssa Mandi (DF) — 5.688.000 € — descuento 1,49% — 4 puntos en 1 jornada
- Buba Sangaré (DF) — 5.386.000 € — descuento 1,12% — -3 puntos en 2 jornadas
- Chupete (DL) — 25.769.000 € — sin descuento — -1 punto en su única jornada — libre
- Gonçalo Guedes (DL) — 22.176.000 € — sin descuento — "injury", sin jornadas con nota — libre
- Maguette Gueye (MC) — 5.263.000 € — sin descuento — 7 puntos en 2 jornadas — libre
- Peque Fernández (MC) — 4.427.000 € — sin descuento — 8 puntos en 2 jornadas — libre
- Diego Gómez (MC) — 333.000 € — sin descuento — sin jornadas con nota — libre

## Nuestra plantilla
Tres jugadores en estado distinto de "ok" (de los 13 que trae el brief, no 15 según el aviso de arriba):
- Augusto Batalla (PT) — "injury" — rival: FC Barcelona, fuera. Pierde valor hoy (-635.000 €, -2,5%).
- Luis Rioja (MC) — "injury" — rival: Betis, en casa.
- Kike García (DL) — "injury" — rival: Real Sociedad, fuera.

Exposición a cláusula: los 13 están sin blindar (`sin_blindar: 13`). El más expuesto, según el propio brief (`mas_expuesto`), es Augusto Batalla: valor 24.749.000 €, cláusula mínima 37.123.500 € (sobrecoste 1,5x), sin blindar. Ningún otro jugador de la plantilla combina valor alto y falta de blindaje de forma llamativa hoy.

## La liga
Estamos en la posición 6, con 23 puntos (empatados con Fede). El líder es Gonzalo, con 41 puntos y 165.172.000 € de valor de plantilla. En valor de plantilla vamos últimos del grupo (`rank_valor: 10`), con 89.257.000 €; el mayor valor de plantilla lo tiene Mateo, con 214.662.000 € (pero 29 puntos, tercero). No hay datos de blindajes de rivales en la muestra que tengo: `clausulas_top` solo trae candidatos a cláusula mínima (1.000.000 €), ninguno blindado.

## Calendario
Tres jugadores nuestros (Augusto Batalla, Alemão, Peio Canales) visitan al FC Barcelona, el equipo de mayor valor medio de plantilla del calendario que tengo delante junto al Real Madrid (27.337.142 € frente a 29.352.307 €). Es el cruce más exigente de la jornada para nosotros.

## Qué vigilar
- Estado de Luis Rioja y Kike García antes de sus partidos (Betis en casa, Real Sociedad fuera): si pasan a "ok", entran en la conversación de alineación; si siguen "injury", asumir la baja.
- Cláusula de Augusto Batalla (37.123.500 €, sin blindar): si en un próximo brief aparece con `blindado: true` o cambia de `dueño`, es señal de que un rival se lo plantea o de que lo hemos protegido.
- `medias_fiables`: si pasa a `true` con más jornadas, se podrá usar `media`/`media_por_millon` para fichajes y capitanía con más confianza que los puntos brutos de hoy.
