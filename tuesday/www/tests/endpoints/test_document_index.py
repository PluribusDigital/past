import unittest
import json
from unittest.mock import patch
from api import Server, app, DB
from api.models import Document

class TestDocumentIndex(unittest.TestCase):
    connArgs = {'database': 'pasp_test'}

    @classmethod
    def setUpClass(cls):
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
        b = dict(document)
        b['title'] = 'Delorean Time Machine'
        b['authors'] = 'Brown, Doc; McFly, Marty Jr.'
        b['path'] = '/patent/9898'

        c = dict(document)
        c['title'] = 'Railroad Time Machine'
        c['authors'] = 'Brown, Doc; Brown, Clara'
        c['path'] = '/patent/7676'

        documents = [document, b, c]
        with DB.connection(**cls.connArgs) as conn:
            store = Document(conn)
            for i, doc in enumerate(documents):
                store.add(doc)

    def setUp(self):
        self.patcher = patch('api.endpoints.document_index.DB')
        self.mockDB = self.patcher.start()
        self.mockDB.connection.return_value = DB.connection(**self.connArgs)

        self.target = app.test_client()
        self.url = Server.absoluteUrl('/document')

    def tearDown(self):
        self.patcher.stop()

    @classmethod
    def tearDownClass(cls):
        sql = "DELETE FROM document WHERE tokenizer = %s;"
        
        with DB.connection(**cls.connArgs) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, ('tok',))

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
        self.assertEqual('The document', result[0]['title'])

    def test_get_offset(self):
        url = self.url + '?offset=1'
        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(2, len(result))
        self.assertEqual('Delorean Time Machine', result[0]['title'])

    def test_get_limit_offset(self):
        url = self.url + '?limit=1&offset=1'
        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(1, len(result))
        self.assertEqual('Delorean Time Machine', result[0]['title'])

    def test_get_filter_title(self):
        url = self.url + '?filter=delorean'
        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(1, len(result))
        self.assertEqual('Delorean Time Machine', result[0]['title'])

    def test_get_filter_author(self):
        url = self.url + '?filter=brown'
        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(2, len(result))
        self.assertEqual('Delorean Time Machine', result[0]['title'])

    def test_get_filter_patent_number(self):
        url = self.url + '?filter=9898'
        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(1, len(result))
        self.assertEqual('Delorean Time Machine', result[0]['title'])

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
