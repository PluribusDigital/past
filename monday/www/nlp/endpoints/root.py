from nlp.jot import Jotter
from flask import request, abort
from flask_restful import Resource

class Reader(object):
    def __init__(self, s):
        self.text = s

    def __iter__(self):
        yield (self.text, '')

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

        jotter = Jotter.build()
        reader = Reader(s)

        result = [x for x in jotter.run(reader, 0)]

        # build the clusters
        return result, 201

