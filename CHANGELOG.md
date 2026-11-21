# Wijzigingen

Alle noemenswaardige wijzigingen aan dit project staan in dit bestand.
De opmaak volgt [Keep a Changelog](https://keepachangelog.com/nl/1.1.0/) en het project gebruikt [Semantic Versioning](https://semver.org/lang/nl/).

## [1.1.1] - 2026-11-21

### 📝 Documentatie
- README, CHANGELOG en release-notities staan nu in het Nederlands, want de integratie is enkel bedoeld voor klanten van BASE in België. De README beschrijft nu ook het overstappen naar aanmelden met e-mail, Opnieuw configureren en het verwijderen van apparaten.

### 🔧 Gewijzigd
- Commentaar en docstrings in de code zijn in het Nederlands. De werking is ongewijzigd; namen in de code en logmeldingen blijven Engels, en de schermen in Home Assistant blijven vertaald in het Nederlands, Frans, Duits en Engels.

## [1.1.0] - 2026-11-20

### 🎉 Release
- Eerste stabiele release sinds 1.0.0. De code is gelijk aan 1.1.0-alpha.1 en bevat alles sinds 1.0.0: de login wisselen tussen telefoonnummer en e-mail (herauthenticatie en Opnieuw configureren), een gemaskeerd wachtwoordveld met autocomplete-hints, apparaten verwijderen waarvan het nummer niet meer in het account zit, en het telefoonnummer als serienummer van het apparaat.

### 📝 Documentatie
- De status in de README staat op uitgebracht, en er is een regel bij Problemen oplossen voor de overstap naar aanmelden met e-mail.

## [1.1.0-alpha.1] - 2026-11-20

### 🔧 Gewijzigd
- De versienummering gaat verder vanaf de gepubliceerde release 1.0.0, zodat HACS en Semantic Versioning deze pre-release boven 1.0.0 plaatsen. De code is gelijk aan 1.0.0-alpha.6, met alle wijzigingen sinds 1.0.0: de stap Opnieuw configureren, het loginveld bij herauthenticatie, het gemaskeerde wachtwoordveld, het verwijderen van verouderde apparaten en het telefoonnummer als serienummer.

## [1.0.0-alpha.6] - 2026-11-20

### 🎨 Verbeterd
- Elk apparaat toont zijn telefoonnummer als serienummer op de apparaatpagina, zodat je apparaten met een eigen naam nog altijd aan hun simkaart kan koppelen.

## [1.0.0-alpha.5] - 2026-11-20

### ✨ Toegevoegd
- Apparaten kunnen verwijderd worden via Instellingen > Apparaten en diensten als hun nummer niet meer in het BASE-account zit (bijvoorbeeld na het opzeggen van een nummer). Apparaten van actieve nummers blijven beschermd.

## [1.0.0-alpha.4] - 2026-11-20

### 🔒 Beveiliging
- Het wachtwoordveld is nu gemaskeerd in alle formulieren (toevoegen, herauthenticeren, opnieuw configureren). Voordien stond het wachtwoord leesbaar in beeld tijdens het typen.

### 🎨 Verbeterd
- De velden voor login en wachtwoord dragen de autocomplete-hints `username` en `current-password`, zodat de wachtwoordbeheerder van de browser de gegevens kan aanbieden en bewaren.

## [1.0.0-alpha.3] - 2026-11-20

### 🎨 Verbeterd
- Herauthenticatie toont nu ook het loginveld (telefoonnummer of e-mail), vooraf ingevuld met de huidige login. De knop in de melding van Home Assistant volstaat om naar een nieuwe login over te stappen; Opnieuw configureren is niet langer de enige weg.

### 🌍 Vertalingen
- Bijgewerkte teksten voor herauthenticatie in het Engels, Nederlands, Frans en Duits.

## [1.0.0-alpha.2] - 2026-11-20

### ✨ Toegevoegd
- Stap Opnieuw configureren: wijzig de login (telefoonnummer of e-mail) en het wachtwoord van een bestaande entry via Instellingen > Apparaten en diensten, zonder de integratie te verwijderen.

### 🐛 Opgelost
- Een entry die met een telefoonnummer aangemaakt was, kon niet herstellen nadat het My BASE-account naar aanmelden met e-mail overstapte: herauthenticatie vroeg enkel een nieuw wachtwoord en hield de oude login met telefoonnummer.

### 🌍 Vertalingen
- Teksten voor Opnieuw configureren in het Engels, Nederlands, Frans en Duits. De tekst bij herauthenticatie verwijst naar Opnieuw configureren als de login zelf gewijzigd is.

### 🔧 Gewijzigd
- `hacs.json` vermeldt nu Home Assistant 2024.11.0 als minimale versie (nodig voor de hulpfuncties van Opnieuw configureren).

## [1.0.0-alpha.1]

- Eerste alpharelease.
