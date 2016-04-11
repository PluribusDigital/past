import unittest
import json
import sys
from nlp.jot import JavaBridge, CompoundTagger

class Test_JavaBridge(unittest.TestCase):
    def setUp(self):
        self.sents = [
            'Call me Ishmael .'.split(),
            'Some years ago - never mind how long precisely - having little or no money in my purse , and nothing particular to interest me on shore , I thought I would sail about a little and see the watery part of the world .'.split(),
            'It is a way I have of driving off the spleen and regulating the circulation .'.split(),
            'Whenever I find myself growing grim about the mouth ;'.split(),
            'whenever it is a damp , drizzly November in my soul ;'.split(),
            'whenever I find myself involuntarily pausing before coffin warehouses , and bringing up the rear of every funeral I meet ;'.split(),
            "and especially whenever my hypos get such an upper hand of me , that it requires a strong moral principle to prevent me from deliberately stepping into the street , and methodically knocking people 's hats off".split(),
            'then , I account it high time to get to sea as soon as I can .'.split(),
            'This is my substitute for pistol and ball .'.split(), 
            'With a philosophical flourish Cato throws himself upon his sword ;'.split(),
            'I quietly take to the ship .'.split(),
            'There is nothing surprising in this .'.split(),
            'If they but knew it , almost all men in their degree , some time or other , cherish very nearly the same feelings towards the ocean with me .'.split()
            ]

        self.expected = [
            [(u'Call', u'VB'), (u'me', u'PRP'), (u'Ishmael', u'NNP'), (u'.', u'.')]
            ]

    def tearDown(self):
        pass

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def test_taggerA(self):
        target = JavaBridge('english-left3words-distsim.tagger')
        actual = target.tag_sents(self.sents)
        self.assertEqual(13, len(actual))

    def test_taggerB(self):
        target = JavaBridge('english-bidirectional-distsim.tagger')
        actual = target.tag_sents(self.sents)
        self.assertEqual(13, len(actual))

    def test_taggerC(self):
        target = CompoundTagger()
        actual = target(self.sents)
        for i,x in enumerate(actual):
            print(i, x)
        self.assertEqual(13, len(actual))

if __name__ == '__main__':
    unittest.main()
