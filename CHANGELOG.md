# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0-alpha.4] - 2026-11-20

### 🔒 Security
- The password field is now masked in all forms (add, re-authenticate, reconfigure). Before, the password was shown as plain text while typing.

### 🎨 Improved
- Login and password fields carry `username` and `current-password` autocomplete hints, so the browser password manager can offer and save the credentials.

## [1.0.0-alpha.3] - 2026-11-20

### 🎨 Improved
- Re-authentication now also shows the login field (phone number or email), prefilled with the current login. The "Re-authenticate" button in the Home Assistant notification is enough to switch to a new login; Reconfigure is no longer the only way.

### 🌍 Translations
- Updated re-authentication texts in English, Dutch, French and German.

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
