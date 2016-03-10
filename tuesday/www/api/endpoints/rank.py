import math
from decimal import *
from urllib.parse import *

from flask import request
from flask_restful import abort, Resource
from flask_restful.reqparse import RequestParser
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from api import DB
from api.tfidf import Tf_Idf
from api.models import Document, Corpus
from api.endpoints import DocumentIndex

PLACES = Decimal('0.0001')

def score(x):
    score = x['tfidf']
    score = float(score.quantize(PLACES)) if math.isfinite(score) else 'Inf'
    return score

class Rank(Resource):
    """The endpoint for ranking documents based on keywords"""
    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, **kwargs):
        self.basePath = '/' if 'prefix' not in kwargs else kwargs['prefix']

    # -------------------------------------------------------------------------
    # Request Methods
    # -------------------------------------------------------------------------

    def parseArgs(self):
        parser = RequestParser(trim=True, bundle_errors=True)
        parser.add_argument('field', location='args', dest='text', 
                            default='token',
                            choices=['lemma', 'token', 'stem'])
        parser.add_argument('limit', location='args', type=int, default=10)
        parser.add_argument('corpus', dest='corpus')
        args = parser.parse_args()
        return args

    def buildFields(self, args, words):
        parsed = unquote_plus(words).lower()
        tokens = parsed.split()
        field = args['text']

        if field == 'lemma':
            fn = WordNetLemmatizer().lemmatize
            return {field: [fn(x) for x in tokens]} 
        elif field == 'stem':
            fn = SnowballStemmer("english").stem
            return {field: [fn(x) for x in tokens]} 

        return {field: tokens}

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def get(self, words):
        args = self.parseArgs()
        limit = args['limit']

        # build the field/filter
        fields = self.buildFields(args, words)

        with DB.connection() as connection:
            # get the corpus ID
            corpus_id = None
            if 'corpus' in args and args['corpus']:
                corpus = Corpus(connection).find(args['corpus'])
                if not corpus:
                    message = "Corpus '{0}' not found".format(args['corpus'])
                    abort(405, message=message)
                corpus_id = corpus['id']

            calc = Tf_Idf(connection)
            gen = calc.rank(fields, limit, corpus_id)
            pass1 = {row['doc_id'] : (score(row), row['count'])
                     for i, row in enumerate(gen)
                     if i < limit}
        
            # get the docs
            store = Document(connection)
            docs = store.getThese(*pass1.keys())

        # get the document URL
        elem = urlparse(request.base_url)
        url = '{0}://{1}{2}{3}'.format(elem.scheme, elem.netloc, self.basePath,
                                       '/document')

        # convert to ATOM entries
        results = []
        build = DocumentIndex.atomEntryBuilder(url)
        for k,v in docs.items():
            row = {'entry': build(v)}
            row['score'], row['count'] = pass1[k]
            results.append(row)

        return results, 200
