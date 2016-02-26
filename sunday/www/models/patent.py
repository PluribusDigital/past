
class Patent(object):
    """ The object-relational mapper for the `patent` table
    """

    def __init__(self, connection):
        self.conn = connection
        self.dataFields = ['type', 'number', 'date', 'kind', 'abstract', 'title']
        self.allFields = ['id'] + self.dataFields

    # -------------------------------------------------------------------------
    # Helper Methods
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

    # -------------------------------------------------------------------------
    # ORM Methods
    # -------------------------------------------------------------------------

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
