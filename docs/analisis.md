**Aviso de fiabilidad:** el brief de hoy trae dos problemas señalados en `validaciones`: "la plantilla tiene 14 jugadores, no 15" y "valores no finitos en campos que no deberian estarlo: sobrecoste (x14)". Las cifras de plantilla y de cláusulas de hoy pueden no ser fiables en esos puntos.

## Titular
El mercado cierra en 16,3 horas y, entre los 12 candidatos que tengo delante (de 20 en total), Miguel Sierra (MC, 11 puntos en sus 2 jornadas disputadas, 4.125.000 €) es el más sólido.

## Decisión
- **Fichaje:** Miguel Sierra (MC), 4.125.000 €, cierra en 16,3 horas. Es el único candidato del mercado con nota en las dos jornadas disputadas (11 puntos), muy por debajo del saldo disponible (58.543.000 €). Recomendado antes del cierre.
- **Alineación:** Kike Salas (DF) está en estado "red" (sancionado) para el partido en casa ante Atlético de Madrid — no se puede alinear. Augusto Batalla (PT) está "injury" y su equipo visita al FC Barcelona — buscar alternativa en portería antes de la próxima alineación; el brief no da fecha exacta del cierre de alineaciones. Adrián Niño (DL) sigue "injury". Facundo Garcés (DF) está en "other" (sin ficha/no convocado), no disponible.
- **Capitán:** `capitan_activo` es `true`, toca elegir. `medias_fiables` es `false`, así que no se puede ordenar por media, y el brief no trae dato de probabilidad de gol. Con esa limitación, el único criterio disponible en bruto es el reparto de puntos por jornada: Ángel Pérez (MC) suma 12 puntos en sus 2 jornadas con nota, el registro más consistente de la plantilla entre los jugadores en estado "ok", con partido en casa ante Villarreal. Candidato a capitán, con la reserva de que la muestra son solo 2 jornadas.
- Nada más exige acción hoy en el resto de la plantilla.

## Ventana de mercado
Los 12 candidatos que tengo delante cierran todos en 16,3 horas (todos "asequible", sin descuento sobre su valor):
- Miguel Sierra (MC) — 4.125.000 € — 11 puntos en 2 jornadas
- Gerard Martín (DF) — 24.753.000 € — 10 puntos en su único partido
- Martín Satriano (DL) — 26.015.000 € — 9 puntos en 2 jornadas
- Jesús Vázquez (DF) — 2.663.000 € — 7 puntos en su único partido
- José Luis Gayà (DF) — 10.511.000 € — 6 puntos en su único partido
- Jonathan Asp Jensen (MC) — 5.924.000 € — 5 puntos en su único partido
- Chupete (DL) — 25.769.000 € — 2 puntos en su único partido
- Johnny Cardoso (MC) — 3.917.000 € — sin nota todavía
- Davinchi (DF) — 5.142.000 € — sin nota todavía
- Thiago Pitarch (MC) — 1.343.000 € — "injury", sin nota
- Unai Vencedor (MC) — 493.000 € — "other", sin nota
- Thomas Lemar (MC) — 329.000 € — "other", sin nota

## Nuestra plantilla
Cuatro jugadores en estado distinto de "ok" (de los 14 que trae el brief, no 15 según la validación de arriba):
- Augusto Batalla (PT) — "injury" — rival: FC Barcelona, fuera.
- Kike Salas (DF) — "red" — rival: Atlético de Madrid, en casa.
- Adrián Niño (DL) — "injury" — rival: Deportivo de A Coruña, en casa.
- Facundo Garcés (DF) — "other" — rival: Villarreal, en casa.

Exposición a cláusula: los 14 están sin blindar (`sin_blindar: 14`). No hay datos de cláusula hoy (`clausulas_resumen.con_dueno: 0`, `clausulas_top` vacío), así que no se puede afirmar qué rival podría rescindir a quién. Los más caros y sin blindar son Augusto Batalla (24.749.000 €) y Javi Guerra (24.744.000 €), ambos también bajan de valor hoy, pero sin dato de cláusula no hay forma de valorar riesgo real.

## La liga
Estamos en la posición 8537 de la tabla, con 144.035.000 € de valor de plantilla (`rank_valor: 83`) y 57 puntos. El líder, Ander, tiene 162 puntos y 374.208.000 € de valor de plantilla. No hay datos de cláusulas hoy (`con_dueno: 0`), así que no se puede decir qué rivales han blindado a quién.

## Calendario
Tres de los nuestros (Lucas Boyé, Ángel Pérez, Facundo Garcés) reciben en casa a Villarreal, el rival de mayor valor medio de plantilla entre los que enfrentamos esta jornada después del Barcelona (18.744.217 €). Dos más (Kike Salas, Lucien Agoumé) reciben al Atlético de Madrid (18.219.551 €). Augusto Batalla visita al FC Barcelona, el equipo de mayor valor medio de todo el calendario que tengo delante (27.337.142 €), aunque está de baja y no jugará.

## Qué vigilar
- Estado de Augusto Batalla: si pasa de "injury" a "ok" antes del partido ante el Barcelona, replantear si merece la pena alinearlo pese al rival; si sigue "injury", asumir la baja y no contar con él.
- Datos de cláusula: hoy `con_dueno` es 0 y no hay `clausulas_top`. En cuanto el brief vuelva a traer candidatos con dueño, revisar la exposición real de Batalla y Javi Guerra, los más caros y sin blindar de la plantilla.
- Recuento de plantilla: el brief señala 14 jugadores en vez de 15. Si el próximo brief sigue en 14, confirmar si es un hueco real de fichaje o un fallo de los datos.
