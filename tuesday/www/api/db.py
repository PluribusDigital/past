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
        
        user = anyKey(keys, 'POSTGRES_USER', 'PGUSER')
        if not user:
            sys.stderr.write("Username must be specified in the '.env' file\n")
            return None

        password = anyKey(keys, 'POSTGRES_PASSWORD', 'PGPASSWORD')
        if not password:
            sys.stderr.write("Password must be specified in the '.env' file\n")
            return None

        database = anyKey(keys, 'database', 'POSTGRES_DB', 'PGDATABASE')
        if not database:
            sys.stderr.write("The database must be specified in the '.env' file\n")
            return None

        host = anyKey(keys, 'POSTGRES_HOST', 'PGHOST')
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
        taggerPath = relToAbs('../../db/seed/seed-tally.txt')
        sql = """
        COPY tally
        FROM STDIN
        WITH (FORMAT 'csv', HEADER true, DELIMITER '\t');
        """

        with open(taggerPath, 'r') as f:
            with conn.cursor() as cur:
                cur.execute('TRUNCATE tally')
                cur.copy_expert(sql=sql, file=f)
