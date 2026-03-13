"""API client for BASE Belgium."""
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
    """Base exception for API errors."""


class BaseBelgiumAuthError(BaseBelgiumApiError):
    """Authentication error."""


class BaseBelgiumApi:
    """API client for BASE Belgium."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the API client."""
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
        """Resolve phone number to Okta login via alias lookup."""
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
        """Authenticate with BASE Belgium via Okta IDX flow."""
        # Step 1: Check if already authenticated
        response = self.session.get(URL_USERDETAILS, timeout=30)
        if response.status_code == 200:
            _LOGGER.debug("Already authenticated")
            return
        if response.status_code != 401:
            raise BaseBelgiumApiError(
                f"Unexpected status from userdetails: {response.status_code}"
            )

        # Step 2: Get authorization page (follows redirects to Okta)
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

        # Step 3: Extract stateToken from Okta page
        match = re.search(r'"stateToken":"(.*?)","helpLinks"', response.text)
        if not match:
            match = re.search(r'"stateToken":"(.*?)"', response.text)
        if not match:
            raise BaseBelgiumApiError("Could not find stateToken in login page")
        state_token = match.group(1).encode("latin1").decode("unicode_escape")

        # Step 4: Introspect to get stateHandle
        response = self._post_json(URL_INTROSPECT, {"stateToken": state_token})
        data = response.json()
        state_handle = data.get("stateHandle")
        if not state_handle:
            raise BaseBelgiumApiError("No stateHandle in introspect response")

        # Step 5: Device fingerprint and nonce (for cookies)
        try:
            self.session.get(URL_FINGERPRINT, timeout=10)
            self.session.post(URL_DEVICE_NONCE, timeout=10)
        except Exception:
            _LOGGER.debug("Device fingerprint/nonce failed, continuing")

        # Step 6: Resolve username via alias lookup and identify user
        actual_login = self._resolve_username(self.username)
        response = self._post_json(
            URL_IDENTIFY,
            {"identifier": actual_login, "stateHandle": state_handle},
        )
        data = response.json()
        state_handle = data.get("stateHandle", state_handle)

        # Step 7: Find password authenticator
        password_id = None
        for auth in data.get("authenticators", {}).get("value", []):
            if auth.get("type") == "password":
                password_id = auth.get("id")
                break

        if not password_id:
            raise BaseBelgiumAuthError("No password authenticator found")

        # Step 8: Challenge with password authenticator
        response = self._post_json(
            URL_CHALLENGE,
            {"authenticator": {"id": password_id}, "stateHandle": state_handle},
        )
        data = response.json()
        state_handle = data.get("stateHandle", state_handle)

        # Step 9: Submit password
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

        # Step 10: Follow success redirect to complete OAuth
        success_href = data.get("success", {}).get("href")
        if not success_href:
            raise BaseBelgiumAuthError(
                "No success URL in authentication response"
            )
        self.session.get(success_href, timeout=30, allow_redirects=True)

        # Verify authentication
        response = self.session.get(URL_USERDETAILS, timeout=30)
        if response.status_code != 200:
            raise BaseBelgiumAuthError("Authentication verification failed")

        # Set XSRF token if available
        xsrf = self.session.cookies.get("TOKEN-XSRF")
        if xsrf:
            self.session.headers["X-TOKEN-XSRF"] = xsrf

        _LOGGER.debug("Successfully authenticated with BASE Belgium")

    def get_product_spec(self, specurl: str) -> dict:
        """Get product specification (data rates, included services)."""
        try:
            url = specurl.replace("api.prd.telenet.be", "api.prd.base.be")
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                return response.json().get("product", {})
        except Exception as err:
            _LOGGER.debug("Failed to get product spec: %s", err)
        return {}

    def get_all_data(self, previous_data: dict | None = None) -> dict:
        """Get all mobile data (subscriptions + usage + product specs)."""
        self.login()
        prev = previous_data or {}
        result = {
            "subscriptions": prev.get("subscriptions", []),
            "usage": prev.get("usage", {}),
            "specs": prev.get("specs", {}),
        }

        # Get subscriptions
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

            # Get usage
            try:
                url = f"{URL_MOBILE_USAGE}/{identifier}/usages"
                usage_response = self.session.get(url, timeout=30)
                if usage_response.status_code == 200:
                    result["usage"][identifier] = usage_response.json()
            except Exception as err:
                _LOGGER.warning("Failed to get usage for %s: %s", identifier, err)

            # Get product spec for data rate calculation
            specurl = sub.get("specurl", "")
            if specurl and specurl not in result["specs"]:
                spec = self.get_product_spec(specurl)
                if spec:
                    result["specs"][specurl] = spec

        return result

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def _post_json(self, url: str, data: dict) -> requests.Response:
        """POST JSON data to a URL."""
        self.session.headers["Content-Type"] = "application/json;charset=UTF-8"
        response = self.session.post(url, data=json.dumps(data), timeout=30)
        return response
