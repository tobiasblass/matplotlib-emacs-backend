import logging
_log = logging.getLogger(__name__)

from matplotlib.backend_bases import (
    _Backend, FigureManagerBase)
import matplotlib.backends.backend_svg as backend_svg
import tempfile
import subprocess

def emacs_eval(expressions):
    "Evaluate the given expressions in the emacs server"
    command = ['emacsclient', '-e'] + expressions
    _log.debug("Running command %s", command)
    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        _log.error("Failed to run emacs command %s: %s", command, e.stderr)

import os
class ShareableTempFile():
    "Implements a temporary file that can be shared with other processes, even on windows."
    def __init__(self, suffix=None):
        handle, self.name = tempfile.mkstemp(suffix=suffix)
        self.file = os.fdopen(handle)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    def close(self):
        self.file.close()
        os.unlink(self.name)


@_Backend.export
class EmacsBackend(_Backend):
    FigureCanvas = backend_svg.FigureCanvas
    class FigureManager(FigureManagerBase):
        def __init__(self, canvas, num):
            super().__init__(canvas, num)
            _log.debug('Initializing FigureManager')
        def show(self):
            # Use insert-file-contents in the future
            with ShareableTempFile(suffix='.svg') as f:
                self.canvas.print_svg(f.name)
                emacs_eval(['''(with-current-buffer (get-buffer-create "*matplotlib*")
                                 (when (eq major-mode 'image-mode)
                                   (image-mode-as-text))
                                 (read-only-mode -1)
                                 (erase-buffer)
                                 (insert-file-contents "{}")
                                 (image-mode)
                                 (switch-to-buffer-other-window (current-buffer)))'''.format(os.path.abspath(f.name).replace('\\','/'))])
                

    def __init__(self, filename=None):
        super().__init__()
        _log.debug('Initializing backend')
        self.filename = filename
            
    def trigger_manager_draw(manager):
        _log.debug('Should trigger drawing of', manager, 'now')
    def mainloop():
        _log.debug('Should start the main loop now')
    
