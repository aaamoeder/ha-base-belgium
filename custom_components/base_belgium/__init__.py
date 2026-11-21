"""BASE Belgium-integratie voor Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import DOMAIN
from .coordinator import BaseBelgiumCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Zet BASE Belgium op vanuit een config entry."""
    coordinator = BaseBelgiumCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Verwerk gewijzigde opties: herlaad de integratie zodat het nieuwe interval geldt."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Sta toe dat een apparaat verwijderd wordt als zijn nummer niet meer in het BASE-account zit."""
    coordinator: BaseBelgiumCoordinator | None = hass.data.get(DOMAIN, {}).get(
        entry.entry_id
    )
    if coordinator is None or coordinator.data is None:
        return True
    active = {
        sub.get("identifier")
        for sub in coordinator.data.get("subscriptions", [])
    }
    return not any(
        domain == DOMAIN and identifier in active
        for domain, identifier in device_entry.identifiers
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Ontlaad een config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: BaseBelgiumCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await hass.async_add_executor_job(coordinator.api.close)
    return unload_ok
