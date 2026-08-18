"""Etapa de render: data.json + analisis.md -> docs/index.html.

Separada de run.py porque entre ambas se ejecuta Claude Code, que es quien
escribe el analisis. Si no hay analisis todavia, el sitio se genera igual.
"""
import json
from pathlib import Path

from . import analysis, build_site

FALLBACK = "_Analisis pendiente de generar._"


def main():
    payload = json.loads(Path("docs/data.json").read_text(encoding="utf-8"))

    md_path = Path("docs/analisis.md")
    texto = md_path.read_text(encoding="utf-8") if md_path.exists() else FALLBACK

    brief_path = Path("data/brief.json")
    if brief_path.exists() and texto != FALLBACK:
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
        avisos = analysis.verificar_numeros(texto, brief)
        if avisos:
            print(f"  AVISO cifras no presentes en el brief: {avisos}")

    out = build_site.build(payload, texto)
    print(f"  generado {out}")


if __name__ == "__main__":
    main()
