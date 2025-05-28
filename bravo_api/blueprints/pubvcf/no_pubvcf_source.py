import logging
from flask_caching import Cache
from cachelib import BaseCache, NullCache

logger = logging.getLogger(__name__)


class NoPubVcfSource():

    def __init__(self, src: str = "", cache_klass: [BaseCache, Cache] = NullCache):
        self.cache = cache_klass()
        self.src = src

    def get_url(self, chrom: str, userid: str):
        return None

    def available_vcfs(self):
        return []
