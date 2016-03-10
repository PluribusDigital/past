import unittest
import json
from decimal import *
from unittest.mock import patch
from api import DB, Server, app

SCORE = 1.0
FIELDS = {'lemma': 'abc'}

class Test_Keyword(unittest.TestCase):
    connArgs = {'database': 'pasp_test'}

    def setUp(self):
        self.patcher = patch('api.endpoints.keyword.DB')
        self.mockDB = self.patcher.start()
        self.mockDB.connection.return_value = DB.connection(**self.connArgs)

        self.patchTfidf = patch('api.endpoints.keyword.Tf_Idf.keywords')
        self.mock = self.patchTfidf.start()

        self.target = app.test_client()
        self.url = Server.absoluteUrl('/document/1/keywords')
        self.urlCorpus = Server.absoluteUrl('/corpus/2/keywords')
        self.urlDocCorpus = Server.absoluteUrl('/document/1/corpus/2/keywords')
        self.url404 = Server.absoluteUrl('/document/0/keywords')

    def tearDown(self):
        self.patcher.stop()
        self.patchTfidf.stop()

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def buildResults(self, score, limit, fields):
        record = {k:fields[k] for k in fields}
        record['tfidf'] = score
        return [dict(record) for i in range(limit)]

    def verifyResults(self, rv, score, limit, fields):
        result = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(limit, len(result))
        for row in result:
            self.assertEqual(len(fields) + 1, len(row))
            self.assertIn('score', row)
            self.assertEqual(score, row['score'])
            for f in fields:
                self.assertIn(f, row)
                self.assertEqual(fields[f], row[f])

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_get_document(self):
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, FIELDS)

        rv = self.target.get(self.url)

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma'], 1, 10, None)
        self.verifyResults(rv, SCORE, 10, FIELDS)

    def test_get_document_corpus(self):
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, FIELDS)

        rv = self.target.get(self.urlDocCorpus)

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma'], 1, 10, 2)
        self.verifyResults(rv, SCORE, 10, FIELDS)

    def test_get_corpus(self):
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, FIELDS)

        rv = self.target.get(self.urlCorpus)

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma'], None, 10, 2)
        self.verifyResults(rv, SCORE, 10, FIELDS)

    def test_get_field_lemma(self):
        fields = {'lemma': 'be'}
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, fields)

        rv = self.target.get(self.url + '?field=lemma')

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma'], 1, 10, None)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_field_token(self):
        fields = {'token': 'is'}
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, fields)

        rv = self.target.get(self.url + '?field=token')

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['token'], 1, 10, None)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_field_stem(self):
        fields = {'stem': 'be'}
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, fields)

        rv = self.target.get(self.url + '?field=stem')

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['stem'], 1, 10, None)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_field_foo(self):
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, FIELDS)

        rv = self.target.get(self.url + '?field=foo')

        self.assertEqual(400, rv.status_code)

    def test_get_with_morphology(self):
        fields = {'lemma': 'be', 'morph_id': 23}
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, fields)

        rv = self.target.get(self.url + '?morph=1')

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma', 'morph_id'], 1, 10, None)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_with_part_of_speech(self):
        fields = {'lemma': 'be', 'pos': 'VERB'}
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, fields)

        rv = self.target.get(self.url + '?partOfSpeech=1')

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma', 'pos'], 1, 10, None)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_with_syntax(self):
        fields = {'lemma': 'be', 'syntax_id': 23}
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, fields)

        rv = self.target.get(self.url + '?syntax=1')

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma', 'syntax_id'], 1, 10, None)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_with_all(self):
        fields = {'lemma': 'be', 
                  'morph_id': 23,
                  'pos': 'VERB',
                  'syntax_id': 23}
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, fields)

        rv = self.target.get(self.url + '?morph=1&partOfSpeech=1&syntax=1')

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma', 'pos', 'morph_id',
                                           'syntax_id'], 1, 10, None)
        self.verifyResults(rv, SCORE, 10, fields)

    def test_get_with_limit(self):
        self.mock.return_value = self.buildResults(Decimal(SCORE), 20, FIELDS)

        rv = self.target.get(self.url + '?limit=15')

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma'], 1, 15, None)
        self.verifyResults(rv, SCORE, 15, FIELDS)

    def test_get_infinite_in_results(self):
        self.mock.return_value = self.buildResults(float('inf'), 20, FIELDS)

        rv = self.target.get(self.url)

        self.assertEqual(200, rv.status_code)
        self.mock.assert_called_once_with(['lemma'], 1, 10, None)
        self.verifyResults(rv, 'Inf', 10, FIELDS)

    def test_get_document_not_there(self):
        self.mock.return_value = []

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
