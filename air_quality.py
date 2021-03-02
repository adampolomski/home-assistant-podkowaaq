"""Platform air quality monitoring in Podkowa Leśna."""
import logging
import time
from datetime import timedelta
from functools import partial

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.air_quality import AirQualityEntity, PLATFORM_SCHEMA

_LOGGER = logging.getLogger(__name__)

DOMAIN = "podkowaaq"
SCAN_INTERVAL = timedelta(minutes=20)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("station"): cv.string
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    repository = MeasurementRepository()
    add_entities([PodkowaAQ(repository)])


class Measurement:

    def pm25(self):
        return None

    def pm10(self):
        return None


class MeasurementRepository:
    URL = 'https://powietrze.podkowalesna.pl/webapp/data/averages'
    METRICS = ["PM10", "PM25"]

    def collect(self):
        end = int(time.time())
        start = end - 7200

        response = requests.get(MeasurementRepository.URL, {
            "_dc": 1614541470669,
            "type": "chart",
            "avg": "1h",
            "start": start,
            "end": end,
            "vars": MeasurementRepository._vars("PD01")
        })

        return JsonMeasurement(response.json())

    @staticmethod
    def _vars(station):
        pattern = "{0}_{1}:A1h"
        vars = map(partial(pattern.format, station), MeasurementRepository.METRICS)
        vars = ','.join(vars)
        return vars


class JsonMeasurement(Measurement):

    def __init__(self, json):
        self._json = json

    def _value(self, metric):
        index = MeasurementRepository.METRICS.index(metric)
        return self._json['values'][index][-1]['v']

    def pm25(self):
        return self._value("PM25")

    def pm10(self):
        return self._value("PM10")


class PodkowaAQ(AirQualityEntity):

    def __init__(self, repository: MeasurementRepository):
        """Initialize the sensor."""
        self._repository = repository
        self._measurement = Measurement()

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'pd01'

    @property
    def particulate_matter_2_5(self):
        return self._measurement.pm25()

    @property
    def particulate_matter_10(self):
        return self._measurement.pm10()

    def update(self):
        """Fetch new state data for the sensor."""
        self._measurement = self._repository.collect()
