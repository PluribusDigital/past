import sys
import json
from flask import request
from flask_restful import abort, Resource
from api import DB
from api.models import Corpus

class CorpusDetail(Resource):
    """The _RUD endpoint for a single corpus"""

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def get(self, id):
        with DB.connection() as connection:
            store = Corpus(connection)
            corpus = store.get(id)

        if not corpus:
            abort(404, message="'{}' doesn't exist".format(id))
        
        return {
                "id": corpus['id'],
                "name": corpus['name']
                }

    def put(self, id):
        if not request.data:
            abort(400, message="Corpus not in the correct format")        

        s = request.data.decode('utf-8') if request.data else '{}'
        if s[0] != '{':
            abort(400, message="Corpus not in the correct format")        

        try:
            corpus = json.loads(s)
            corpus['id'] = id
            name = corpus['name']
        except:
            err = str(sys.exc_info()[0])
            abort(400, message="Corpus not in the correct format. " + err)

        with DB.connection() as connection:
            store = Corpus(connection)
            if store.find(name):
                abort(409, message="Corpus already exists")

            try:
                result = store.update(corpus)
            except KeyError:
                abort(404, message="'{}' doesn't exist".format(id))
            except ValueError as v:
                abort(400, message=v)

        return '', 204

    def delete(self, id):
        with DB.connection() as connection:
            store = Corpus(connection)
            try:
                result = store.delete(id)
            except KeyError:
                abort(404, message="'{}' doesn't exist".format(id))

        return '', 204
