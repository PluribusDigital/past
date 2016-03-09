from urllib.parse import *

from flask import request
from flask_restful import abort, Resource
from api import DB
from api.models import Document, Corpus
from api.endpoints import DocumentIndex

class CorpusDocumentIndex(Resource):
    """ Return the list of related document endpoints for one corpus"""
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
                                       '/document')

        with DB.connection() as connection:
            storeD = Document(connection)
            storeC = Corpus(connection)

            corpus = storeC.get(id)
            if not corpus:
                abort(404, message="'{}' doesn't exist".format(id))

            build = DocumentIndex.atomEntryBuilder(url)
            return [build(x) for x in storeD.getMembersOf(id)]

