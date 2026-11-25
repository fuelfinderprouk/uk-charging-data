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

## char.gy catalogue

`chargy-locations.json` is collected from char.gy's separate official UK PCPR
open-data feed. It is not OCM data or app source. Attribute char.gy and retain
its source/update information; the original provider's data terms apply.
Official documentation:
<https://help.char.gy/support/solutions/articles/77000576948-public-charge-point-regulations-2023>.

The `chargy.yml` workflow runs daily at 04:43 UTC, with manual dispatch also
available. The source caps pages at 50, so the collector pauses six seconds
between requests. It requires a complete successful collection, checks IDs
and totals, excludes non-public/non-UK records and preserves the previous
file on errors. The first complete publication was verified on 25 November
2026: 6,134 public UK location records and 6,136 EVSE records.

No API key is required. This is a dated metadata snapshot, not live socket
availability: source states such as WORKING and FAULTED must not be interpreted
as current occupied/free counts. Tariffs are not included; app clients retrieve
the separate official tariff feed and retain its qualifications and unknowns.

The snapshot is available at:
<https://raw.githubusercontent.com/fuelfinderprouk/uk-charging-data/main/charging_snapshot.json>
