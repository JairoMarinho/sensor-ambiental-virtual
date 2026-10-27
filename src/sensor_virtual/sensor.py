from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import random
from typing import Callable


TEMPERATURA_MINIMA = 15.0
TEMPERATURA_MAXIMA = 40.0
UMIDADE_MINIMA = 20.0
UMIDADE_MAXIMA = 100.0


@dataclass(frozen=True)
class LeituraAmbiental:
    identificador: str
    local: str
    data_hora: str
    temperatura_c: float
    umidade_percentual: float
    situacao: str

    def como_dicionario(self) -> dict[str, str | float]:
        return asdict(self)


class SensorAmbientalVirtual:
    def __init__(
        self,
        identificador: str = "sensor-sala-01",
        local: str = "Sala de Aula",
        temperatura_inicial: float = 25.0,
        umidade_inicial: float = 60.0,
        gerador: random.Random | None = None,
        relogio: Callable[[], datetime] | None = None,
    ) -> None:
        if not identificador.strip():
            raise ValueError("o identificador do sensor não pode ficar vazio")
        if not local.strip():
            raise ValueError("o local do sensor não pode ficar vazio")
        if not TEMPERATURA_MINIMA <= temperatura_inicial <= TEMPERATURA_MAXIMA:
            raise ValueError("a temperatura inicial deve estar entre 15 e 40 °C")
        if not UMIDADE_MINIMA <= umidade_inicial <= UMIDADE_MAXIMA:
            raise ValueError("a umidade inicial deve estar entre 20 e 100%")

        self.identificador = identificador.strip()
        self.local = local.strip()
        self._temperatura = temperatura_inicial
        self._umidade = umidade_inicial
        self._gerador = gerador if gerador is not None else random.Random()
        self._relogio = relogio if relogio is not None else self._agora

    def medir(self) -> LeituraAmbiental:
        self._temperatura = self._limitar(
            self._temperatura + self._gerador.uniform(-0.4, 0.4),
            TEMPERATURA_MINIMA,
            TEMPERATURA_MAXIMA,
        )
        self._umidade = self._limitar(
            self._umidade + self._gerador.uniform(-1.5, 1.5),
            UMIDADE_MINIMA,
            UMIDADE_MAXIMA,
        )

        temperatura = round(self._temperatura, 1)
        umidade = round(self._umidade, 1)

        return LeituraAmbiental(
            identificador=self.identificador,
            local=self.local,
            data_hora=self._relogio().astimezone(timezone.utc).isoformat(timespec="seconds"),
            temperatura_c=temperatura,
            umidade_percentual=umidade,
            situacao=self.classificar(temperatura, umidade),
        )

    @staticmethod
    def classificar(temperatura: float, umidade: float) -> str:
        if temperatura >= 30.0:
            return "calor"
        if temperatura <= 18.0:
            return "frio"
        if umidade >= 80.0:
            return "umidade_alta"
        if umidade <= 30.0:
            return "umidade_baixa"
        return "confortavel"

    @staticmethod
    def _limitar(valor: float, minimo: float, maximo: float) -> float:
        return max(minimo, min(valor, maximo))

    @staticmethod
    def _agora() -> datetime:
        return datetime.now(timezone.utc)
