import unittest
import json
from unittest.mock import patch
from api import Server, app, DB
from api.models import Corpus

class Test_CorpusDetail(unittest.TestCase):
    connArgs = {'database': 'pasp_test'}
    cor_id = 0

    @classmethod
    def setUpClass(cls):
        cls.cor_id = cls.addRecord()

    def setUp(self):
        self.patcher = patch('api.endpoints.corpus_detail.DB')
        self.mockDB = self.patcher.start()
        self.mockDB.connection.return_value = DB.connection(**self.connArgs)

        self.target = app.test_client()
        assert(self.cor_id != 0)
        self.url = Server.absoluteUrl('/corpus/{0}'.format(self.cor_id))
        self.url404 = Server.absoluteUrl('/corpus/0')

    def tearDown(self):
        self.patcher.stop()

    @classmethod
    def tearDownClass(cls):
        sql = "DELETE FROM corpus WHERE id > 1;"
        
        with DB.connection(**cls.connArgs) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    @classmethod
    def addRecord(cls, name='FOO'):
        with DB.connection(**cls.connArgs) as conn:
            store = Corpus(conn)
            return store.findOrAdd(name)['id']

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_get(self):
        rv = self.target.get(self.url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(self.cor_id, result['id'])
        self.assertEqual('foo', result['name'])

    def test_get_not_found(self):
        rv = self.target.get(self.url404)
        self.assertEqual(404, rv.status_code)

    def test_delete(self):
        id = self.addRecord('BAR')
        url = Server.absoluteUrl('/corpus/{0}'.format(id))

        rv = self.target.delete(url)
        self.assertEqual(204, rv.status_code)

    def test_delete_not_found(self):
        rv = self.target.delete(self.url404)
        self.assertEqual(404, rv.status_code)

    def test_put(self):
        id = self.addRecord('BAZ')
        url = Server.absoluteUrl('/corpus/{0}'.format(id))
        data = {'name': 'CHARLIE'}

        rv = self.target.put(url, data=json.dumps(data))
        self.assertEqual(204, rv.status_code)

        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual('charlie', result['name'])

    def test_put_collision(self):
        data = {'name': 'FOO'}
        rv = self.target.put(self.url, data=json.dumps(data))
        self.assertEqual(409, rv.status_code)

    def test_put_not_found(self):
        data = {'name': 'FLOO'}
        rv = self.target.put(self.url404, data=json.dumps(data))
        self.assertEqual(404, rv.status_code)

    def test_put_bad_format_1(self):
        rv = self.target.put(self.url, data={'a': '1'})
        self.assertEqual(400, rv.status_code)

    def test_put_bad_format_2(self):
        data = {'a': '1'}
        rv = self.target.put(self.url, data=json.dumps(data))
        self.assertEqual(400, rv.status_code)

    def test_post(self):
        rv = self.target.post(self.url, data={'a': '1'})
        self.assertEqual(405, rv.status_code)

if __name__ == '__main__':
    unittest.main()
