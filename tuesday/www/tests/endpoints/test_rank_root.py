import unittest
import json
from api import Server, app

class Test_RankRoot(unittest.TestCase):
    def setUp(self):
        self.target = app.test_client()
        self.url = Server.absoluteUrl('/rank')

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_get(self):
        rv = self.target.get(self.url)
        self.assertEqual(200, rv.status_code)

        results = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(3, len(results))
        for result in results:
            self.assertIn('title', result)
            self.assertIn('summary', result)
            self.assertIn('links', result)
            self.assertEqual(1, len(result['links']))
            self.assertIn('href', result['links'][0])
            self.assertIn('rank', result['links'][0]['href'])

    def test_delete(self):
        rv = self.target.delete(self.url)
        self.assertEqual(405, rv.status_code)

    def test_put(self):
        rv = self.target.put(self.url, data={'a': '1'})
        self.assertEqual(405, rv.status_code)

    def test_post(self):
        rv = self.target.post(self.url, data={'a': '1'})
        self.assertEqual(405, rv.status_code)

if __name__ == '__main__':
    unittest.main()
