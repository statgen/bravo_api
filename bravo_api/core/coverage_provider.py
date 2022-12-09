"""
Coverage bins are:
    Continugous positions with difference in mean and median read depth less than the bin value
    are consolidate together.
"""
from abc import ABC, abstractmethod
from pathlib import Path


class CoverageSourceInaccessibleError(Exception):
    """
    Exception class indicating the source of a CoverageProvider could not be read
    """
    pass


class CoverageProvider(ABC):
    """
    Provide coverage data per binned resolution and chromosome
    """

    # Bins from coursest resolution to finest
    _bins = ['bin_0.25', 'bin_0.50', 'bin_0.75', 'bin_1.00', 'full']
    _chroms = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
               '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X']

    def __init__(self, src):
        self.source = Path(src)
        self.validate_source()
        self.catalog = self.discover_files()

    @property
    def bins(self):
        return(self._bins)

    @abstractmethod
    def validate_source(self):
        """
        Coverage source must be reachable and readable.
        """
        pass

    @abstractmethod
    def evaluate_catalog(self):
        """
        Compile list of warnings about issues with catalog.
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
