"""Etapa determinista: captura -> metricas -> data.json + brief.json."""
import json
import sys
from pathlib import Path

from . import analysis, metrics, parse

RAW = Path("data/raw")


def latest_capture():
    files = sorted(RAW.glob("*.json.gz"))
    if not files:
        sys.exit("No hay capturas en data/raw/")
    return files[-1]


def main():
    captura = latest_capture()
    print(f"Procesando {captura.name}")

    meta, jugadores, mercado_df, standings = parse.parse_capture(captura)
    raw = parse.load_raw(captura)
    saldo = (raw.get("balance") or {}).get("current", 0)

    payload = metrics.compute_all(
        jugadores, mercado_df, standings, saldo, meta)

    hist = parse.build_history(RAW, "data/history.parquet")
    payload["meta"]["dias_historico"] = int(hist["market_date"].nunique())

    Path("docs").mkdir(exist_ok=True)
    Path("docs/data.json").write_text(
        json.dumps(payload, ensure_ascii=False, default=str),
        encoding="utf-8")
    analysis.write_brief(payload)

    print(f"  {len(jugadores)} jugadores, {len(mercado_df)} en mercado, "
          f"{payload['meta']['dias_historico']} dias de historico")
    print("  escritos docs/data.json y data/brief.json")


if __name__ == "__main__":
    main()
