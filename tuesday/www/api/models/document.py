from api.models.corpus import Corpus

class Document(object):
    """ The object-relational mapper for the `document` table
    """
    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, connection):
        self.conn = connection
        self.dataFields = ['hash', 'path', 'date_created', 'title', 
                           'authors', 'tokenizer', 'tagger', 'lemmatizer', 
                           'stemmer', 'syntaxer', 'type']
        self.allFields = ['id', 'scanned'] + self.dataFields

    # -------------------------------------------------------------------------
    # Other Methods
    # -------------------------------------------------------------------------

    def buildFind(self, reader):
        return {
            'path': reader.absolutePath(), 
            'hash': reader.hash()
            }

    def newRow(self, reader):
        return {
            'path': reader.absolutePath(), 
            'hash': reader.hash(),
            'date_created': reader.documentDate(),
            'title': reader.title(),
            'authors': reader.authors()
            }

    # -------------------------------------------------------------------------
    # ORM Methods
    # -------------------------------------------------------------------------

    def _attachForeignKeyRelations(self, document):
        sql = """
        SELECT c.name
        FROM document as a
        INNER JOIN membership as b on a.id = b.doc_id
        INNER JOIN corpus as c on b.corpus_id = c.id
        WHERE a.id = %s;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (document['id'], ))
            corpora = [row[0] for row in cur]

        document['corpus'] = corpora
        return document

    def get(self, id, includeRelations=False):
        template = "SELECT {0} FROM document WHERE id = %s;"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql, (id, ))
            record = cur.fetchone()

        if not record:
            return None

        document = {x[0]:x[1] for x in zip(self.allFields, record) }
        if includeRelations:
            return self._attachForeignKeyRelations(document)
        return document

    def getAll(self):
        template = "SELECT {0} FROM document"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql)
            for record in cur:
                yield {x[0]:x[1] for x in zip(self.allFields, record)}

    def getMembersOf(self, corpus_id):
        template = """
        SELECT {0}
        FROM document
        INNER JOIN membership as m on m.doc_id = id
        WHERE m.corpus_id = %s;
        """
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql, (corpus_id, ))
            return [{x[0]:x[1] 
                     for x in zip(self.allFields, record)}
                     for record in cur 
                    ]

    def getThese(self, *list):
        if not list:
            return {}

        template = "SELECT {0} FROM document WHERE id IN ({1})"
        sql = template.format(', '.join(self.allFields),
                              ', '.join([str(x) for x in list]))

        with self.conn.cursor() as cur:
            cur.execute(sql)
            return {record[0]: {x[0]:x[1] 
                                for x in zip(self.allFields, record)}
                    for record in cur
                    }

    def find(self, fields, multipleMeansOr=True):
        keys = {k for k in fields if k in self.allFields}
        if not keys:
            allFields = ', '.join(self.allFields)
            raise ValueError('Search only works on {0}'.format(allFields))

        template = "SELECT {0} FROM document WHERE {1};"
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

    def filter(self, searchText):
        if not searchText:
            raise StopIteration

        template = """
        SELECT {0} FROM document 
        WHERE title ILIKE %s OR authors ILIKE %s OR path LIKE %s
        """
        sql = template.format(', '.join(self.allFields))
        params = [x.format(searchText) for x in ["%{0}%", "%{0}%", "%/{0}%"]]

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            for record in cur:
                yield {x[0]:x[1] for x in zip(self.allFields, record)}

    def add(self, doc, *corpora):
        template = "INSERT INTO document ({0}) VALUES ({1}) RETURNING ID;"
        sql = template.format(', '.join(self.dataFields),
                              ', '.join(['%({0})s'.format(x) 
                                         for x in self.dataFields]))

        with self.conn.cursor() as cur:
            cur.execute(sql, doc)
            id = cur.fetchone()[0]

        if corpora:
            repo = Corpus(self.conn)
            for c in corpora:
                corpus = repo.findOrAdd(c)
                self.addMembership(id, corpus['id'])

        return id

    def addMembership(self, id, corpus_id):
        sql = "INSERT INTO membership (doc_id, corpus_id) VALUES (%s, %s)"
        with self.conn.cursor() as cur:
            cur.execute(sql, (id, corpus_id))

    def removeMembership(self, id, corpus_id):
        sql = """
        DELETE FROM membership
        WHERE doc_id = %s
          AND corpus_id = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (id, corpus_id))
            affected = cur.rowcount

        if not affected:
            t = "Error deleting membership. doc={0} or corpus={1} not found"
            raise KeyError(t.format(id, corpus_id))

        return affected == 1

    def restamp(self, id):
        sql = """
        UPDATE document 
        SET scanned = now() 
        WHERE id = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (id, ))

    def update(self, doc):
        keys = {k for k in doc if k in self.dataFields}
        if not keys:
            fields = ', '.join(self.dataFields)
            raise ValueError('Update only works on {0}'.format(fields))

        template = "UPDATE document SET {0} WHERE id = %(id)s;"
        sql = template.format(', '.join(['{0} = %({0})s'.format(x) 
                                         for x in keys]))

        with self.conn.cursor() as cur:
            cur.execute(sql, doc)
            affected = cur.rowcount

        if not affected:
            templ = "Document not updated. Possible cause: id = {0} not found"
            raise KeyError(templ.format(doc['id']))

        return affected == 1

    def delete(self, id):
        sql = "DELETE FROM document WHERE id = %s;"
        
        with self.conn.cursor() as cur:
            cur.execute(sql, (id, ))
            affected = cur.rowcount

        if not affected:
            t = "Error deleting document. Possible cause: id = {0} not found"
            raise KeyError(t.format(id))

        return affected == 1
