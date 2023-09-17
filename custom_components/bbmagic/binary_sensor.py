"""Support for BBMagic Flood (unencrypted)"""
from __future__ import annotations

from homeassistant import config_entries
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothEntityKey,
    PassiveBluetoothProcessorCoordinator,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info
from bluetooth_sensor_state_data import SensorUpdate

from .const import DOMAIN, MOISTURE_KEY

MOISTURE_SENSOR = BinarySensorEntityDescription(
    key=MOISTURE_KEY,
    name="Moisture",
    device_class=BinarySensorDeviceClass.MOISTURE,
)

ALL_SENSORS = dict(map(lambda x: (x.key, x), [MOISTURE_SENSOR]))


def device_key_to_bluetooth_entity_key(device_key) -> PassiveBluetoothEntityKey:
    """Convert a device key to an entity key."""
    return PassiveBluetoothEntityKey(device_key.key, device_key.device_id)


def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate,
) -> PassiveBluetoothDataUpdate:
    """Convert a sensor update to a bluetooth data update."""
    return PassiveBluetoothDataUpdate(
        devices={
            device_id: sensor_device_info_to_hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions={
            device_key_to_bluetooth_entity_key(device_key): ALL_SENSORS[device_key.key]
            for device_key in sensor_update.binary_entity_descriptions.keys()
            if device_key.key in ALL_SENSORS
        },
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
            for device_key, sensor_values in sensor_update.binary_entity_values.items()
            if device_key.key in ALL_SENSORS
        },
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.binary_entity_values.items()
            if device_key.key in ALL_SENSORS
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BLE sensors."""
    coordinator: PassiveBluetoothProcessorCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]
    processor = PassiveBluetoothDataProcessor(sensor_update_to_bluetooth_data_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(
            BBMagicFloodBluetoothSensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(coordinator.async_register_processor(processor))


class BBMagicFloodBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity, BinarySensorEntity
):
    @property
    def is_on(self) -> bool | None:
        return self.processor.entity_data.get(self.entity_key)
