# UK charging location data

Open-licensed UK charging location snapshots used by Fuel Finder Pro UK. This repository contains public location data and its collector, not the app source.

The monthly snapshot contains OCM location IDs, addresses, coordinates, connector types, rated power where supplied, access metadata and source credits. It is a dated catalogue, not live availability or pricing, and does not claim every UK charger. GB includes Northern Ireland.

## Attribution and licensing

Source: [Open Charge Map](https://openchargemap.org/develop/), plus the original providers named in each record's DataProvider object. Each record retains its provider title and licence text. Data remains under its respective provider licence; this repository does not relicense third-party data. Consumers must retain the applicable attribution and licence conditions.

Original listings: https://openchargemap.org/site/poi/details/{ID}

## Monthly refresh

The workflow requests an update at 03:17 UTC on the first of each month. GitHub may delay scheduled runs. Set the encrypted Actions secret OPEN_CHARGE_MAP_API_KEY before running it. Never commit credentials. Invalid or incomplete downloads leave the previous snapshot unchanged.

Download: https://raw.githubusercontent.com/fuelfinderprouk/uk-charging-data/main/charging_snapshot.json
