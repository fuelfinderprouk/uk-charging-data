# UK charging location data

Open-licensed UK charging location snapshots used by Fuel Finder Pro UK. This
repository contains public location data and its collector, not the app source.

`charging_snapshot.json` contains OCM location IDs, addresses, coordinates,
connector types, rated power where supplied, access metadata and source credits.
It is a dated catalogue, not live availability or pricing. It does not claim to
contain every UK charger. GB is OCM's country code for the United Kingdom,
including Northern Ireland.

## Monthly refresh

GitHub Actions requests a refresh at 03:17 UTC on the first day of each month.
Scheduled runs may be delayed by GitHub. Manual workflow dispatch is also
available. Set the encrypted repository Actions secret `OPEN_CHARGE_MAP_API_KEY`
to an OCM application key. Credentials must never be committed to this repo.

The collector fetches open-licensed records in ID order until the API returns
an empty page. Incomplete or invalid downloads leave the previous snapshot
unchanged. The app validates downloads and keeps its last good local copy.

## Attribution and licensing

Source: [Open Charge Map](https://openchargemap.org/develop/), plus the original
providers named in each record's `DataProvider` object. Each record retains its
provider title and licence text. Data remains under its respective provider
licence; this repository does not relicense third-party data. Consumers must
retain the applicable attribution and licence conditions.

Original listings: `https://openchargemap.org/site/poi/details/{ID}`.
Export API: <https://openchargemap.org/develop/api>.

The snapshot is available at:
<https://raw.githubusercontent.com/fuelfinderprouk/uk-charging-data/main/charging_snapshot.json>
