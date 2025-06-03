import logging
from flask_caching import Cache
from cachelib import BaseCache, NullCache

logger = logging.getLogger(__name__)


class NoPubVcfSource():

    def __init__(self, src: str = "", cache: [BaseCache, Cache, None] = None):
        self.src = src
        if cache is None:
            self.cache = NullCache()
        else:
            self.cache = cache

    def get_url(self, chrom: str, userid: str):
        return None

    def available_vcfs(self):
        return []
