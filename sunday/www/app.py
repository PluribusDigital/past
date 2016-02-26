import os
import sys
from flask import Flask, request
from flask_restful import abort, Api, Resource
from flask_restful.reqparse import RequestParser

# -----------------------------------------------------------------------------

def envKeys():
    ''' Generator for the list of keys in the .env file and the environ vars
    '''
    env = dict(os.environ)
    for pair in env.items():
        yield pair
    yield ('PGUSER', 'jfarley')
    yield ('PGDATABASE', 'sunday')

def anyKey(keys, *candidates):
    for key in candidates:
        if key in keys:
            return keys[key]
# -----------------------------------------------------------------------------

class DB():
    # -------------------------------------------------------------------------
    # Connection Methods
    # -------------------------------------------------------------------------
    @classmethod
    def connection(cls, **kwargs):
        import psycopg2

        keys = {k:v for k,v in envKeys()}
        keys.update(kwargs)
        
        user = anyKey(keys, 'POSTGRES_USER', 'PGUSER')
        if not user:
            print("User Name must be specified in the '.env' file", 
                  file=sys.stderr)
            return None

        password = anyKey(keys, 'POSTGRES_PASSWORD', 'PGPASSWORD')
        if not password:
            print("Password must be specified in the '.env' file", 
                  file=sys.stderr)
            return None

        database = anyKey(keys, 'database', 'PGDATABASE', 'POSTGRES_DB')
        if not database:
            print("The database must be specified in the '.env' file or kwargs", 
                  file=sys.stderr)
            return None

        return psycopg2.connect(database=database, user=user, password=password)

# -----------------------------------------------------------------------------

class Patent(object):
    """ The object-relational mapper for the `patent` table
    """
    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, connection):
        self.conn = connection
        self.dataFields = ['type', 'number', 'date', 'kind', 'abstract', 'title']
        self.allFields = ['id'] + self.dataFields

    # -------------------------------------------------------------------------
    # ORM Methods
    # -------------------------------------------------------------------------

    def _projection(self, record):
        a = {x[0]:x[1] for x in zip(self.allFields, record) }
        a['date'] = a['date'].isoformat()
        return a

    def _attachForeignKeyRelations(self, patent):
        #sql = """
        #SELECT c.name
        #FROM document as a
        #INNER JOIN membership as b on a.id = b.doc_id
        #INNER JOIN corpus as c on b.corpus_id = c.id
        #WHERE a.id = %s;
        #"""
        #with self.conn.cursor() as cur:
        #    cur.execute(sql, (document['id'], ))
        #    corpora = [row[0] for row in cur]

        #document['corpus'] = corpora
        return patent

    def get(self, id, includeRelations=False):
        template = "SELECT {0} FROM patent WHERE id = %s;"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql, (id, ))
            record = cur.fetchone()

        if not record:
            return None

        patent = self._projection(record)
        if includeRelations:
            return self._attachForeignKeyRelations(patent)
        return patent

    def getAll(self):
        template = "SELECT {0} FROM patent"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql)
            for record in cur:
                yield self._projection(record)

# -----------------------------------------------------------------------------

class Root(Resource):
    """ Return the list of available top-level endpoints
    """
    def get(self):
        return [{'title': 'Patents',
                  'summary': 'Parsed patent documents',
                  'links': [{
                             'href': request.base_url + 'patent',
                             'rel': 'collection',
                             'title': 'Patents',
                             'type': 'application/json'
                             }]
                 }]

class PatentIndex(Resource):
    """ Return the list of available patent endpoints"""

    @classmethod
    def atomEntryBuilder(cls, baseUri):
        """Curries a function to build a URL from a patent object """
        def build(x):
            title = x['title'] 
            id = x['id']

            entry = {'title': title,
                     'number': x['number'],
                     'date': x['date'],
                     'links': [{
                                'href': baseUri + '/{}'.format(id),
                                'rel': 'item',
                                'title': 'View/Edit',
                                'type': 'application/json'
                                }]
                      }        
            #if x['authors'].lower() not in ['', 'document conversion']:
            #    entry['author'] = x['authors']

            return entry
        return build

    def parseArgs(self):
        parser = RequestParser()
        parser.add_argument('limit', location='args', type=int, default=20)
        parser.add_argument('offset', location='args', type=int, default=0)
        args = parser.parse_args()
        return args

    def get(self):
        args = self.parseArgs()
        limit = args['limit']
        start = args['offset']
        end = start + limit

        with DB.connection() as connection:
            store = Patent(connection)
            if request.base_url[-1] == '/':
                baseUri = request.base_url[:-1]
            else:
                baseUri = request.base_url

            build = self.atomEntryBuilder(baseUri)
            if limit:
                return [build(x) 
                        for i,x in enumerate(store.getAll())
                        if start <= i < end]
            else:
                return [build(x) 
                        for i,x in enumerate(store.getAll())
                        if start <= i]

class PatentDetail(Resource):
    """The _RUD endpoint for a single patent"""

    def get(self, id):
        with DB.connection() as connection:
            store = Patent(connection)
            doc = store.get(id)

        if not doc:
            abort(404, message="'{}' doesn't exist".format(id))
        
        return doc

# -----------------------------------------------------------------------------

app = Flask(__name__)
api = Api(app)
api.add_resource(Root, '/')
api.add_resource(PatentIndex, '/patent', '/patent/')
api.add_resource(PatentDetail, '/patent/<id>', '/patent/<id>/')

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
