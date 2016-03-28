import sys
import time
from operator import itemgetter
from decimal import *
from math import acos
from urllib.parse import *
from flask import request
from flask_restful import abort, Resource
from flask_restful.reqparse import RequestParser
from api import DB
from api.models import Document, DocumentKeyword
from api.endpoints import DocumentIndex

PLACES = Decimal('0.0001')
ZERO = Decimal(0)
DISTANCE_THRESH = Decimal(acos(ZERO)) - PLACES
MINIMUM_TFIDF = Decimal(1)

# NOT THREAD SAFE
lastCached = None
vectors = {}

def clamp(val, minv, maxv):
    return minv if val < minv else maxv if val > maxv else val

def distance(v1, v2):
    """ Calculates the Ochiai coefficient between two vectors"""

    result = ZERO
    
    lengthV1 = ZERO
    lengthV2 = ZERO
    dot = ZERO

    words = set(v1).union(set(v2))
    for word in words:
        x = Decimal(v1[word]) if word in v1 else ZERO
        y = Decimal(v2[word]) if word in v2 else ZERO
        
        lengthV1 += x * x
        lengthV2 += y * y
        try:
            dot += x * y
        except InvalidOperation as e:
            pass

    denom = lengthV1.sqrt() * lengthV2.sqrt()
    x = dot/denom if denom > ZERO else ZERO
    bounded_x = clamp(x, Decimal(-1), Decimal(1))
    return Decimal(acos(bounded_x)) / DISTANCE_THRESH

class DocumentClosest(Resource):
    """ Return the list of documents 'closest' to the relevant document"""

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, **kwargs):
        self.basePath = '/' if 'prefix' not in kwargs else kwargs['prefix']
        self.start = time.time()

    # -------------------------------------------------------------------------
    # Other Methods
    # -------------------------------------------------------------------------

    def _checkCache(self, connection):
        import time
        from datetime import datetime
        global lastCached

        # TODO: Recalculate if the latest document entered is newer than the cache
        if not lastCached:
            self.elapsed("Building Closest Document cache")
            self._buildCache(connection)
            lastCached = datetime.now()

    def _buildCache(self, connection):
        global vectors
        from collections import defaultdict

        # reset the cache
        vectors = defaultdict(dict)
        weighted = DocumentKeyword(connection)
        for r in weighted.get_all_raw():
            value = Decimal(r[2])
            if value > MINIMUM_TFIDF:
                vectors[r[1]][r[0]] = Decimal(r[2]) 

    def elapsed(self, message):
        import sys
        end = time.time()
        hours, rem = divmod(end-self.start, 3600)
        minutes, seconds = divmod(rem, 60)
        tpl = "{0:0>2}:{1:0>2}:{2:05.2f}\t{3}\n"
        sys.stderr.write(tpl.format(int(hours), int(minutes), seconds, message))

   # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def parseArgs(self):
        parser = RequestParser()
        parser.add_argument('limit', location='args', type=int, default=10)
        args = parser.parse_args()
        return args

    def get(self, id):
        global vectors

        # get the document URL
        elem = urlparse(request.base_url)
        url = '{0}://{1}{2}{3}'.format(elem.scheme, elem.netloc, self.basePath,
                                       '/document')

        args = self.parseArgs()
        limit = args['limit']

        with DB.connection() as connection:
            store = Document(connection)
            document = store.get(id)
            if not document:
                abort(404, message="'{}' doesn't exist".format(id))

            self.elapsed('Loading keywords')
            self._checkCache(connection)
            assert(len(vectors) > 0)

            self.elapsed('Calculating distance for all docs')
            dist = {}
            for j in vectors:
                if j != id:
                    dist[j] = distance(vectors[id], vectors[j])

            gen = sorted(dist.items(), key=itemgetter(1))
            build = DocumentIndex.atomEntryBuilder(url)
            results = []

            self.elapsed('Finding results')
            for i, pair in enumerate(gen):
                if i < limit and pair[1] < 1.0:
                    entry = build(store.get(pair[0]))
                    entry['distance'] = "{:.3f}".format(pair[1])
                    results.append(entry)
            return results
