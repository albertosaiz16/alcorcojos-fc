"""Prepara el brief que leerá Claude Code.

Este módulo NO llama a ninguna API. Solo reduce el payload completo a los
hechos relevantes del día y los deja en disco. El Action de Claude Code lee
ese fichero y escribe docs/analisis.md.

La separación es deliberada: el brief es determinista y versionado, así que
siempre puedes comprobar sobre qué cifras exactas se escribió cada análisis.
"""
import json
import re
from pathlib import Path

TOP = 8


def build_brief(payload):
    """Reduce el payload a lo esencial. Lo estable se descarta."""
    return {
        "fecha": payload["meta"]["market_date"],
        "temporada": payload["meta"]["temporada"],
        "dias_historico": payload["meta"].get("dias_historico"),
        "saldo": payload["meta"]["saldo"],
        "universo": payload["universo"],
        "variaciones_resumen": payload["variaciones"]["resumen"],
        "mayores_subidas": payload["variaciones"]["suben"][:TOP],
        "mayores_bajadas": payload["variaciones"]["bajan"][:TOP],
        "clausulas_resumen": payload["clausulas"]["resumen"],
        "clausulas_top": payload["clausulas"]["candidatos"][:TOP],
        "mi_plantilla": payload["plantilla"]["jugadores"],
        "plantilla_resumen": payload["plantilla"]["resumen"],
        "alertas": payload["alertas"],
        "mercado_resumen": payload["mercado"]["resumen"],
        "mercado_top": payload["mercado"]["pujas"][:TOP],
        "liga": payload["liga"],
    }


def write_brief(payload, path="data/brief.json"):
    brief = build_brief(payload)
    Path(path).write_text(
        json.dumps(brief, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8")
    return brief


def verificar_numeros(texto, brief):
    """Comprueba que las cifras largas del texto existan en el brief.

    Red de seguridad contra el fallo tipico: que el modelo se invente un
    valor de mercado. No es prueba formal, pero atrapa lo evidente.
    """
    conocidos = set(re.findall(r"\d+", json.dumps(brief, default=str)))
    return [t for t in re.findall(r"\d[\d.,]{5,}", texto)
            if re.sub(r"[.,]", "", t) not in conocidos]
