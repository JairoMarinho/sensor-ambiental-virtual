from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.integracao.leituras import RepositorioLeituras, normalizar_leitura
from src.sensor_virtual.storage import salvar_registro


def processar_payload(
    payload: bytes,
    repositorio: RepositorioLeituras,
    arquivo_historico: Path | None = None,
) -> dict[str, object]:
    """Valida uma mensagem MQTT e atualiza o estado usado pelo dashboard."""

    try:
        dados = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as erro:
        raise ValueError("payload MQTT não contém um objeto JSON válido") from erro
    if not isinstance(dados, dict):
        raise ValueError("payload MQTT deve conter um objeto JSON")

    leitura = normalizar_leitura(dados)
    duplicatas_anteriores = repositorio.estatisticas()["duplicatas"]
    leitura_atualizada = repositorio.atualizar(leitura)
    duplicatas_atuais = repositorio.estatisticas()["duplicatas"]
    if arquivo_historico is not None and duplicatas_atuais == duplicatas_anteriores:
        salvar_registro(arquivo_historico, leitura_atualizada)
    return leitura_atualizada


class ConsumidorMQTT:
    """Assina o tópico de sensoriamento e alimenta o repositório em memória."""

    def __init__(
        self,
        repositorio: RepositorioLeituras,
        host: str = "127.0.0.1",
        porta: int = 1883,
        topico: str = "cidade/sala-01/ambiente",
        arquivo_historico: Path | None = None,
        usuario: str | None = None,
        senha: str | None = None,
    ) -> None:
        try:
            import paho.mqtt.client as mqtt
        except ModuleNotFoundError as erro:
            raise RuntimeError(
                "paho-mqtt não está instalado; execute 'python3 -m pip install -e .'"
            ) from erro

        self._mqtt = mqtt
        self._repositorio = repositorio
        self._host = host
        self._porta = porta
        self._topico = topico
        self._arquivo_historico = arquivo_historico
        self._cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if usuario:
            self._cliente.username_pw_set(usuario, senha)
        self._cliente.on_connect = self._ao_conectar
        self._cliente.on_message = self._ao_receber
        self._cliente.on_disconnect = self._ao_desconectar

    def iniciar(self) -> None:
        self._cliente.connect_async(self._host, self._porta, keepalive=30)
        self._cliente.loop_start()

    def encerrar(self) -> None:
        self._cliente.disconnect()
        self._cliente.loop_stop()

    def _ao_conectar(
        self,
        cliente: Any,
        dados_usuario: object,
        flags: object,
        codigo: object,
        propriedades: object,
    ) -> None:
        if not _codigo_indica_falha(codigo):
            cliente.subscribe(self._topico, qos=1)
            print(f"MQTT conectado; aguardando mensagens em {self._topico}")
        else:
            print(f"Falha ao conectar ao MQTT: código {codigo}")

    def _ao_receber(self, cliente: Any, dados_usuario: object, mensagem: Any) -> None:
        try:
            leitura = processar_payload(
                mensagem.payload,
                self._repositorio,
                self._arquivo_historico,
            )
            print(
                "Leitura recebida: "
                f"{leitura['temperatura_c']:.1f} °C, "
                f"{leitura['umidade_percentual']:.1f}%"
            )
        except ValueError as erro:
            print(f"Mensagem MQTT descartada: {erro}")

    def _ao_desconectar(
        self,
        cliente: Any,
        dados_usuario: object,
        flags: object,
        codigo: object,
        propriedades: object,
    ) -> None:
        if _codigo_indica_falha(codigo):
            print("Conexão MQTT interrompida; o cliente tentará reconectar.")


def _codigo_indica_falha(codigo: object) -> bool:
    falha = getattr(codigo, "is_failure", None)
    if falha is not None:
        return bool(falha)
    return codigo != 0
