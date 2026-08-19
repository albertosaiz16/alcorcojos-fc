"""Convierte una captura cruda en una tabla normalizada de jugadores."""
import gzip
import json
import re
from pathlib import Path

import pandas as pd

POSITIONS = {1: "PT", 2: "DF", 3: "MC", 4: "DL"}


def load_raw(path):
    """Lee una captura .json.gz y devuelve el dict crudo."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def parse_players(raw):
    """Extrae los jugadores de todos los chunks paginados."""
    players = {}
    for chunk in raw["chunks"]:
        payload = json.loads(chunk["html"])
        for p in payload["data"]["players"]:
            players[p["id"]] = p

    rows = []
    for p in players.values():
        match = p.get("match_info") or {}
        streak = [s for s in (p.get("streak") or []) if s != "-"]
        rows.append({
            "id": p["id"],
            "nombre": p["name"],
            "posicion": POSITIONS.get(p["position"], "?"),
            "id_equipo": p["id_team"],
            "valor": p["value"],
            "valor_prev": p["prev_value"],
            "clausula": p["clause"],
            "puntos": p["points"],
            "media": p["avg"],
            "jornadas_con_nota": len(streak),
            "estado": p["status"] or "ok",
            "id_dueno": p["id_uc"],
            "dueno": p["uc_name"],
            "es_mio": bool(p["is_mine"]),
            "escudo": bool(p["shield"]),
            "rank_clausula": p["clausesRank"],
            "rival": match.get("rival_team_id"),
            "local": match.get("is_home"),
        })

    df = pd.DataFrame(rows)
    df["libre"] = df["id_dueno"].isna() | (df["id_dueno"] == 0)

    # Un valor previo de 0 significa alta nueva en el universo, no una
    # subida del 100%. Sin este filtro, delta_valor sale igual al valor
    # entero del jugador y encabeza el ranking de mayores subidas.
    tiene_prev = df["valor_prev"].notna() & (df["valor_prev"] > 0)
    df["es_alta_nueva"] = ~tiene_prev
    df["delta_valor"] = (df["valor"] - df["valor_prev"]).where(tiene_prev, 0)
    df["delta_pct"] = (df["delta_valor"] / df["valor_prev"]).where(tiene_prev)
    return df


_LI = re.compile(r"<li\s+data-position=")


def parse_market(raw):
    """Extrae las pujas abiertas del HTML de /market.

    Se parsea elemento a elemento en vez de con un patrón único que asume
    el orden de los atributos. El patrón anterior exigía la secuencia
    position -> price -> owner -> ends -> id_player: un cambio de orden en
    la plantilla de Marca lo dejaba en cero pujas sin avisar, y con `re.S`
    un fallo parcial podía emparejar atributos de elementos distintos.
    """
    html = raw["pages"]["mercado"]
    trozos = _LI.split(html)[1:]
    rows = []
    for t in trozos:
        t = t[:4000]
        price = re.search(r'data-price="(\d+)"', t)
        ends = re.search(r'data-ends="(\d+)"', t)
        owner = re.search(r'data-owner="(\d*)"', t)
        pid = (re.search(r'data-id_player="(\d+)"', t)
               or re.search(r'href="players/(\d+)/', t))
        if not (price and pid):
            continue
        rows.append({
            "id": int(pid.group(1)),
            "precio_salida": int(price.group(1)),
            "id_vendedor": (int(owner.group(1))
                            if owner and owner.group(1) else None),
            "cierra_ts": int(ends.group(1)) if ends else None,
        })
    if not rows:
        return pd.DataFrame(
            columns=["id", "precio_salida", "id_vendedor", "cierra_ts"])
    return pd.DataFrame(rows).drop_duplicates("id")


def parse_standings(raw):
    """Extrae la clasificación de la liga.

    El HTML trae dos listados: la tabla completa y un widget reducido con
    solo tres rivales y tú. Las filas del widget no llevan ni jugadores ni
    valor, y la tuya lleva la posición como "?" en vez de un número.

    Dos arreglos respecto a la versión anterior:
      - El nombre se leía con `class="name\\s*">`, que no casa con
        `class="name myself"`. Tu propia fila salía siempre como "?".
      - La deduplicación se fiaba del orden del HTML. Ahora se prefiere
        explícitamente la fila que trae datos completos.
    """
    html = raw["pages"]["clasificacion"]
    rows = []
    for block in html.split('class="btn btn-sw-link user"')[1:]:
        uid = re.search(r'href="users/(\d+)/', block)
        if not uid:
            continue
        pos = re.search(r'class="position">\s*(\d+)', block)
        name = re.search(r'class="name[^"]*">\s*([^<]+?)\s*<', block)
        squad = re.search(r'(\d+)\s*jugadores', block)
        valor = re.search(r'€\s*([\d.]+)', block)
        pts = re.search(r'class="points">\s*(-?\d+)', block)
        rows.append({
            "id_usuario": int(uid.group(1)),
            "posicion": int(pos.group(1)) if pos else None,
            "nombre": name.group(1) if name else None,
            "n_jugadores": int(squad.group(1)) if squad else None,
            "valor_plantilla": (int(valor.group(1).replace(".", ""))
                                if valor else None),
            "puntos": int(pts.group(1)) if pts else None,
            "_completa": bool(pos and squad and valor),
        })
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = (df.sort_values("_completa", ascending=False)
            .drop_duplicates("id_usuario", keep="first")
            .drop(columns="_completa"))
    df["nombre"] = df["nombre"].fillna("?")

    # Ranking por valor de plantilla: no coincide con `posicion`, que es la
    # clasificacion por puntos. Confundir las dos lleva a leer mal la tabla.
    df["rank_valor"] = df["valor_plantilla"].rank(
        ascending=False, method="min")
    return df.sort_values("posicion", na_position="last").reset_index(drop=True)


def dias_historico(raw_dir):
    """Número de capturas diarias distintas guardadas hasta hoy."""
    return len({f.name.split(".")[0]
                for f in Path(raw_dir).glob("*.json.gz")})


def parse_capture(path, raw_dir=None):
    """Parsea una captura completa. Devuelve (meta, jugadores, mercado, liga)."""
    raw = load_raw(path)
    ctx = raw.get("context") or {}
    feats = raw.get("features") or {}
    meta = {
        "market_date": raw["market_date"],
        "captured_at": raw["ts"],
        "id_liga": (ctx.get("community") or {}).get("id"),
        # Ojo: cfg.season es un campo muerto que sigue diciendo "22/23".
        # El bueno es context.season.name.
        "temporada": (ctx.get("season") or {}).get("name"),
        "capitan_activo": bool(feats.get("captain")
                               or feats.get("league_captain")),
        "mercado_bloqueado": bool(feats.get("market_lock")),
        "n_jugadores_captura": raw.get("n_jugadores"),
        "dias_historico": (dias_historico(raw_dir) if raw_dir
                           else dias_historico(Path(path).parent)),
    }
    jugadores = parse_players(raw)
    jugadores["market_date"] = meta["market_date"]

    mercado = parse_market(raw)
    jugadores["en_mercado"] = jugadores["id"].isin(mercado["id"])
    return meta, jugadores, mercado, parse_standings(raw)


def build_history(raw_dir, out_path, estricto=False):
    """Acumula todas las capturas en un histórico deduplicado por día.

    Con `estricto=True` propaga la excepción en vez de imprimir un aviso.
    Un fichero ilegible no es ruido: es un día de histórico perdido, y el
    histórico de valores no se puede reconstruir a posteriori.
    """
    frames, fallos = [], []
    for f in sorted(Path(raw_dir).glob("*.json.gz")):
        try:
            _, jugadores, _, _ = parse_capture(f, raw_dir=raw_dir)
            frames.append(jugadores)
        except Exception as exc:
            if estricto:
                raise
            fallos.append((f.name, str(exc)))
            print(f"  aviso: {f.name} ilegible ({exc})")
    if fallos:
        print(f"  {len(fallos)} capturas ilegibles de "
              f"{len(frames) + len(fallos)}")
    if not frames:
        return pd.DataFrame()
    hist = pd.concat(frames, ignore_index=True)
    hist = hist.drop_duplicates(["market_date", "id"], keep="last")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    hist.to_parquet(out_path, index=False)
    return hist