import sys
import json
from flask import request
from flask_restful import abort, Resource
from api import DB
from api.models import Document

class DocumentDetail(Resource):
    """The _RUD endpoint for a single document"""

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------

    def get(self, id):
        with DB.connection() as connection:
            store = Document(connection)
            doc = store.get(id)

        if not doc:
            abort(404, message="'{}' doesn't exist".format(id))
        
        # fix the title if it is missing        
        title = doc['title'] 
        if not title:
            splitChar = '/' if '/' in doc['path'] else '\\'
            title = doc['path'].split(splitChar)[-1]

        # fix the path to be a "real" URL 
        path = doc['path']

        return {
                "id": doc['id'],
                "scanned": doc['scanned'].isoformat(),
                "path": path,
                "dateCreated": doc['date_created'],
                "title": title,
                "authors": doc['authors'], 
                "type": doc['type']
                }

    def put(self, id):
        if not request.data:
            abort(400, message="Document not in the correct format")        

        s = request.data.decode('utf-8') if request.data else '{}'
        if s[0] != '{':
            abort(400, message="Document not in the correct format")        

        try:
            doc = json.loads(s)
            doc['id'] = id
        except:
            err = sys.exc_info()[0]
            print(err)
            abort(400, message="Document not in the correct format")

        with DB.connection() as connection:
            store = Document(connection)
            try:
                result = store.update(doc)
            except KeyError:
                abort(404, message="'{}' doesn't exist".format(id))
            except ValueError as v:
                abort(400, message=v)

        return '', 204

    def delete(self, id):
        with DB.connection() as connection:
            store = Document(connection)
            try:
                result = store.delete(id)
            except KeyError:
                abort(404, message="'{}' doesn't exist".format(id))

        return '', 204
