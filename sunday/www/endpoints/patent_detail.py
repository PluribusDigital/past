from .db import DB
from models import Patent
from flask_restful import abort, Resource

class PatentDetail(Resource):
    """The _RUD endpoint for a single patent"""

    def get(self, id):
        with DB.connection() as connection:
            store = Patent(connection)
            doc = store.get(id)

        if not doc:
            abort(404, message="'{}' doesn't exist".format(id))
        
        return doc
