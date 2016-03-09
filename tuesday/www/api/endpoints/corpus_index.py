import json
from flask import request
from flask_restful import abort, Resource
from flask_restful.reqparse import RequestParser
from api import DB
from api.models import Corpus

class CorpusIndex(Resource):
    """ Return the list of available corpus endpoints"""

    # -------------------------------------------------------------------------
    # Class Methods
    # -------------------------------------------------------------------------
    
    @classmethod
    def atomEntryBuilder(cls, baseUri, keywordBaseUri=None):
        """Curries a function to build a URL from a corpus object """
        if not keywordBaseUri:
            keywordBaseUri = baseUri

        def build(x):
            title = x['name'] 
            id = x['id']

            entry = {'title': title,
                     'links': [{
                                'href': baseUri + '/{}'.format(id),
                                'rel': 'item',
                                'title': 'View/Edit',
                                'type': 'application/json'
                                },
                               {
                                'href': baseUri + '/{}/document'.format(id),
                                'rel': 'related',
                                'title': 'Documents',
                                'type': 'application/json'
                                },
                               {
                                'href': keywordBaseUri + '/{}/keywords'.format(id),
                                'rel': 'related',
                                'title': 'Keywords',
                                'type': 'application/json'
                                }]
                      }
        
            return entry
        return build

    # -------------------------------------------------------------------------
    # Request Methods
    # -------------------------------------------------------------------------

    def parseArgs(self):
        parser = RequestParser()
        parser.add_argument('limit', location='args', type=int, default=0)
        parser.add_argument('offset', location='args', type=int, default=0)
        args = parser.parse_args()
        return args

    @classmethod
    def extractPostBody(cls, request):
        if not request.data:
            abort(400, message="Corpus not in the correct format")        

        s = request.data.decode('utf-8') if request.data else '{}'
        if s[0] != '{':
            abort(400, message="Corpus not in the correct format")        

        try:
            corpus = json.loads(s)
        except:
            err = sys.exc_info()[0]
            print(err)
            abort(400, message="Corpus not in the correct format")

        if 'name' not in corpus:
            abort(400, message="Corpus not in the correct format")

        return corpus

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def get(self):
        args = self.parseArgs()
        limit = args['limit']
        start = args['offset']
        end = start + limit

        with DB.connection() as connection:
            store = Corpus(connection)
            build = self.atomEntryBuilder(request.base_url)
            if limit:
                return [build(x) 
                        for i,x in enumerate(store.getAll())
                        if start <= i < end]
            else:
                return [build(x) 
                        for i,x in enumerate(store.getAll())
                        if start <= i]

    def post(self):
        corpus = self.extractPostBody(request)

        with DB.connection() as connection:
            store = Corpus(connection)
            name = corpus['name']
            if store.find(name):
                abort(409, message="Corpus already exists")

            result = store.findOrAdd(name)

        build = self.atomEntryBuilder(request.base_url)
        return build(result), 201
