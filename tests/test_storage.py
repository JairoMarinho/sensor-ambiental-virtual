import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.sensor_virtual.sensor import SensorReading
from src.sensor_virtual.storage import append_reading, read_readings


class StorageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.reading = SensorReading(
            device_id="test-01",
            location="Sala",
            timestamp="2026-09-29T12:00:00+00:00",
            temperature_c=25.0,
            humidity_percent=60.0,
            status="confortavel",
        )

    def test_append_and_read_round_trip(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "readings.jsonl"
            append_reading(path, self.reading)
            append_reading(path, self.reading)

            values = read_readings(path)

            self.assertEqual(len(values), 2)
            self.assertEqual(values[0], self.reading.to_dict())

    def test_invalid_json_reports_line(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "readings.jsonl"
            path.write_text(json.dumps(self.reading.to_dict()) + "\ninvalid\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "linha 2"):
                read_readings(path)


if __name__ == "__main__":
    unittest.main()
