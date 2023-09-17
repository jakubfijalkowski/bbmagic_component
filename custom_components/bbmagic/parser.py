import logging

from home_assistant_bluetooth import BluetoothServiceInfo
from bluetooth_sensor_state_data import BluetoothData

from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfElectricPotential,
)

from .const import UPTIME_KEY, VOLTAGE_KEY, TEMPERATURE_KEY, MOISTURE_KEY, BATTERY_KEY

_LOGGER = logging.getLogger(__name__)


class BBFloodBluetoothDeviceData(BluetoothData):
    """Data for BBFlood BLE sensors."""

    def _start_update(self, data: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing BBFlood BLE advertisement data: %s", data)
        payload = data.manufacturer_data[65535]
        timestamp = int.from_bytes(payload[0:4], "little")
        v_sup = payload[5] / 71.0
        alert = payload[7] & 0x01
        chip_temp = payload[8]

        battery = 100.0 - min(max(3.0 - v_sup, 0.0), 3.0 - 1.8) / (3.0 - 1.8) * 100.0
        self.update_sensor(UPTIME_KEY, UnitOfTime.SECONDS, timestamp)
        self.update_sensor(VOLTAGE_KEY, UnitOfElectricPotential.VOLT, round(v_sup, 2))
        self.update_sensor(BATTERY_KEY, PERCENTAGE, round(battery, 0))
        self.update_sensor(TEMPERATURE_KEY, UnitOfTemperature.CELSIUS, chip_temp)
        self.update_binary_sensor(MOISTURE_KEY, alert)
