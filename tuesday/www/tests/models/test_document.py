﻿import unittest
from api.models import Document
from api import DB

class Test_Document(unittest.TestCase):
    def setUp(self):
        self.connection = DB.connection(**{'database': 'pasp_test'})
        self.target = Document(self.connection)
        self.document = {
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
        self.validateSql = "SELECT COUNT(*) FROM membership WHERE doc_id = %s;"

    def tearDown(self):
        if self.connection:
            self.connection.rollback()
            self.connection.close()

    # -------------------------------------------------------------------------
    # Other Methods
    # -------------------------------------------------------------------------

    def seedCorpus(self, name='foo'):
        sql = "INSERT INTO corpus (name) VALUES (%s) RETURNING ID;"
        with self.connection.cursor() as cur:
            cur.execute(sql, (name, ))
            id = cur.fetchone()[0]

        return id

    def seedForFilter(self):
        b = dict(self.document)
        b['title'] = 'Delorean Time Machine'
        b['authors'] = 'Brown, Doc; McFly, Marty Jr.'
        b['path'] = '/patent/9898'

        c = dict(self.document)
        c['title'] = 'Railroad Time Machine'
        c['authors'] = 'Brown, Doc; Brown, Clara'
        c['path'] = '/patent/7676'

        documents = [dict(self.document), b, c]
        return [self.target.add(x) for x in documents]

    def corpus_count(self, id):
        with self.connection.cursor() as cur:
            cur.execute(self.validateSql, (id, ))
            return cur.fetchone()[0]

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_01_insert(self):
        id = self.target.add(self.document)
        self.assertTrue(id > 0)

    def test_01_insert_partial(self):
        del self.document['authors']
        with self.assertRaises(KeyError):
            self.target.add(self.document)        

    def test_01_insert_with_1_corpus(self):
        id = self.target.add(self.document, 'a')
        self.assertTrue(id > 0)
        self.assertEqual(1, self.corpus_count(id))

    def test_01_insert_with_N_corpus(self):
        id = self.target.add(self.document, 'a', 'b', 'c')
        self.assertTrue(id > 0)
        self.assertEqual(3, self.corpus_count(id))

    def test_02_get(self):
        id = self.target.add(self.document)
        actual = self.target.get(id)
        self.assertIsNotNone(actual)
        self.assertEqual(id, actual['id'])
        for k in self.document:
            self.assertEqual(self.document[k], actual[k])
        self.assertNotIn('corpus', actual)

    def test_02_get_with_corpus(self):
        id = self.target.add(self.document, 'a', 'b', 'c')
        actual = self.target.get(id, True)
        self.assertIsNotNone(actual)
        self.assertEqual(id, actual['id'])
        for k in self.document:
            self.assertEqual(self.document[k], actual[k])
        self.assertTrue('corpus' in actual)
        self.assertEqual(3, len(actual['corpus']))
        for c in actual['corpus']:
            self.assertIn(c, ['a', 'b', 'c'])

    def test_02_get_not_there(self):
        actual = self.target.get(1)
        self.assertIsNone(actual)

    def test_03_find_by_empty(self):
        with self.assertRaises(ValueError):
            docs = self.target.find({})

    def test_03_find_by_bad_fields(self):
        with self.assertRaises(ValueError):
            docs = self.target.find({'abc': '123'})

    def test_03_find_by_hash(self):
        id = self.target.add(self.document)
        docs = self.target.find({'hash' : '1234567890'})
        self.assertEqual(1, len(docs))
        self.assertEqual(id, docs[0]['id'])

    def test_03_find_by_hash_not_there(self):
        docs = self.target.find({'hash' : 'abc123'})
        self.assertEqual(0, len(docs))

    def test_03_find_by_path(self):
        id = self.target.add(self.document)
        docs = self.target.find({'path' : '/root/details.docx'})
        self.assertEqual(1, len(docs))
        self.assertEqual(id, docs[0]['id'])

    def test_03_find_by_path_not_there(self):
        docs = self.target.find({'path' : 'details.docx'})
        self.assertEqual(0, len(docs))

    def test_03_find_by_path_and_hash(self):
        id = self.target.add(self.document)
        docs = self.target.find({'hash' : '1234567890', 
                                 'path' : '/root/details.docx'})
        self.assertEqual(1, len(docs))
        self.assertEqual(id, docs[0]['id'])

    def test_03_find_by_path_and_hash_bad_hash_OR(self):
        id = self.target.add(self.document)
        docs = self.target.find({'hash' : 'abc123',
                                 'path' : '/root/details.docx'})
        self.assertEqual(1, len(docs))
        self.assertEqual(id, docs[0]['id'])

    def test_03_find_by_path_and_hash_bad_path_OR(self):
        id = self.target.add(self.document)
        docs = self.target.find({'hash' : '1234567890',
                                 'path' : 'details.docx'})
        self.assertEqual(1, len(docs))
        self.assertEqual(id, docs[0]['id'])

    def test_03_find_by_path_and_hash_bad_hash_AND(self):
        id = self.target.add(self.document)
        docs = self.target.find({'hash' : 'abc123',
                                 'path' : '/root/details.docx'}, 
                                False)
        self.assertEqual(0, len(docs))

    def test_03_find_by_path_and_hash_bad_path_AND(self):
        id = self.target.add(self.document)
        docs = self.target.find({'hash' : '1234567890',
                                 'path' : 'details.docx'}, 
                                False)
        self.assertEqual(0, len(docs))

    def test_04_update(self):
        id = self.target.add(self.document)
        clone = dict(self.document)
        for k in clone:
            clone[k] = 'abc'
        clone['id'] = id

        actual = self.target.update(clone)
        self.assertTrue(actual)

    def test_04_update_not_there(self):
        clone = dict(self.document)
        clone['id'] = 0

        with self.assertRaises(KeyError):
            actual = self.target.update(clone)

    def test_05_get_all(self):
        id1 = self.target.add(self.document)
        id2 = self.target.add(self.document)
        id3 = self.target.add(self.document)
        
        docs = list(self.target.getAll())
        self.assertEqual(3, len(docs))

    def test_06_delete(self):
        id = self.target.add(self.document)
        actual = self.target.delete(id)
        self.assertTrue(actual)

    def test_06_delete_not_there(self):
        with self.assertRaises(KeyError):
            actual = self.target.delete(0)

    def test_07_get_these(self):
        id1 = self.target.add(self.document)
        id2 = self.target.add(self.document)
        id3 = self.target.add(self.document)
        
        docs = self.target.getThese(id2, id3)
        self.assertEqual(2, len(docs))
        self.assertIn(id2, docs)
        self.assertIn(id3, docs)

    def test_08_get_memberOf_corpus(self):
        id = self.seedCorpus()
        self.target.add(self.document, 'foo', 'b', 'c')
        actual = self.target.getMembersOf(id)
        self.assertIsNotNone(actual)
        self.assertEqual(1, len(actual))

    def test_08_get_memberOf_corpus_not_exist(self):
        actual = self.target.getMembersOf(0)
        self.assertIsNotNone(actual)
        self.assertEqual(0, len(actual))

    def test_09_removeMembership(self):
        corpus_id = self.seedCorpus()
        other_id = self.seedCorpus('b')
        id = self.target.add(self.document, 'foo', 'b', 'c')
        actual = self.target.removeMembership(id, corpus_id)
        self.assertTrue(actual)
        
        docs = self.target.getMembersOf(other_id)
        self.assertIsNotNone(docs)
        self.assertEqual(1, len(docs))

    def test_09_removeMembership_corpus_not_exist(self):
        id = self.target.add(self.document)
        with self.assertRaises(KeyError):
            self.target.removeMembership(id, 0)

    def test_10_filter_empty(self):
        ids = self.seedForFilter()
        docs = list(self.target.filter(''))
        self.assertEqual(0, len(docs))

    def test_10_filter_match_title(self):
        ids = self.seedForFilter()
        docs = list(self.target.filter('machine'))
        self.assertEqual(2, len(docs))
        self.assertEqual(ids[1], docs[0]['id'])
        self.assertEqual(ids[2], docs[1]['id'])

    def test_10_filter_match_author(self):
        ids = self.seedForFilter()
        docs = list(self.target.filter('brown'))
        self.assertEqual(2, len(docs))
        self.assertEqual(ids[1], docs[0]['id'])
        self.assertEqual(ids[2], docs[1]['id'])

    def test_10_filter_match_patentnumber(self):
        ids = self.seedForFilter()
        docs = list(self.target.filter('9898'))
        self.assertEqual(1, len(docs))
        self.assertEqual(ids[1], docs[0]['id'])

    def test_10_filter_no_match(self):
        ids = self.seedForFilter()
        docs = list(self.target.filter('qaz'))
        self.assertEqual(0, len(docs))

if __name__ == '__main__':
    unittest.main()
