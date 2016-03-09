import unittest
import json
from unittest.mock import patch
from api import Server, app, DB
from api.models import Corpus

class Test_CorpusIndex(unittest.TestCase):
    connArgs = {'database': 'pasp_test'}

    @classmethod
    def setUpClass(cls):
        with DB.connection(**cls.connArgs) as conn:
            store = Corpus(conn)
            for i in range(3):
                store.findOrAdd(str(i))

    def setUp(self):
        self.patcher = patch('api.endpoints.corpus_index.DB')
        self.mockDB = self.patcher.start()
        self.mockDB.connection.return_value = DB.connection(**self.connArgs)

        self.target = app.test_client()
        self.url = Server.absoluteUrl('/corpus')

    def tearDown(self):
        self.patcher.stop()

    @classmethod
    def tearDownClass(cls):
        sql = "DELETE FROM corpus WHERE id > 1"
        
        with DB.connection(**cls.connArgs) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_get(self):
        rv = self.target.get(self.url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(3, len(result))

    def test_get_limit(self):
        url = self.url + '?limit=1'
        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(1, len(result))
        self.assertEqual('0', result[0]['title'])

    def test_get_offset(self):
        url = self.url + '?offset=1'
        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(2, len(result))
        self.assertEqual('1', result[0]['title'])

    def test_get_limit_offset(self):
        url = self.url + '?limit=1&offset=1'
        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(1, len(result))
        self.assertEqual('1', result[0]['title'])

    def test_delete(self):
        rv = self.target.delete(self.url)
        self.assertEqual(405, rv.status_code)

    def test_put(self):
        rv = self.target.put(self.url, data={'a': '1'})
        self.assertEqual(405, rv.status_code)

    def test_post(self):
        data = {'name': 'BAZ'}
        rv = self.target.post(self.url, data=json.dumps(data))
        self.assertEqual(201, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual('baz', result['title'])

    def test_post_bad_format(self):
        data = {'foo': 'bar'}
        rv = self.target.post(self.url, data=json.dumps(data))
        self.assertEqual(400, rv.status_code)

    def test_post_collision(self):
        data = {'name': '1'}
        rv = self.target.post(self.url, data=json.dumps(data))
        self.assertEqual(409, rv.status_code)

if __name__ == '__main__':
    unittest.main()
