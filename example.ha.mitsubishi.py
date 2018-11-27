"""
Mitsubishi platform to control HVAC using MAC-568IF-E Interface over Echonet
Protocol

Uses mitsubishi_echonet python Library for API calls.
Plan is to eventually upload library to PyPi
"""

DOMAIN = "mitsubishi"

from homeassistant.components.climate import (
    ClimateDevice, ATTR_TARGET_TEMP_HIGH, ATTR_TARGET_TEMP_LOW,
    SUPPORT_TARGET_TEMPERATURE, SUPPORT_TARGET_HUMIDITY,
    SUPPORT_TARGET_HUMIDITY_LOW, SUPPORT_TARGET_HUMIDITY_HIGH,
    SUPPORT_AWAY_MODE, SUPPORT_HOLD_MODE, SUPPORT_FAN_MODE,
    SUPPORT_OPERATION_MODE, SUPPORT_AUX_HEAT, SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE_HIGH, SUPPORT_TARGET_TEMPERATURE_LOW,
    SUPPORT_ON_OFF)
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT, ATTR_TEMPERATURE
from custom_components.mitsubishi_echonet import lib_mitsubishi as mit #new line

SUPPORT_FLAGS = SUPPORT_TARGET_HUMIDITY_LOW | SUPPORT_TARGET_HUMIDITY_HIGH

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Demo climate devices."""
    add_entities([
        MitsubishiClimate('PEA_RP140', 21, TEMP_CELSIUS, None, None, 22, 'On High',
                     None, None, None, 'cool', None, None, None, None)
   ])


class MitsubishiClimate(ClimateDevice):
    """Representation of a demo climate device."""

    def __init__(self, name, target_temperature, unit_of_measurement,
                 away, hold, current_temperature, current_fan_mode,
                 target_humidity, current_humidity, current_swing_mode,
                 current_operation, aux, target_temp_high, target_temp_low,
                 is_on):
        """Initialize the climate device."""
        self._name = name
        self._api = mit.HomeAirConditioner('192.168.1.11') #new line
        data = self._api.Update()
        self._support_flags = SUPPORT_FLAGS
        if target_temperature is not None:
            self._support_flags = \
                self._support_flags | SUPPORT_TARGET_TEMPERATURE
        if away is not None:
            self._support_flags = self._support_flags | SUPPORT_AWAY_MODE
        if hold is not None:
            self._support_flags = self._support_flags | SUPPORT_HOLD_MODE
        if current_fan_mode is not None:
            self._support_flags = self._support_flags | SUPPORT_FAN_MODE
        if target_humidity is not None:
            self._support_flags = \
                self._support_flags | SUPPORT_TARGET_HUMIDITY
        if current_swing_mode is not None:
            self._support_flags = self._support_flags | SUPPORT_SWING_MODE
        if current_operation is not None:
            self._support_flags = self._support_flags | SUPPORT_OPERATION_MODE
        if aux is not None:
            self._support_flags = self._support_flags | SUPPORT_AUX_HEAT
        if target_temp_high is not None:
            self._support_flags = \
                self._support_flags | SUPPORT_TARGET_TEMPERATURE_HIGH
        if target_temp_low is not None:
            self._support_flags = \
                self._support_flags | SUPPORT_TARGET_TEMPERATURE_LOW
        if is_on is not None:
            self._support_flags = self._support_flags | SUPPORT_ON_OFF
        self._target_temperature = data['set_temperature']
        self._target_humidity = target_humidity
        self._unit_of_measurement = unit_of_measurement
        self._away = away
        self._hold = hold
        self._current_temperature = data['room_temperature']
        self._current_humidity = current_humidity
        self._current_fan_mode = data['fan_speed']
        self._current_operation = (data['mode'] if data['status'] is 'On' else data['status'])
        self._aux = aux
        self._current_swing_mode = current_swing_mode
        #self._fan_list = ['On Low', 'On High', 'Auto Low', 'Auto High', 'Off']
        self._fan_list = ['Low', 'Medium-High']
        self._operation_list = ['Heating', 'Cooling', 'Air circulator', 'Dehumidification', 'Automatic', 'Off']
        self._swing_list = ['Auto', '1', '2', '3', 'Off']
        self._target_temperature_high = target_temp_high
        self._target_temperature_low = target_temp_low
        self._on = True if data['status'] is 'On' else False


    def update(self):
        """Get the latest state from the HVAC."""
        data = self._api.Update()
        self._target_temperature = data['set_temperature']
        self._current_temperature = data['room_temperature']
        self._current_fan_mode = data['fan_speed']
        self._current_operation =  (data['mode'] if data['status'] is 'On' else data['status'])
        self._on = True if data['status'] is 'On' else False

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        return self._target_temperature_high

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        return self._target_temperature_low

    @property
    def current_humidity(self):
        """Return the current humidity."""
        return self._current_humidity

    @property
    def target_humidity(self):
        """Return the humidity we try to reach."""
        return self._target_humidity

    @property
    def current_operation(self):
        """Return current operation ie. heat, cool, idle."""
        return self._current_operation

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return self._operation_list

    @property
    def is_away_mode_on(self):
        """Return if away mode is on."""
        return self._away

    @property
    def current_hold_mode(self):
        """Return hold mode setting."""
        return self._hold

    @property
    def is_aux_heat_on(self):
        """Return true if aux heat is on."""
        return self._aux

    @property
    def is_on(self):
        """Return true if the device is on."""
        return self._on

    @property
    def current_fan_mode(self):
        """Return the fan setting."""
        return self._current_fan_mode

    @property
    def fan_list(self):
        """Return the list of available fan modes."""
        return self._fan_list

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._api.SetOperationalTemperature(kwargs.get(ATTR_TEMPERATURE))
            self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
        if kwargs.get(ATTR_TARGET_TEMP_HIGH) is not None and \
           kwargs.get(ATTR_TARGET_TEMP_LOW) is not None:
            self._target_temperature_high = kwargs.get(ATTR_TARGET_TEMP_HIGH)
            self._target_temperature_low = kwargs.get(ATTR_TARGET_TEMP_LOW)
        self.schedule_update_ha_state()

    def set_humidity(self, humidity):
        """Set new target temperature."""
        self._target_humidity = humidity
        self.schedule_update_ha_state()

    def set_swing_mode(self, swing_mode):
        """Set new target temperature."""
        self._current_swing_mode = swing_mode
        self.schedule_update_ha_state()

    def set_fan_mode(self, fan_mode):
        """Set new target temperature."""
        self._api.SetFanSpeed(fan_mode)
        self._current_fan_mode = fan_mode
        self.schedule_update_ha_state()

    def set_operation_mode(self, operation_mode):
        """Set new operation mode."""
        if operation_mode == 'Off':
            self.turn_off()
        else:
            if self._on == False:
                self.turn_on()
            self._api.SetMode(operation_mode)
        self._current_operation = operation_mode
        self.schedule_update_ha_state()

    @property
    def current_swing_mode(self):
        """Return the swing setting."""
        return self._current_swing_mode

    @property
    def swing_list(self):
        """List of available swing modes."""
        return self._swing_list

    def turn_away_mode_on(self):
        """Turn away mode on."""
        self._away = True
        self.schedule_update_ha_state()

    def turn_away_mode_off(self):
        """Turn away mode off."""
        self._away = False
        self.schedule_update_ha_state()

    def set_hold_mode(self, hold_mode):
        """Update hold_mode on."""
        self._hold = hold_mode
        self.schedule_update_ha_state()

    def turn_aux_heat_on(self):
        """Turn auxiliary heater on."""
        self._aux = True
        self.schedule_update_ha_state()

    def turn_aux_heat_off(self):
        """Turn auxiliary heater off."""
        self._aux = False
        self.schedule_update_ha_state()

    def turn_on(self):
        """Turn on."""
        self._api.On()
        self._on = True
        self.schedule_update_ha_state()

    def turn_off(self):
        """Turn off."""
        self._api.Off()
        self._on = False
        self.schedule_update_ha_state()
