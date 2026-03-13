<p align="center">
  <img src="https://raw.githubusercontent.com/aaamoeder/ha-base-belgium/main/brand/icon.png" alt="BASE Belgium for Home Assistant" width="128">
</p>

<h1 align="center">BASE Belgium for Home Assistant</h1>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge" alt="HACS Custom"></a>
  <a href="https://github.com/aaamoeder/ha-base-belgium/releases"><img src="https://img.shields.io/github/release/aaamoeder/ha-base-belgium.svg?style=for-the-badge" alt="GitHub Release"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License: MIT"></a>
</p>

<p align="center">
  A Home Assistant custom integration for <a href="https://www.base.be">BASE Belgium</a> mobile subscribers.<br>
  Track your mobile data usage, remaining credit, billing cycle and out-of-bundle costs directly in your smart home.
</p>

---

## Features

| Feature | Description |
|---------|-------------|
| **Data usage** | Total, used and remaining data in GB |
| **Monetary tracking** | Used and remaining allowance in EUR |
| **Usage percentage** | How much of your bundle you've consumed |
| **Data today** | Daily data usage tracking with automatic midnight reset |
| **Days remaining** | Countdown to next billing date |
| **Out of bundle** | Extra costs outside your bundle |
| **Prepaid credit** | Current credit balance for prepaid SIMs |
| **Multi-SIM** | Supports multiple phone numbers per account |
| **Diagnostics** | Download debug data from the integration page |

## Installation

### HACS (Recommended)

1. Open **HACS** in your Home Assistant instance
2. Click the **three dots** menu (top right) and select **Custom repositories**
3. Add this repository URL:
   ```
   https://github.com/aaamoeder/ha-base-belgium
   ```
4. Set the category to **Integration** and click **Add**
5. Find **BASE Belgium** in the HACS store and click **Install**
6. **Restart** Home Assistant

### Manual installation

1. Download the [latest release](https://github.com/aaamoeder/ha-base-belgium/releases/latest)
2. Copy the `custom_components/base_belgium` folder to your `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **BASE Belgium**
3. Enter your credentials:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `phone` | string | yes | Your BASE Belgium phone number (e.g. `0470123456`) or email |
| `password` | string | yes | Your BASE Belgium / My BASE password |

> The integration supports **re-authentication** — if your session expires, Home Assistant will prompt you to re-enter your credentials.

### Options

After setup, go to **Settings** > **Devices & Services** > **BASE Belgium** > **Configure** to change:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `scan_interval` | number | no | `240` | How often to fetch data from BASE (minutes, range: 60–1440) |

## Entities

### Postpaid sensors

| Sensor | Description | Unit |
|--------|-------------|------|
| Used | Monetary allowance consumed | EUR |
| Remaining | Monetary allowance left | EUR |
| Usage percentage | Percentage of bundle used | % |
| Data total | Total data equivalent | GB |
| Data used | Data equivalent consumed | GB |
| Data remaining | Data equivalent left | GB |
| Data today | Data used since midnight | GB |
| Days remaining | Days until next billing date | days |
| Out of bundle | Extra costs outside bundle | EUR |

### Prepaid sensors

| Sensor | Description | Unit |
|--------|-------------|------|
| Credit | Current prepaid credit balance | EUR |
| Out of bundle | Extra costs outside bundle | EUR |

## How it works

BASE Belgium does not provide a public API. This integration authenticates via the same Okta Identity Engine flow used by the My BASE website, then fetches usage data from their internal API.

- **Polling interval**: configurable, default 240 minutes (range: 60–1440 minutes)
- **Authentication**: lazy login — only authenticates when session cookies expire
- **Data preservation**: on partial failure, retains previous data to prevent sensor dropouts
- **Re-auth flow**: triggers HA re-authentication prompt on credential failures

## Supported languages

| Language | Status |
|----------|--------|
| English | Fully translated |
| Nederlands | Fully translated |
| Fran&ccedil;ais | Fully translated |
| Deutsch | Fully translated |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Integration not loading | Clear browser cache and restart HA |
| Authentication failed | Check credentials, re-authenticate via **Settings > Integrations** |
| Sensors showing "unknown" | Wait for the first data fetch (up to 4 hours) or check logs for errors |
| Data values seem wrong | BASE updates usage data with some delay; check again after next poll |

## Disclaimer

This integration is **not affiliated with or endorsed by BASE or Telenet**. It relies on undocumented APIs, which means it may break if BASE changes their systems. Use at your own risk.

## License

[MIT License](LICENSE) — see LICENSE file for details.
