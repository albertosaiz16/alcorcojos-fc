"""Métricas derivadas. Todo determinista: mismos datos, mismo resultado."""
import pandas as pd

CLAUSE_FLOOR = 1_000_000


def variaciones(jugadores, n=15):
    """Mayores subidas y bajadas de valor del día."""
    df = jugadores[jugadores["valor_prev"].notna()].copy()
    cols = ["id", "nombre", "posicion", "valor", "delta_valor", "delta_pct",
            "dueno", "es_mio"]
    return {
        "suben": df.nlargest(n, "delta_valor")[cols].to_dict("records"),
        "bajan": df.nsmallest(n, "delta_valor")[cols].to_dict("records"),
        "resumen": {
            "suben": int((df["delta_valor"] > 0).sum()),
            "bajan": int((df["delta_valor"] < 0).sum()),
            "igual": int((df["delta_valor"] == 0).sum()),
        },
    }


def clausulas(jugadores, saldo, n=25):
    """Jugadores de rivales cuya cláusula podrías pagar.

    El ratio cláusula/valor es constante (1.5) salvo por el suelo de 1M,
    así que ordenar por sobrecoste identifica dónde el suelo te penaliza
    menos. La calidad del fichaje la aportará el modelo cuando exista.
    """
    df = jugadores[(~jugadores["libre"]) & (~jugadores["es_mio"])].copy()
    df["sobrecoste"] = df["clausula"] / df["valor"]
    df["asequible"] = df["clausula"] <= saldo
    df["media_por_millon"] = df["media"] / (df["clausula"] / 1_000_000)
    df = df.sort_values(["asequible", "media_por_millon"],
                        ascending=[False, False])
    cols = ["id", "nombre", "posicion", "valor", "clausula", "sobrecoste",
            "asequible", "media", "puntos", "media_por_millon", "dueno",
            "estado", "escudo"]
    return {
        "candidatos": df.head(n)[cols].to_dict("records"),
        "resumen": {
            "con_dueno": int(len(df)),
            "asequibles": int(df["asequible"].sum()),
            "clausula_mas_barata": int(df["clausula"].min()) if len(df) else 0,
        },
    }


def plantilla(jugadores):
    """Estado de tus jugadores."""
    df = jugadores[jugadores["es_mio"]].sort_values("valor", ascending=False)
    cols = ["id", "nombre", "posicion", "valor", "delta_valor", "delta_pct",
            "clausula", "puntos", "media", "estado", "rival", "local",
            "escudo"]
    return {
        "jugadores": df[cols].to_dict("records"),
        "resumen": {
            "n": int(len(df)),
            "valor_total": int(df["valor"].sum()),
            "delta_total": int(df["delta_valor"].sum()),
            "riesgo_clausula": int(df["clausula"].sum()),
            "tocados": int((df["estado"] != "ok").sum()),
        },
    }


def mercado(jugadores, mercado_df, saldo):
    """Pujas abiertas, cruzadas con los datos del jugador."""
    if mercado_df.empty:
        return {"pujas": [], "resumen": {}}
    df = mercado_df.merge(jugadores, on="id", how="left")
    df["descuento"] = 1 - df["precio_salida"] / df["valor"]
    df["asequible"] = df["precio_salida"] <= saldo
    df = df.sort_values("descuento", ascending=False)
    cols = ["id", "nombre", "posicion", "valor", "precio_salida", "descuento",
            "asequible", "delta_valor", "media", "puntos", "estado", "libre",
            "cierra_ts"]
    return {
        "pujas": df[cols].to_dict("records"),
        "resumen": {
            "n": int(len(df)),
            "libres": int(df["libre"].sum()),
            "asequibles": int(df["asequible"].sum()),
        },
    }


def calendario(jugadores):
    """Próximo rival por equipo, para dificultad de calendario."""
    df = (jugadores.dropna(subset=["rival"])
          .groupby("id_equipo")
          .agg(rival=("rival", "first"),
               local=("local", "first"),
               jugadores=("id", "count"),
               valor_medio=("valor", "mean"))
          .reset_index())
    return df.to_dict("records")


def alertas(jugadores):
    """Jugadores tuyos con problema de estado."""
    df = jugadores[jugadores["es_mio"] & (jugadores["estado"] != "ok")]
    return df[["id", "nombre", "posicion", "estado", "valor"]].to_dict(
        "records")


def compute_all(jugadores, mercado_df, standings, saldo, meta):
    """Ejecuta todas las métricas y devuelve el payload del dashboard."""
    return {
        "meta": {**meta, "saldo": saldo},
        "variaciones": variaciones(jugadores),
        "clausulas": clausulas(jugadores, saldo),
        "plantilla": plantilla(jugadores),
        "mercado": mercado(jugadores, mercado_df, saldo),
        "calendario": calendario(jugadores),
        "alertas": alertas(jugadores),
        "liga": standings.to_dict("records"),
        "universo": {
            "total": int(len(jugadores)),
            "libres": int(jugadores["libre"].sum()),
            "lesionados": int((jugadores["estado"] == "injury").sum()),
            "dudas": int((jugadores["estado"] == "doubt").sum()),
        },
    }
