from unittest import TestCase
from mock import Mock

from air_quality import *
import json

class TestMeasurementRepository(TestCase):

    def test_json_measurement(self):
        measurement = JsonMeasurement(TestMeasurementRepository.response())
        self.assertEqual(44.5056, measurement.pm10())
        self.assertEqual(36.0333, measurement.pm25())

    # def test_collect(self):
    #     repository = MeasurementRepository("pd01")
    #
    #     measurement = repository.collect()
    #     self.assertEqual(1, measurement.pm10())
    #     self.assertEqual(1, measurement.pm25())

    @staticmethod
    def response():
        with open('response.json') as json_file:
            return json.load(json_file)
