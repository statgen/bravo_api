from abc import ABC, abstractmethod


class CramSource(ABC):
    """
    Validate and provide read from crams files.
    """

    def __init__(self, src, ref):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def read_seqs(pos, ref, alt, sample_no, sample_het):
        pass

    @abstractmethod
    def sample_id_to_location(sample_id):
        pass
