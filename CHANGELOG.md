# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-11-20

### 🎉 Release
- First stable release since 1.0.0. The code is identical to 1.1.0-alpha.1 and includes everything since 1.0.0: switch login between phone number and email (re-authentication and Reconfigure), masked password field with autocomplete hints, removal of devices whose number left the account, and the phone number as device serial number.

### 📝 Documentation
- README status updated to released, and a troubleshooting entry for switching to email login.

## [1.1.0-alpha.1] - 2026-11-20

### 🔧 Changed
- Version numbering continues from the published 1.0.0 release, so HACS and Semantic Versioning order this pre-release above 1.0.0. The code is identical to 1.0.0-alpha.6, which contains all changes since 1.0.0: reconfigure step, login field in re-authentication, masked password field, removal of stale devices and the phone number as device serial number.

## [1.0.0-alpha.6] - 2026-11-20

### 🎨 Improved
- Each device now shows its phone number as serial number on the device page, so devices with a custom name can still be matched to their SIM.

## [1.0.0-alpha.5] - 2026-11-20

### ✨ Added
- Devices can be removed from Settings > Devices & services when their number is no longer part of the BASE account (for example after cancelling a number). Devices of active numbers stay protected.

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
