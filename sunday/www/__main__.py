from endpoints import *
from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
api.add_resource(Root, '/')
api.add_resource(PatentIndex, '/patent', '/patent/')
api.add_resource(PatentDetail, '/patent/<id>', '/patent/<id>/')

app.run(host='0.0.0.0', debug=True)
