import os
import sys
import psycopg2

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

class DB():
    # -------------------------------------------------------------------------
    # Connection Methods
    # -------------------------------------------------------------------------
    @classmethod
    def connection(cls, **kwargs):
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
