from flask import request
from flask_restful import Resource

class Root(Resource):
    """ Return the list of available top-level endpoints
    """
    def get(self):
        return [{'title': 'Patents',
                  'summary': 'Parsed patent documents',
                  'links': [{
                             'href': request.base_url + 'patent',
                             'rel': 'collection',
                             'title': 'Patents',
                             'type': 'application/json'
                             }]
                 }]

