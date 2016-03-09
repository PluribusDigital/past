import sys
import os
import psycopg2

def relToAbs(fileName):
    dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(dir, fileName))

def envKeys():
    ''' Generator for the list of keys in the .env file
    '''
    env = dict(os.environ)
    for pair in env.items():
        yield pair
    
def anyKey(keys, *candidates):
    for key in candidates:
        if key in keys:
            return keys[key]

def loadSql(fileName):
    fullPath = relToAbs(fileName)
    with open(fullPath, 'r') as f:
        sql = f.read()
    return sql

class DB(object):
    description = 'database commands for PASP'

    # -------------------------------------------------------------------------
    # Connection Methods
    # -------------------------------------------------------------------------
    @classmethod
    def connection(cls, **kwargs):
        keys = {k:v for k,v in envKeys()}
        keys.update(kwargs)
        
        user = anyKey(keys, 'PASP_DATABASE_USER', 'POSTGRES_USER', 'PGUSER')
        if not user:
            sys.stderr.write("Username must be specified in the '.env' file\n")
            return None

        password = anyKey(keys, 'PASP_DATABASE_PASSWORD', 'POSTGRES_PASSWORD', 
                          'PGPASSWORD')
        if not password:
            sys.stderr.write("Password must be specified in the '.env' file\n")
            return None

        database = anyKey(keys, 'database', 'PASP_DATABASE', 'POSTGRES_DB', 
                          'PGDATABASE')
        if not database:
            sys.stderr.write("The database must be specified in the '.env' file\n")
            return None

        host = anyKey('PASP_DATABASE_HOST')
        if not host:
            host = 'localhost'

        dsn = "host={0} dbname={1} user={2} password={3}"
        return psycopg2.connect(dsn.format(host, database, user, password))

    @classmethod
    def _seed_delta(cls, conn):
        sql = loadSql('../../db/trigger-rebuild-delta.sql')
        with conn.cursor() as cur:
            cur.execute(sql)

    @classmethod
    def _seed_tally(cls, conn):
        taggerPath = relToAbs('../../db/seed/seed_tally.txt')
        with open(taggerPath, 'r') as f:
            with conn.cursor() as cur:
                cur.execute('TRUNCATE tally')
                cur.copy_from(f, 'tally', columns=['corpus_id','token',
                                                    'lemma','stem','pos',
                                                    'morph_id','syntax_id',
                                                    'doc_count','count'])
