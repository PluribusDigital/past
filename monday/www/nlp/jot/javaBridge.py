import os
import sys
import tempfile
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess
import warnings

from nltk.internals import find_file, find_binary, find_jar, config_java, java, _java_options, _decode_stdoutdata
from nltk.tag import StanfordTagger
from nltk import compat

_stanford_url = 'http://nlp.stanford.edu/software'

class JavaBridge(StanfordTagger):
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

        # Create a temporary input file
        self._input_file_path = self.getTempFileName()

        cmd = list(self._cmd)
        cmd.extend(['-encoding', encoding])
        
        # Write the actual sentences to the temporary input file
        with open(self._input_file_path, 'wb') as finput:
            _input = '\n'.join((' '.join(x) for x in sentences))
            _input = _input.encode(encoding)
            finput.write(_input)
        
        # Set up the classpath.
        classpaths=[self._stanford_jar]
        classpath=os.path.pathsep.join(classpaths)

        # Construct the full command string.
        cmd = list(cmd)
        cmd = ['-cp', classpath] + cmd
        cmd = [self.java_bin] + _java_options + cmd

        # Call java via a subprocess
        p = subprocess.Popen(cmd, 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stanpos_output, _stderr = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            p.terminate()
            p.kill()
            stanpos_output, _stderr = p.communicate()

        # Delete the temporary file
        os.unlink(self._input_file_path) 

        sys.stderr.write('{0}\n'.format(_decode_stdoutdata(_stderr)))
        sys.stderr.flush()

        # Check the return code.
        if p.returncode != 0:
            #sys.stderr.write('{0}\n'.format(_decode_stdoutdata(_stderr)))
            #sys.stderr.flush()
            raise OSError('Java command failed : ' + str(cmd))

        stanpos_output = stanpos_output.decode(encoding)
        
        # Return java configurations to their default values
        config_java(options=default_options, verbose=False)
                
        return self.parse_output(stanpos_output, sentences)

    @property
    def _cmd(self):
        return ['edu.stanford.nlp.tagger.maxent.MaxentTagger',
                '-model', self._stanford_model, 
                '-textFile', self._input_file_path, 
                '-tokenize', 'false',
                '-outputFormatOptions', 'keepEmptySentences']
