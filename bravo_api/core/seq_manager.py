class SequencesClient(object):
    @property
    def window_bp(self):
        self._window_bp

    def __init__(self, cram_src, reference_path, cache_dir):
        self._cram_src = cram_src
