import sys, traceback
from flask import request
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from api import DB
from api.models import Document

class DocumentIndex(Resource):
    """ Return the list of available document endpoints"""

    # -------------------------------------------------------------------------
    # Class Methods
    # -------------------------------------------------------------------------
    
    @classmethod
    def atomEntryBuilder(cls, baseUri):
        """Curries a function to build a URL from a document object """
        def build(x):
            title = x['title'] 
            if not title:
                splitChar = '/' if '/' in x['path'] else '\\'
                title = x['path'].split(splitChar)[-1]
            id = x['id']

            entry = {'title': title,
                     'type': x['type'],
                     'source': x['path'],
                     'updated': x['scanned'].isoformat(),
                     'links': [{
                                'href': baseUri + '/{}'.format(id),
                                'rel': 'item',
                                'title': 'View/Edit',
                                'type': 'application/json'
                                },
                               {
                                'href': baseUri + '/{}/corpus'.format(id),
                                'rel': 'related',
                                'title': 'Corpora',
                                'type': 'application/json'
                                },
                               {
                                'href': baseUri + '/{}/keywords'.format(id),
                                'rel': 'related',
                                'title': 'Keywords',
                                'type': 'application/json'
                                },
                               {
                                'href': baseUri + '/{}/closest'.format(id),
                                'rel': 'related',
                                'title': 'Closest Documents',
                                'type': 'application/json'
                                }]
                      }
        
            if x['authors'].lower() not in ['', 'document conversion']:
                entry['author'] = x['authors']

            return entry
        return build

    # -------------------------------------------------------------------------
    # Request Methods
    # -------------------------------------------------------------------------

    def parseArgs(self):
        parser = RequestParser()
        parser.add_argument('limit', location='args', type=int, default=1000)
        parser.add_argument('offset', location='args', type=int, default=0)
        parser.add_argument('filter', location='args', type=str, default='')
        args = parser.parse_args()
        return args

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def get(self):
        try:
            args = self.parseArgs()
            limit = args['limit']
            start = args['offset']
            filter = args['filter']
            end = start + limit

            with DB.connection() as connection:
                store = Document(connection)
                build = self.atomEntryBuilder(request.base_url)
                fnGet = store.filter(filter) if filter else store.getAll()
                if limit:
                    return [build(x) 
                            for i,x in enumerate(fnGet)
                            if start <= i < end]
                else:
                    return [build(x) 
                            for i,x in enumerate(fnGet)
                            if start <= i]
        except Exception:
            sys.stderr.write('Failed\n')
            for fncall in traceback.format_exception(*sys.exc_info()):
                sys.stderr.write(fncall)
