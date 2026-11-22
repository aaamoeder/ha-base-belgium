"""API-client voor BASE Belgium."""
from __future__ import annotations

import json
import logging
import re

import requests

from .const import (
    URL_ALIAS_LOOKUP,
    URL_AUTHORIZATION,
    URL_CHALLENGE,
    URL_CHALLENGE_ANSWER,
    URL_DEVICE_NONCE,
    URL_FINGERPRINT,
    URL_IDENTIFY,
    URL_INTROSPECT,
    URL_MOBILE_SUBS,
    URL_MOBILE_USAGE,
    URL_USERDETAILS,
)

_LOGGER = logging.getLogger(__name__)


class BaseBelgiumApiError(Exception):
    """Basisuitzondering voor API-fouten."""


class BaseBelgiumAuthError(BaseBelgiumApiError):
    """Fout bij het aanmelden."""


class BaseBelgiumApi:
    """API-client voor BASE Belgium."""

    def __init__(self, username: str, password: str) -> None:
        """Initialiseer de API-client."""
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "x-alt-referer": "https://www.base.be/nl/my-base/",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.base.be",
            "Referrer": "https://www.base.be",
        })

    def _resolve_username(self, username: str) -> str:
        """Zet een telefoonnummer om naar de Okta-login via de alias-lookup."""
        phone = username.replace(" ", "")
        if phone.startswith("0") and len(phone) == 10:
            phone = "+32" + phone[1:]
        elif phone.startswith("0032"):
            phone = "+" + phone[2:]
        elif phone.startswith("32") and not phone.startswith("+"):
            phone = "+" + phone

        try:
            response = requests.post(
                URL_ALIAS_LOOKUP,
                json={"alias": phone},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code == 200:
                resolved = response.json().get("login", phone)
                _LOGGER.debug("Resolved %s to %s", username, resolved)
                return resolved
        except Exception:
            _LOGGER.debug("Alias lookup failed, using phone directly: %s", phone)

        return phone

    def login(self) -> None:
        """Meld aan bij BASE Belgium via de Okta IDX-flow."""
        # Stap 1: controleer of we al aangemeld zijn
        response = self.session.get(URL_USERDETAILS, timeout=30)
        if response.status_code == 200:
            _LOGGER.debug("Already authenticated")
            return
        if response.status_code != 401:
            raise BaseBelgiumApiError(
                f"Unexpected status from userdetails: {response.status_code}"
            )

        # Stap 2: haal de autorisatiepagina op (volgt de doorverwijzingen naar Okta)
        response = self.session.get(
            URL_AUTHORIZATION,
            params={
                "lang": "nl",
                "style_hint": "care",
                "targetUrl": "https://www.base.be/nl/my-base/",
            },
            timeout=30,
            allow_redirects=True,
        )
        if response.status_code != 200:
            raise BaseBelgiumApiError(
                f"Authorization page failed: {response.status_code}"
            )

        # Stap 3: haal de stateToken uit de Okta-pagina
        match = re.search(r'"stateToken":"(.*?)","helpLinks"', response.text)
        if not match:
            match = re.search(r'"stateToken":"(.*?)"', response.text)
        if not match:
            raise BaseBelgiumApiError("Could not find stateToken in login page")
        state_token = match.group(1).encode("latin1").decode("unicode_escape")

        # Stap 4: introspect om de stateHandle te krijgen
        response = self._post_json(URL_INTROSPECT, {"stateToken": state_token})
        data = response.json()
        state_handle = data.get("stateHandle")
        if not state_handle:
            raise BaseBelgiumApiError("No stateHandle in introspect response")

        # Stap 5: apparaatvingerafdruk en nonce (voor de cookies)
        try:
            self.session.get(URL_FINGERPRINT, timeout=10)
            self.session.post(URL_DEVICE_NONCE, timeout=10)
        except Exception:
            _LOGGER.debug("Device fingerprint/nonce failed, continuing")

        # Stap 6: zoek de gebruikersnaam via de alias-lookup en identificeer de gebruiker
        actual_login = self._resolve_username(self.username)
        response = self._post_json(
            URL_IDENTIFY,
            {"identifier": actual_login, "stateHandle": state_handle},
        )
        data = response.json()
        state_handle = data.get("stateHandle", state_handle)

        # Stap 7: zoek de wachtwoord-authenticator
        password_id = None
        for auth in data.get("authenticators", {}).get("value", []):
            if auth.get("type") == "password":
                password_id = auth.get("id")
                break

        if not password_id:
            raise BaseBelgiumAuthError("No password authenticator found")

        # Stap 8: challenge met de wachtwoord-authenticator
        response = self._post_json(
            URL_CHALLENGE,
            {"authenticator": {"id": password_id}, "stateHandle": state_handle},
        )
        data = response.json()
        state_handle = data.get("stateHandle", state_handle)

        # Stap 9: verstuur het wachtwoord
        response = self._post_json(
            URL_CHALLENGE_ANSWER,
            {"credentials": {"passcode": self.password}, "stateHandle": state_handle},
        )
        data = response.json()

        if "messages" in data:
            messages = data["messages"].get("value", [])
            error_msgs = [m.get("message", "") for m in messages]
            raise BaseBelgiumAuthError(
                f"Authentication failed: {'; '.join(error_msgs)}"
            )

        # Stap 10: volg de doorverwijzing na succes om OAuth af te ronden
        success_href = data.get("success", {}).get("href")
        if not success_href:
            raise BaseBelgiumAuthError(
                "No success URL in authentication response"
            )
        self.session.get(success_href, timeout=30, allow_redirects=True)

        # Controleer de aanmelding. Het wachtwoord is hier al aanvaard: weigert
        # BASE toch de sessie (bv. tijdens onderhoud van My BASE), dan is dat een
        # tijdelijke fout en geen fout wachtwoord, zodat HA vanzelf opnieuw probeert.
        response = self.session.get(URL_USERDETAILS, timeout=30)
        if response.status_code != 200:
            self.session.cookies.clear()
            raise BaseBelgiumApiError(
                "Password accepted but My BASE refused the session "
                f"(status {response.status_code}); My BASE may be in maintenance"
            )

        # Zet de XSRF-token als die er is
        xsrf = self.session.cookies.get("TOKEN-XSRF")
        if xsrf:
            self.session.headers["X-TOKEN-XSRF"] = xsrf

        _LOGGER.debug("Successfully authenticated with BASE Belgium")

    def get_product_spec(self, specurl: str) -> dict:
        """Haal de productspecificatie op (datatarieven, inbegrepen diensten)."""
        try:
            url = specurl.replace("api.prd.telenet.be", "api.prd.base.be")
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                return response.json().get("product", {})
        except Exception as err:
            _LOGGER.debug("Failed to get product spec: %s", err)
        return {}

    def get_all_data(self, previous_data: dict | None = None) -> dict:
        """Haal alle mobiele gegevens op (abonnementen, verbruik en productspecificaties)."""
        self.login()
        prev = previous_data or {}
        result = {
            "subscriptions": prev.get("subscriptions", []),
            "usage": prev.get("usage", {}),
            "specs": prev.get("specs", {}),
        }

        # Haal de abonnementen op
        try:
            subs_response = self.session.get(
                URL_MOBILE_SUBS,
                params={"producttypes": "MOBILE"},
                timeout=30,
            )
            if subs_response.status_code == 200:
                result["subscriptions"] = subs_response.json()
            else:
                _LOGGER.warning("Failed to get subscriptions: %s", subs_response.status_code)
        except Exception as err:
            _LOGGER.warning("Failed to get subscriptions: %s", err)

        for sub in result["subscriptions"]:
            identifier = sub.get("identifier", "")
            if not identifier:
                continue

            # Haal het verbruik op
            try:
                url = f"{URL_MOBILE_USAGE}/{identifier}/usages"
                usage_response = self.session.get(url, timeout=30)
                if usage_response.status_code == 200:
                    result["usage"][identifier] = usage_response.json()
            except Exception as err:
                _LOGGER.warning("Failed to get usage for %s: %s", identifier, err)

            # Haal de productspecificatie op voor de berekening van het datatarief
            specurl = sub.get("specurl", "")
            if specurl and specurl not in result["specs"]:
                spec = self.get_product_spec(specurl)
                if spec:
                    result["specs"][specurl] = spec

        return result

    def close(self) -> None:
        """Sluit de sessie."""
        self.session.close()

    def _post_json(self, url: str, data: dict) -> requests.Response:
        """Stuur JSON-gegevens met POST naar een URL."""
        self.session.headers["Content-Type"] = "application/json;charset=UTF-8"
        response = self.session.post(url, data=json.dumps(data), timeout=30)
        return response
