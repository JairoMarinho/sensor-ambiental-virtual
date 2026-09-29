"""Persistência local das leituras do sensor."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .sensor import SensorReading


def append_reading(path: Path, reading: SensorReading) -> None:
    """Acrescenta uma leitura ao arquivo JSON Lines."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        json.dump(reading.to_dict(), stream, ensure_ascii=False, separators=(",", ":"))
        stream.write("\n")


def read_readings(path: Path) -> list[dict[str, object]]:
    """Lê e valida superficialmente todas as linhas de um arquivo JSONL."""

    if not path.exists():
        raise FileNotFoundError(f"arquivo de leituras não encontrado: {path}")

    readings: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"JSON inválido na linha {line_number}: {error.msg}") from error
            if not isinstance(value, dict):
                raise ValueError(f"leitura inválida na linha {line_number}: esperado objeto JSON")
            readings.append(value)
    return readings


def format_readings(readings: Iterable[dict[str, object]]) -> str:
    """Formata leituras para inspeção humana no terminal."""

    return "\n".join(json.dumps(item, ensure_ascii=False) for item in readings)
