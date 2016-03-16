import unittest
from api.models import Document, Jot
from api import Tf_Idf, DB
from cProfile import Profile
from pstats import Stats

dbConnectionInfo = {'database': 'pasp_test'}
DOC_ID = 1
CORPUS_ID = 2

def relToAbs(fileName):
    import os
    dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(dir, fileName))

@unittest.skip("Skip until DB seeding can be worked out")
class Test_Tfidf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with DB.connection(**dbConnectionInfo) as conn:
            cls.reset_db(conn)
            DB._seed_tally(conn)
            cls.addDoc(conn)
            DB._seed_delta(conn)

    def setUp(self):
        self.connection = DB.connection(**dbConnectionInfo)
        self.target = Tf_Idf(self.connection)
        #self.pr = Profile()
        #self.pr.enable()
        #print("\n<<<---", self.id())

    def tearDown(self):
        if self.connection:
            self.connection.rollback()
            self.connection.close()
        #p = Stats (self.pr)
        #p.strip_dirs()
        #p.sort_stats ('cumtime')
        #p.print_stats (0.1)
        #print("\n--->>>")

    @classmethod
    def tearDownClass(cls):
        with DB.connection(**dbConnectionInfo) as conn:
            cls.reset_db(conn)

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    @classmethod
    def reset_db(cls, conn):
        with conn.cursor() as cur:
            cur.execute('TRUNCATE corpus RESTART IDENTITY CASCADE')
            cur.execute("TRUNCATE document RESTART IDENTITY CASCADE")
            cur.execute('INSERT INTO corpus (name) VALUES (%s)', ('english',))

    @classmethod
    def addDoc(cls, conn):
        import json

        docOrm = Document(conn)
        doc = {x: '' for x in docOrm.dataFields}
        doc_id = docOrm.add(doc, 'test')

        fileName = relToAbs('models/test-jots.json')
        with open(fileName) as f:
            jots = json.load(f)

        for jot in jots:
            jot['doc_id'] = doc_id
        
        orm = Jot(conn)
        orm.add(jots)

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_nD(self):
        count = self.target.nD()
        self.assertEqual(1114, count)

    def test_nC(self):
        count = self.target.nC(CORPUS_ID)
        self.assertEqual(1, count)
        count = self.target.nC(CORPUS_ID + 1)
        self.assertEqual(0, count)

    def test_Delta(self):
        vector = self.target.Delta('lemma', 'saw')
        self.assertDictEqual(vector, {DOC_ID: 3})
        vector = self.target.Delta('token', 'saw')
        self.assertDictEqual(vector, {DOC_ID: 2})
        vector = self.target.Delta('stem', 'foo')
        self.assertDictEqual(vector, {})

    def test_nDelta(self):
        count = self.target.nDelta('lemma', 'saw')
        self.assertEqual(217, count)
        count = self.target.nDelta('lemma', 'beef')
        self.assertEqual(18, count)

    def test_PairedDelta(self):
        pairs = self.target.PairedDelta(['lemma'])
        self.assertEqual(40664, len(pairs))
        self.assertEqual(217, pairs[('saw', )])
        self.assertEqual(18, pairs[('beef', )])

    def test_Chi(self):
        vector = self.target.Chi('lemma', 'saw', CORPUS_ID)
        self.assertDictEqual(vector, {DOC_ID: 3})
        vector = self.target.Chi('token', 'saw', CORPUS_ID)
        self.assertDictEqual(vector, {DOC_ID: 2})
        vector = self.target.Chi('stem', 'foo', CORPUS_ID)
        self.assertDictEqual(vector, {})

    def test_nChi(self):
        count = self.target.nChi('lemma', 'saw', CORPUS_ID)
        self.assertEqual(1, count)
        count = self.target.nChi('lemma', 'beef', CORPUS_ID)
        self.assertEqual(0, count)

    def test_PairedChi(self):
        pairs = self.target.PairedChi(['lemma'], CORPUS_ID)
        self.assertEqual(12, len(pairs))
        self.assertEqual(1, pairs[('saw', )])
        self.assertEqual(0, pairs[('beef', )])

    def test_Tau(self):
        pairs = self.target.Tau(['lemma'], DOC_ID)
        self.assertEqual(6, len(pairs))
        self.assertEqual(3, pairs[('saw', )])
        self.assertEqual(1, pairs[('felt', )])
        self.assertEqual(1, pairs[('go', )])
        self.assertFalse(('the', ) in pairs)

    def test_nTau(self):
        count = self.target.nTau(DOC_ID)
        self.assertEqual(12, count)

    def test_TauCorpus(self):
        pairs = self.target.TauCorpus(['lemma'], CORPUS_ID)
        self.assertEqual(6, len(pairs))
        self.assertEqual(3, pairs[('saw', )])
        self.assertEqual(1, pairs[('felt', )])
        self.assertEqual(1, pairs[('go', )])
        self.assertFalse(('the', ) in pairs)

    def test_calculate(self):
        T = {('saw', ): 3, ('felt', ): 3, ('go', ): 1}
        D = {('saw', ): 1, ('go', ): 10}
        d = 10
        vector = {k:c for k,c in self.target._calculate(T, D, d)}
        self.assertEqual(300, vector[('saw', )])
        self.assertEqual(0, vector[('go', )])
        self.assertEqual(float('inf'), vector[('felt', )])

    def test_calculateNormalized(self):
        T = {('saw', ): 3, ('felt', ): 3, ('go', ): 1, ('make-saw-5%'): 53}
        D = {('saw', ): 1, ('go', ): 100}
        d = 100
        vector = {k:c for k,c in self.target._calculateNormalized(T, D, d)}
        self.assertEqual(10, vector[('saw', )])
        self.assertEqual(0, vector[('go', )])
        self.assertEqual(float('inf'), vector[('felt', )])

    def test_forDistance(self):
        from decimal import Decimal
        D = {('saw', ): 1, ('go', ): 10}
        d = 10
        gen = self.target.forDistance(DOC_ID, D, d)
        vector = {x['lemma']:x['tfidf'] for x in gen}
        self.assertAlmostEqual(Decimal(300/12), vector['saw'])
        self.assertEqual(0, vector['go'])
        self.assertEqual(float('inf'), vector['felt'])

    @unittest.skip('Documenting a test case')
    def test_keywords(self):
        self.fail('Not Implemented')

    @unittest.skip('Documenting a test case')
    def test_rank(self):
        self.fail('Not Implemented')

if __name__ == '__main__':
    unittest.main()#defaultTest='Test_Tfidf.test_PairedDelta')
