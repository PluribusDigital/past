import unittest
import json
from unittest.mock import patch
from api import Server, app, DB
from api.models import Corpus, Document

class Test_CorpusDocumentIndex(unittest.TestCase):
    connArgs = {'database': 'pasp_test'}

    @classmethod
    def setUpClass(cls):
        cls.cor_id = cls.addRecord()
        cls.addDocuments()

    def setUp(self):
        self.patcher = patch('api.endpoints.corpus_document_index.DB')
        self.mockDB = self.patcher.start()
        self.mockDB.connection.return_value = DB.connection(**self.connArgs)

        self.target = app.test_client()
        assert(self.cor_id != 0)
        self.url = Server.absoluteUrl('/corpus/{0}/document'.format(self.cor_id))
        self.url404 = Server.absoluteUrl('/corpus/0/document')

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
    def addRecord(cls, name='FOO'):
        with DB.connection(**cls.connArgs) as conn:
            store = Corpus(conn)
            return store.findOrAdd(name)['id']

    @classmethod
    def addDocuments(cls):
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
            for i in range(3):
                clone = dict(document)
                clone['title'] = 'Document {0}'.format(i + 1)
                store.add(clone, 'FOO', 'BAR')

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_get(self):
        rv = self.target.get(self.url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(3, len(result))
        for row in result:
            self.assertIn(row['title'], ['Document 1', 
                                         'Document 2', 
                                         'Document 3'])
            self.assertEqual(4, len(row['links']))

    def test_get_not_exist(self):
        rv = self.target.get(self.url404)
        self.assertEqual(404, rv.status_code)

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
