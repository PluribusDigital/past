from .db import DB
from models import Patent
from flask import request
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

class PatentIndex(Resource):
    """ Return the list of available patent endpoints"""

    @classmethod
    def atomEntryBuilder(cls, baseUri):
        """Curries a function to build a URL from a patent object """
        def build(x):
            title = x['title'] 
            id = x['id']

            entry = {'title': title,
                     'number': x['number'],
                     'date': x['date'],
                     'links': [{
                                'href': baseUri + '/{}'.format(id),
                                'rel': 'item',
                                'title': 'View/Edit',
                                'type': 'application/json'
                                }]
                      }        
            #if x['authors'].lower() not in ['', 'document conversion']:
            #    entry['author'] = x['authors']

            return entry
        return build

    def parseArgs(self):
        parser = RequestParser()
        parser.add_argument('limit', location='args', type=int, default=20)
        parser.add_argument('offset', location='args', type=int, default=0)
        args = parser.parse_args()
        return args

    def get(self):
        args = self.parseArgs()
        limit = args['limit']
        start = args['offset']
        end = start + limit

        with DB.connection() as connection:
            store = Patent(connection)
            if request.base_url[-1] == '/':
                baseUri = request.base_url[:-1]
            else:
                baseUri = request.base_url

            build = self.atomEntryBuilder(baseUri)
            if limit:
                return [build(x) 
                        for i,x in enumerate(store.getAll())
                        if start <= i < end]
            else:
                return [build(x) 
                        for i,x in enumerate(store.getAll())
                        if start <= i]
