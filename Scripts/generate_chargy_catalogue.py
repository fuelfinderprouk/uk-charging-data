#!/usr/bin/env python3
"""Collect the official char.gy location feed once centrally, not on every phone."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import time
import urllib.request


def collect():
    rows = []
    total = None
    seen = set()
    for _ in range(400):
        url = f'https://char.gy/open-ocpi/locations?limit=50&offset={len(rows)}'
        request = urllib.request.Request(url, headers={'User-Agent': 'FuelFinderProUK-Catalogue/1.0'})
        with urllib.request.urlopen(request, timeout=60) as response:
            page = json.load(response)
            expected = int(response.headers['X-Total-Count'])
        if page.get('status_code') != 1000 or not isinstance(page.get('data'), list):
            raise ValueError('Unsuccessful OCPI page')
        if total is not None and total != expected:
            raise ValueError('Catalogue count changed during collection; keep previous file')
        total = expected
        for row in page['data']:
            identity = (row.get('country_code'), row.get('party_id'), row.get('id'))
            if not all(identity) or identity in seen:
                raise ValueError('Missing or repeated location identity')
            seen.add(identity)
        rows.extend(page['data'])
        print(f'char.gy: {len(rows)}/{total} locations', flush=True)
        if len(rows) == total:
            return rows
        if not page['data'] or len(rows) > total:
            raise ValueError('Incomplete or overfull catalogue')
        # The official endpoint caps pages at 50. Keep this central crawl gentle.
        # HTTP failures (including 403/429) stop the run; never publish a partial file.
        time.sleep(2)
    raise ValueError('Catalogue exceeds pagination safety limit')


def write_catalogue(rows, output):
    if len(rows) < 1_000:
        raise ValueError('Unexpectedly small catalogue')
    if any(r.get('country_code') != 'GB' or r.get('party_id') != 'CGY' for r in rows):
        raise ValueError('Unexpected operator identity')
    source_count = len(rows)
    rows = [r for r in rows if r.get('publish') is not False and r.get('country') in ('GB', 'GBR')]
    if len(rows) < 1_000:
        raise ValueError('Unexpectedly small published UK catalogue')
    if output.exists():
        previous = json.loads(output.read_text())['locations']
        if len(rows) < len(previous) * 0.8:
            raise ValueError('Unexpected catalogue shrinkage; keep previous file')
    payload = dict(schemaVersion=1, countryCode='GB',
                   downloadedAt=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                   source='https://char.gy/open-ocpi/locations', sourceRecordCount=source_count, locations=rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=output.parent, delete=False) as file:
        json.dump(payload, file, ensure_ascii=False, separators=(',', ':'))
        temporary = Path(file.name)
    temporary.replace(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    write_catalogue(collect(), args.output)


if __name__ == '__main__':
    main()
