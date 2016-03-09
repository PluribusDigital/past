from urllib.parse import *

from flask import request, redirect
from flask_restful import abort, Resource
from api import DB
from api.models import Document

class DocumentCorpusDetail(Resource):
    """ Provide an end point for removing a document from a corpus """
    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, **kwargs):
        self.basePath = '/' if 'prefix' not in kwargs else kwargs['prefix']

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def get(self, doc_id, corpus_id):
        # get the document URL
        elem = urlparse(request.base_url)
        url = '{0}://{1}{2}{3}{4}'.format(elem.scheme, elem.netloc, 
                                          self.basePath, '/corpus/', corpus_id)
        return redirect(url, code=303)

    def delete(self, doc_id, corpus_id):
        with DB.connection() as connection:
            store = Document(connection)
            try:
                result = store.removeMembership(doc_id, corpus_id)
            except KeyError as ke:
                abort(404, message=str(ke))

        return '', 204
