import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('chargy', Path(__file__).parents[1] / 'generate_chargy_catalogue.py')
chargy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chargy)


class Response(io.BytesIO):
    def __init__(self, rows, total, status=1000):
        super().__init__(json.dumps({'data': rows, 'status_code': status}).encode())
        self.headers = {'X-Total-Count': str(total)}


class CollectorTests(unittest.TestCase):
    def testFollowsActualPageLengthUntilFullTotal(self):
        pages = [Response([{'id': 'a', 'country_code': 'GB', 'party_id': 'CGY'}], 2),
                 Response([{'id': 'b', 'country_code': 'GB', 'party_id': 'CGY'}], 2)]
        with patch.object(chargy.urllib.request, 'urlopen', side_effect=pages) as request, patch.object(chargy.time, 'sleep'):
            self.assertEqual(len(chargy.collect()), 2)
            self.assertIn('offset=1', request.call_args_list[-1].args[0].full_url)

    def testDuplicateAndChangingTotalsAreRejected(self):
        row = {'id': 'a', 'country_code': 'GB', 'party_id': 'CGY'}
        for pages in [[Response([row], 2), Response([row], 2)], [Response([row], 2), Response([], 3)]]:
            with patch.object(chargy.urllib.request, 'urlopen', side_effect=pages), patch.object(chargy.time, 'sleep'):
                with self.assertRaises(ValueError):
                    chargy.collect()

    def testBadCollectionDoesNotOverwritePreviousSnapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'catalogue.json'
            output.write_text('{"locations":[]}')
            with self.assertRaises(ValueError):
                chargy.write_catalogue([], output)
            self.assertEqual(output.read_text(), '{"locations":[]}')

    def testPublishedSnapshotExcludesNonPublicAndForeignRecords(self):
        rows = [{'id': str(i), 'country_code': 'GB', 'party_id': 'CGY', 'country': 'GBR', 'publish': True} for i in range(1_000)]
        rows += [dict(rows[0], id='private', publish=False), dict(rows[0], id='foreign', country='IRL')]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'catalogue.json'
            chargy.write_catalogue(rows, output)
            saved = json.loads(output.read_text())
            self.assertEqual(len(saved['locations']), 1_000)
            self.assertEqual(saved['sourceRecordCount'], 1_002)


if __name__ == '__main__':
    unittest.main()
