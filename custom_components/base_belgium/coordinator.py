"""Data coordinator for BASE Belgium."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BaseBelgiumApi, BaseBelgiumApiError, BaseBelgiumAuthError
from .const import CONF_PHONE, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BaseBelgiumCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching BASE Belgium data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )
        self.entry = entry
        self.api = BaseBelgiumApi(
            username=entry.data[CONF_PHONE],
            password=entry.data[CONF_PASSWORD],
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from BASE Belgium API."""
        try:
            return await self.hass.async_add_executor_job(
                self.api.get_all_data, self.data
            )
        except BaseBelgiumAuthError as err:
            self.api.session.cookies.clear()
            raise ConfigEntryAuthFailed(
                f"Authentication failed: {err}"
            ) from err
        except BaseBelgiumApiError as err:
            raise UpdateFailed(f"API error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
