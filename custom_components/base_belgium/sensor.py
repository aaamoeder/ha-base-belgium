"""Sensor platform for BASE Belgium."""
from __future__ import annotations

from datetime import datetime, timezone
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BaseBelgiumCoordinator

_LOGGER = logging.getLogger(__name__)


def _format_phone(phone: str) -> str:
    """Format phone number for display."""
    if len(phone) == 10 and phone.startswith("0"):
        return f"{phone[:4]} {phone[4:6]} {phone[6:8]} {phone[8:]}"
    return phone


def _parse_eur(value: str | float | int | None) -> float:
    """Parse a EUR value that might use comma as decimal separator."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(",", "."))


def _get_data_rate(specs: dict, specurl: str) -> float | None:
    """Get data rate in EUR per MB from product spec."""
    spec = specs.get(specurl, {})
    for rate in spec.get("rates", []):
        if rate.get("type") == "Mobile data" and rate.get("unit") == "MB":
            return _parse_eur(rate.get("cost"))
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BASE Belgium sensors from a config entry."""
    coordinator: BaseBelgiumCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []
    data = coordinator.data or {}

    for sub in data.get("subscriptions", []):
        identifier = sub.get("identifier", "")
        if not identifier:
            continue

        phone_display = _format_phone(identifier)
        label = sub.get("label", phone_display)
        specurl = sub.get("specurl", "")
        is_prepaid = "prepaid" in specurl.lower() or "BPRB" in specurl

        if is_prepaid:
            entities.append(
                BaseCreditSensor(coordinator, entry, identifier, phone_display, label)
            )
        else:
            entities.extend([
                BaseMonetaryUsedSensor(coordinator, entry, identifier, phone_display, label),
                BaseMonetaryRemainingSensor(coordinator, entry, identifier, phone_display, label),
                BaseMonetaryPercentageSensor(coordinator, entry, identifier, phone_display, label),
                BaseDataEquivTotalSensor(coordinator, entry, identifier, phone_display, label, specurl),
                BaseDataEquivUsedSensor(coordinator, entry, identifier, phone_display, label, specurl),
                BaseDataEquivRemainingSensor(coordinator, entry, identifier, phone_display, label, specurl),
                BaseDaysRemainingSensor(coordinator, entry, identifier, phone_display, label),
                BaseDataTodaySensor(coordinator, entry, identifier, phone_display, label, specurl),
            ])

        entities.append(
            BaseOutOfBundleSensor(coordinator, entry, identifier, phone_display, label)
        )

    async_add_entities(entities)


class BaseBelgiumSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for BASE Belgium sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BaseBelgiumCoordinator,
        entry: ConfigEntry,
        identifier: str,
        phone_display: str,
        label: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._identifier = identifier
        self._phone_display = phone_display
        self._label = label
        self._entry = entry

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._identifier)},
            "name": f"BASE {self._label}",
            "manufacturer": "BASE",
            "model": "Mobile",
        }

    def _get_usage(self) -> dict:
        """Get current usage data for this identifier."""
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get("usage", {}).get(self._identifier, {})

    def _get_total_monetary(self) -> dict:
        """Get total monetary data."""
        return self._get_usage().get("total", {}).get("monetary", {})


class BaseCreditSensor(BaseBelgiumSensorBase):
    """Sensor for prepaid credit."""

    _attr_translation_key = "credit"
    _attr_icon = "mdi:currency-eur"
    _attr_native_unit_of_measurement = "EUR"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_credit"

    @property
    def native_value(self) -> float | None:
        credit = self._get_usage().get("credit", {})
        remaining = credit.get("remainingUnits")
        if remaining is not None:
            return _parse_eur(remaining)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        usage = self._get_usage()
        return {
            "valid_until": usage.get("validUntil"),
            "last_updated": usage.get("lastUpdated"),
        }


class BaseMonetaryUsedSensor(BaseBelgiumSensorBase):
    """Sensor for monetary allowance used."""

    _attr_translation_key = "monetary_used"
    _attr_icon = "mdi:cash-minus"
    _attr_native_unit_of_measurement = "EUR"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_monetary_used"

    @property
    def native_value(self) -> float | None:
        monetary = self._get_total_monetary()
        used = monetary.get("usedUnits")
        if used is not None:
            return round(_parse_eur(used), 2)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        monetary = self._get_total_monetary()
        usage = self._get_usage()
        return {
            "total_eur": _parse_eur(monetary.get("startUnits")),
            "remaining_eur": _parse_eur(monetary.get("remainingUnits")),
            "included_percentage": monetary.get("initialIncludedPercentage"),
            "carryover_percentage": monetary.get("initialCarryOverPercentage"),
            "last_updated": usage.get("lastUpdated"),
            "next_billing_date": usage.get("nextBillingDate"),
        }


class BaseMonetaryRemainingSensor(BaseBelgiumSensorBase):
    """Sensor for monetary allowance remaining."""

    _attr_translation_key = "monetary_remaining"
    _attr_icon = "mdi:cash"
    _attr_native_unit_of_measurement = "EUR"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_monetary_remaining"

    @property
    def native_value(self) -> float | None:
        monetary = self._get_total_monetary()
        remaining = monetary.get("remainingUnits")
        if remaining is not None:
            return round(_parse_eur(remaining), 2)
        return None


class BaseMonetaryPercentageSensor(BaseBelgiumSensorBase):
    """Sensor for monetary usage percentage."""

    _attr_translation_key = "monetary_percentage"
    _attr_icon = "mdi:percent"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_monetary_percentage"

    @property
    def native_value(self) -> float | None:
        monetary = self._get_total_monetary()
        pct = monetary.get("usedPercentage")
        if pct is not None:
            return pct
        return None


class _BaseDataEquivSensor(BaseBelgiumSensorBase):
    """Base for data equivalent sensors."""

    def __init__(self, coordinator, entry, identifier, phone_display, label, specurl):
        super().__init__(coordinator, entry, identifier, phone_display, label)
        self._specurl = specurl

    def _calc_data_gb(self, eur_value: float) -> float | None:
        """Convert EUR to GB using data rate from product spec."""
        specs = (self.coordinator.data or {}).get("specs", {})
        rate = _get_data_rate(specs, self._specurl)
        if rate and rate > 0:
            mb = eur_value / rate
            return round(mb / 1024, 1)
        return None


class BaseDataEquivTotalSensor(_BaseDataEquivSensor):
    """Sensor for total data equivalent in GB."""

    _attr_translation_key = "data_total"
    _attr_icon = "mdi:database"
    _attr_native_unit_of_measurement = "GB"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_data_total"

    @property
    def native_value(self) -> float | None:
        monetary = self._get_total_monetary()
        total_eur = _parse_eur(monetary.get("startUnits"))
        if total_eur > 0:
            return self._calc_data_gb(total_eur)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        monetary = self._get_total_monetary()
        included = _parse_eur(monetary.get("startUnits", 0))
        carryover_pct = monetary.get("initialCarryOverPercentage", 0)
        included_pct = monetary.get("initialIncludedPercentage", 0)
        attrs = {}
        if included > 0 and included_pct > 0:
            attrs["included_gb"] = self._calc_data_gb(included * included_pct / 100)
            attrs["carryover_gb"] = self._calc_data_gb(included * carryover_pct / 100)
        return attrs


class BaseDataEquivUsedSensor(_BaseDataEquivSensor):
    """Sensor for used data equivalent in GB."""

    _attr_translation_key = "data_used"
    _attr_icon = "mdi:download"
    _attr_native_unit_of_measurement = "GB"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_data_used"

    @property
    def native_value(self) -> float | None:
        monetary = self._get_total_monetary()
        used_eur = _parse_eur(monetary.get("usedUnits"))
        return self._calc_data_gb(used_eur)


class BaseDataEquivRemainingSensor(_BaseDataEquivSensor):
    """Sensor for remaining data equivalent in GB."""

    _attr_translation_key = "data_remaining"
    _attr_icon = "mdi:download-outline"
    _attr_native_unit_of_measurement = "GB"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_data_remaining"

    @property
    def native_value(self) -> float | None:
        monetary = self._get_total_monetary()
        remaining_eur = _parse_eur(monetary.get("remainingUnits"))
        if remaining_eur > 0:
            return self._calc_data_gb(remaining_eur)
        return None


class BaseDaysRemainingSensor(BaseBelgiumSensorBase):
    """Sensor for days remaining in billing period."""

    _attr_translation_key = "days_remaining"
    _attr_icon = "mdi:calendar-clock"
    _attr_native_unit_of_measurement = "days"

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_days_remaining"

    @property
    def native_value(self) -> int | None:
        usage = self._get_usage()
        next_billing = usage.get("nextBillingDate")
        if next_billing:
            try:
                billing_date = datetime.fromisoformat(
                    next_billing.replace("Z", "+00:00")
                )
                now = datetime.now(timezone.utc)
                delta = (billing_date - now).days
                return max(0, delta)
            except (ValueError, TypeError):
                pass
        return None


class BaseOutOfBundleSensor(BaseBelgiumSensorBase):
    """Sensor for out-of-bundle costs."""

    _attr_translation_key = "out_of_bundle"
    _attr_icon = "mdi:cash-alert"
    _attr_native_unit_of_measurement = "EUR"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_out_of_bundle"

    @property
    def native_value(self) -> float | None:
        oob = self._get_usage().get("outOfBundle", {})
        used = oob.get("usedUnits")
        if used is not None:
            return _parse_eur(used)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        oob = self._get_usage().get("outOfBundle", {})
        details = oob.get("details", [])
        return {d["type"]: d["value"] for d in details if "type" in d}


class BaseDataTodaySensor(_BaseDataEquivSensor, RestoreEntity):
    """Sensor for data used today (tracked via daily diff)."""

    _attr_translation_key = "data_today"
    _attr_icon = "mdi:calendar-today"
    _attr_native_unit_of_measurement = "GB"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, entry, identifier, phone_display, label, specurl):
        super().__init__(coordinator, entry, identifier, phone_display, label, specurl)
        self._daily_start_eur: float | None = None
        self._daily_start_date: str | None = None

    @property
    def unique_id(self) -> str:
        return f"{self._identifier}_data_today"

    async def async_added_to_hass(self) -> None:
        """Restore previous state on startup."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.attributes:
            self._daily_start_eur = last_state.attributes.get("daily_start_eur")
            self._daily_start_date = last_state.attributes.get("daily_start_date")

    @property
    def native_value(self) -> float | None:
        monetary = self._get_total_monetary()
        current_used_eur = _parse_eur(monetary.get("usedUnits"))
        today = datetime.now().strftime("%Y-%m-%d")

        if self._daily_start_date != today:
            self._daily_start_eur = current_used_eur
            self._daily_start_date = today

        if self._daily_start_eur is not None:
            diff_eur = current_used_eur - self._daily_start_eur
            if diff_eur >= 0:
                return self._calc_data_gb(diff_eur)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict:
        monetary = self._get_total_monetary()
        return {
            "daily_start_eur": self._daily_start_eur,
            "daily_start_date": self._daily_start_date,
            "current_used_eur": _parse_eur(monetary.get("usedUnits")),
        }
