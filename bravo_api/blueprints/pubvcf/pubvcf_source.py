from abc import ABC, abstractmethod
from typing import Union


class PubVcfSource(ABC):
    def __init__(self, src, cache):
        pass

    @abstractmethod
    def get_url(self, chrom: str, userid: str) -> Union[str, None]:
        pass

    @abstractmethod
    def available_vcfs(self) -> list:
        pass
