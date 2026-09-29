"""Interface de linha de comando do sensor virtual."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Sequence

from .sensor import EnvironmentalSensor
from .storage import append_reading, format_readings, read_readings


DEFAULT_DATA_FILE = Path("data/readings.jsonl")


def non_negative_float(value: str) -> float:
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("o valor deve ser maior ou igual a zero")
    return number


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("o valor deve ser maior que zero")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sensor-virtual",
        description="Sensor virtual de temperatura e umidade para a camada de percepção IoT.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="gera e armazena novas leituras")
    generate.add_argument("--count", type=positive_int, default=5, help="quantidade de leituras (padrão: 5)")
    generate.add_argument("--interval", type=non_negative_float, default=1.0, help="segundos entre leituras (padrão: 1)")
    generate.add_argument("--device-id", default="sensor-sala-01", help="identificador do dispositivo")
    generate.add_argument("--location", default="Sala de Aula", help="localização do dispositivo")
    generate.add_argument("--output", type=Path, default=DEFAULT_DATA_FILE, help="arquivo JSONL de saída")

    read = subparsers.add_parser("read", help="lê o histórico armazenado")
    read.add_argument("--input", type=Path, default=DEFAULT_DATA_FILE, help="arquivo JSONL de entrada")
    read.add_argument("--limit", type=positive_int, help="exibe somente as últimas N leituras")
    return parser


def run_generate(args: argparse.Namespace) -> int:
    sensor = EnvironmentalSensor(device_id=args.device_id, location=args.location)
    print(f"Sensor {args.device_id!r} iniciado em {args.location!r}.")
    print(f"Gravando {args.count} leitura(s) em {args.output}.")

    try:
        for index in range(args.count):
            reading = sensor.collect()
            append_reading(args.output, reading)
            print(json.dumps(reading.to_dict(), ensure_ascii=False))
            if index < args.count - 1 and args.interval:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nColeta interrompida pelo usuário; leituras anteriores foram preservadas.")
        return 130

    print("Coleta concluída.")
    return 0


def run_read(args: argparse.Namespace) -> int:
    try:
        readings = read_readings(args.input)
    except (FileNotFoundError, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    if args.limit:
        readings = readings[-args.limit :]
    if not readings:
        print("Nenhuma leitura encontrada.")
        return 0

    print(format_readings(readings))
    print(f"Total exibido: {len(readings)} leitura(s).")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "generate":
        return run_generate(args)
    return run_read(args)
