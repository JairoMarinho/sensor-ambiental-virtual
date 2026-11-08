from datetime import datetime, timezone
import json
import random
import unittest

from src.dashboard.server import criar_resposta
from src.sensor_virtual.sensor import SensorAmbientalVirtual


class TesteDashboard(unittest.TestCase):
    def test_resposta_da_api_contem_leitura_do_sensor(self) -> None:
        instante = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
        sensor = SensorAmbientalVirtual(
            identificador="sensor-teste",
            local="Sala de teste",
            gerador=random.Random(4),
            relogio=lambda: instante,
        )

        resposta = json.loads(criar_resposta(sensor))

        self.assertEqual(resposta["identificador"], "sensor-teste")
        self.assertEqual(resposta["local"], "Sala de teste")
        self.assertEqual(resposta["data_hora"], "2026-11-08T12:00:00+00:00")
        self.assertIn("temperatura_c", resposta)
        self.assertIn("umidade_percentual", resposta)


if __name__ == "__main__":
    unittest.main()
