"""Prepara el brief que leerá Claude Code.

Este módulo NO llama a ninguna API. Solo reduce el payload completo a los
hechos relevantes del día y los deja en disco. El Action de Claude Code lee
ese fichero y escribe docs/analisis.md.

La separación es deliberada: el brief es determinista y versionado, así que
siempre puedes comprobar sobre qué cifras exactas se escribió cada análisis.
Para que eso sea cierto de verdad, cada brief se guarda con su fecha en
data/briefs/ y data/brief.json es solo una copia del último. La versión
anterior sobrescribía un único fichero, con lo cual el histórico no existía.

Tres cambios de fondo respecto a la versión anterior:

  - `calendario` llega al brief. Se calculaba en metrics.py y build_brief no
    lo seleccionaba, así que el analista nunca ha visto un rival ni una
    localía.
  - El truncado ya no es un TOP=8 uniforme. Cada sección tiene su tope y su
    criterio, y el brief declara de cuántos elementos se ha quedado con esos
    pocos, para que el modelo sepa que no está viendo el mercado entero.
  - `verificar_numeros` cubre los números cortos (porcentajes, medias,
    ratios), que eran justamente los que se escapaban.
"""
import json
import re
import shutil
from pathlib import Path

TOPES = {
    "subidas": 8,
    "bajadas": 8,
    "clausulas": 10,
    "mercado": 12,      # mas alto: viene ordenado por urgencia, no por gusto
    "calendario": 20,   # un equipo por fila, cabe entero
}


def build_brief(payload):
    """Reduce el payload a lo esencial. Lo estable se descarta."""
    var = payload["variaciones"]
    cla = payload["clausulas"]
    mer = payload["mercado"]
    cal = payload.get("calendario", [])

    return {
        "fecha": payload["meta"]["market_date"],
        "temporada": payload["meta"]["temporada"],
        "dias_historico": payload["meta"].get("dias_historico"),
        "jornadas_disputadas": payload["meta"].get("jornadas_disputadas"),
        "medias_fiables": payload["meta"].get("medias_fiables", False),
        "capitan_activo": payload["meta"].get("capitan_activo"),
        "saldo": payload["meta"]["saldo"],

        "universo": payload["universo"],

        "variaciones_resumen": var["resumen"],
        "mayores_subidas": var["suben"][:TOPES["subidas"]],
        "mayores_bajadas": var["bajan"][:TOPES["bajadas"]],
        "altas_nuevas": var.get("altas_nuevas", []),

        "clausulas_resumen": cla["resumen"],
        "clausulas_top": cla["candidatos"][:TOPES["clausulas"]],
        "clausulas_top_de": cla["resumen"].get("candidatos_de"),

        "mi_plantilla": payload["plantilla"]["jugadores"],
        "plantilla_resumen": payload["plantilla"]["resumen"],
        "alertas": payload["alertas"],

        "mercado_resumen": mer["resumen"],
        "mercado_top": mer["pujas"][:TOPES["mercado"]],
        "mercado_top_de": mer["resumen"].get("n"),

        "calendario": cal[:TOPES["calendario"]],
        "liga": payload["liga"],

        # Si esto no viene vacio, el analisis del dia no es de fiar.
        "validaciones": payload.get("validaciones", []),
    }


def write_brief(payload, dir_briefs="data/briefs", latest="data/brief.json"):
    """Escribe el brief del día y actualiza la copia `latest`."""
    brief = build_brief(payload)
    Path(dir_briefs).mkdir(parents=True, exist_ok=True)
    destino = Path(dir_briefs) / f"{brief['fecha']}.json"
    destino.write_text(
        json.dumps(brief, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8")
    Path(latest).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(destino, latest)
    return brief


# --- verificacion de cifras --------------------------------------------

_NUM = re.compile(r"-?\d[\d.,]*\d|\d")


def _variantes(token):
    """Normalizaciones plausibles de un número escrito en texto español.

    "14.191.000" -> "14191000"   (puntos como millares)
    "2,50"       -> "2.5"        (coma como decimal)
    "1,94"       -> "1.94"
    """
    t = token.strip().lstrip("-")
    salidas = {t}
    salidas.add(t.replace(".", "").replace(",", ""))          # 14191000
    salidas.add(t.replace(".", "").replace(",", "."))         # 2.50
    return {s.rstrip(".") for s in salidas if s}


def _conocidos(brief):
    """Todas las formas en que una cifra del brief puede aparecer escrita."""
    vistos = set()

    def rec(o):
        if isinstance(o, dict):
            for v in o.values():
                rec(v)
        elif isinstance(o, list):
            for v in o:
                rec(v)
        elif isinstance(o, bool) or o is None:
            pass
        elif isinstance(o, int):
            vistos.add(str(abs(o)))
        elif isinstance(o, float):
            a = abs(o)
            vistos.add(f"{a:.10f}".rstrip("0").rstrip("."))
            vistos.add(str(int(a)) if a == int(a) else "")
            # redondeos que el analista puede escribir legitimamente
            for d in (0, 1, 2, 3):
                vistos.add(f"{round(a, d):.{d}f}".rstrip(".") if d else
                           str(int(round(a))))
                vistos.add(f"{round(a * 100, d):.{d}f}")      # porcentajes
        elif isinstance(o, str) and o.replace(".", "").isdigit():
            vistos.add(o)

    rec(brief)
    return {v for v in vistos if v}


def verificar_numeros(texto, brief, minimo_digitos=2):
    """Devuelve las cifras del texto que no se corresponden con el brief.

    Red de seguridad contra el fallo típico: que el modelo se invente una
    cifra. La versión anterior solo miraba tokens de seis caracteres o más,
    con lo que ignoraba todos los porcentajes, medias y conteos —justo los
    números que el modelo tiene que derivar y por tanto los únicos que
    puede inventarse. Sobre un análisis real, de 26 cifras solo comprobaba
    10, y las 16 restantes eran precisamente las de riesgo.

    Sigue sin ser una prueba formal: con quinientos jugadores en el JSON,
    una coincidencia por azar es posible. La solución definitiva es que el
    analista cite la procedencia de cada cifra en vez de escribirla suelta.
    """
    conocidos = _conocidos(brief)
    sospechosas = []
    for token in _NUM.findall(texto):
        digitos = sum(c.isdigit() for c in token)
        if digitos < minimo_digitos:
            continue
        if not (_variantes(token) & conocidos):
            sospechosas.append(token)
    return sospechosas


def comprobar_o_fallar(texto, brief):
    """Para usar en el Action: revienta si hay cifras sin respaldo.

    La función anterior devolvía una lista que nadie leía. Si no falla el
    build, la verificación es decoración.
    """
    problemas = verificar_numeros(texto, brief)
    if problemas:
        raise ValueError(
            "Cifras sin respaldo en el brief: " + ", ".join(problemas[:20]))
    if brief.get("validaciones"):
        raise ValueError(
            "El brief trae validaciones fallidas: "
            + "; ".join(brief["validaciones"]))
    return True