import unittest
import json
from api import Server, app

class Test_Root(unittest.TestCase):
    def setUp(self):
        self.target = app.test_client()
        self.url = Server.absoluteUrl('/')

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_get(self):
        rv = self.target.get(self.url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(3, len(result))
        for i, ep in enumerate(['corpus', 'document', 'rank']):
            self.assertIn('title', result[i])
            self.assertIn('summary', result[i])
            self.assertIn('links', result[i])
            self.assertEqual(1, len(result[i]['links']))
            self.assertIn('href', result[i]['links'][0])
            self.assertIn(ep, result[i]['links'][0]['href'])

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
