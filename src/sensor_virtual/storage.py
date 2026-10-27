from __future__ import annotations

import json
from pathlib import Path

from .sensor import LeituraAmbiental


def salvar_leitura(arquivo: Path, leitura: LeituraAmbiental) -> None:
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    linha = json.dumps(leitura.como_dicionario(), ensure_ascii=False)

    with arquivo.open("a", encoding="utf-8") as saida:
        saida.write(linha + "\n")


def carregar_leituras(arquivo: Path) -> list[dict[str, object]]:
    if not arquivo.is_file():
        raise FileNotFoundError(f"arquivo de leituras não encontrado: {arquivo}")

    leituras: list[dict[str, object]] = []
    with arquivo.open(encoding="utf-8") as entrada:
        for numero_linha, linha in enumerate(entrada, start=1):
            if not linha.strip():
                continue

            try:
                registro = json.loads(linha)
            except json.JSONDecodeError as erro:
                raise ValueError(
                    f"conteúdo inválido na linha {numero_linha}: {erro.msg}"
                ) from erro

            if not isinstance(registro, dict):
                raise ValueError(f"a linha {numero_linha} não contém um objeto JSON")

            leituras.append(registro)

    return leituras
