**Aviso de fiabilidad:** el brief de hoy trae un problema señalado en `validaciones`: "la plantilla tiene 14 jugadores, no 15". Las cifras de plantilla de hoy pueden no ser fiables en ese punto. Además, `medias_fiables` es `false` (solo 2 jornadas disputadas): ninguna media ni ranking por rendimiento en este análisis debe tomarse como fiable; se citan puntos brutos donde aporten información.

## Titular
El mercado cierra en 19,1 horas y, entre los 12 candidatos que tengo delante (de 48 en total), Abde Rebbach (MC, 7 puntos en sus 2 jornadas, 5.453.000 €, 27,36% de descuento) es el más sólido.

## Decisión
- **Fichaje: no hace falta hoy.** Tenemos cobertura en las dos posiciones tocadas: cuatro centrocampistas más aparte de Rioja (Bernal, Canales, Gueye, Almeida, Barja) y tres defensas más aparte de Krug (Tárrega, Bretones, Pastor). No se justifica pagar por Abde Rebbach (5.453.000 €) ni por ningún otro solo por esas dos bajas, aunque el mercado cierre en 19,1 horas.
- **Alineación:** dos jugadores fuera de estado "ok" antes de su próximo partido — Luis Rioja (MC, "injury") y Martín Krug (DF, "other", no es lesión: sin ficha o fuera de convocatoria) — ambos ante el Betis, en casa. Los dos, fuera de la convocatoria mientras siga su estado actual.
- **Capitán:** `capitan_activo` es `true`, toca elegir. `medias_fiables` es `false`, así que no se puede ordenar por `media` ni `media_por_millon`, y el brief no trae dato de probabilidad de gol. Roberto Fernández (DL) suma 21 puntos en sus 2 jornadas, el mayor acumulado de la plantilla con diferencia, y su posición de delantero le da más probabilidad de marcar que el resto. Con la reserva de que la muestra es de 2 jornadas, es el candidato más razonable.
- Nada más exige acción hoy: en `clausulas_top` no hay ganga aprovechable — los 10 candidatos están al mínimo legal de 1.000.000 €, la lista está ordenada por coste y no por calidad (`ordenado_por` lo dice explícitamente) y ninguno es nuestro.

## Ventana de mercado
Los 12 candidatos que tengo delante (de 48 en el mercado) cierran todos en 19,1 horas. Puntos brutos, no medias:
- Fran Pérez (MC) — 1.331.000 € — descuento 36,04% — 4 puntos en 2 jornadas
- Aihen Muñoz (DF) — 430.000 € — descuento 30,08% — 3 puntos en su única jornada
- Abde Rebbach (MC) — 5.453.000 € — descuento 27,36% — 7 puntos en 2 jornadas
- Rodrigo Mendoza (MC) — 2.764.000 € — descuento 20,02% — 7 puntos en 2 jornadas
- Jon Pacheco (DF) — 361.000 € — descuento 19,24% — sin jornadas con nota
- Arnaut Danjuma (DL) — 7.706.000 € — descuento 10,44% — 3 puntos en su única jornada
- Paco Cortés (MC) — 602.000 € — descuento 6,08% — 1 punto en su única jornada
- Víctor García (MC) — 1.962.000 € — descuento 6,08% — 4 puntos en 2 jornadas
- Óscar Valentín (MC) — 6.584.000 € — descuento 3,67% — 7 puntos en 2 jornadas
- Tai Abed (MC) — 329.000 € — descuento 3,52% — sin jornadas con nota (estado "other")
- Tajon Buchanan (MC) — 18.749.000 € — descuento 2,99% — 7 puntos en 2 jornadas
- Carl Starfelt (DF) — 9.233.000 € — descuento 2,60% — sin jornadas con nota

## Nuestra plantilla
Dos jugadores en estado distinto de "ok" (de los 14 que trae el brief, no 15 según el aviso de arriba):
- Luis Rioja (MC) — "injury" — rival: Betis, en casa. Sin blindar, cláusula 16.275.000 €.
- Martín Krug (DF) — "other" (no es lesión: sin ficha o fuera de convocatoria) — rival: Betis, en casa. Sin blindar, cláusula 1.000.000 €.

Exposición a cláusula: 11 de los 14 están sin blindar (`sin_blindar: 11`). El más expuesto, según el propio brief (`mas_expuesto`), es Marc Bernal: valor 22.053.000 €, cláusula 33.079.500 € (sobrecoste 1,5x, es decir, al mínimo legal, sin blindaje), 5 puntos en su única jornada.

## La liga
Estamos en la posición 7 de 10, con 28 puntos. El líder es Gonzalo, con 52 puntos y 154.063.000 € de valor de plantilla. En valor de plantilla vamos en el puesto 9 de 10 (`rank_valor: 9`), con 103.273.000 €; el mayor valor de plantilla lo tiene Mateo (`rank_valor: 1`), con 196.215.000 €, aunque solo suma 29 puntos (posición 6). No hay blindajes nuevos visibles en los datos de hoy: los 10 jugadores de `clausulas_top` figuran todos sin blindar.

## Calendario
Dos jugadores nuestros visitan a los rivales de mayor valor medio del calendario que tengo delante: Alemão y Peio Canales juegan fuera contra el FC Barcelona (valor medio 27.261.107 €), y Álex Pastor juega fuera contra el Real Madrid (valor medio 29.243.654 €, el más alto del calendario). Son los cruces más exigentes de la jornada para nosotros.

## Qué vigilar
- Estado de Luis Rioja y Martín Krug antes del partido ante el Betis (en casa): si alguno pasa a "ok", entra en la conversación de alineación; si siguen así, asumir la baja o ausencia.
- Cláusula de Marc Bernal, nuestro jugador más expuesto (33.079.500 €, sin blindar): si su valor sube de forma notable o vemos blindajes nuevos sobre jugadores similares en `clausulas_top`, valorar blindarlo.
- Ventana de mercado: los 48 fichajes visibles cierran en 19,1 horas; pasado ese plazo, se pierden opciones como Abde Rebbach (5.453.000 €) o Rodrigo Mendoza (2.764.000 €, 20,02% de descuento, 7 puntos en 2 jornadas).
