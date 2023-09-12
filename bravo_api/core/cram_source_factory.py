"""
Instantiate cram source class appropriate for the given source.
"""
from bravo_api.core.cram_source import CramSource
from bravo_api.core.fs_cram_source import FSCramSource
from bravo_api.core.s3_cram_source import S3CramSource


class CramSourceFactory():
    @staticmethod
    def build(src: str, ref: str, cache: str) -> CramSource:
        if src.startswith('s3://'):
            return(S3CramSource(src, ref, cache))
        else:
            return(FSCramSource(src, ref, cache))
