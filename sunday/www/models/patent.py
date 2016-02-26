def _projection(record, fields):
    return {x[0]:x[1] for x in zip(fields, record) }

class Patent(object):
    """ The object-relational mapper for the `patent` table
    """
    def __init__(self, connection):
        self.conn = connection
        self.dataFields = ['type', 'number', 'date', 'kind', 'abstract', 'title']
        self.allFields = ['id'] + self.dataFields
        self.template = """
        SELECT {0} 
        FROM patent as a
        INNER JOIN {1} on a.id = patent_id
        WHERE a.id = %s
        ORDER BY sequence;
        """

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _projectionMain(self, record):
        a = _projection(record, self.allFields)
        a['date'] = a['date'].isoformat()
        return a

    def _attachRelated(self, patent, fields, table):
        sql = self.template.format(','.join(fields), table)
        with self.conn.cursor() as cur:
            cur.execute(sql, (patent['id'], ))
            return [_projection(row, fields) for row in cur]

    def _attachAssignee(self, patent):
        fields = ['name_first', 'name_last', 'organization', 'sequence']
        patent['assignee'] = self._attachRelated(patent, fields, 'rawassignee')

    def _attachClaims(self, patent):
        fields = ['text', 'dependent', 'sequence']
        patent['claims'] = self._attachRelated(patent, fields, 'claim')

    def _attachInventor(self, patent):
        fields = ['name_first', 'name_last', 'sequence']
        patent['inventors'] = self._attachRelated(patent, fields, 'rawinventor')

    def _attachLawyer(self, patent):
        fields = ['name_first', 'name_last', 'organization', 'country', 
                  'sequence']
        patent['lawyers'] = self._attachRelated(patent, fields, 'rawlawyer')

    # -------------------------------------------------------------------------
    # ORM Methods
    # -------------------------------------------------------------------------

    def get(self, id, includeRelations=True):
        template = "SELECT {0} FROM patent WHERE id = %s;"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql, (id, ))
            record = cur.fetchone()

        if not record:
            return None

        patent = self._projectionMain(record)
        if includeRelations:
            self._attachClaims(patent)
            self._attachAssignee(patent)
            self._attachInventor(patent)
            self._attachLawyer(patent)
            return patent
        return patent

    def getAll(self):
        template = "SELECT {0} FROM patent"
        sql = template.format(', '.join(self.allFields))

        with self.conn.cursor() as cur:
            cur.execute(sql)
            for record in cur:
                yield self._projectionMain(record)
