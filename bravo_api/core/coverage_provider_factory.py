"""
Generate coverage provider appropriate for the coverage source.
"""
from bravo_api.core.coverage_provider import CoverageProvider
from bravo_api.core.fs_coverage_provider import FSCoverageProvider
from bravo_api.core.s3_coverage_provider import S3CoverageProvider


class CoverageProviderFactory():
    @staticmethod
    def build(src: str) -> CoverageProvider:
        if src.startswith('s3://'):
            return(S3CoverageProvider(src))
        else:
            return(FSCoverageProvider(src))
