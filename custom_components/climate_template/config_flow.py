"""Config flow for the Daikin platform."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import uuid4

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PASSWORD, CONF_CLIENT_ID,CONF_COUNTRY_CODE, CONF_IP_ADDRESS
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, KEY_MAC, TIMEOUT

_LOGGER = logging.getLogger(__name__)


class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the Daikin config flow."""
        self.host: str | None = None

    @property
    def schema(self) -> vol.Schema:
        """Return current schema."""
        return vol.Schema(
            {
                vol.Required(CONF_HOST, default=self.host): str,
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_COUNTRY_CODE): str,
            }
        )

    async def _create_entry(
        self,
        host: str,
        ipaddr: str,
        apiKey: str | None = None,
        apiSecret: str | None = None,
        apiDeviceID: str | None = None,
        apiRegion: str | None=None,
    ) -> FlowResult:
        """Register new entry."""
        if not self.unique_id:
            await self.async_set_unique_id(apiDeviceID)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=host,
            data={
                CONF_IP_ADDRESS: ipaddr,
                CONF_API_KEY: apiKey,
                CONF_CLIENT_ID: apiDeviceID,
                CONF_PASSWORD: apiSecret,
                CONF_COUNTRY_CODE: apiRegion,
            },
        )

    async def _create_device(
        self, host: str, key: str | None = None, password: str | None = None
    ) -> FlowResult:
        """Create device."""
       
        uuid = None
        key = None

        if not password:
            password = None

        try:
            """ Get Device Details"""
            host = "Test"
            ipaddr = "192.168.1.163"
            apiKey = "df"
            apiSecret = ""
            apiDeviceID = ""
            apiRegion = "us"

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error creating device")
            return self.async_show_form(
                step_id="user",
                data_schema=self.schema,
                errors={"base": "unknown"},
            )

        
        return await self._create_entry( host, ipaddr, apiKey, apiSecret, apiDeviceID ,apiRegion )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """User initiated config flow."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=self.schema)
        if user_input.get(CONF_API_KEY) and user_input.get(CONF_PASSWORD):
            self.host = user_input[CONF_HOST]
            return self.async_show_form(
                step_id="user",
                data_schema=self.schema,
                errors={"base": "api_password"},
            )
        return await self._create_device(
            user_input[CONF_HOST],
            user_input.get(CONF_IP_ADDRESS),
            user_input.get(CONF_API_KEY),
            user_input.get(CONF_PASSWORD),
            user_input.get(CONF_CLIENT_ID),
            user_input.get(CONF_COUNTRY_CODE),
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Prepare configuration for a discovered Daikin device."""
        _LOGGER.debug("Zeroconf user_input: %s", discovery_info)
        devices = Discovery().poll(ip=discovery_info.host)
        if not devices:
            _LOGGER.debug(
                (
                    "Could not find MAC-address for %s, make sure the required UDP"
                    " ports are open (see integration documentation)"
                ),
                discovery_info.host,
            )
            return self.async_abort(reason="cannot_connect")
        await self.async_set_unique_id(next(iter(devices))[KEY_MAC])
        self._abort_if_unique_id_configured()
        self.host = discovery_info.host
        return await self.async_step_user()