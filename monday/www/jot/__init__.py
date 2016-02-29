from pathlib import Path
print('Importing', Path(__file__).resolve())

from .xray import XRay, WordInstance
#from .jot import Jot
from .morphology import Morphology
#from .compoundTagger import CompoundTagger
from .jotter import Jotter
#from .tfidf import Tf_Idf