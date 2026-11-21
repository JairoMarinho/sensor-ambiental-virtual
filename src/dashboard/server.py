from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Protocol, Sequence
from urllib.parse import urlparse

from src.integracao.leituras import RepositorioLeituras, SemLeituraDisponivel
from src.mqtt.consumer import ConsumidorMQTT
from src.sensor_virtual.sensor import SensorAmbientalVirtual


PASTA_DASHBOARD = Path(__file__).resolve().parents[2] / "dashboard"
ARQUIVOS_PUBLICOS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


class FonteLeitura(Protocol):
    def mais_recente(self) -> dict[str, object]: ...


def obter_leitura(
    fonte: SensorAmbientalVirtual | FonteLeitura,
) -> dict[str, object]:
    if isinstance(fonte, SensorAmbientalVirtual):
        return fonte.medir().como_dicionario()
    return fonte.mais_recente()


def criar_resposta(fonte: SensorAmbientalVirtual | FonteLeitura) -> bytes:
    leitura = obter_leitura(fonte)
    return json.dumps(leitura, ensure_ascii=False).encode("utf-8")


def criar_manipulador(
    fonte: SensorAmbientalVirtual | FonteLeitura,
) -> type[BaseHTTPRequestHandler]:
    class ManipuladorDashboard(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            caminho = urlparse(self.path).path

            if caminho == "/api/leitura":
                try:
                    resposta = criar_resposta(fonte)
                except SemLeituraDisponivel as erro:
                    self._responder_json(
                        {"erro": str(erro)},
                        status=HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                    return
                self._responder(resposta, "application/json; charset=utf-8")
                return

            if caminho == "/api/historico" and isinstance(fonte, RepositorioLeituras):
                self._responder_json({"leituras": fonte.historico(limite=20)})
                return

            if caminho == "/api/status" and isinstance(fonte, RepositorioLeituras):
                self._responder_json(fonte.estatisticas())
                return

            arquivo_publico = ARQUIVOS_PUBLICOS.get(caminho)
            if arquivo_publico is None:
                self.send_error(HTTPStatus.NOT_FOUND, "Recurso não encontrado")
                return

            nome, tipo = arquivo_publico
            self._responder((PASTA_DASHBOARD / nome).read_bytes(), tipo)

        def _responder_json(
            self,
            conteudo: dict[str, object],
            status: HTTPStatus = HTTPStatus.OK,
        ) -> None:
            self._responder(
                json.dumps(conteudo, ensure_ascii=False).encode("utf-8"),
                "application/json; charset=utf-8",
                status=status,
            )

        def _responder(
            self,
            conteudo: bytes,
            tipo: str,
            status: HTTPStatus = HTTPStatus.OK,
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(conteudo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(conteudo)

        def log_message(self, formato: str, *argumentos: object) -> None:
            return

    return ManipuladorDashboard


def executar(
    host: str,
    porta: int,
    fonte: str,
    broker: str,
    porta_mqtt: int,
    topico: str,
    arquivo_dados: Path,
) -> None:
    consumidor: ConsumidorMQTT | None = None
    if fonte == "virtual":
        origem: SensorAmbientalVirtual | RepositorioLeituras = SensorAmbientalVirtual(
            identificador="sensor-sala-01",
            local="Sala de Aula",
        )
    else:
        origem = RepositorioLeituras()
        consumidor = ConsumidorMQTT(
            repositorio=origem,
            host=broker,
            porta=porta_mqtt,
            topico=topico,
            arquivo_historico=arquivo_dados,
        )
        consumidor.iniciar()

    servidor = ThreadingHTTPServer((host, porta), criar_manipulador(origem))

    print(f"Dashboard disponível em http://{host}:{porta}")
    print(f"Fonte de dados: {fonte}")
    print("Pressione Ctrl+C para encerrar.")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        servidor.server_close()
        if consumidor is not None:
            consumidor.encerrar()


def main(argv: Sequence[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(description="Servidor local do dashboard ambiental")
    analisador.add_argument("--host", default="127.0.0.1")
    analisador.add_argument("--port", type=int, default=8000)
    analisador.add_argument(
        "--source",
        choices=("mqtt", "virtual"),
        default="mqtt",
        help="origem das leituras exibidas no dashboard",
    )
    analisador.add_argument("--broker", default="127.0.0.1")
    analisador.add_argument("--mqtt-port", type=int, default=1883)
    analisador.add_argument("--topic", default="cidade/sala-01/ambiente")
    analisador.add_argument(
        "--data-file",
        type=Path,
        default=Path("data/leituras-mqtt.jsonl"),
    )
    argumentos = analisador.parse_args(argv)

    executar(
        argumentos.host,
        argumentos.port,
        argumentos.source,
        argumentos.broker,
        argumentos.mqtt_port,
        argumentos.topic,
        argumentos.data_file,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
