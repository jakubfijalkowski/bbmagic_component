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
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info
from bluetooth_sensor_state_data import SensorUpdate

from .const import DOMAIN, UPTIME_KEY, VOLTAGE_KEY, TEMPERATURE_KEY, BATTERY_KEY

UPTIME_SENSOR = SensorEntityDescription(
    key=UPTIME_KEY,
    name="Uptime",
    device_class=SensorDeviceClass.DURATION,
    native_unit_of_measurement=UnitOfTime.SECONDS,
    state_class=SensorStateClass.TOTAL_INCREASING,
    entity_category=EntityCategory.DIAGNOSTIC,
)

TEMPERATURE_SENSOR = SensorEntityDescription(
    key=TEMPERATURE_KEY,
    name="Temperature",
    device_class=SensorDeviceClass.TEMPERATURE,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    state_class=SensorStateClass.MEASUREMENT,
    entity_category=EntityCategory.DIAGNOSTIC,
)

VOLTAGE_SENSOR = SensorEntityDescription(
    key=VOLTAGE_KEY,
    name="Battery Voltage",
    device_class=SensorDeviceClass.VOLTAGE,
    native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    state_class=SensorStateClass.MEASUREMENT,
    entity_category=EntityCategory.DIAGNOSTIC,
)

BATTERY_SENSOR = SensorEntityDescription(
    key=BATTERY_KEY,
    name="Battery %",
    device_class=SensorDeviceClass.BATTERY,
    native_unit_of_measurement=PERCENTAGE,
    state_class=SensorStateClass.MEASUREMENT,
    entity_category=EntityCategory.DIAGNOSTIC,
)

ALL_SENSORS = dict(
    map(
        lambda x: (x.key, x),
        [UPTIME_SENSOR, TEMPERATURE_SENSOR, VOLTAGE_SENSOR, BATTERY_SENSOR],
    )
)


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
            for device_key in sensor_update.entity_descriptions.keys()
            if device_key.key in ALL_SENSORS
        },
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
            for device_key, sensor_values in sensor_update.entity_values.items()
            if device_key.key in ALL_SENSORS
        },
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.entity_values.items()
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


class BBMagicFloodBluetoothSensorEntity(PassiveBluetoothProcessorEntity, SensorEntity):
    @property
    def native_value(self) -> int | float | None:
        return self.processor.entity_data.get(self.entity_key)
