from flask import request
from flask_restful import Resource

class Root(Resource):
    """ Return the list of available top-level endpoints
    """
    def get(self):
        return [{'title': 'Corpora',
                 'summary': 'The document collections contained within PASP',
                 'links': [{
                            'href': request.base_url + 'corpus',
                            'rel': 'collection',
                            'title': 'Corpora',
                            'type': 'application/json'
                            }]
                 },
                 {'title': 'Documents',
                  'summary': 'The documents that have been scanned into PASP',
                  'links': [{
                             'href': request.base_url + 'document',
                             'rel': 'collection',
                             'title': 'Documents',
                             'type': 'application/json'
                             }]
                 },
                 {'title': 'Rankings',
                  'summary': 'Search for documents that contain one or more terms',
                  'links': [{
                             'href': request.base_url + 'rank',
                             'rel': 'collection',
                             'title': 'Rankings',
                             'type': 'application/json'
                           }]
                 }]
