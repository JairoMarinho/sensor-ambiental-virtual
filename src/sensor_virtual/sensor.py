"""Modelo e simulação do sensor ambiental virtual."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import random
from typing import Callable


@dataclass(frozen=True, slots=True)
class SensorReading:
    """Uma medição produzida pelo dispositivo virtual."""

    device_id: str
    location: str
    timestamp: str
    temperature_c: float
    humidity_percent: float
    status: str

    def to_dict(self) -> dict[str, str | float]:
        """Converte a medição para um objeto serializável em JSON."""

        return asdict(self)


class EnvironmentalSensor:
    """Simula temperatura e umidade por meio de variações graduais."""

    def __init__(
        self,
        device_id: str = "sensor-sala-01",
        location: str = "Sala de Aula",
        initial_temperature: float = 25.0,
        initial_humidity: float = 60.0,
        random_source: random.Random | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not device_id.strip():
            raise ValueError("device_id não pode ser vazio")
        if not location.strip():
            raise ValueError("location não pode ser vazio")
        if not 15.0 <= initial_temperature <= 40.0:
            raise ValueError("temperatura inicial deve estar entre 15 e 40 °C")
        if not 20.0 <= initial_humidity <= 100.0:
            raise ValueError("umidade inicial deve estar entre 20 e 100%")

        self.device_id = device_id
        self.location = location
        self._temperature = initial_temperature
        self._humidity = initial_humidity
        self._random = random_source or random.Random()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def collect(self) -> SensorReading:
        """Coleta uma nova leitura, mantendo valores em faixas plausíveis."""

        self._temperature = self._clamp(
            self._temperature + self._random.uniform(-0.4, 0.4), 15.0, 40.0
        )
        self._humidity = self._clamp(
            self._humidity + self._random.uniform(-1.5, 1.5), 20.0, 100.0
        )

        temperature = round(self._temperature, 1)
        humidity = round(self._humidity, 1)
        timestamp = self._clock().astimezone(timezone.utc).isoformat(timespec="seconds")

        return SensorReading(
            device_id=self.device_id,
            location=self.location,
            timestamp=timestamp,
            temperature_c=temperature,
            humidity_percent=humidity,
            status=self.classify(temperature, humidity),
        )

    @staticmethod
    def classify(temperature: float, humidity: float) -> str:
        """Classifica a condição usando limites simples para demonstração."""

        if temperature >= 30.0:
            return "alerta_calor"
        if temperature <= 18.0:
            return "alerta_frio"
        if humidity >= 80.0:
            return "alerta_umidade_alta"
        if humidity <= 30.0:
            return "alerta_umidade_baixa"
        return "confortavel"

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(value, maximum))
