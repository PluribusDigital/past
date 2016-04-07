from nltk.tag import StanfordPOSTagger

# -----------------------------------------------------------------------------
# Single Tuple Processing Functions
# -----------------------------------------------------------------------------

def checkSymbols(t):
    word, tag = t
    if word in ['(', '[', '{']:
        return word, '('
    if word in [')', ']', '}']:
        return word, ')'
    if word in [unichr(0x00A7)]:
        return word, 'SYM'

    return word, tag

# -----------------------------------------------------------------------------
# Multiple Tuple Processing Functions
# -----------------------------------------------------------------------------

def pickWinner(a, b):
    assert(a[0] == b[0])  # the words should match!

    tagA = a[1]
    tagB = b[1]

    if tagB == 'FW': # the 'better' tagger is bad at words like 'kilobyte'
        return a[0], tagA

    return a[0], tagB

class CompoundTagger(object):
    """ This tagger takes the 'best' values from multiple taggers and 
    fixes up any glaring mistakes (e.g. '(' is tagged as NOUN) 
    """
    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------

    def __init__(self):
        self.taggerA = StanfordPOSTagger('english-left3words-distsim.tagger')
        #self.taggerB = StanfordPOSTagger('english-bidirectional-distsim.tagger',
        #                                 java_options='-mx3000m')

    def __call__(self, sents):
        # get the raw answers
        taggedA = self.taggerA.tag_sents(sents)

        #try:
        #    taggedB = self.taggerB.tag_sents(sents)

        #    # merge
        #    tagged0 = []
        #    for iSent in range(len(taggedA)):
        #        accum = []
        #        for iTuple in range(len(taggedA[iSent])):
        #            a = taggedA[iSent][iTuple]
        #            b = taggedB[iSent][iTuple]
        #            c = checkSymbols(pickWinner(a,b))
        #            accum.append(c)
        #        tagged0.append(accum)

        #    return tagged0
        #except OSError:
        return [[checkSymbols(t) for t in s] for s in taggedA] 
