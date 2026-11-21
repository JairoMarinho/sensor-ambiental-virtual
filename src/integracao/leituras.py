from __future__ import annotations

from collections import deque
from datetime import datetime
import math
from threading import Lock
from typing import Mapping

from src.sensor_virtual.sensor import SensorAmbientalVirtual


class SemLeituraDisponivel(RuntimeError):
    """Indica que o coletor ainda não recebeu uma leitura válida."""


def normalizar_leitura(dados: Mapping[str, object]) -> dict[str, object]:
    """Valida e normaliza uma leitura recebida do sensor físico ou virtual."""

    campos_obrigatorios = {
        "identificador",
        "local",
        "data_hora",
        "temperatura_c",
        "umidade_percentual",
    }
    ausentes = sorted(campos_obrigatorios - dados.keys())
    if ausentes:
        raise ValueError(f"campos obrigatórios ausentes: {', '.join(ausentes)}")

    identificador = _texto(dados["identificador"], "identificador")
    local = _texto(dados["local"], "local")
    data_hora = _data_iso_8601(dados["data_hora"])
    temperatura = _numero(dados["temperatura_c"], "temperatura_c")
    umidade = _numero(dados["umidade_percentual"], "umidade_percentual")

    if not -40.0 <= temperatura <= 80.0:
        raise ValueError("temperatura_c deve estar entre -40 e 80")
    if not 0.0 <= umidade <= 100.0:
        raise ValueError("umidade_percentual deve estar entre 0 e 100")

    situacao_recebida = dados.get("situacao")
    situacao = (
        _texto(situacao_recebida, "situacao")
        if situacao_recebida is not None
        else SensorAmbientalVirtual.classificar(temperatura, umidade)
    )

    return {
        "identificador": identificador,
        "local": local,
        "data_hora": data_hora,
        "temperatura_c": round(temperatura, 1),
        "umidade_percentual": round(umidade, 1),
        "situacao": situacao,
    }


class RepositorioLeituras:
    """Mantém as leituras mais recentes com acesso seguro entre threads."""

    def __init__(self, limite: int = 120) -> None:
        if limite <= 0:
            raise ValueError("o limite do histórico deve ser positivo")
        self._leituras: deque[dict[str, object]] = deque(maxlen=limite)
        self._lock = Lock()
        self._recebidas = 0
        self._duplicatas = 0

    def atualizar(self, dados: Mapping[str, object]) -> dict[str, object]:
        leitura = normalizar_leitura(dados)
        with self._lock:
            self._recebidas += 1
            if self._leituras and _chave(self._leituras[-1]) == _chave(leitura):
                self._duplicatas += 1
                return dict(self._leituras[-1])
            self._leituras.append(leitura)
        return dict(leitura)

    def mais_recente(self) -> dict[str, object]:
        with self._lock:
            if not self._leituras:
                raise SemLeituraDisponivel("nenhuma leitura foi recebida pelo coletor")
            return dict(self._leituras[-1])

    def historico(self, limite: int | None = None) -> list[dict[str, object]]:
        with self._lock:
            leituras = list(self._leituras)
        if limite is not None:
            if limite < 0:
                raise ValueError("o limite não pode ser negativo")
            leituras = leituras[-limite:] if limite else []
        return [dict(leitura) for leitura in leituras]

    def estatisticas(self) -> dict[str, int]:
        with self._lock:
            return {
                "mensagens_recebidas": self._recebidas,
                "mensagens_unicas": self._recebidas - self._duplicatas,
                "duplicatas": self._duplicatas,
            }


def _chave(leitura: Mapping[str, object]) -> tuple[object, object, object, object]:
    return (
        leitura["identificador"],
        leitura["data_hora"],
        leitura["temperatura_c"],
        leitura["umidade_percentual"],
    )


def _texto(valor: object, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} deve ser um texto não vazio")
    return valor.strip()


def _numero(valor: object, campo: str) -> float:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{campo} deve ser numérico")
    numero = float(valor)
    if not math.isfinite(numero):
        raise ValueError(f"{campo} deve ser finito")
    return numero


def _data_iso_8601(valor: object) -> str:
    texto = _texto(valor, "data_hora")
    try:
        instante = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError as erro:
        raise ValueError("data_hora deve usar o formato ISO 8601") from erro
    if instante.tzinfo is None:
        raise ValueError("data_hora deve informar o fuso horário")
    return texto
