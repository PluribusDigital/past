class Corpus(object):
    """ The object-relational mapper for the `corpus` table
    """
    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, connection):
        self.conn = connection
        self.dataFields = ['name']
        self.allFields = ['id'] + self.dataFields

    # -------------------------------------------------------------------------
    # ORM Methods
    # -------------------------------------------------------------------------

    def get(self, id):
        template = "SELECT {0} FROM corpus WHERE id = %s;"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql, (id, ))
            record = cur.fetchone()

        if not record:
            return None

        corpus = {x[0]:x[1] for x in zip(self.allFields, record) }
        return corpus

    def getAll(self):
        template = "SELECT {0} FROM corpus WHERE id <> 1"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql)
            return [{x[0]:x[1] 
                     for x in zip(self.allFields, record)}
                     for record in cur 
                    ]

    def getMembers(self, doc_id):
        template = """
        SELECT {0}
        FROM corpus
        INNER JOIN membership on corpus_id = id
        WHERE doc_id = %s;
        """
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql, (doc_id, ))
            return [{x[0]:x[1] 
                     for x in zip(self.allFields, record)}
                     for record in cur 
                    ]

    def find(self, name):
        name = name.lower()
        template = "SELECT {0} FROM corpus WHERE name = %s;"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql, (name, ))
            record = cur.fetchone()

        if record:
            corpus = {x[0]:x[1] for x in zip(self.allFields, record) }
            return corpus

    def findOrAdd(self, name):
        name = name.lower()
        corpus = self.find(name)
        if corpus:
            return corpus

        sql = "INSERT INTO corpus (name) VALUES (%s) RETURNING ID;"
        with self.conn.cursor() as cur:
            cur.execute(sql, (name, ))
            id = cur.fetchone()[0]

        corpus = {'id': id, 'name': name}
        return corpus

    def update(self, corpus):
        keys = {k for k in corpus if k in self.dataFields}
        if not keys:
            fields = ', '.join(self.dataFields)
            raise ValueError('Update only works on {0}'.format(fields))

        template = "UPDATE corpus SET {0} WHERE id = %(id)s;"
        sql = template.format(', '.join(['{0} = %({0})s'.format(x) 
                                         for x in keys]))

        # make sure the name is lowercase
        if 'name' in corpus:
            corpus['name'] = corpus['name'].lower()

        with self.conn.cursor() as cur:
            cur.execute(sql, corpus)
            affected = cur.rowcount

        if not affected:
            templ = "Corpus not updated. Possible cause: id = {0} not found"
            raise KeyError(templ.format(corpus['id']))

        return affected == 1

    def delete(self, id):
        sql = "DELETE FROM corpus WHERE id = %s;"
        
        with self.conn.cursor() as cur:
            cur.execute(sql, (id, ))
            affected = cur.rowcount

        if not affected:
            t = "Error deleting corpus. Possible cause: id = {0} not found"
            raise KeyError(t.format(id))

        return affected == 1
