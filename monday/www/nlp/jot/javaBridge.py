import os
import sys
import tempfile
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

from nltk.internals import find_file, find_binary, find_jar, config_java, _java_options, _decode_stdoutdata

_stanford_url = 'http://nlp.stanford.edu/software'

class Channels():
    def __init__(self, encoding='utf8'):
        self.inputPath = ''
        self._encoding = encoding

    def __enter__(self):
        self.inputPath = self.getTempFileName()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.unlink(self.inputPath)

    # -------------------------------------------------------------------------

    def getTempFileName(self):
        fh, filePath = tempfile.mkstemp(text=True)
        os.close(fh)
        return filePath

    # -------------------------------------------------------------------------

    def send(self, sentences):
        with open(self.inputPath, 'wb') as f:
            for x in sentences:
                s = ' '.join(x)
                f.write(s.encode(self._encoding))
                f.write('\n')

class JavaBridge():
    _SEPARATOR = '_'
    _JAR = 'stanford-postagger.jar'

    # -------------------------------------------------------------------------

    def __init__(self, model_filename, encoding='utf8', verbose=False, java_options='-mx1000m'):
        self._stanford_jar = find_jar(
                self._JAR, None,
                searchpath=(), url=_stanford_url,
                verbose=verbose)

        self._stanford_model = find_file(model_filename,
                env_vars=('STANFORD_MODELS',), verbose=verbose)

        self.java_bin = find_binary('java', None, 
                                    env_vars=['JAVAHOME', 'JAVA_HOME'], 
                                    verbose=verbose, binary_names=['java.exe'])

        self._encoding = encoding
        self.java_options = java_options

    # -------------------------------------------------------------------------

    def getTempFileName(self):
        fh, filePath = tempfile.mkstemp(text=True)
        os.close(fh)
        return filePath

    # -------------------------------------------------------------------------

    def tag_sents(self, sentences):
        encoding = self._encoding
        default_options = ' '.join(_java_options)
        config_java(options=self.java_options, verbose=False)

        cmd = list(self._cmd)
        cmd.extend(['-encoding', encoding])
        
        # Set up the classpath.
        classpaths=[self._stanford_jar]
        classpath=os.path.pathsep.join(classpaths)

        # Construct the full command string.
        cmd = list(cmd)
        cmd = ['-cp', classpath] + cmd
        cmd = [self.java_bin] + _java_options + cmd

        # Establish communication with Java
        with Channels(encoding) as c:
            c.send(sentences)

            with open(c.inputPath, 'rb') as fin:        
                # Call java via a subprocess
                p = subprocess.Popen(cmd, stdin=fin,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    stanpos_output, _stderr = p.communicate(timeout=30)
                except subprocess.TimeoutExpired:
                    p.terminate()
                    p.kill()
                    stanpos_output, _stderr = ('', '')

        # Check the return code.
        if p.returncode != 0:
            sys.stderr.write('{0}\n'.format(_decode_stdoutdata(_stderr)))
            sys.stderr.flush()
            raise OSError('Java command failed : ' + str(cmd))

        stanpos_output = stanpos_output.decode(encoding)
        
        # Return java configurations to their default values
        config_java(options=default_options, verbose=False)
                
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

    @property
    def _cmd(self):
        return ['edu.stanford.nlp.tagger.maxent.MaxentTagger',
                '-model', self._stanford_model, 
                '-tokenize', 'false',
                '-outputFormatOptions', 'keepEmptySentences']
