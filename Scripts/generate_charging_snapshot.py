#!/usr/bin/env python3
"""Refresh the bundled, open-licensed UK OCM location catalogue (no live data)."""
import argparse
import json
import os
import re
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBFIELDS = {
    'AddressInfo': ('Title', 'AddressLine1', 'AddressLine2', 'Town', 'Postcode', 'Latitude', 'Longitude'),
    'StatusType': ('IsOperational',), 'UsageType': ('Title',), 'OperatorInfo': ('Title',),
    'DataProvider': ('Title', 'License', 'IsOpenDataLicensed'),
    'Connections': ('ConnectionType', 'PowerKW', 'Quantity', 'Reference'),
}


def trim(record):
    result = {'ID': record['ID']}
    for field, keys in SUBFIELDS.items():
        value = record.get(field)
        if isinstance(value, dict):
            result[field] = {k: value[k] for k in keys if value.get(k) is not None}
        elif field == 'Connections' and isinstance(value, list):
            result[field] = [{k: ({'Title': c[k].get('Title')} if k == 'ConnectionType' else c[k])
                              for k in keys if c.get(k) is not None} for c in value]
    return result


def download(key):
    records = []
    last_id = 0
    for _ in range(100):
        query = urllib.parse.urlencode(dict(output='json', countrycode='GB', opendata='true',
            sortby='id_asc', greaterthanid=last_id, maxresults=5000, compact='false', verbose='false'))
        request = urllib.request.Request('https://api.openchargemap.io/v3/poi/?' + query,
            headers={'X-API-Key': key, 'User-Agent': 'FuelFinderProUK-Snapshot/1.0'})
        with urllib.request.urlopen(request, timeout=90) as response:
            page = json.load(response)
        if not isinstance(page, list):
            raise ValueError('Expected OCM record array')
        if not page:
            return records
        ids = [r['ID'] for r in page]
        if ids != sorted(set(ids)) or ids[0] <= last_id:
            raise ValueError('OCM pagination did not advance; previous snapshot preserved')
        if any(r.get('DataProvider', {}).get('IsOpenDataLicensed') is not True for r in page):
            raise ValueError('Record missing explicit open-data licence flag')
        records.extend(trim(r) for r in page)
        last_id = ids[-1]
        print(f'Downloaded {len(records)} open-licensed UK locations', flush=True)
        # Fetch until an empty page: a server-side page cap must not truncate the catalogue.
        time.sleep(1)
    raise ValueError('Pagination safety limit reached; previous snapshot preserved')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'FuelFinderProUK/Resources/charging_snapshot.json')
    args = parser.parse_args()
    key = os.environ.get('OPEN_CHARGE_MAP_API_KEY', '')
    if not key:
        config = (ROOT / 'Config/Secrets.xcconfig').read_text()
        match = re.search(r'^\s*OPEN_CHARGE_MAP_API_KEY\s*=\s*(.*?)\s*$', config, re.M)
        key = match.group(1).strip().strip('"') if match else ''
    if not key or key.startswith('$('):
        raise SystemExit('Configure OPEN_CHARGE_MAP_API_KEY first')
    records = download(key)
    if not records:
        raise ValueError('Empty catalogue; previous snapshot preserved')
    if args.output.exists():
        previous = json.loads(args.output.read_text())['records']
        if len(records) < len(previous) * 0.8:
            raise ValueError('Unexpected catalogue shrinkage; previous snapshot preserved')
    payload = dict(schemaVersion=1, downloadedAt=datetime.now(timezone.utc).isoformat(),
                   source='https://openchargemap.org', countryCode='GB', records=records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=args.output.parent, delete=False) as f:
        json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
        temp_path = Path(f.name)
    temp_path.replace(args.output)
    print(f'Saved {len(records)} records ({args.output.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()
