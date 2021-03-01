from homeassistant.components.air_quality import AirQualityEntity

DOMAIN = "podkowaaq"

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([PodkowaAQ()])

class PodkowaAQ( AirQualityEntity ):

    def __init__(self):
        """Initialize the sensor."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Example Temperature'

    @property
    def particulate_matter_2_5(self):
        return 20

    @property
    def particulate_matter_10(self):
        return 20

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """