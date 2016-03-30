# -*- coding: utf-8 -*-

import math
from collections import Counter
from decimal import *
from operator import itemgetter
from functools import partial
from collections import defaultdict

EXCLUSIONS = {'wherein', 'plurality', 'configure', 'thereof', 'comprise',
             'andwherein'}

class Tf_Idf(object):
    """ Calculates the Term Freqency-Inverse Document Frequency vector
    To help with naming inside this module:
    
    D = The set of all documents
    d = One document

    C_id = A set of documents, a corpus

    Delta = The set of all documents that contains the term 't'
          = { (d, |t in d|) : t in d and d in D }
    
    Chi   = The set of documents in corpus C_id that contains the term 't'
          = { (d, |t in d|) : t in d and d in C_id }

    Tau   = The set of terms contained in a document
          = { (t, |t in d|) : t in d }
    """

    facts = ['token', 'lemma', 'stem', 'pos', 'morph_id', 'syntax_id']
    values = ['docs', 'count']

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, connection):
        self.conn = connection

    # -------------------------------------------------------------------------
    # Count Methods
    # -------------------------------------------------------------------------

    def nD(self):
        """ Total number of documents in the system """
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM document")
            d0 = Decimal(cur.fetchone()[0])
            cur.execute("SELECT max(doc_count) FROM tally")
            d1 = Decimal(cur.fetchone()[0])
            return d0 + d1

    def nC(self, corpus_id):
        """ Total number of documents in `corpus_id` """
        sql = "SELECT COUNT(DISTINCT doc_id) FROM membership WHERE corpus_id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (corpus_id, ))
            return Decimal(cur.fetchone()[0])

    # -------------------------------------------------------------------------
    # Delta Methods
    # -------------------------------------------------------------------------

    def Delta(self, key, value):
        template = """
        SELECT doc_id, sum(count)
        FROM jot
        WHERE {0} = %s
        GROUP BY {0}, doc_id
        """
        sql = template.format(key)

        with self.conn.cursor() as cur:
            cur.execute(sql, (value, ))
            return Counter({x[0]:x[1] for x in cur})

    def nDelta(self, key, value):
        templateA = """
        SELECT count(DISTINCT doc_id)
        FROM jot
        WHERE {0} = %s
        GROUP BY {0}
        """
        templateB = "SELECT doc_count FROM tally WHERE {0} = %s"
        
        sqls = [templateA.format(key), templateB.format(key)]

        accum = 0
        with self.conn.cursor() as cur:
            for sql in sqls:
                cur.execute(sql, (value, ))
                accum += sum([x[0] for x in cur])
        return accum

    def cachedPairedDelta(self):
        sql = """
        SELECT lemma, count
        FROM delta
        """
        with self.conn.cursor() as cur:
            cur.execute(sql)
            result = {(x[0],):x[1] for x in cur}
        return result

    def PairedDelta(self, keys):
        if len(keys) == 1 and keys[0] == 'lemma':
            return self.cachedPairedDelta()

        templateA = """
        SELECT {0}, count(DISTINCT doc_id)
        FROM jot
        GROUP BY {0}
        """
        templateB = """
        SELECT {0}, sum(doc_count) 
        FROM tally 
        GROUP BY {0}
        """

        cols = ', '.join(keys)
        sqls = [templateA.format(cols), templateB.format(cols)]

        accum = Counter()
        with self.conn.cursor() as cur:
            for sql in sqls:
                cur.execute(sql)
                batch = Counter({tuple(x[0:-1]):x[-1] for x in cur})
                accum.update(batch)
        return accum

    # -------------------------------------------------------------------------
    # Chi Methods
    # -------------------------------------------------------------------------

    def Chi(self, key, value, corpus_id):
        template = """
        SELECT doc_id, sum(count)
        FROM jot
        WHERE doc_id IN (SELECT DISTINCT doc_id 
                         FROM membership 
                         WHERE corpus_id = %(corpus)s)
         and {0} = %(value)s
        GROUP BY {0}, doc_id
        """
        sql = template.format(key)

        with self.conn.cursor() as cur:
            cur.execute(sql, {'value': value, 'corpus':corpus_id})
            return Counter({x[0]:x[1] for x in cur})

    def nChi(self, key, value, corpus_id):
        template = """
        SELECT count(DISTINCT doc_id)
        FROM jot
        WHERE doc_id IN (SELECT DISTINCT doc_id 
                         FROM membership 
                         WHERE corpus_id = %(corpus)s)
         and {0} = %(value)s
        GROUP BY {0}
        """
        sql = template.format(key)

        with self.conn.cursor() as cur:
            cur.execute(sql, {'value': value, 'corpus':corpus_id})
            return sum([x[0] for x in cur])

    def PairedChi(self, keys, corpus_id):
        template = """
        SELECT {0}, count(DISTINCT doc_id)
        FROM jot
        WHERE doc_id IN (SELECT DISTINCT doc_id 
                         FROM membership 
                         WHERE corpus_id = %s)
        GROUP BY {0}
        """
        sql = template.format(', '.join(keys))

        with self.conn.cursor() as cur:
            cur.execute(sql, (corpus_id, ))
            return Counter({tuple(x[0:-1]):x[-1] for x in cur})

    # -------------------------------------------------------------------------
    # Tau Methods
    # -------------------------------------------------------------------------

    def nTau(self, doc_id):
        sql = """
        SELECT sum(count)
        FROM jot
        WHERE doc_id = %s
          AND pos NOT IN ('ADP', 'AUX', 'CONJ', 'DET', 'PART', 'PRON', 'PUNCT')
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (doc_id, ))
            return Decimal(sum([x[0] for x in cur]))

    def Tau(self, keys, doc_id):
        template = """
        SELECT {0}, sum(count)
        FROM jot
        WHERE doc_id = %s
          AND pos NOT IN ('ADP', 'AUX', 'CONJ', 'DET', 'PART', 'PRON', 'PUNCT')
        GROUP BY {0}
        """
        sql = template.format(', '.join(keys))

        with self.conn.cursor() as cur:
            cur.execute(sql, (doc_id, ))
            return Counter({tuple(x[0:-1]):x[-1] for x in cur})

    def TauCorpus(self, keys, corpus_id):
        template = """
        SELECT {0}, sum(count)
        FROM jot
        WHERE doc_id IN (SELECT DISTINCT doc_id 
                    FROM membership 
                    WHERE corpus_id = %s)
          AND pos NOT IN ('ADP', 'AUX', 'CONJ', 'DET', 'PART', 'PRON', 'PUNCT')
        GROUP BY {0}
        """
        sql = template.format(', '.join(keys))

        with self.conn.cursor() as cur:
            cur.execute(sql, (corpus_id, ))
            return Counter({tuple(x[0:-1]):x[-1] for x in cur})

    # -------------------------------------------------------------------------
    # Calculate Methods
    # -------------------------------------------------------------------------

    def _calculate(self, T, D, nDocs):
        for t in T:
            if t not in D:
                yield (t, float('inf'))
            else:
                idf = Decimal(-100.0 * math.log10(D[t] / nDocs))
                yield (t, T[t]*idf)

    def _calculateNormalized(self, T, D, nDocs):
        nT = Decimal(sum([T[t] for t in T]))
        for t in T:
            if t not in D:
                yield (t, float('inf'))
            else:
                idf = Decimal(-100.0 * math.log10(D[t] / nDocs))
                yield (t, (T[t] / nT)*idf)

    # -------------------------------------------------------------------------
    # Process Methods
    # -------------------------------------------------------------------------

    def forDistance(self, doc_id, D, nDocs):
        T = self.Tau(['lemma'], doc_id) 
        gen0 = self._calculateNormalized(T, D, nDocs)
        for row in gen0:
            v = {'lemma': row[0][0],
                 'tfidf': row[1], 
                 'doc_id': doc_id}
            yield v

    def keywords(self, fields, doc_id, limit, corpus_id=None):
        keys = [k for k in fields if k in self.facts]
        if not keys:
            allFields = ', '.join(self.facts)
            raise ValueError('Search only works on {0}'.format(allFields))

        if doc_id and corpus_id:
            T = self.Tau(keys, doc_id) 
            D = self.PairedChi(keys, corpus_id)
            nDocs = self.nC(corpus_id)
        elif doc_id:
            T = self.Tau(keys, doc_id) 
            D = self.PairedDelta(keys)
            nDocs = self.nD()
        elif corpus_id:
            T = self.TauCorpus(keys, corpus_id)
            D = self.PairedChi(keys, corpus_id)
            nDocs = self.nC(corpus_id)
        else:
            raise ValueError('Must specify at least one document or corpus')

        gen0 = self._calculateNormalized(T, D, nDocs)
        gen1 = sorted(gen0, key=itemgetter(1), reverse=True)
        for i, row in enumerate(gen1):
            if i >= limit:
                break
            v = {x[0]:x[1] for x in zip(keys, row[0])}
            v['tfidf'] = row[1]
            yield v

    def rank(self, fields, limit, corpus_id=None):
        keys = [k for k in fields if k in self.facts]
        if not keys:
            allFields = ', '.join(self.facts)
            raise ValueError('Search only works on {0}'.format(allFields))

        # flatten the fields and keys
        tuples = [(k,v) for k in keys for v in fields[k]]

        # determine the correct 'getting' functions
        if corpus_id:
            nDfn = partial(self.nChi, corpus_id=corpus_id)
            Dfn = partial(self.Chi, corpus_id=corpus_id)
            nDocs = self.nC(corpus_id)
        else:
            nDfn = self.nDelta
            Dfn = self.Delta
            nDocs = self.nD()

        # accmulate the results
        freqByDoc = defaultdict(list)
        countByDoc = Counter()
        for k,v in tuples:
            nd = nDfn(k, v)
            for d, t in Dfn(k, v).items():
                nt = self.nTau(d)
                idf = Decimal(-100.0 * math.log10(nd / nDocs))
                tfidf = (t / nt) * idf
                freqByDoc[d].append(tfidf)
                countByDoc[d] += t

        # only return documents that match all terms
        ids = list(freqByDoc.keys())
        for id in ids:
            if len(freqByDoc[id]) < len(tuples):
                del freqByDoc[id]

        # complete the calculation
        data = {k:sum(freqByDoc[k]) for k in freqByDoc}

        # return the results
        gen = sorted(data.items(), key=itemgetter(1), reverse=True)
        for i, row in enumerate(gen):
            if i >= limit:
                break
            doc_id, tfidf = row
            yield {'doc_id': doc_id, 'tfidf': tfidf, 'count':countByDoc[doc_id] }

'''
Use this query to determine the `EXCLUSIONS`

SELECT b.lemma, max(a.dc) / cast(sum(b.doc_count) as float) as boost
FROM (
        SELECT lemma, count(DISTINCT doc_id) as dc
        FROM jot
        WHERE doc_id IN (SELECT DISTINCT doc_id 
                         FROM membership 
                         WHERE corpus_id = 2)
	  AND pos NOT IN ('ADP', 'AUX', 'CONJ', 'DET', 'PART', 'PRON', 'PUNCT')
        GROUP BY lemma
	order by dc desc
	limit 100
) as a
INNER JOIN tally as b ON b.lemma = a.lemma
GROUP BY b.lemma
ORDER BY boost desc
'''