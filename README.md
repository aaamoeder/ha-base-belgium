## Doel
Home Assistant-integratie (HACS) die het dataverbruik, het resterende tegoed, de facturatieperiode en de kosten buiten de bundel van een BASE-abonnement (België) als sensoren toont, zodat je ze in dashboards en automatiseringen kan gebruiken.

<p align="center">
  <img src="https://raw.githubusercontent.com/aaamoeder/ha-base-belgium/main/brand/icon.png" alt="BASE Belgium voor Home Assistant" width="128">
</p>

<h1 align="center">BASE Belgium voor Home Assistant</h1>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge" alt="HACS Custom"></a>
  <a href="https://github.com/aaamoeder/ha-base-belgium/releases"><img src="https://img.shields.io/github/release/aaamoeder/ha-base-belgium.svg?style=for-the-badge" alt="GitHub Release"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="Licentie: MIT"></a>
</p>

<p align="center">
  Een Home Assistant-integratie voor klanten van <a href="https://www.base.be">BASE</a> met een mobiel abonnement.<br>
  Volg je dataverbruik, je resterende tegoed, je facturatieperiode en je kosten buiten de bundel rechtstreeks in je slimme woning.
</p>

---

<p align="center">
  <em>Heb je iets aan dit project? Trakteer me dan gerust op een koffie</em> ☕
</p>

<p align="center">
  <a href="https://buymeacoffee.com/aaamoeder">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="217">
  </a>
</p>

---

## Functies

| Functie | Beschrijving |
|---------|--------------|
| **Dataverbruik** | Totale, verbruikte en resterende data in GB |
| **Bedragen** | Verbruikt en resterend bedrag van de bundel in EUR |
| **Verbruikspercentage** | Hoeveel van je bundel al verbruikt is |
| **Data vandaag** | Dataverbruik per dag, telt om middernacht opnieuw vanaf nul |
| **Resterende dagen** | Aftellen tot de volgende factuurdatum |
| **Buiten bundel** | Extra kosten buiten je bundel |
| **Prepaid-tegoed** | Huidig tegoed van prepaid-simkaarten |
| **Meerdere simkaarten** | Ondersteunt meerdere telefoonnummers per account |
| **Diagnose** | Download diagnosegegevens vanaf de pagina van de integratie |

## Installatie

### HACS (aanbevolen)

1. Open **HACS** in Home Assistant
2. Klik rechtsboven op de **drie puntjes** en kies **Custom repositories**
3. Voeg deze repository toe:
   ```
   https://github.com/aaamoeder/ha-base-belgium
   ```
4. Kies als categorie **Integration** en klik op **Add**
5. Zoek **BASE Belgium** in HACS en klik op **Download**
6. **Herstart** Home Assistant

### Handmatige installatie

1. Download de [laatste release](https://github.com/aaamoeder/ha-base-belgium/releases/latest)
2. Kopieer de map `custom_components/base_belgium` naar je map `config/custom_components/`
3. Herstart Home Assistant

## Instellen

1. Ga naar **Instellingen** > **Apparaten en diensten** > **Integratie toevoegen**
2. Zoek **BASE Belgium**
3. Vul je gegevens in:

| Naam | Type | Verplicht | Beschrijving |
|------|------|-----------|--------------|
| `phone` | tekst | ja | Je BASE-telefoonnummer (bv. `0470123456`) of je e-mailadres |
| `password` | tekst | ja | Je wachtwoord van My BASE |

> De integratie ondersteunt **herauthenticatie**: lukt het aanmelden niet meer, dan vraagt Home Assistant je om je gegevens opnieuw in te vullen. Daar kan je ook overstappen van telefoonnummer naar e-mailadres. Via **Opnieuw configureren** kan je de login en het wachtwoord op elk moment wijzigen.

### Opties

Na het instellen kan je via **Instellingen** > **Apparaten en diensten** > **BASE Belgium** > **Configureren** het volgende wijzigen:

| Naam | Type | Verplicht | Standaard | Beschrijving |
|------|------|-----------|-----------|--------------|
| `scan_interval` | getal | nee | `240` | Hoe vaak de gegevens bij BASE opgehaald worden (in minuten, van 60 tot 1440) |

## Entiteiten

Elk telefoonnummer wordt een apparaat, met het nummer als serienummer. Een apparaat van een nummer dat niet meer in je account zit, kan je verwijderen via **Apparaten en diensten**.

### Sensoren voor een abonnement

| Sensor | Beschrijving | Eenheid |
|--------|--------------|---------|
| Verbruikt | Verbruikt bedrag van de bundel | EUR |
| Resterend | Resterend bedrag van de bundel | EUR |
| Verbruikspercentage | Percentage van de bundel dat verbruikt is | % |
| Data totaal | Totaal data-equivalent | GB |
| Data verbruikt | Verbruikt data-equivalent | GB |
| Data resterend | Resterend data-equivalent | GB |
| Data vandaag | Data verbruikt sinds middernacht | GB |
| Resterende dagen | Dagen tot de volgende factuurdatum | dagen |
| Buiten bundel | Extra kosten buiten de bundel | EUR |

### Sensoren voor prepaid

| Sensor | Beschrijving | Eenheid |
|--------|--------------|---------|
| Tegoed | Huidig prepaid-tegoed | EUR |
| Buiten bundel | Extra kosten buiten de bundel | EUR |

## Hoe het werkt

BASE heeft geen publieke API. De integratie meldt aan via dezelfde Okta-loginflow als de website van My BASE en haalt daarna het verbruik op bij de interne API.

- **Interval**: instelbaar, standaard 240 minuten (van 60 tot 1440 minuten)
- **Aanmelden**: enkel opnieuw als de sessiecookies verlopen zijn
- **Gegevens bewaren**: lukt een deel van het ophalen niet, dan blijven de vorige waarden staan, zodat sensoren niet wegvallen
- **Herauthenticatie**: bij een fout met de inloggegevens vraagt Home Assistant om opnieuw aan te melden

## Talen

| Taal | Status |
|------|--------|
| Nederlands | Volledig vertaald |
| Français | Volledig vertaald |
| Deutsch | Volledig vertaald |
| English | Volledig vertaald |

## Problemen oplossen

| Probleem | Oplossing |
|----------|-----------|
| De integratie laadt niet | Leeg de cache van je browser en herstart Home Assistant |
| Aanmelden mislukt | Controleer je gegevens en meld opnieuw aan via **Instellingen > Apparaten en diensten** |
| Sensoren tonen "onbekend" | Wacht tot de eerste keer gegevens opgehaald zijn (tot 4 uur) of kijk in de logboeken |
| Waarden lijken niet te kloppen | BASE werkt het verbruik met wat vertraging bij; kijk na de volgende ophaalronde opnieuw |
| Aanmelden mislukt nadat je My BASE op aanmelden met e-mail zette | Open de melding voor herauthenticatie (of **Opnieuw configureren**) en vervang het telefoonnummer door je e-mailadres |

## Status

Deze integratie is **uitgebracht** (huidige versie `1.1.1`) en wordt dagelijks gebruikt. Ze steunt op API's van BASE die niet gedocumenteerd zijn, dus een wijziging bij BASE kan ze zonder waarschuwing breken. Open in dat geval een issue.

## Disclaimer

Deze integratie is **niet verbonden met of goedgekeurd door BASE of Telenet**. Ze steunt op API's die niet gedocumenteerd zijn en kan dus stoppen met werken als BASE iets wijzigt. Gebruik op eigen risico.

## Licentie

[MIT-licentie](LICENSE), zie het bestand LICENSE.
