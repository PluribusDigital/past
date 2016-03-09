import unittest
from decimal import Decimal
from api.models import DocumentKeyword
from api import DB

class Test_DocumentKeyword(unittest.TestCase):
    def setUp(self):
        self.connection = DB.connection(**{'database': 'pasp_test'})
        self.target = DocumentKeyword(self.connection)

    def tearDown(self):
        if self.connection:
            self.connection.rollback()
            self.connection.close()

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def generator(self, doc_id=1):
        sql = "INSERT INTO document (id) VALUES (%s)"
        with self.connection.cursor() as cur:
            cur.execute(sql, (doc_id,))

        terms = {
            'locker': Decimal('11.5141'),
            'micro': Decimal('8.6712'),
            'truck': Decimal('7.2466'),
            'door': Decimal('4.7606'),
            'switch': Decimal('4.4076'),
            'fastener': Decimal('3.9582'),
            'stopper': Decimal('3.3115'),
            'status': Decimal('3.3012'),
            'lock': Decimal('3.1351'),
            'security': Decimal('2.6488'),
            'control': Decimal('2.3931'),
            'rear': Decimal('2.0837'),
            'flash': Decimal('1.9596'),
            'unlock': Decimal('1.7395'),
            'pivotally': Decimal('1.6889'),
            'led': Decimal('1.6103'),
            'checking': Decimal('1.4553'),
            'structure': Decimal('1.2646'),
            'period': Decimal('1.249'),
            "won't": Decimal('1.2468') }
        
        for k in sorted(terms):
            yield {'doc_id': doc_id, 'lemma': k, 'tfidf': terms[k]}
        
    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_1_add(self):
        records = self.target.add(self.generator())
        self.assertEqual(20, records)

    def test_2_get_all_raw(self):
        self.target.add(self.generator())
        records = list(self.target.get_all_raw())
        self.assertEqual(20, len(records))
        self.assertAlmostEqual(Decimal('1.4553'), Decimal(records[0][2]))

    def test_3_get_exists(self):
        self.target.add(self.generator())
        records = list(self.target.get(1))
        self.assertEqual(20, len(records))
        self.assertAlmostEqual(Decimal('1.4553'), records[0]['tfidf'])

    def test_4_get_doesntexist(self):
        records = list(self.target.get(132))
        self.assertEqual(0, len(records))

    def test_5_truncate(self):
        self.target.add(self.generator())
        result = self.target.truncate()
        self.assertEqual(20, result)

        records = list(self.target.get_all_raw())
        self.assertEqual(0, len(records))

if __name__ == '__main__':
    unittest.main(failfast=True)
