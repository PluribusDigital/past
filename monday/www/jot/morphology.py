import nltk
import sys

class Morphology(object):
    """Object relational mapper for the `morphology` table"""

    table = {}

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, connection):
        #self.conn = connection
        #with self.conn.cursor() as cur:
        #    cur.execute('SELECT id, tagset_penn, tagset_universal FROM morphology;')
        #    for id, k, univ in cur:
        #        self.table[k] = {'universal': univ, 'id':id}
        self.table = {
            "!": {'id':1, 'universal':"PUNCT"},
            '"': {'id':2, 'universal':"PUNCT"},
            "'": {'id':3, 'universal':"PUNCT"},
            "''": {'id':4, 'universal':"PUNCT"},
            ",": {'id':5, 'universal':"PUNCT"},
            ".": {'id':6, 'universal':"PUNCT"},
            ":": {'id':7, 'universal':"PUNCT"},
            "?": {'id':8, 'universal':"PUNCT"},
            "CC": {'id': 9, 'universal':"CONJ"},
            "CD": {'id': 10, 'universal':"NUM"},
            "DT": {'id': 11, 'universal':"DET"},
            "EX": {'id': 12, 'universal':"ADV"},
            "FW": {'id': 13, 'universal':"X"},
            "IN": {'id': 14, 'universal':"ADP"},
            "JJ": {'id': 15, 'universal':"ADJ"},
            "JJR": {'id': 16, 'universal':"ADJ"},
            "JJS": {'id': 17, 'universal':"ADJ"},
            "LS": {'id': 18, 'universal':"NUM"},
            "MD": {'id': 19, 'universal':"AUX"},
            "NN": {'id': 20, 'universal':"NOUN"},
            "NNP": {'id': 21, 'universal':"NOUN"},
            "NNPS": {'id': 22, 'universal':"NOUN"},
            "NNS": {'id': 23, 'universal':"NOUN"},
            "PDT": {'id': 24, 'universal':"DET"},
            "POS": {'id': 25, 'universal':"PART"},
            "PRP": {'id': 26, 'universal':"PRON"},
            "PRP$": {'id': 27, 'universal':"DET"},
            "RB": {'id': 28, 'universal':"ADV"},
            "RBR": {'id': 29, 'universal':"ADV"},
            "RBS": {'id': 30, 'universal':"ADV"},
            "RP": {'id': 31, 'universal':"PART"},
            "SYM": {'id': 32, 'universal':"SYM"},
            "TO": {'id': 33, 'universal':"PART"},
            "UH": {'id': 34, 'universal':"INTJ"},
            "VB": {'id': 35, 'universal':"VERB"},
            "VBD": {'id': 36, 'universal':"VERB"},
            "VBG": {'id': 37, 'universal':"VERB"},
            "VBN": {'id': 38, 'universal':"VERB"},
            "VBP": {'id': 39, 'universal':"VERB"},
            "VBZ": {'id': 40, 'universal':"VERB"},
            "WDT": {'id': 41, 'universal':"DET"},
            "WP": {'id': 42, 'universal':"PRON"},
            "WP$": {'id': 43, 'universal':"DET"},
            "WRB": {'id': 44, 'universal':"ADV"},
            "``": {'id':45, 'universal':"PUNCT"},
            "-NONE-": {'id': 46, 'universal':"X"},
            "#": {'id': 47, 'universal':"SYM"},
            "$": {'id': 48, 'universal':"SYM"},
            "(": {'id': 49, 'universal':"PUNCT"},
            ")": {'id': 50, 'universal':"PUNCT"}
            }

    # -------------------------------------------------------------------------
    # CRUD Methods
    # -------------------------------------------------------------------------

    def tryGetAddPenn(self, tag):
        if tag not in self.table:
            sys.stderr.write('{0} not found in table\n.'.format(tag))
            with self.conn.cursor() as cur:
                cur.execute("""INSERT INTO morphology 
                (tagset_universal, tagset_penn) VALUES (%s, %s)
                RETURNING id
                """, ('X', tag))
                id = cur.fetchone()[0]
            self.table[tag] = {'id': id, 'universal': 'X'}

        return self.table[tag]


