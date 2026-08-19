"""Métricas derivadas. Todo determinista: mismos datos, mismo resultado.

Columnas que espera de `jugadores`:
    id, nombre, posicion, valor, valor_prev, delta_valor, delta_pct,
    clausula, media, puntos, dueno, es_mio, libre, estado, escudo,
    id_equipo, rival, local, jornadas_con_nota, es_alta_nueva

`jornadas_con_nota` es nueva y la tiene que producir el parser, contando
las entradas de `streak` distintas de "-". Sin ella todo el módulo asume
una sola jornada y se niega a ordenar por medias, que es el
comportamiento seguro pero no el útil.
"""
import json
import math
from pathlib import Path

import pandas as pd

CLAUSE_FLOOR = 1_000_000
CLAUSE_BASE = 1.5          # multiplicador mínimo; el dueño puede subirlo
MIN_JORNADAS_PARA_MEDIA = 3
HORIZONTE_CIERRE_H = 48

# Campos que legitimamente vienen vacios: jugador sin dueno, sin rank de
# clausula, sin partido asignado. Si aparece un nulo fuera de esta lista es
# que una operacion numerica ha fallado, y eso si hay que reportarlo.
NULABLES_ESPERADOS = {
    "dueno", "id_dueno", "rank_clausula", "rival", "rival_nombre", "local",
    "delta_pct", "valor_prev", "media_por_millon", "cierra_ts",
    "horas_para_cierre", "posicion", "n_jugadores", "valor_plantilla",
    "puntos", "rank_valor", "delta_pct_total", "mas_expuesto",
}


def cargar_equipos(path="data/equipos.json"):
    """Diccionario id_equipo -> nombre. Devuelve {} si no existe todavía."""
    p = Path(path)
    if not p.exists():
        return {}
    crudo = json.loads(p.read_text(encoding="utf-8"))
    return {int(k): v for k, v in crudo.items()
            if k.isdigit() and v}


def _limpiar(obj, incidencias=None, clave=None):
    """Convierte NaN/Inf en None, pero deja constancia.

    La versión anterior silenciaba divisiones por cero: un alta nueva con
    valor_prev == 0 producía delta_pct = inf, que salía del pipeline como
    un `null` de aspecto inocente. Ahora se anota en `incidencias` para que
    compute_all lo pueda reportar.
    """
    if isinstance(obj, dict):
        return {k: _limpiar(v, incidencias, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_limpiar(v, incidencias, clave) for v in obj]
    if isinstance(obj, float) and not math.isfinite(obj):
        if incidencias is not None and clave not in NULABLES_ESPERADOS:
            incidencias.append(clave or "?")
        return None
    return obj


def _jornadas(jugadores):
    """Jornadas disputadas en la competición, según los datos disponibles."""
    if "jornadas_con_nota" not in jugadores.columns:
        return 0
    s = jugadores["jornadas_con_nota"].dropna()
    return int(s.max()) if len(s) else 0


def variaciones(jugadores, n=15):
    """Mayores subidas y bajadas de valor del día.

    Los jugadores sin valor previo (altas nuevas del universo) van a su
    propia lista. Antes entraban en `suben` con delta_valor == valor, lo
    que ponía un fantasma de 44 millones en cabeza del ranking.
    """
    cols = ["id", "nombre", "posicion", "valor", "delta_valor", "delta_pct",
            "dueno", "es_mio"]
    if "es_alta_nueva" in jugadores.columns:
        tiene_prev = ~jugadores["es_alta_nueva"].astype(bool)
    else:
        tiene_prev = (jugadores["valor_prev"].notna()
                      & (jugadores["valor_prev"] > 0))
    df = jugadores[tiene_prev].copy()
    altas = jugadores[~tiene_prev].copy()

    return {
        "suben": df.nlargest(n, "delta_valor")[cols].to_dict("records"),
        "bajan": df.nsmallest(n, "delta_valor")[cols].to_dict("records"),
        "altas_nuevas": altas[["id", "nombre", "posicion", "valor"]]
                        .to_dict("records"),
        "resumen": {
            "suben": int((df["delta_valor"] > 0).sum()),
            "bajan": int((df["delta_valor"] < 0).sum()),
            "igual": int((df["delta_valor"] == 0).sum()),
            "sin_valor_previo": int(len(altas)),
            "comparables": int(len(df)),
        },
    }


def clausulas(jugadores, saldo, n=25):
    """Jugadores de rivales cuya cláusula podrías pagar.

    El multiplicador cláusula/valor NO es constante. El mínimo es 1.5 (con
    suelo de 1.000.000 EUR), pero el propietario puede subirlo pagando. Un
    `sobrecoste` alto no es una penalización del suelo: es un rival que ha
    invertido dinero en blindar a ese jugador, y por tanto una señal de
    intención, no una oportunidad.

    El orden depende de cuántas jornadas se hayan disputado. Con menos de
    tres, `media` es una o dos observaciones y ordenar por
    `media_por_millon` produce un ranking aleatorio con dos decimales; en
    ese caso se ordena por coste ascendente, que al menos es un hecho.
    """
    df = jugadores[(~jugadores["libre"]) & (~jugadores["es_mio"])].copy()
    if df.empty:
        return {"candidatos": [], "resumen": {
            "con_dueno": 0, "asequibles": 0, "clausula_mas_barata": 0,
            "candidatos_de": 0, "ordenado_por": "n/a"}}

    suelo = df["valor"].clip(lower=CLAUSE_FLOOR / CLAUSE_BASE) * CLAUSE_BASE
    df["sobrecoste"] = df["clausula"] / df["valor"]
    df["blindado"] = df["clausula"] > suelo * 1.01     # margen de redondeo
    df["asequible"] = df["clausula"] <= saldo
    df["media_por_millon"] = df["media"] / (df["clausula"] / 1_000_000)

    jornadas = _jornadas(jugadores)
    if jornadas >= MIN_JORNADAS_PARA_MEDIA:
        orden, asc = ["asequible", "media_por_millon"], [False, False]
        criterio = "media_por_millon"
    else:
        orden, asc = ["asequible", "clausula"], [False, True]
        criterio = "clausula (media no fiable con %d jornadas)" % jornadas
    df = df.sort_values(orden, ascending=asc)

    cols = ["id", "nombre", "posicion", "valor", "clausula", "sobrecoste",
            "blindado", "asequible", "media", "puntos", "jornadas_con_nota",
            "media_por_millon", "dueno", "estado", "escudo"]
    cols = [c for c in cols if c in df.columns]
    return {
        "candidatos": df.head(n)[cols].to_dict("records"),
        "resumen": {
            "con_dueno": int(len(df)),
            "asequibles": int(df["asequible"].sum()),
            "blindados": int(df["blindado"].sum()),
            "clausula_mas_barata": int(df["clausula"].min()),
            "candidatos_de": int(len(df)),
            "ordenado_por": criterio,
        },
    }


def plantilla(jugadores, equipos=None):
    """Estado de tus jugadores, con su exposición a cláusula.

    Añade `sobrecoste` y `blindado`: sin ellos era imposible ver que toda
    la plantilla estaba al mínimo de 1.5x, que es la información
    estratégica más relevante que hay aquí.
    """
    equipos = equipos or {}
    df = jugadores[jugadores["es_mio"]].sort_values("valor", ascending=False)
    df = df.copy()
    suelo = df["valor"].clip(lower=CLAUSE_FLOOR / CLAUSE_BASE) * CLAUSE_BASE
    df["sobrecoste"] = df["clausula"] / df["valor"]
    df["blindado"] = df["clausula"] > suelo * 1.01
    df["rival_nombre"] = df["rival"].map(
        lambda r: equipos.get(int(r)) if pd.notna(r) else None)

    cols = ["id", "nombre", "posicion", "valor", "delta_valor", "delta_pct",
            "clausula", "sobrecoste", "blindado", "puntos", "media",
            "jornadas_con_nota", "estado", "rival", "rival_nombre", "local",
            "escudo"]
    cols = [c for c in cols if c in df.columns]
    return {
        "jugadores": df[cols].to_dict("records"),
        "resumen": {
            "n": int(len(df)),
            "valor_total": int(df["valor"].sum()),
            "delta_total": int(df["delta_valor"].sum()),
            "delta_pct_total": (float(df["delta_valor"].sum()
                                      / df["valor_prev"].sum())
                                if df["valor_prev"].sum() else None),
            "tocados": int((df["estado"] != "ok").sum()),
            "sin_blindar": int((~df["blindado"]).sum()),
            # Suma de clausulas: solo util como referencia, nadie compra una
            # plantilla entera. La exposicion real es por jugador.
            "suma_clausulas": int(df["clausula"].sum()),
            "mas_expuesto": (df[~df["blindado"]]
                             .nlargest(1, "valor")["nombre"].tolist() or [None])[0],
        },
    }


def mercado(jugadores, mercado_df, saldo, ahora_ts):
    """Pujas abiertas, ordenadas por lo que caduca antes.

    El orden anterior era por descuento, y build_brief cortaba a 8 de 43:
    una puja que cerraba en cuatro horas podía no llegar nunca al analista
    si no era de las más rebajadas. Aquí manda el reloj.
    """
    vacio = {"pujas": [], "resumen": {"n": 0, "libres": 0, "asequibles": 0,
                                      "cierran_pronto": 0, "ya_cerradas": 0, "sin_cruce": 0}}
    if mercado_df.empty:
        return vacio

    df = mercado_df.merge(jugadores, on="id", how="left")

    # Un jugador del mercado que no cruza con el universo es sintoma de que
    # algo lo filtro aguas arriba. Antes salia con todos los campos a null.
    sin_cruce = int(df["nombre"].isna().sum())
    df = df[df["nombre"].notna()].copy()

    df["descuento"] = 1 - df["precio_salida"] / df["valor"]
    df["asequible"] = df["precio_salida"] <= saldo
    df["horas_para_cierre"] = (df["cierra_ts"] - ahora_ts) / 3600.0
    df["cerrada"] = df["horas_para_cierre"] < 0
    df["cierra_pronto"] = (~df["cerrada"]) & (
        df["horas_para_cierre"] <= HORIZONTE_CIERRE_H)

    # Primero lo que caduca dentro del horizonte, por urgencia; despues el
    # resto, por descuento.
    df = df.sort_values(
        ["cerrada", "cierra_pronto", "horas_para_cierre", "descuento"],
        ascending=[True, False, True, False])

    cols = ["id", "nombre", "posicion", "valor", "precio_salida", "descuento",
            "asequible", "delta_valor", "media", "puntos", "jornadas_con_nota",
            "estado", "libre", "cierra_ts", "horas_para_cierre",
            "cierra_pronto", "cerrada"]
    cols = [c for c in cols if c in df.columns]
    return {
        "pujas": df[cols].to_dict("records"),
        "resumen": {
            "n": int(len(df)),
            "libres": int(df["libre"].sum()),
            "asequibles": int(df["asequible"].sum()),
            "cierran_pronto": int(df["cierra_pronto"].sum()),
            "ya_cerradas": int(df["cerrada"].sum()),
            "sin_cruce": sin_cruce,
        },
    }


def calendario(jugadores, equipos=None):
    """Próximo rival por equipo. Se calculaba y no llegaba al brief."""
    equipos = equipos or {}
    if "rival" not in jugadores.columns:
        return []
    df = (jugadores.dropna(subset=["rival"])
          .groupby("id_equipo")
          .agg(rival=("rival", "first"),
               local=("local", "first"),
               jugadores=("id", "count"),
               valor_medio=("valor", "mean"))
          .reset_index())
    df["equipo_nombre"] = df["id_equipo"].map(lambda t: equipos.get(int(t)))
    df["rival_nombre"] = df["rival"].map(lambda r: equipos.get(int(r)))
    return df.to_dict("records")


def alertas(jugadores, equipos=None):
    """Jugadores tuyos con problema de estado, con su próximo partido."""
    equipos = equipos or {}
    df = jugadores[jugadores["es_mio"] & (jugadores["estado"] != "ok")].copy()
    if df.empty:
        return []
    df["rival_nombre"] = df["rival"].map(
        lambda r: equipos.get(int(r)) if pd.notna(r) else None)
    cols = ["id", "nombre", "posicion", "estado", "valor", "clausula",
            "rival", "rival_nombre", "local"]
    cols = [c for c in cols if c in df.columns]
    return df[cols].to_dict("records")


def validar(jugadores, payload, esperado_n=None):
    """Aserciones baratas. Devuelve una lista de problemas, vacía si todo ok.

    Se ejecutan aquí y no en tests porque los datos cambian cada día: lo
    que hay que vigilar no es que el código funcione, sino que el mundo
    siga pareciéndose a lo que el código asume.
    """
    p = []
    total = payload["universo"]["total"]
    if esperado_n and total < esperado_n:
        p.append(f"universo cayo a {total} (esperados >= {esperado_n}); "
                 "revisa los filtros de la captura")
    n_plantilla = payload["plantilla"]["resumen"]["n"]
    if n_plantilla != 15:
        p.append(f"la plantilla tiene {n_plantilla} jugadores, no 15")
    v = payload["variaciones"]["resumen"]
    if v["comparables"] + v["sin_valor_previo"] != total:
        p.append("las variaciones no suman el universo")
    if payload["mercado"]["resumen"].get("sin_cruce"):
        p.append(f"{payload['mercado']['resumen']['sin_cruce']} pujas sin "
                 "cruce con el universo")
    if not payload["meta"].get("equipos_resueltos"):
        p.append("data/equipos.json vacio: los rivales van como id numerico")
    if "jornadas_con_nota" not in jugadores.columns:
        p.append("falta la columna jornadas_con_nota; las medias no son fiables")
    ids_sin_nombre = sorted(
        set(jugadores["id_equipo"].dropna().astype(int))
        - set(payload["meta"].get("equipos_conocidos", [])))
    if payload["meta"].get("equipos_resueltos") and ids_sin_nombre:
        p.append(f"ids de equipo sin nombre en equipos.json: {ids_sin_nombre}")
    return p


def _ts_captura(meta):
    """Instante de la captura, en segundos epoch. Es el reloj del brief:
    usar la hora de ejecucion haria que un reprocesado antiguo declarase
    cerradas pujas que estaban abiertas cuando se capturaron."""
    return pd.Timestamp(meta["captured_at"]).timestamp()


def compute_all(jugadores, mercado_df, standings, saldo, meta,
                equipos=None, esperado_n=500):
    """Ejecuta todas las métricas y devuelve el payload del dashboard."""
    equipos = equipos if equipos is not None else cargar_equipos()
    incidencias = []
    jornadas = _jornadas(jugadores)

    payload = {
        "meta": {
            **meta,
            "saldo": saldo,
            "jornadas_disputadas": jornadas,
            "medias_fiables": jornadas >= MIN_JORNADAS_PARA_MEDIA,
            "equipos_resueltos": bool(equipos),
            "equipos_conocidos": sorted(equipos),
        },
        "variaciones": variaciones(jugadores),
        "clausulas": clausulas(jugadores, saldo),
        "plantilla": plantilla(jugadores, equipos),
        "mercado": mercado(jugadores, mercado_df, saldo,
                           _ts_captura(meta)),
        "calendario": calendario(jugadores, equipos),
        "alertas": alertas(jugadores, equipos),
        "liga": standings.to_dict("records"),
        "universo": {
            "total": int(len(jugadores)),
            "libres": int(jugadores["libre"].sum()),
            "lesionados": int((jugadores["estado"] == "injury").sum()),
            "dudas": int((jugadores["estado"] == "doubt").sum()),
            "otros": int((jugadores["estado"] == "other").sum()),
        },
    }
    payload = _limpiar(payload, incidencias)
    payload["validaciones"] = validar(jugadores, payload, esperado_n)
    if incidencias:
        cuenta = {c: incidencias.count(c) for c in set(incidencias)}
        payload["validaciones"].append(
            "valores no finitos en campos que no deberian estarlo: "
            + ", ".join(f"{k} (x{v})" for k, v in sorted(cuenta.items())))
    return payload