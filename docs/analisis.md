## Titular
El mercado cierra en unas 16,1 horas para los 40 candidatos que tengo delante; el mejor descuento entre los que están `ok` es Hamza Abdelkarim (DL, -9,04%, 5.261.000 € por un jugador de 5.784.000 €).

## Decisión
Capitán: Alemão (DL). Es el único delantero sano de la plantilla (Kike García está `injury`); hizo 5 puntos en su único partido y vuelve a jugar en casa ante Alavés. No hay dato de probabilidad de gol en el brief, así que la posición es el mejor proxy disponible.

No fichar hoy pese al cierre de mercado: entre los jugadores `ok` el mayor descuento visible es del 9,04% (Hamza Abdelkarim) y solo hay 1 jornada de datos — no justifica gastar de los 94.587.000 € de saldo. El descuento más alto de la lista (Marash Kumbulla, -26,67%) es sobre un jugador `injury`, no una ganga.

No rescindir cláusulas hoy: `clausulas_top` está ordenada por coste, no por calidad ("clausula (media no fiable con 1 jornadas)"), y las medias no son fiables todavía. No hay ningún candidato ahí que destaque por rendimiento.

No alinear a Kike García (injury) ante el Real Madrid mientras mantenga ese estado. Vigilar a Luis Rioja (doubt) antes de recibir al Celta de Vigo: si sigue en duda cerca del partido, no capitanearlo ni forzar su titularidad.

## Ventana de mercado
Los 40 candidatos del mercado cierran en ~16,1 horas (veo 12 de esos 40):
- Marash Kumbulla (DF) — descuento 26,67%, estado `injury`, no libre.
- Marcão (DF) — descuento 10,84%, estado `other`, no libre.
- Hamza Abdelkarim (DL) — descuento 9,04%, estado `ok`, no libre.
- Asier Villalibre (DL) — descuento 6,31%, estado `ok`, no libre.
- Eduardo Camavinga (MC) — descuento 1,77%, estado `ok`, no libre.
- Sin descuento (precio = valor): Christantus Uche (DL, injury, libre), Gavi (MC, ok, libre), Rubén García (MC, ok, libre), Gabriel Moscardo (MC, ok, libre), Rodrigo Mendoza (MC, ok, libre), Carlos Martín (MC, ok, libre), Yvan Neyou (MC, other, no libre).

## Nuestra plantilla
Estados distintos de `ok` (4 de 15):
- Luis Rioja (MC) — `doubt`. Rival: Celta de Vigo, en casa. Valor 13.620.000 €, cláusula 20.430.000 €.
- Kike García (DL) — `injury`. Rival: Real Madrid, en casa. Valor 5.882.000 €, cláusula 8.823.000 €.
- Martín Krug (DF) — `other`. Rival: Osasuna, fuera. Valor 477.000 €, cláusula 1.000.000 €.
- Alejandro Iturbe (PT) — `other`. Rival: FC Barcelona, en casa. Valor 347.000 €, cláusula 1.000.000 €.

Exposición a cláusula: los 15 están sin blindar (`sin_blindar: 15`). El más expuesto por valor es Augusto Batalla, según `mas_expuesto` (cláusula 40.479.000 €, sobrecoste 1,5×, el mínimo posible).

## La liga
Posición 10ª de 10, pero todos los mánagers tienen 0 puntos: la jornada no ha consolidado y esa posición es provisional. Por valor de plantilla vamos 6º de 10 (`rank_valor`), con 103.762.000 €. El líder en valor es Gonzalo (`rank_valor` 1), con 187.291.000 €.

De los jugadores con dueño, 25 de 138 están blindados, pero el brief no me dice cuáles en los datos que tengo delante (los de `clausulas_top` están todos sin blindar). Dos jugadores en manos de rivales suben por encima del umbral: Orri Óskarsson (DL, dueño Mateo) +548.000 € (+2,89%) y Lorenzo Amatucci (MC, dueño Martín) +533.000 € (+3,17%).

## Calendario
Varios jugadores nuestros reciben a rivales fuertes esta jornada: Lucas Cepeda y Alejandro Iturbe (este último `other`) juegan en casa ante el FC Barcelona (valor medio de su plantilla 28.257.153 €); Kike García (`injury`) recibe al Real Madrid, el equipo con mayor valor medio de plantilla del calendario que tengo delante (29.573.230 €). Álex Pastor visita al Atlético de Madrid (valor medio 18.654.964 €).

## Qué vigilar
- Estado de Luis Rioja antes del partido ante el Celta de Vigo: si pasa a `ok`, se puede alinear y capitanear con normalidad; si pasa a `injury` o sigue `doubt` cerca del partido, dejarlo fuera.
- Estado de Kike García antes de recibir al Real Madrid: si pasa a `ok`, replantear su titularidad; mientras siga `injury`, descartarlo.
- `medias_fiables`: en cuanto pase a `true` con más jornadas, se podrá usar `media`/`media_por_millon` para elegir capitán y objetivos de fichaje con criterio de rendimiento, no solo por posición o coste.

Nota: no hay dato de probabilidad de gol/expected goals en el brief, así que la elección de capitán se apoya en posición (DL) como único proxy disponible. Tampoco hay precio de venta explícito para valorar si conviene transferir a Krug o Iturbe (estado `other`). Sobre los 25 blindados de la liga, el brief solo da el agregado, no la lista de jugadores.
