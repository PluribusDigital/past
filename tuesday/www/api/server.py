import os
import argparse
import api.endpoints as EP
from flask import Flask, send_file
from flask_restful import abort, Api

API_ROOT = '/api/v1'
KWARGS = {'prefix' : API_ROOT}

dir = os.path.dirname(__file__)

app = Flask(__name__, static_folder='../../app')
api = Api(app, prefix=API_ROOT)
api.add_resource(EP.Root, '/')
api.add_resource(EP.CorpusIndex, '/corpus')
api.add_resource(EP.CorpusDetail, '/corpus/<int:id>')
api.add_resource(EP.CorpusDocumentIndex, '/corpus/<int:id>/document',
                 resource_class_kwargs=KWARGS)
api.add_resource(EP.DocumentIndex, '/document')
api.add_resource(EP.DocumentDetail, '/document/<int:id>')
api.add_resource(EP.DocumentClosest, '/document/<int:id>/closest')
api.add_resource(EP.DocumentCorpusIndex, '/document/<int:id>/corpus',
                 resource_class_kwargs=KWARGS)
api.add_resource(EP.DocumentCorpusDetail, 
                 '/document/<int:doc_id>/corpus/<int:corpus_id>',
                 resource_class_kwargs=KWARGS)
#api.add_resource(EP.Keyword, 
#                 '/document/<int:doc_id>/keywords', 
#                 '/document/<int:doc_id>/corpus/<int:corpus_id>/keywords',
#                 '/corpus/<int:corpus_id>/keywords')
api.add_resource(EP.RankRoot, '/rank')
#api.add_resource(EP.Rank, '/rank/<words>', resource_class_kwargs=KWARGS)

@app.route('/')
@app.route('/document')
@app.route('/corpus')
def toStart():
    return send_file('../../app/index.html')

@app.route(API_ROOT + '/<path:path>')
def handleBadApiPath(path):
    abort(405, message='Unsupported path')

@app.route('/<path:path>')
def singlePageRoute(path):
    fullPath = os.path.join(dir, '../../app', path)
    if os.path.exists(fullPath):
        return send_file(fullPath)
    return send_file('../../app/index.html')

@app.route('/bower_components/<path:path>')
def bower(path):
    fullPath = os.path.join(dir, '../../bower_components', path)
    return send_file(fullPath)

class Server(object):
    description = 'provide HTTP services'

    # -------------------------------------------------------------------------
    # Process
    # -------------------------------------------------------------------------

    @classmethod
    def absoluteUrl(cls, relative):
        f = "{0}{1}" if relative[0] == '/' else "{0}/{1}"
        return f.format(API_ROOT, relative)

    @classmethod
    def run(cls, **kwargs):
        app.run(host='0.0.0.0', debug=False, threaded=True)
