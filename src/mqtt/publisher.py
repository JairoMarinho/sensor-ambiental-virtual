from __future__ import annotations

import argparse
import json
import time
from typing import Sequence

from src.sensor_virtual.sensor import SensorAmbientalVirtual


def executar(
    host: str,
    porta: int,
    topico: str,
    quantidade: int,
    intervalo: float,
    identificador: str,
    local: str,
) -> None:
    try:
        import paho.mqtt.client as mqtt
    except ModuleNotFoundError as erro:
        raise RuntimeError(
            "paho-mqtt não está instalado; execute 'python3 -m pip install -e .'"
        ) from erro

    sensor = SensorAmbientalVirtual(identificador=identificador, local=local)
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.connect(host, porta, keepalive=30)
    cliente.loop_start()
    try:
        for indice in range(quantidade):
            leitura = sensor.medir().como_dicionario()
            payload = json.dumps(leitura, ensure_ascii=False)
            resultado = cliente.publish(topico, payload, qos=1)
            resultado.wait_for_publish(timeout=5)
            if resultado.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"falha na publicação MQTT: código {resultado.rc}")
            print(payload)
            if indice + 1 < quantidade:
                time.sleep(intervalo)
    finally:
        cliente.disconnect()
        cliente.loop_stop()


def main(argv: Sequence[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(
        description="Publica leituras virtuais no mesmo tópico usado pelo ESP32"
    )
    analisador.add_argument("--broker", default="127.0.0.1")
    analisador.add_argument("--mqtt-port", type=int, default=1883)
    analisador.add_argument("--topic", default="cidade/sala-01/ambiente")
    analisador.add_argument("--count", type=int, default=10)
    analisador.add_argument("--interval", type=float, default=2.0)
    analisador.add_argument("--device-id", default="sensor-virtual-teste")
    analisador.add_argument("--location", default="Sala de Aula")
    argumentos = analisador.parse_args(argv)

    if argumentos.count < 1:
        analisador.error("--count deve ser maior que zero")
    if argumentos.interval < 0:
        analisador.error("--interval não pode ser negativo")

    executar(
        argumentos.broker,
        argumentos.mqtt_port,
        argumentos.topic,
        argumentos.count,
        argumentos.interval,
        argumentos.device_id,
        argumentos.location,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
