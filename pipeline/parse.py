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
            "en_mercado": p["id_market"] is not None,
            "escudo": bool(p["shield"]),
            "rank_clausula": p["clausesRank"],
            "rival": match.get("rival_team_id"),
            "local": match.get("is_home"),
        })

    df = pd.DataFrame(rows)
    df["libre"] = df["id_dueno"].isna() | (df["id_dueno"] == 0)
    df["delta_valor"] = df["valor"] - df["valor_prev"].fillna(df["valor"])
    df["delta_pct"] = df["delta_valor"] / df["valor_prev"].where(
        df["valor_prev"] > 0)
    return df


def parse_market(raw):
    """Extrae las pujas abiertas del HTML de /market."""
    html = raw["pages"]["mercado"]
    pattern = re.compile(
        r'data-position="(?P<pos>\d+)"\s+data-price="(?P<price>\d+)"'
        r'\s+data-owner="(?P<owner>\d*)"[^>]*data-ends="(?P<ends>\d+)"'
        r'.*?data-id_player="(?P<pid>\d+)"',
        re.S)
    rows = [{
        "id": int(m["pid"]),
        "precio_salida": int(m["price"]),
        "id_vendedor": int(m["owner"]) if m["owner"] else None,
        "cierra_ts": int(m["ends"]),
    } for m in pattern.finditer(html)]
    return pd.DataFrame(rows).drop_duplicates("id")


def parse_standings(raw):
    """Extrae la clasificación de la liga."""
    html = raw["pages"]["clasificacion"]
    rows = []
    for block in html.split('class="btn btn-sw-link user"')[1:]:
        uid = re.search(r'href="users/(\d+)/', block)
        pos = re.search(r'class="position">\s*(\d+)', block)
        name = re.search(r'class="name\s*">\s*([^<]+?)\s*<', block)
        squad = re.search(r'(\d+)\s*jugadores.*?([\d.]{7,})', block, re.S)
        pts = re.search(r'class="points">\s*(-?\d+)', block)
        if not (uid and pos):
            continue
        rows.append({
            "id_usuario": int(uid.group(1)),
            "posicion": int(pos.group(1)),
            "nombre": name.group(1) if name else "?",
            "n_jugadores": int(squad.group(1)) if squad else None,
            "valor_plantilla": (
                int(squad.group(2).replace(".", "")) if squad else None),
            "puntos": int(pts.group(1)) if pts else None,
        })
    return pd.DataFrame(rows).drop_duplicates("id_usuario")


def parse_capture(path):
    """Parsea una captura completa. Devuelve (meta, jugadores, mercado, liga)."""
    raw = load_raw(path)
    ctx = raw.get("context") or {}
    meta = {
        "market_date": raw["market_date"],
        "captured_at": raw["ts"],
        "id_liga": (ctx.get("community") or {}).get("id"),
        "temporada": (ctx.get("season") or {}).get("name"),
    }
    jugadores = parse_players(raw)
    jugadores["market_date"] = meta["market_date"]
    return meta, jugadores, parse_market(raw), parse_standings(raw)


def build_history(raw_dir, out_path):
    """Acumula todas las capturas en un histórico deduplicado por día."""
    frames = []
    for f in sorted(Path(raw_dir).glob("*.json.gz")):
        try:
            _, jugadores, _, _ = parse_capture(f)
            frames.append(jugadores)
        except Exception as exc:
            print(f"  aviso: {f.name} ilegible ({exc})")
    if not frames:
        return pd.DataFrame()
    hist = pd.concat(frames, ignore_index=True)
    hist = hist.drop_duplicates(["market_date", "id"], keep="last")
    hist.to_parquet(out_path, index=False)
    return hist
