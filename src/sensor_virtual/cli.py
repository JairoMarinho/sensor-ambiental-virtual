from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Sequence

from .sensor import SensorAmbientalVirtual
from .storage import carregar_leituras, salvar_leitura


ARQUIVO_PADRAO = Path("data/leituras.jsonl")


def inteiro_positivo(valor: str) -> int:
    numero = int(valor)
    if numero < 1:
        raise argparse.ArgumentTypeError("informe um número inteiro maior que zero")
    return numero


def numero_nao_negativo(valor: str) -> float:
    numero = float(valor)
    if numero < 0:
        raise argparse.ArgumentTypeError("informe um valor maior ou igual a zero")
    return numero


def criar_analisador() -> argparse.ArgumentParser:
    analisador = argparse.ArgumentParser(
        prog="sensor-virtual",
        description="Simulação de um sensor ambiental para aplicações IoT.",
    )
    comandos = analisador.add_subparsers(dest="comando", required=True)

    gerar = comandos.add_parser("generate", help="gera novas leituras ambientais")
    gerar.add_argument("--count", type=inteiro_positivo, default=5, help="quantidade de leituras")
    gerar.add_argument("--interval", type=numero_nao_negativo, default=1.0, help="intervalo em segundos")
    gerar.add_argument("--device-id", default="sensor-sala-01", help="identificador do sensor")
    gerar.add_argument("--location", default="Sala de Aula", help="local monitorado")
    gerar.add_argument("--output", type=Path, default=ARQUIVO_PADRAO, help="arquivo de saída")

    consultar = comandos.add_parser("read", help="consulta leituras já armazenadas")
    consultar.add_argument("--input", type=Path, default=ARQUIVO_PADRAO, help="arquivo de entrada")
    consultar.add_argument("--limit", type=inteiro_positivo, help="número máximo de registros exibidos")

    return analisador


def gerar_leituras(argumentos: argparse.Namespace) -> int:
    sensor = SensorAmbientalVirtual(
        identificador=argumentos.device_id,
        local=argumentos.location,
    )

    print(f"Sensor: {sensor.identificador}")
    print(f"Local: {sensor.local}")

    try:
        for posicao in range(argumentos.count):
            leitura = sensor.medir()
            salvar_leitura(argumentos.output, leitura)
            print(json.dumps(leitura.como_dicionario(), ensure_ascii=False))

            ultima_leitura = posicao == argumentos.count - 1
            if not ultima_leitura and argumentos.interval > 0:
                time.sleep(argumentos.interval)
    except KeyboardInterrupt:
        print("\nColeta encerrada.")
        return 130

    print(f"{argumentos.count} leitura(s) gravada(s) em {argumentos.output}.")
    return 0


def consultar_historico(argumentos: argparse.Namespace) -> int:
    try:
        leituras = carregar_leituras(argumentos.input)
    except (FileNotFoundError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    if argumentos.limit is not None:
        leituras = leituras[-argumentos.limit :]

    if not leituras:
        print("O arquivo não possui leituras.")
        return 0

    for leitura in leituras:
        print(json.dumps(leitura, ensure_ascii=False))

    print(f"Total: {len(leituras)} leitura(s).")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    argumentos = criar_analisador().parse_args(argv)
    if argumentos.comando == "generate":
        return gerar_leituras(argumentos)
    return consultar_historico(argumentos)
