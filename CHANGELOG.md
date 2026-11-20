# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0-alpha.2] - 2026-11-20

### ✨ Added
- Reconfigure step: change the login (phone number or email) and password of an existing entry from Settings > Devices & services, without removing the integration.

### 🐛 Fixed
- An entry created with a phone number could not recover after the My BASE account moved to email login: re-authentication only asked for a new password and kept the old phone number login.

### 🌍 Translations
- Reconfigure texts in English, Dutch, French and German. The re-authentication text now points to Reconfigure when the login itself changed.

### 🔧 Changed
- `hacs.json` now declares Home Assistant 2024.11.0 as minimum version (needed for the reconfigure helpers).

## [1.0.0-alpha.1]

- First alpha release.
