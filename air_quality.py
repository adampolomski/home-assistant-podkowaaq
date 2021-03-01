"""Platform air quality monitoring in Podkowa Leśna."""
import logging
import time
from functools import partial

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.air_quality import AirQualityEntity

DOMAIN = "podkowaaq"
_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({vol.Required("station"): cv.string, })}, extra=vol.PREVENT_EXTRA
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    repository = MeasurementRepository()
    add_entities([PodkowaAQ(repository)])


class Measurement():

    def __init__(self, pm25: float, pm10: float):
        self._pm25 = pm25
        self._pm10 = pm10

    def pm25(self):
        return self._pm25

    def pm10(self):
        return self._pm10


class MeasurementRepository():
    URL = 'https://powietrze.podkowalesna.pl/webapp/data/averages'
    METRICS = ["PM10", "PM25"]

    def collect(self):
        end = int(time.time())
        start = end - 7200

        pattern = "{0}_{1}:A1h"
        vars = map(partial(pattern.format, "PD01"), MeasurementRepository.METRICS)
        vars = ','.join(vars)

        x = requests.get(MeasurementRepository.URL,
                         {"_dc": 1614541470669, "type": "chart", "avg": "1h", "start": start, "end": end, "vars": vars})
        pm10 = x.json()['values'][0][0]['v']
        pm25 = x.json()['values'][1][0]['v']
        return Measurement(pm25, pm10)


class PodkowaAQ(AirQualityEntity):

    def __init__(self, repository: MeasurementRepository):
        """Initialize the sensor."""
        self._repository = repository

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Air Quality'

    @property
    def particulate_matter_2_5(self):
        return self._measurement.pm25()

    @property
    def particulate_matter_10(self):
        return self._measurement.pm10()

    def update(self):
        """Fetch new state data for the sensor."""
        self._measurement = self._repository.collect()
