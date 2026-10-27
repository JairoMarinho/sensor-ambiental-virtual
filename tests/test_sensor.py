from datetime import datetime, timezone
import random
import unittest

from src.sensor_virtual.sensor import SensorAmbientalVirtual


class TesteSensorAmbiental(unittest.TestCase):
    def test_leitura_possui_dados_do_sensor(self) -> None:
        instante = datetime(2026, 10, 27, 12, 30, tzinfo=timezone.utc)
        sensor = SensorAmbientalVirtual(
            identificador="sala-02",
            local="Laboratório 2",
            gerador=random.Random(12),
            relogio=lambda: instante,
        )

        leitura = sensor.medir()

        self.assertEqual(leitura.identificador, "sala-02")
        self.assertEqual(leitura.local, "Laboratório 2")
        self.assertEqual(leitura.data_hora, "2026-10-27T12:30:00+00:00")
        self.assertGreaterEqual(leitura.temperatura_c, 15.0)
        self.assertLessEqual(leitura.temperatura_c, 40.0)
        self.assertGreaterEqual(leitura.umidade_percentual, 20.0)
        self.assertLessEqual(leitura.umidade_percentual, 100.0)

    def test_classificacao_das_condicoes_ambientais(self) -> None:
        classificar = SensorAmbientalVirtual.classificar

        self.assertEqual(classificar(31.0, 50.0), "calor")
        self.assertEqual(classificar(17.0, 50.0), "frio")
        self.assertEqual(classificar(25.0, 85.0), "umidade_alta")
        self.assertEqual(classificar(25.0, 25.0), "umidade_baixa")
        self.assertEqual(classificar(24.0, 55.0), "confortavel")

    def test_valores_iniciais_invalidos_sao_rejeitados(self) -> None:
        with self.assertRaises(ValueError):
            SensorAmbientalVirtual(identificador=" ")
        with self.assertRaises(ValueError):
            SensorAmbientalVirtual(temperatura_inicial=50.0)
        with self.assertRaises(ValueError):
            SensorAmbientalVirtual(umidade_inicial=10.0)


if __name__ == "__main__":
    unittest.main()
