import unittest
from api.models import Corpus
from api import DB

class Test_Corpus(unittest.TestCase):
    def setUp(self):
        self.connection = DB.connection(**{'database': 'pasp_test'})
        self.target = Corpus(self.connection)

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

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_1_findOrAdd_does_not_exist(self):
        corpus = self.target.findOrAdd('BAR')
        self.assertIsNotNone(corpus)
        self.assertTrue(corpus['id'] > 1)
        self.assertEqual('bar', corpus['name'])

    def test_1_findOrAdd_exists(self):
        id = self.seedCorpus()
        corpus = self.target.findOrAdd('FOO')
        self.assertIsNotNone(corpus)
        self.assertEqual(id, corpus['id'])

    def test_2_get(self):
        id = self.seedCorpus()
        corpus = self.target.get(id)
        self.assertIsNotNone(corpus)
        self.assertEqual(id, corpus['id'])
        self.assertEqual('foo', corpus['name'])

    def test_2_get_not_exists(self):
        corpus = self.target.get(0)
        self.assertIsNone(corpus)

    def test_3_update(self):
        id = self.seedCorpus()
        clone = {'name': 'BAZ', 'id': id}

        actual = self.target.update(clone)
        self.assertTrue(actual)

        corpus = self.target.get(id)
        self.assertEqual('baz', corpus['name'])

    def test_3_update_not_there(self):
        clone = {'name': 'BAZ', 'id': 0}

        with self.assertRaises(KeyError):
            actual = self.target.update(clone)

    def test_4_get_all(self):
        id1 = self.seedCorpus('FOO')
        id2 = self.seedCorpus('BAR')
        id3 = self.seedCorpus('BAZ')
        
        actual = self.target.getAll()
        self.assertEqual(3, len(actual))

    def test_5_delete(self):
        id = self.seedCorpus()
        actual = self.target.delete(id)
        self.assertTrue(actual)

    def test_5_delete_not_there(self):
        with self.assertRaises(KeyError):
            actual = self.target.delete(0)

if __name__ == '__main__':
    unittest.main()
