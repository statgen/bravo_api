from abc import ABC, abstractmethod


class CramSourceInaccessibleError(Exception):
    """
    Exception class indicating the CramSource data could not be read.
    """
    pass


class VariantMapError(Exception):
    """
    Exception class indicating a problem with the variant map data.
    """
    pass


class ReferenceInaccessibleError(Exception):
    """
    Exception class indicating the CramSource reference could not be read.
    """
    pass


class CramSource(ABC):
    """
    Validate and provide read from crams files.
    """

    _window_bp = 100

    def __init__(self, src, ref):
        pass

    @abstractmethod
    def get_info(self, variant_id):
        pass

    @abstractmethod
    def get_crai(self, variant_id, sample_no, sample_het):
        pass

    @abstractmethod
    def get_cram(self, variant_id, sample_no, sample_het, start_byte, stop_byte):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def read_seqs(self, pos, ref, alt, sample_no, sample_het):
        pass

    @abstractmethod
    def sample_id_to_location(self, sample_id):
        pass

