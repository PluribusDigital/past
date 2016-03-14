import unittest
import json
from unittest.mock import patch
from api import Server, app, DB
from api.models import Corpus, Document

class Test_DocumentCorpusDetail(unittest.TestCase):
    connArgs = {'database': 'pasp_test'}

    @classmethod
    def setUpClass(cls):
        cls.corpus_id = cls.addCorpus()
        cls.doc_id = cls.addDocument()

    def setUp(self):
        self.patcher = patch('api.endpoints.document_corpus_detail.DB')
        self.mockDB = self.patcher.start()
        self.mockDB.connection.return_value = DB.connection(**self.connArgs)

        self.target = app.test_client()
        assert(self.doc_id != 0)
        assert(self.corpus_id != 0)
        self.urlTemplate = Server.absoluteUrl('/document/{0}/corpus/{1}').format
        self.url = self.urlTemplate(self.doc_id, self.corpus_id)
        self.url404 = self.urlTemplate(0, 0)

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
    def addCorpus(cls, name='FOO'):
        with DB.connection(**cls.connArgs) as conn:
            store = Corpus(conn)
            return store.findOrAdd(name)['id']

    @classmethod
    def addDocument(cls):
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
        self.assertEqual(303, rv.status_code)

    def test_delete(self):
        rv = self.target.delete(self.url)
        self.assertEqual(204, rv.status_code)

    def test_delete_not_there(self):
        rv = self.target.delete(self.url404)
        self.assertEqual(404, rv.status_code)

    def test_put(self):
        rv = self.target.put(self.url, data={'a': '1'})
        self.assertEqual(405, rv.status_code)

    def test_post(self):
        rv = self.target.put(self.url, data={'a': '1'})
        self.assertEqual(405, rv.status_code)

if __name__ == '__main__':
    unittest.main()
