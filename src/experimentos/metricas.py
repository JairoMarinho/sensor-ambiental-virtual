from __future__ import annotations

from datetime import datetime
from statistics import fmean
from typing import Iterable, Mapping


def calcular_metricas(
    amostras: Iterable[tuple[Mapping[str, object], datetime]],
    quantidade_esperada: int,
) -> dict[str, float | int]:
    if quantidade_esperada <= 0:
        raise ValueError("quantidade_esperada deve ser maior que zero")

    chaves: set[tuple[object, object]] = set()
    latencias: list[float] = []
    recebidas = 0

    for leitura, instante_recebimento in amostras:
        recebidas += 1
        chave = (
            leitura.get("identificador"),
            leitura.get("data_hora"),
            leitura.get("temperatura_c"),
            leitura.get("umidade_percentual"),
        )
        if chave in chaves:
            continue
        chaves.add(chave)

        instante_coleta = datetime.fromisoformat(
            str(leitura["data_hora"]).replace("Z", "+00:00")
        )
        if instante_coleta.tzinfo is None or instante_recebimento.tzinfo is None:
            raise ValueError("instantes de coleta e recebimento devem informar o fuso")
        latencias.append(max(0.0, (instante_recebimento - instante_coleta).total_seconds()))

    unicas = len(chaves)
    return {
        "mensagens_esperadas": quantidade_esperada,
        "mensagens_recebidas": recebidas,
        "mensagens_unicas": unicas,
        "duplicatas": recebidas - unicas,
        "completude_percentual": round(100.0 * unicas / quantidade_esperada, 2),
        "latencia_media_s": round(fmean(latencias), 3) if latencias else 0.0,
        "latencia_maxima_s": round(max(latencias), 3) if latencias else 0.0,
    }
