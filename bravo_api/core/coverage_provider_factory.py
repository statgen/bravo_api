"""
Generate coverage provider appropriate for the coverage source.
"""
from bravo_api.core.coverage_provider import FSCoverageProvider, S3CoverageProvider


class CoverageProviderFactory():
    @staticmethod
    def build_provider(src):
        return(1)
