from operator import itemgetter

class Jot(object):
    """ The object-relational mapper for the `jot` table
    """

    facts = ['token', 'lemma', 'stem', 'pos', 'morph_id', 'syntax_id', 
             'doc_id']
    values = ['count']

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, connection):
        self.conn = connection
        self.allFields = self.facts + self.values

    # -------------------------------------------------------------------------
    # Database Methods
    # -------------------------------------------------------------------------

    def add(self, jotGen):
        template = "INSERT INTO jot ({0}) VALUES ({1});"
        sql = template.format(', '.join(self.allFields),
                              ', '.join(['%({0})s'.format(x) 
                                         for x in self.allFields]))
        count = 0
        with self.conn.cursor() as cur:
            for jot in jotGen:
                cur.execute(sql, jot)
                count += cur.rowcount

        return count

    def find(self, fields, multipleMeansOr=False):
        keys = {k for k in fields if k in self.facts}
        if not keys:
            allFields = ', '.join(self.facts)
            raise ValueError('Search only works on {0}'.format(allFields))

        template = "SELECT {0} FROM jot WHERE {1};"
        operation = ' OR ' if multipleMeansOr else ' AND ' 
        sql = template.format(', '.join(self.allFields),
                              operation.join(['{0} = %({0})s'.format(x)
                                              for x in keys]))
        values = {k:fields[k] for k in keys}

        with self.conn.cursor() as cur:
            cur.execute(sql, values)
            return [{x[0]:x[1] 
                     for x in zip(self.allFields, record)}
                     for record in cur 
                    ]

    def clear(self, doc_id):
        sql = "DELETE FROM jot WHERE doc_id = %s;"
        
        with self.conn.cursor() as cur:
            cur.execute(sql, (doc_id, ))
            affected = cur.rowcount

        if not affected:
            raise ValueError("Jots not dropped. \
            Possible cause: id = {0} not found".format(doc_id))

        return affected

