import math
from decimal import *

from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from api import DB
from api.tfidf import Tf_Idf, EXCLUSIONS

PLACES = Decimal('0.0001')

def projection(x):
    score = x['tfidf']
    score = float(score.quantize(PLACES)) if math.isfinite(score) else 'Inf'
    x['score'] = score
    del x['tfidf']
    return x

def allow(x):
    return (x['lemma'] not in EXCLUSIONS) if 'lemma' in x else True

class Keyword(Resource):
    """The endpoint for determining the keywords in a document or corpus"""

    # -------------------------------------------------------------------------
    # Request Methods
    # -------------------------------------------------------------------------

    def parseArgs(self):
        parser = RequestParser(trim=True, bundle_errors=True)
        parser.add_argument('field', location='args', dest='text', 
                            default='lemma',
                            choices=['lemma', 'token', 'stem'])
        parser.add_argument('morph', location='args', type=bool, 
                            dest='morph_id', default=False)
        parser.add_argument('partOfSpeech', location='args', type=bool, 
                            dest='pos', default=False)
        parser.add_argument('syntax', location='args', type=bool, 
                            dest='syntax_id', default=False)
        parser.add_argument('limit', location='args', type=int, default=10)
        args = parser.parse_args()
        return args

    def buildFields(self, args):
        fields = [args['text']]
        for field in ['pos', 'morph_id', 'syntax_id']:
            if args[field]:
                fields.append(field)

        return fields

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def get(self, doc_id=None, corpus_id=None):
        args = self.parseArgs()
        limit = args['limit']

        fields = self.buildFields(args)

        with DB.connection() as connection:
            calc = Tf_Idf(connection)
            gen = calc.keywords(fields, doc_id, limit, corpus_id)
            results = [projection(row) 
                       for i, row in enumerate(filter(allow, gen))
                       if i < limit]
        
        return results, 200 if results else 404
