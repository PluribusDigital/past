import unittest
import json
from unittest.mock import patch
from api import Server, app, DB
from api.models import Document

class TestDocumentDetail(unittest.TestCase):
    connArgs = {'database': 'pasp_test'}
    doc_id = 0

    @classmethod
    def setUpClass(cls):
        cls.doc_id = cls.addRecord()

    def setUp(self):
        self.patcher = patch('api.endpoints.document_detail.DB')
        self.mockDB = self.patcher.start()
        self.mockDB.connection.return_value = DB.connection(**self.connArgs)

        self.target = app.test_client()
        assert(self.doc_id != 0)
        self.url = Server.absoluteUrl('/document/{0}'.format(self.doc_id))
        self.url404 = Server.absoluteUrl('/document/0')

    def tearDown(self):
        self.patcher.stop()

    @classmethod
    def tearDownClass(cls):
        sql = "DELETE FROM document WHERE tokenizer = %s;"
        
        with DB.connection(**cls.connArgs) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, ('tok',))

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
                    }
        with DB.connection(**cls.connArgs) as conn:
            store = Document(conn)
            return store.add(document)

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_get(self):
        rv = self.target.get(self.url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertNotIn('hash', result)
        self.assertIn('scanned', result)
        self.assertEqual(self.doc_id, result['id'])
        self.assertEqual('/root/details.docx', result['path'])
        self.assertEqual('1999-01-01', result['dateCreated'])
        self.assertEqual('The document', result['title'])
        self.assertEqual('John Doe', result['authors'])

    def test_get_not_found(self):
        rv = self.target.get(self.url404)
        self.assertEqual(404, rv.status_code)

    def test_delete(self):
        id = self.addRecord()
        url = Server.absoluteUrl('/document/{0}'.format(id))

        rv = self.target.delete(url)
        self.assertEqual(204, rv.status_code)

    def test_delete_not_found(self):
        rv = self.target.delete(self.url404)
        self.assertEqual(404, rv.status_code)

    def test_put(self):
        id = self.addRecord()
        url = Server.absoluteUrl('/document/{0}'.format(id))
        data = {'title': 'new', 'authors': 'new'}

        rv = self.target.put(url, data=json.dumps(data))
        self.assertEqual(204, rv.status_code)

        rv = self.target.get(url)
        self.assertEqual(200, rv.status_code)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual('/root/details.docx', result['path'])
        self.assertEqual('1999-01-01', result['dateCreated'])
        self.assertEqual('new', result['title'])
        self.assertEqual('new', result['authors'])

    def test_put_not_found(self):
        data = {'title': 'new', 'authors': 'new'}
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
