import jot
from flask import request, abort
from flask_restful import Resource

class Root(Resource):
    """ Return the list of available top-level endpoints
    """
    def parse(self, encoded):
        if not encoded:
            return None
        
        s = encoded.decode('utf-8')
        return s

    def get(self):
        return 'Usage: POST ' + request.base_url + '\n<text to process>'

    def post(self):
        """Adds a new name set to the list
        Returns the new id and a link record
        """
        s = self.parse(request.data)
        if not s:
            abort(400, message="You must supply some text")

        jotter = jot.Jotter.build()

        # build the clusters
        return s, 201

