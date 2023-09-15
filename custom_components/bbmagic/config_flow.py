from typing import Any

import voluptuous as vol
import re

from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
)

from .const import DOMAIN, MAC_REGEX


class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> config_entries.FlowResult:
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {"name": f"Flood {discovery_info.address}"}

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="BBMagic Flood", data={})

        self._set_confirm_only()
        return self.async_show_form(step_id="bluetooth_confirm")

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors = {}
        if user_input is not None:
            address = str(user_input[CONF_ADDRESS]).upper()
            if not re.match(MAC_REGEX, address):
                errors[CONF_ADDRESS] = "The MAC address is invalid"
            else:
                await self.async_set_unique_id(address, raise_on_progress=False)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="BBMagic Flood", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): str}),
            errors=errors,
        )
