"""
Coverage bins are:
    Continugous positions with difference in mean and median read depth less than the bin value
    are consolidate together.
"""
from abc import ABC, abstractmethod, abstractproperty


class CoverageProvider(ABC):
    """
    Provide coverage data
    """

    def __init__(self, src):
        self.source = src
        self.catalog = self.discover_files(src)

    @abstractproperty
    def bins(self):
        pass

    @abstractmethod
    def validate(self):
        """
        At least one coverage file must be reachable.
        """
        pass

    @abstractmethod
    def evaluate_source(self):
        """
        Compile list of issues with source.
        """
        pass

    @abstractmethod
    def discover_files(self, src):
        """
        Create coverage catalog
        """
        pass

    @abstractmethod
    def coverage(chr, start, stop, bin):
        """
        Lookup coverage for range at given resolution
        """
        pass


class FSCoverageProvider(CoverageProvider):
    GLOB_SUFFIX = '*.tsv.gz'
    # Bins from coursest resolution to finest
    BINS = ['bin_0.25', 'bin_0.50', 'bin_0.75', 'bin_1.00', 'full']
    # Query lengths corresponding to resolution temp put here.
    QSIZE = [10_000, 3000, 1000, 300, 0]

    def validate(self):
        return(True)

    def evaluate_source(self):
        return([])

    def discover_files(self, src):
        return({})

    def coverage(self, chr, start, stop, bin):
        return([])
