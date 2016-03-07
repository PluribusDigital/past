import sys
import nltk
import unicodedata
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from collections import Counter
from jot import Morphology, XRay, CompoundTagger

def buildTranslateTable():
    ''' Creates the default table for replacing accented and non-english \
    characters with an ASCII equivalent.  
    This only works for single character replacement.
    '''
    table = {}
    if sys.version >= '3':
        table = dict.fromkeys(c for c in range(sys.maxunicode)
                                if unicodedata.combining(chr(c)))
    else:
        table = dict.fromkeys(c for c in range(sys.maxunicode)
                                if unicodedata.combining(unichr(c)))

    # punctuation
    table[0x2013] = u"-"
    table[0x2014] = u"-"
    table[0x2018] = u"'"
    table[0x2019] = u"'"
    table[0x201C] = u'"'
    table[0x201D] = u'"'
    table[0x2022] = u'*'      # bullet
    table[0x2044] = u'/'
    table[10] = u' '
    table[13] = u' '

    return table

def lowerCase(x):
    for wi in x:
        wi.token = wi.token.lower()

    return x

# -----------------------------------------------------------------------------
# Partial/Curry Methods
# -----------------------------------------------------------------------------

def bindLemma(lemmatizer):
    lemma_map = {'ADJ': 'a', 'AUX': 'v', 'VERB': 'v', 'ADV': 'r'}

    def bind(x):
        for wi in x:
            lemma_pos = lemma_map[wi.pos] if wi.pos in lemma_map else 'n'
            wi.lemma = lemmatizer(wi.token, lemma_pos)

        return x
    return bind

def bindMorphology(morphology):
    def bind(x):
        for wi in x:
            row = morphology.tryGetAddPenn(wi.pos_penn)
            wi.pos = row['universal']
            wi.morph_id = row['id']

        return x
    return bind

def bindStemmer(stemmer):
    def bind(x):
        for wi in x:
            wi.stem = stemmer(wi.lemma)
        return x
    return bind

def bindTagger(tagger):
    def bind(x):
        all = list(x.sents)
        tags = [tag for s in tagger(all) for word, tag in s]
        for i, wi in enumerate(x):
            wi.pos_penn = tags[i]

        return x
    return bind

def bindTokenizer(tokenizer, translateTable):
    def unit(reader):
        i = 0
        x = XRay()

        for text, context in reader:
            sent = unicodedata.normalize('NFKD', text)
            sent = sent.translate(translateTable)
            sent = sent.strip()
            if not sent:
                continue

            tokens = tokenizer(sent)
            for token in tokens:
                x.addToken(token, context, i)   
                if token in ['.', ';', ':']:
                    i += 1
        return x
    return unit

class Jotter(object):
    """ Creates a list of `jots` from a source reader
    """

    # -------------------------------------------------------------------------
    # Factory Methods
    # -------------------------------------------------------------------------
    @classmethod
    def build(cls):
        #path = 'taggers/maxent_treebank_pos_tagger/english.pickle'
        #tagger = nltk.data.load(path).tag_sents
        tagger = CompoundTagger()

        connection = ''

        pipeline = [
                    bindTagger(tagger),
                    lowerCase,
                    bindMorphology(Morphology(connection)),
                    bindLemma(WordNetLemmatizer().lemmatize),
                    bindStemmer(SnowballStemmer("english").stem)
                    ]

        return Jotter(bindTokenizer(nltk.word_tokenize, buildTranslateTable()), 
                      pipeline)

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self, unit, pipeline):
        self.unit = unit
        self.pipeline = pipeline

    # -------------------------------------------------------------------------
    # Contract Methods
    # -------------------------------------------------------------------------

    def run(self, reader, doc_id):

        # Execute pipeline methods
        x = self.unit(reader)
        for fn in self.pipeline:
            x = fn(x)

        # Tally
        total = Counter(x.jots)

        # Emit the results
        for mk in total:
            yield {
                'token': mk[0],
                'lemma': mk[1],
                'stem': mk[2],
                'pos': mk[3],
                'morph_id': mk[4],
                'syntax_id': mk[5],
                'doc_id': doc_id,
                'count': total[mk]
                }

    