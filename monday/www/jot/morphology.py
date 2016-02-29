import nltk
import sys

class Morphology(object):
    """Object relational mapper for the `morphology` table"""

    table = {}

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, connection):
        self.conn = connection
        with self.conn.cursor() as cur:
            cur.execute('SELECT id, tagset_penn, tagset_universal FROM morphology;')
            for id, k, univ in cur:
                self.table[k] = {'universal': univ, 'id':id}

    # -------------------------------------------------------------------------
    # CRUD Methods
    # -------------------------------------------------------------------------

    def tryGetAddPenn(self, tag):
        if tag not in self.table:
            print(tag, 'not found in table', file=sys.stderr)
            with self.conn.cursor() as cur:
                cur.execute("""INSERT INTO morphology 
                (tagset_universal, tagset_penn) VALUES (%s, %s)
                RETURNING id
                """, ('X', tag))
                id = cur.fetchone()[0]
            self.table[tag] = {'id': id, 'universal': 'X'}

        return self.table[tag]


