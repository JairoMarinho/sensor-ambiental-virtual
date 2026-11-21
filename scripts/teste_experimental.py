from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Sequence
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from src.experimentos.metricas import calcular_metricas


def consultar_json(url: str) -> dict[str, object]:
    with urlopen(url, timeout=3) as resposta:
        conteudo = json.load(resposta)
    if not isinstance(conteudo, dict):
        raise ValueError("a API não retornou um objeto JSON")
    return conteudo


def coletar(
    url: str,
    duracao: float,
    intervalo_consulta: float,
) -> list[tuple[dict[str, object], datetime]]:
    amostras_por_chave: dict[
        tuple[object, object, object, object],
        tuple[dict[str, object], datetime],
    ] = {}
    fim = time.monotonic() + duracao
    while time.monotonic() < fim:
        try:
            leitura = consultar_json(url)
            chave = (
                leitura.get("identificador"),
                leitura.get("data_hora"),
                leitura.get("temperatura_c"),
                leitura.get("umidade_percentual"),
            )
            amostras_por_chave.setdefault(
                chave,
                (leitura, datetime.now(timezone.utc)),
            )
        except (HTTPError, URLError, TimeoutError, ValueError) as erro:
            print(f"Consulta sem leitura válida: {erro}")
        time.sleep(intervalo_consulta)
    return list(amostras_por_chave.values())


def main(argv: Sequence[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(
        description="Mede completude, duplicatas e latência do fluxo sensor-dashboard"
    )
    analisador.add_argument("--url", default="http://127.0.0.1:8000/api/leitura")
    analisador.add_argument("--duration", type=float, default=60.0)
    analisador.add_argument("--poll-interval", type=float, default=1.0)
    analisador.add_argument("--sensor-interval", type=float, default=5.0)
    analisador.add_argument(
        "--output",
        type=Path,
        default=Path("data/resultado-experimento.json"),
    )
    argumentos = analisador.parse_args(argv)
    if min(argumentos.duration, argumentos.poll_interval, argumentos.sensor_interval) <= 0:
        analisador.error("duração e intervalos devem ser maiores que zero")

    inicio = datetime.now(timezone.utc)
    status_url = argumentos.url.rsplit("/", 1)[0] + "/status"
    status_inicial = consultar_json(status_url)
    esperado = max(1, round(argumentos.duration / argumentos.sensor_interval))
    amostras = coletar(argumentos.url, argumentos.duration, argumentos.poll_interval)
    metricas = calcular_metricas(amostras, esperado)
    status_final = consultar_json(status_url)
    for campo in ("mensagens_recebidas", "mensagens_unicas", "duplicatas"):
        metricas[campo] = int(status_final[campo]) - int(status_inicial[campo])
    metricas["completude_percentual"] = round(
        100.0 * int(metricas["mensagens_unicas"]) / esperado,
        2,
    )
    resultado = {
        "inicio_utc": inicio.isoformat(timespec="seconds"),
        "duracao_s": argumentos.duration,
        "intervalo_sensor_s": argumentos.sensor_interval,
        **metricas,
    }
    argumentos.output.parent.mkdir(parents=True, exist_ok=True)
    argumentos.output.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
