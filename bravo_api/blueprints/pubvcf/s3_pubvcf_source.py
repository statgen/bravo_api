"""
Provide Links to VCFs from S3 Bucket.
"""
import logging
import boto3
from flask_caching import Cache
from cachelib import BaseCache, SimpleCache

logger = logging.getLogger(__name__)


class S3PubVcfSource():

    def __init__(self, src: str, ref: str, cache: [BaseCache, Cache] = None):
        """
        :param src: String. S3 url of the prefix containing the runtime public vcfs
        """
        self.client = boto3.client('s3')
        self.source = src.rstrip('/')

        logger.debug('S3CramSource initialized.')

        if(cache is None):
            self.cache = SimpleCache(threshold=10)
        else:
            self.cache = cache
