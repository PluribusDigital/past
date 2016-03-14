from decimal import Decimal

class DocumentKeyword(object):
    """ The object-relational mapper for the `dockw` table
    """

    facts = ['lemma', 'doc_id']
    values = ['tfidf']

    def projection(self, x):
        return {'lemma' : x[0], 
                'doc_id': x[1],
                'tfidf' : Decimal(x[2]),
               }

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, connection):
        self.conn = connection
        self.allFields = self.facts + self.values

    # -------------------------------------------------------------------------
    # Database Methods
    # -------------------------------------------------------------------------

    def add(self, dockwGen):
        template = "INSERT INTO dockw ({0}) VALUES ({1});"
        sql = template.format(', '.join(self.allFields),
                              ', '.join(['%({0})s'.format(x) 
                                         for x in self.allFields]))
        count = 0
        with self.conn.cursor() as cur:
            cur.executemany(sql, dockwGen)
            count += cur.rowcount

        return count


        row_templ = "('{0}', {1}, {2:.7f})"
        rows = [row_templ.format(x['lemma'].replace("'", "''"), 
                                 x['doc_id'], 
                                 x['tfidf'])
                for x in dockwGen]

        template = "INSERT INTO dockw (lemma, doc_id, tfidf) VALUES {0};"
        sql = template.format(', '.join(rows))

        count = 0
        with self.conn.cursor() as cur:
            cur.execute(sql)
            affected = cur.rowcount

        return affected

    def get(self, doc_id):
        template = "SELECT {0} FROM dockw WHERE doc_id = %s;"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql, (doc_id, ))
            for record in cur:
                yield self.projection(record)

    def get_all_raw(self):
        template = "SELECT {0} FROM dockw"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql)
            for record in cur:
                yield record

    def truncate(self):
        sql = "DELETE FROM dockw"
        
        with self.conn.cursor() as cur:
            cur.execute(sql)
            affected = cur.rowcount

        return affected
