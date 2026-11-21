from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from src.dashboard.server import criar_manipulador
from src.experimentos.metricas import calcular_metricas
from src.integracao.leituras import RepositorioLeituras, normalizar_leitura
from src.mqtt.consumer import _codigo_indica_falha, processar_payload


LEITURA = {
    "identificador": "esp32-teste",
    "local": "Laboratório",
    "data_hora": "2026-11-21T12:00:00+00:00",
    "temperatura_c": 25.4,
    "umidade_percentual": 61.2,
}


class TesteIntegracaoEntrega3(unittest.TestCase):
    def test_payload_mqtt_chega_ao_dashboard(self) -> None:
        repositorio = RepositorioLeituras()
        processar_payload(json.dumps(LEITURA).encode(), repositorio)
        servidor = ThreadingHTTPServer(("127.0.0.1", 0), criar_manipulador(repositorio))
        thread = Thread(target=servidor.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(
                f"http://127.0.0.1:{servidor.server_port}/api/leitura",
                timeout=2,
            ) as resposta:
                dados = json.load(resposta)
            with urlopen(
                f"http://127.0.0.1:{servidor.server_port}/api/status",
                timeout=2,
            ) as resposta:
                status = json.load(resposta)
        finally:
            servidor.shutdown()
            servidor.server_close()
            thread.join(timeout=2)

        self.assertEqual(dados["identificador"], "esp32-teste")
        self.assertEqual(dados["temperatura_c"], 25.4)
        self.assertEqual(dados["situacao"], "confortavel")
        self.assertEqual(status["mensagens_recebidas"], 1)
        self.assertEqual(status["mensagens_unicas"], 1)

    def test_api_informa_quando_ainda_nao_ha_leitura(self) -> None:
        repositorio = RepositorioLeituras()
        servidor = ThreadingHTTPServer(("127.0.0.1", 0), criar_manipulador(repositorio))
        thread = Thread(target=servidor.serve_forever, daemon=True)
        thread.start()
        try:
            with self.assertRaises(HTTPError) as contexto:
                urlopen(
                    f"http://127.0.0.1:{servidor.server_port}/api/leitura",
                    timeout=2,
                )
        finally:
            servidor.shutdown()
            servidor.server_close()
            thread.join(timeout=2)
        self.assertEqual(contexto.exception.code, 503)

    def test_leitura_mqtt_e_persistida_sem_duplicar(self) -> None:
        repositorio = RepositorioLeituras()
        with TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "leituras.jsonl"
            payload = json.dumps(LEITURA).encode()
            processar_payload(payload, repositorio, arquivo)
            processar_payload(payload, repositorio, arquivo)
            linhas = arquivo.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(linhas), 1)
        self.assertEqual(repositorio.estatisticas()["duplicatas"], 1)

    def test_preserva_leituras_distintas_no_mesmo_segundo(self) -> None:
        repositorio = RepositorioLeituras()
        repositorio.atualizar(normalizar_leitura(LEITURA))
        repositorio.atualizar(
            normalizar_leitura({**LEITURA, "temperatura_c": 26.1})
        )
        self.assertEqual(len(repositorio.historico()), 2)

    def test_rejeita_valores_fora_da_faixa(self) -> None:
        invalida = {**LEITURA, "umidade_percentual": 120}
        with self.assertRaisesRegex(ValueError, "entre 0 e 100"):
            normalizar_leitura(invalida)

    def test_metricas_experimentais(self) -> None:
        coleta = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
        primeira = {**LEITURA, "data_hora": coleta.isoformat()}
        segunda = {
            **LEITURA,
            "data_hora": (coleta + timedelta(seconds=5)).isoformat(),
        }
        amostras = [
            (primeira, coleta + timedelta(seconds=1)),
            (primeira, coleta + timedelta(seconds=2)),
            (segunda, coleta + timedelta(seconds=6)),
        ]
        resultado = calcular_metricas(amostras, quantidade_esperada=2)
        self.assertEqual(resultado["mensagens_unicas"], 2)
        self.assertEqual(resultado["duplicatas"], 1)
        self.assertEqual(resultado["completude_percentual"], 100.0)
        self.assertEqual(resultado["latencia_media_s"], 1.0)

    def test_codigo_de_conexao_da_api_paho_v2(self) -> None:
        class Codigo:
            def __init__(self, falhou: bool) -> None:
                self.is_failure = falhou

        self.assertFalse(_codigo_indica_falha(Codigo(False)))
        self.assertTrue(_codigo_indica_falha(Codigo(True)))


if __name__ == "__main__":
    unittest.main()
