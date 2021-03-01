from unittest import TestCase

from air_quality import MeasurementRepository


class TestMeasurementRepository(TestCase):

    def test_collect(self):
        repository = MeasurementRepository()

        measurement = repository.collect()
        self.assertIsNotNone(measurement)