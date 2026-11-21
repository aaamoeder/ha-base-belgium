"""Config flow voor BASE Belgium."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import BaseBelgiumApi, BaseBelgiumAuthError
from .const import (
    CONF_PHONE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

# Loginvelden met autocomplete-hints, zodat de wachtwoordbeheerder van de browser
# opgeslagen gegevens kan aanbieden, en een gemaskeerd wachtwoordveld.
LOGIN_SELECTOR = TextSelector(
    TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="username")
)
PASSWORD_SELECTOR = TextSelector(
    TextSelectorConfig(
        type=TextSelectorType.PASSWORD, autocomplete="current-password"
    )
)


class BaseBelgiumConfigFlow(ConfigFlow, domain=DOMAIN):
    """Verwerk de config flow voor BASE Belgium."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Verwerk de eerste stap."""
        errors: dict[str, str] = {}

        if user_input is not None:
            phone = user_input[CONF_PHONE]
            password = user_input[CONF_PASSWORD]

            api = BaseBelgiumApi(phone, password)
            try:
                await self.hass.async_add_executor_job(api.login)
            except BaseBelgiumAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected error during login")
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(phone)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"BASE {phone}",
                    data={
                        CONF_PHONE: phone,
                        CONF_PASSWORD: password,
                    },
                )
            finally:
                await self.hass.async_add_executor_job(api.close)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PHONE): LOGIN_SELECTOR,
                    vol.Required(CONF_PASSWORD): PASSWORD_SELECTOR,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> FlowResult:
        """Verwerk de herauthenticatie."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Verwerk de bevestiging van de herauthenticatie."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            login = user_input[CONF_PHONE].strip()
            password = user_input[CONF_PASSWORD]

            api = BaseBelgiumApi(login, password)
            try:
                await self.hass.async_add_executor_job(api.login)
            except BaseBelgiumAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected error during re-auth")
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={
                        CONF_PHONE: login,
                        CONF_PASSWORD: password,
                    },
                )
            finally:
                await self.hass.async_add_executor_job(api.close)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PHONE,
                        default=reauth_entry.data[CONF_PHONE],
                    ): LOGIN_SELECTOR,
                    vol.Required(CONF_PASSWORD): PASSWORD_SELECTOR,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Wijzig de login (telefoonnummer of e-mail) en het wachtwoord."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            login = user_input[CONF_PHONE].strip()
            password = user_input[CONF_PASSWORD]

            api = BaseBelgiumApi(login, password)
            try:
                await self.hass.async_add_executor_job(api.login)
            except BaseBelgiumAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected error during reconfigure")
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data_updates={
                        CONF_PHONE: login,
                        CONF_PASSWORD: password,
                    },
                )
            finally:
                await self.hass.async_add_executor_job(api.close)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PHONE,
                        default=reconfigure_entry.data[CONF_PHONE],
                    ): LOGIN_SELECTOR,
                    vol.Required(CONF_PASSWORD): PASSWORD_SELECTOR,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Geef de options flow terug."""
        return BaseBelgiumOptionsFlow(config_entry)


class BaseBelgiumOptionsFlow(OptionsFlow):
    """Verwerk de opties voor BASE Belgium."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialiseer de options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Beheer de opties."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                }
            ),
        )
