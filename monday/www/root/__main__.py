import sys
from endpoints import *
from flask import Flask
from flask_restful import Api

debugging = True

app = Flask(__name__)
api = Api(app)
api.add_resource(Root, '/')

sys.dont_write_bytecode = debugging
app.run(host='0.0.0.0', debug=False)
