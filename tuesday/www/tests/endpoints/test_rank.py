import unittest
import json
from decimal import *
from unittest.mock import patch
from api import Server, DB, app 
from api.models import Document, Corpus

SCORE = 1.0

class Test_Rank(unittest.TestCase):
    connArgs = {'database': 'pasp_test'}

    @classmethod
    def setUpClass(cls):
        cls.doc_ids, corpus = cls.addRecords(20)
        cls.corpus_id = corpus['id']

    def setUp(self):
        self.patchRank = patch('api.endpoints.rank.Tf_Idf.rank')
        self.mockRank = self.patchRank.start()

        self.patchDB = patch('api.endpoints.rank.DB')
        self.mockDB = self.patchDB.start()
        self.mockDB.connection.return_value = DB.connection(**self.connArgs)

        self.target = app.test_client()
        assert(len(self.doc_ids) == 20)
        assert(self.corpus_id)
        self.url = Server.absoluteUrl('/rank')

    def tearDown(self):
        self.patchRank.stop()
        self.patchDB.stop()

    @classmethod
    def tearDownClass(cls):
        sql = "DELETE FROM document; DELETE FROM corpus"
        
        with DB.connection(**cls.connArgs) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    @classmethod
    def addRecords(cls, count):
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
                    'type' : 'Patent'
                    }
        with DB.connection(**cls.connArgs) as conn:
            store = Document(conn)
            return [store.add(document, 'FOO') for _ in range(count)], \
                   Corpus(conn).find('FOO')

    def buildResults(self, score=Decimal(SCORE), limit=20, count=33):
        return [{'doc_id' : x, 'tfidf':  score, 'count': count} 
                for i, x in enumerate(self.doc_ids)
                if i < limit]

    def verifyResults(self, rv, score, limit, fields, corpus_id=None):
        self.mockRank.assert_called_once_with(fields, limit, corpus_id)

        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(limit, len(result))

        for row in result:
            self.assertIn('score', row)
            self.assertEqual(score, row['score'])
            self.assertIn('count', row)
            self.assertEqual(33, row['count'])
            self.assertIn('entry', row)
            self.assertIn('title', row['entry'])
            self.assertEqual('The document', row['entry']['title'])
            self.assertIn('author', row['entry'])
            self.assertEqual('John Doe', row['entry']['author'])
            self.assertIn('source', row['entry'])
            self.assertEqual('/root/details.docx', row['entry']['source'])
            self.assertIn('links', row['entry'])
            self.assertEqual(4, len(row['entry']['links']))

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_get(self):
        fields = {'token': ['electronic']}
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/electronic')

        self.assertEqual(200, rv.status_code)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_field_lemma(self):
        fields = {'lemma': ['category']}
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/categories?field=lemma')

        self.assertEqual(200, rv.status_code)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_field_token(self):
        fields = {'token': ['category']}
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/category?field=token')

        self.assertEqual(200, rv.status_code)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_field_stem(self):
        fields = {'stem': ['categori']}
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/category?field=stem')

        self.assertEqual(200, rv.status_code)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_field_foo(self):
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/electronic?field=foo')

        self.assertEqual(400, rv.status_code)

    def test_get_with_limit(self):
        fields = {'token': ['electronic']}
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/electronic?limit=15')

        self.assertEqual(200, rv.status_code)
        self.verifyResults(rv, SCORE, 15, fields)

    def test_get_infinite_in_results(self):
        fields = {'token': ['electronic']}
        self.mockRank.return_value = self.buildResults(float('inf'))

        rv = self.target.get(self.url + '/electronic')

        self.assertEqual(200, rv.status_code)
        self.verifyResults(rv, 'Inf', 10, fields)

    def test_get_multiple_words_A(self):
        fields = {'token': ['electronic', 'devices']}
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/electronic devices')

        self.assertEqual(200, rv.status_code)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_multiple_words_B(self):
        fields = {'token': ['electronic', 'devices']}
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/electronic+devices')

        self.assertEqual(200, rv.status_code)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_corpus(self):
        fields = {'token': ['electronic']}
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/electronic?corpus=FOO')

        self.assertEqual(200, rv.status_code)
        self.verifyResults(rv, SCORE, 10, fields, self.corpus_id)

    def test_get_corpus_not_there(self):
        fields = {'token': ['electronic']}
        self.mockRank.return_value = self.buildResults()

        rv = self.target.get(self.url + '/electronic?corpus=BAR')

        self.assertEqual(405, rv.status_code)

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
