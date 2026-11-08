from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

from src.sensor_virtual.sensor import SensorAmbientalVirtual


PASTA_DASHBOARD = Path(__file__).resolve().parents[2] / "dashboard"
ARQUIVOS_PUBLICOS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


def criar_resposta(sensor: SensorAmbientalVirtual) -> bytes:
    leitura = sensor.medir().como_dicionario()
    return json.dumps(leitura, ensure_ascii=False).encode("utf-8")


def criar_manipulador(sensor: SensorAmbientalVirtual) -> type[BaseHTTPRequestHandler]:
    class ManipuladorDashboard(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            caminho = urlparse(self.path).path

            if caminho == "/api/leitura":
                self._responder(criar_resposta(sensor), "application/json; charset=utf-8")
                return

            arquivo_publico = ARQUIVOS_PUBLICOS.get(caminho)
            if arquivo_publico is None:
                self.send_error(HTTPStatus.NOT_FOUND, "Recurso não encontrado")
                return

            nome, tipo = arquivo_publico
            self._responder((PASTA_DASHBOARD / nome).read_bytes(), tipo)

        def _responder(self, conteudo: bytes, tipo: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(conteudo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(conteudo)

        def log_message(self, formato: str, *argumentos: object) -> None:
            return

    return ManipuladorDashboard


def executar(host: str, porta: int) -> None:
    sensor = SensorAmbientalVirtual(
        identificador="sensor-sala-01",
        local="Sala de Aula",
    )
    servidor = ThreadingHTTPServer((host, porta), criar_manipulador(sensor))

    print(f"Dashboard disponível em http://{host}:{porta}")
    print("Pressione Ctrl+C para encerrar.")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        servidor.server_close()


def main(argv: Sequence[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(description="Servidor local do dashboard ambiental")
    analisador.add_argument("--host", default="127.0.0.1")
    analisador.add_argument("--port", type=int, default=8000)
    argumentos = analisador.parse_args(argv)

    executar(argumentos.host, argumentos.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
