from urllib.parse import *

from flask import request
from flask_restful import abort, Resource
from api import DB
from api.models import Document, Corpus
from api.endpoints import CorpusIndex

class DocumentCorpusIndex(Resource):
    """ Return the list of related corpus endpoints for one document"""
    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, **kwargs):
        self.basePath = '/' if 'prefix' not in kwargs else kwargs['prefix']

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def get(self, id):
        # get the document URL
        elem = urlparse(request.base_url)
        url = '{0}://{1}{2}{3}'.format(elem.scheme, elem.netloc, self.basePath,
                                       '/corpus')

        with DB.connection() as connection:
            store = Corpus(connection)
            build = CorpusIndex.atomEntryBuilder(url, request.base_url)
            return [build(x) for x in store.getMembers(id)]

    def post(self, id):
        body = CorpusIndex.extractPostBody(request)

        with DB.connection() as connection:
            storeD = Document(connection)
            storeC = Corpus(connection)

            doc = storeD.get(id, True)
            if not doc:
                abort(404, message="'{}' doesn't exist".format(id))

            name = body['name']
            if name in doc['corpus']:
                return '', 201

            corpus = storeC.findOrAdd(name)
            storeD.addMembership(id, corpus['id'])

        return '', 201
