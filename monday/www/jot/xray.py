
class WordInstance(object):
    """ A structure that holds the detailed decomposition of a token during 
    processing
    """
    def __init__(self, token, context='', sentence_id=0):
        self.sentence_id = sentence_id
        self.token = token
        self.lemma = token
        self.stem = token
        self.pos = 'X'
        self.pos_penn = 'FW'
        self.morph_id = 0
        self.syntax_id = 0
        self.context = context

    def __getitem__(self, name):
        return getattr(self, name)

class XRay(object):
    """ A structure that contains the detailed decomposition of a document
    It is the structure passed around the various processors
    """
    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------
    def __init__(self):
        self._raw = []

    def __iter__(self):
        return iter(self._raw)

    # -------------------------------------------------------------------------
    # NLTK-like properties
    # -------------------------------------------------------------------------

    @property
    def raw(self):
        """
        :return: the document as a single string.
        :rtype: str
        """
        return ' '.join(self.words)

    @property
    def words(self):
        """
        :return: the document as a list of words and punctuation symbols.
        :rtype: list(str)
        """
        for w in self._raw:
            yield w.token

    @property
    def sents(self):
        """
        :return: the document as a list of sentences or utterances, each 
            encoded as a list of word strings.
        :rtype: list(list(str))
        """
        i = 0
        accum = []
        for w in self._raw:
            if w.sentence_id != i:
                i = w.sentence_id
                yield accum
                accum = []
            accum.append(w.token)
        yield accum

    @property
    def tagged_words(self):
        """
        :return: the document as a list of tagged
            words and punctuation symbols, encoded as tuples
            ``(word,tag)``.
        :rtype: list(tuple(str,str))
        """
        for w in self._raw:
            yield (w.token, w.pos_penn)

    @property
    def tagged_sents(self):
        """
        :return: the document as a list of
            sentences, each encoded as a list of ``(word,tag)`` tuples.

        :rtype: list(list(tuple(str,str)))
        """
        i = 0
        accum = []
        for w in self._raw:
            if w.sentence_id != i:
                i = w.sentence_id
                yield accum
                accum = []
            accum.append((w.token, w.pos_penn))
        yield accum

    @property
    def chunked_words(self):
        """
        :return: the document as a list of tagged
            words and chunks.  Words are encoded as ``(word, tag)``
            tuples (if the corpus has tags) or word strings (if the
            corpus has no tags).  Chunks are encoded as depth-one
            trees over ``(word,tag)`` tuples or word strings.
        :rtype: list(tuple(str,str) and Tree)
        """
        pass

    @property
    def chunked_sents(self):
        """
        :return: the document as a list of sentences, each encoded as a Tree.  
            The leaves of these trees are encoded as ``(word, tag)`` tuples (if
            the corpus has tags) or word strings (if the corpus has no
            tags).
        :rtype: list(Tree)
        """
        pass

    @property
    def jots(self):
        """
        :return: the document as a list of `jots`.
        :rtype: list(subset of WordInstance)
        """
        jotFields = ['token', 'lemma', 'stem', 'pos', 'morph_id', 'syntax_id']
        for w in self._raw:
            yield tuple([w[k] for k in jotFields])
                
    # -------------------------------------------------------------------------
    # Mutating Methods
    # -------------------------------------------------------------------------

    def addToken(self, token, context='', sent_idx=0):
        """ Adds the smallest unit of information to the document x-ray
        :param token: a word or punctuation symbol
        :param context: where the token appeared in the document
        :param sent_idx: the sentence number within the document
        """
        self._raw.append(WordInstance(token, context, sent_idx))
