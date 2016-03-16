import unittest
import json
from unittest.mock import patch
from api import Server, app, DB
from api.models import Corpus, Document

class Test_DocumentCorpusIndex(unittest.TestCase):
    connArgs = {'database': 'pasp_test'}

    @classmethod
    def setUpClass(cls):
        cls.doc_id = cls.addRecord()
        with DB.connection(**cls.connArgs) as conn:
            store = Corpus(conn)
            for i in range(3):
                store.findOrAdd(str(i))

    def setUp(self):
        self.patcher = patch('api.endpoints.document_corpus_index.DB')
        self.mockDB = self.patcher.start()
        self.mockDB.connection.return_value = DB.connection(**self.connArgs)

        self.target = app.test_client()
        assert(self.doc_id != 0)
        self.urlTemplate = Server.absoluteUrl('/document/{0}/corpus').format
        self.url = self.urlTemplate(self.doc_id)
        self.url404 = self.urlTemplate(0)

    def tearDown(self):
        self.patcher.stop()

    @classmethod
    def tearDownClass(cls):
        sqls = ["DELETE FROM corpus WHERE id > 1",
                "DELETE FROM document"]
        
        with DB.connection(**cls.connArgs) as conn:
            with conn.cursor() as cur:
                for sql in sqls:
                    cur.execute(sql)

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    @classmethod
    def addRecord(cls):
        document = {
                    'hash' : '1234567890', 
                    'path' : '/root/details.docx',
                    'date_created' : '1999-01-01',
                    'title' : 'The document',
                    'authors' : 'John Doe',
                    'tokenizer' : 'tok',
                    'tagger' : 'tag',
                    'lemmatizer' : 'lem',
                    'stemmer' : 'stem',
                    'syntaxer' : 'syntax',
                    'type': 'Patent'
                    }
        with DB.connection(**cls.connArgs) as conn:
            store = Document(conn)
            return store.add(document, 'FOO', 'BAR')

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_get(self):
        rv = self.target.get(self.url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(2, len(result))
        for row in result:
            self.assertIn(row['title'], ['foo', 'bar'])
            self.assertEqual(3, len(row['links']))

    def test_get_not_exist(self):
        rv = self.target.get(self.url404)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(0, len(result))

    def test_delete(self):
        rv = self.target.delete(self.url)
        self.assertEqual(405, rv.status_code)

    def test_put(self):
        rv = self.target.put(self.url, data={'a': '1'})
        self.assertEqual(405, rv.status_code)

    def test_post_new_corpus(self):
        id = self.addRecord()
        url = self.urlTemplate(id)
        data = {'name': 'BAZ'}

        rv = self.target.post(url, data=json.dumps(data))
        self.assertEqual(201, rv.status_code)

        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(3, len(result))
        for row in result:
            self.assertIn(row['title'], ['foo', 'bar', 'baz'])
            self.assertEqual(3, len(row['links']))

    def test_post_existing_corpus(self):
        id = self.addRecord()
        url = self.urlTemplate(id)
        data = {'name': '1'}

        rv = self.target.post(url, data=json.dumps(data))
        self.assertEqual(201, rv.status_code)

        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(3, len(result))
        for row in result:
            self.assertIn(row['title'], ['foo', 'bar', '1'])
            self.assertEqual(3, len(row['links']))

    def test_post_existing_link(self):
        data = {'name': 'foo'}
        rv = self.target.post(self.url, data=json.dumps(data))
        self.assertEqual(201, rv.status_code)
        self.test_get()

    def test_post_bad_format(self):
        data = {'foo': 'bar'}
        rv = self.target.post(self.url, data=json.dumps(data))
        self.assertEqual(400, rv.status_code)

    def test_post_doc_not_exist(self):
        data = {'name': '1'}
        rv = self.target.post(self.url404, data=json.dumps(data))
        self.assertEqual(404, rv.status_code)

if __name__ == '__main__':
    unittest.main()
