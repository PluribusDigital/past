import unittest
from api.models import Jot
from api import DB

def relToAbs(fileName):
    import os
    dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(dir, fileName))

class Test_Jot(unittest.TestCase):
    def setUp(self):
        self.connection = DB.connection(**{'database': 'pasp_test'})
        self.target = Jot(self.connection)

    def tearDown(self):
        if self.connection:
            self.connection.rollback()
            self.connection.close()

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def jotGenerator(self, doc_id=1):
        import json
        sql = "INSERT INTO document (id) VALUES (%s)"
        with self.connection.cursor() as cur:
            cur.execute(sql, (doc_id,))

        fileName = relToAbs('test-jots.json')
        with open(fileName) as f:
            jots = json.load(f)
        
        for jot in jots:
            jot['doc_id'] = doc_id
            yield jot

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_1_add(self):
        records = self.target.add(self.jotGenerator())
        self.assertEqual(15, records)

    def test_2_find_felt(self):
        records = self.target.add(self.jotGenerator())
        jots = self.target.find({'lemma': 'felt'})
        self.assertEqual(1, len(jots))
        self.assertEqual(1, sum([x['count'] for x in jots]))

    def test_2_find_Noun(self):
        records = self.target.add(self.jotGenerator())
        jots = self.target.find({'pos': 'NOUN'})
        self.assertEqual(4, len(jots))
        self.assertEqual(5, sum([x['count'] for x in jots]))

    def test_2_find_felt_AND_Noun(self):
        records = self.target.add(self.jotGenerator())
        jots = self.target.find({'lemma': 'felt', 'pos': 'NOUN'})
        self.assertEqual(1, len(jots))
        self.assertEqual(1, sum([x['count'] for x in jots]))

    def test_2_find_saw_OR_Noun(self):
        records = self.target.add(self.jotGenerator())
        jots = self.target.find({'lemma': 'saw', 'pos': 'NOUN'}, True)
        self.assertEqual(6, len(jots))
        self.assertEqual(7, sum([x['count'] for x in jots]))

    def test_3_clear(self):
        records = self.target.add(self.jotGenerator(1))
        records = self.target.add(self.jotGenerator(2))
        affected = self.target.clear(1)
        self.assertEqual(15, affected)
        jots = self.target.find({'doc_id': 2})
        self.assertEqual(15, len(jots))

    def test_3_clear_not_found(self):
        with self.assertRaises(ValueError):
            self.target.clear(1)

if __name__ == '__main__':
    unittest.main()
