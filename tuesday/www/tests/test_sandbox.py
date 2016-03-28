import unittest
import sys
import json
import csv
from collections import defaultdict
from itertools import islice, chain
from api import Tf_Idf, DB
from api.models import Document, DocumentKeyword

dbConnectionInfo = {}

citations = [
    ('9087826', '5927505'),
    ('9087826', '7288440'),
    ('9087826', '7884453'),
    ('9087843', '6809412'),
    ('9088421', '5511122'),
    ('9088421', '6839434'),
    ('9088421', '7207061'),
    ('9088421', '8386800'),
    ('9088421', '8732463'),
    ('9088489', '6745022'),
    ('9088489', '7181455'),
    ('9088489', '7707573'),
    ('9088489', '8355696'),
    ('9088523', '6308148'),
    ('9088540', '6035333'),
    ('9088540', '6085165'),
    ('9088540', '6684247'),
    ('9088540', '6829223'),
    ('9088540', '6912568'),
    ('9088540', '8024613'),
    ('9088557', '6694025'),
    ('9088625', '7409431'),
    ('9088625', '7774782'),
    ('9088642', '7317681'),
    ('9088642', '8605567'),
    ('9088693', '8963984'),
    ('9088693', '8970655')
]

closest = {
    '9087826': '8355262',
    '9087843': '8330255',
    '9088421': '8732463',
    '9088489': '6745022',
    '9088523': '7889649',
    '9088540': '8403848',
    '9088557': '7720227',
    '9088625': '8380796',
    '9088642': '8605567',
    '9088693': '8970655'
}

class Test_Sandbox(unittest.TestCase):
    def setUp(self):
        self.connection = DB.connection(**dbConnectionInfo)
        self.dockw = DocumentKeyword(self.connection)
        self.tfidf = Tf_Idf(self.connection)
        self.store = Document(self.connection)

        self.citations = defaultdict(list)
        for r in citations:
            self.citations[r[0]].append(r[1])

    def tearDown(self):
        if self.connection:
            self.connection.rollback()
            self.connection.close()

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def getId(self, patent):
        return next(self.store.filter(patent))['id']

    def buildSet(self, patent, D, nDocs):
        result = defaultdict(dict)

        docs = list(chain([patent, closest[patent]], sorted(self.citations[patent])))
        for c in docs:
            #lemmas = self.tfidf.forDistance(self.getId(c), D, nDocs)
            lemmas = self.tfidf.keywords(['lemma', 'pos'], self.getId(c), 10000)
            for v in lemmas:
                key = (v['lemma'], v['pos'])
                result[key][c] = v['tfidf']

        return docs, result

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_A(self):
        D = self.tfidf.cachedPairedDelta()
        nDocs = self.tfidf.nD()

        for patent in self.citations:
            docs, words = self.buildSet(patent, D, nDocs)

            with open(patent + '.txt', 'w') as f:
                f.write('lemma\tpos\t{0}\n'.format('\t'.join(docs)))
                for w in sorted(words):
                    b = words[w]
                    values = [str(b[d]) if d in b else '' for d in docs]
                    f.write('{0}\t{1}\t{2}\n'.format(w[0], w[1], '\t'.join(values)))

        self.fail('!')

if __name__ == '__main__':
    unittest.main()#defaultTest='Test_Sandbox.test_A')
