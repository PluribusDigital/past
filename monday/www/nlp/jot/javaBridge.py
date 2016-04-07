import os
import sys
import tempfile
import subprocess
import warnings

from nltk.internals import find_file, find_binary, find_jar, config_java, java, _java_options, _decode_stdoutdata
from nltk.tag.api import TaggerI
from nltk import compat

_stanford_url = 'http://nlp.stanford.edu/software'

class JavaBridge():
    _SEPARATOR = '_'
    _JAR = 'stanford-postagger.jar'

    def __init__(self, model_filename, encoding='utf8', 
                 verbose=False, java_options=['-mx1000m']):
        self._stanford_jar = find_jar(
                self._JAR, None,
                searchpath=(), url=_stanford_url,
                verbose=verbose)

        self._stanford_model = find_file(model_filename,
                env_vars=('STANFORD_MODELS',), verbose=verbose)
        self._encoding = encoding
        self.java_options = java_options
        self.java_bin = find_binary('java', None, 
                                    env_vars=['JAVAHOME', 'JAVA_HOME'], 
                                    verbose=verbose, binary_names=['java.exe'])

    def tag_sents(self, sentences):
        encoding = self._encoding
        #default_options = ' '.join(_java_options)
        #config_java(options=self.java_options, verbose=True)

        # Create a temporary input file
        #_input_fh, self._input_file_path = tempfile.mkstemp(text=True)

        cmd = ['-cp', self._stanford_jar,
               'edu.stanford.nlp.tagger.maxent.MaxentTagger',
               '-model', self._stanford_model, 
#               '-textFile', self._input_file_path, 
               '-tokenize', 'false',
               '-outputFormatOptions', 'keepEmptySentences',
               '-encoding', encoding]
        
        # Write the actual sentences to the temporary input file
        #_input_fh = os.fdopen(_input_fh, 'wb')
        _input = '\n'.join((' '.join(x) for x in sentences))
        if isinstance(_input, compat.text_type) and encoding:
            _input = _input.encode(encoding)
        #_input_fh.write(_input)
        #_input_fh.close()
        
        # Construct the full command string.
        cmd = [self.java_bin] + self.java_options + cmd

        # Call java via a subprocess
        p = subprocess.Popen(cmd, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             preexec_fn=os.setpgrp, shell=True)

        (stanpos_output, _stderr) = p.communicate(b'Hello .\n')

        sys.stderr.write('Here\n')
        sys.stderr.flush()

        # Delete the temporary file
        #os.unlink(self._input_file_path) 

        sys.stderr.write('Here\n')
        sys.stderr.flush()

        # Check the return code.
        if p.returncode != 0:
            sys.stderr.write(_decode_stdoutdata(_stderr))
            sys.stderr.write('\n')
            sys.stderr.flush()
            raise OSError('Java command failed : ' + str(cmd))

        sys.stderr.write('Here\n')
        sys.stderr.flush()

        stanpos_output = stanpos_output.decode(encoding)
        
        sys.stderr.write('Here\n')
        sys.stderr.flush()

        # Return java configurations to their default values
        #config_java(options=default_options, verbose=False)
                
        return self.parse_output(stanpos_output, sentences)

    def parse_output(self, text, sentences = None):
        # Output the tagged sentences
        tagged_sentences = []
        for tagged_sentence in text.strip().split("\n"):
            sentence = []
            for tagged_word in tagged_sentence.strip().split():
                word_tags = tagged_word.strip().split(self._SEPARATOR)
                sentence.append((''.join(word_tags[:-1]), word_tags[-1]))
            tagged_sentences.append(sentence)
        return tagged_sentences
