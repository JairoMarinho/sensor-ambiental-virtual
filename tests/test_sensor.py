from datetime import datetime, timezone
import random
import unittest

from src.sensor_virtual.sensor import EnvironmentalSensor


class EnvironmentalSensorTest(unittest.TestCase):
    def test_collect_returns_complete_deterministic_reading(self) -> None:
        instant = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)
        sensor = EnvironmentalSensor(
            device_id="test-01",
            location="Laboratório",
            random_source=random.Random(7),
            clock=lambda: instant,
        )

        reading = sensor.collect()

        self.assertEqual(reading.device_id, "test-01")
        self.assertEqual(reading.location, "Laboratório")
        self.assertEqual(reading.timestamp, "2026-09-29T12:00:00+00:00")
        self.assertGreaterEqual(reading.temperature_c, 15.0)
        self.assertLessEqual(reading.temperature_c, 40.0)
        self.assertGreaterEqual(reading.humidity_percent, 20.0)
        self.assertLessEqual(reading.humidity_percent, 100.0)
        self.assertEqual(reading.status, "confortavel")

    def test_classification_thresholds(self) -> None:
        self.assertEqual(EnvironmentalSensor.classify(30.0, 50.0), "alerta_calor")
        self.assertEqual(EnvironmentalSensor.classify(18.0, 50.0), "alerta_frio")
        self.assertEqual(EnvironmentalSensor.classify(25.0, 80.0), "alerta_umidade_alta")
        self.assertEqual(EnvironmentalSensor.classify(25.0, 30.0), "alerta_umidade_baixa")
        self.assertEqual(EnvironmentalSensor.classify(25.0, 50.0), "confortavel")

    def test_invalid_initial_values_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentalSensor(device_id="")
        with self.assertRaises(ValueError):
            EnvironmentalSensor(initial_temperature=50.0)


if __name__ == "__main__":
    unittest.main()
