from typing import Union
from flask_caching import Cache
from cachelib import BaseCache
from .pubvcf_source import PubVcfSource
from .no_pubvcf_source import NoPubVcfSource
from .s3_pubvcf_source import S3PubVcfSource


class PubVcfSourceFactory():
    @staticmethod
    def build(src: str, cache: Union[BaseCache, Cache] = None) -> PubVcfSource:
        if src.startswith('s3://'):
            return(S3PubVcfSource(src, cache))
        else:
            return(NoPubVcfSource(src, cache))
