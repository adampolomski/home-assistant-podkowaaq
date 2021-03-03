"""Platform air quality monitoring in Podkowa Leśna."""
import logging
import time
from datetime import timedelta
from functools import partial
from typing import Optional

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.air_quality import AirQualityEntity, PLATFORM_SCHEMA
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

DOMAIN = "podkowaaq"

CONF_STATION = "station"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_STATION): cv.string
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    station = config.get(CONF_STATION)
    repository = MeasurementRepository(station)
    add_entities([PodkowaAQ(repository)])


class Measurement:

    def pm25(self):
        return None

    def pm10(self):
        return None


class MeasurementRepository:
    URL = 'https://powietrze.podkowalesna.pl/webapp/data/averages'
    METRICS = ["PM10", "PM25"]

    def __init__(self, station: str):
        assert station.isalnum()
        self._station = station.upper()

    def collect(self) -> Measurement:
        end = int(time.time())
        start = end - 7200

        response = requests.get(MeasurementRepository.URL, {
            "_dc": 1614541470669,
            "type": "chart",
            "avg": "1h",
            "start": start,
            "end": end,
            "vars": MeasurementRepository._parameters(self._station)
        })

        return JsonMeasurement(response.json())

    @staticmethod
    def _parameters(station):
        pattern = "{0}_{1}:A1h"
        parameters = map(partial(pattern.format, station), MeasurementRepository.METRICS)
        parameters = ','.join(parameters)
        return parameters


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

    def __init__(self, station: str, repository: MeasurementRepository):
        """Initialize the sensor."""
        self._repository = repository
        self._measurement = Measurement()
        self._station = station

    @property
    def name(self) -> Optional[str]:
        return 'PodkowaAQ %s' % self._station.upper()

    @property
    def unique_id(self) -> Optional[str]:
        return self._station

    @property
    def particulate_matter_2_5(self):
        return self._measurement.pm25()

    @property
    def particulate_matter_10(self):
        return self._measurement.pm10()

    @Throttle(min_time=timedelta(minutes=20))
    def update(self):
        self._measurement = self._repository.collect()
