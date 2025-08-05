"""
Provide Links to VCFs from S3 Bucket.
"""
import logging
import boto3
import re
import os
import boto3_refresh_session as brs
from typing import Union
from flask_caching import Cache
from cachelib import BaseCache, SimpleCache
from botocore.exceptions import ClientError
from botocore.config import Config
from urllib.parse import urlparse
from .pubvcf_source import PubVcfSource
from ec2_metadata import ec2_metadata


logger = logging.getLogger(__name__)


class S3PubVcfSource(PubVcfSource):

    def __init__(self, src: str, cache: Union[BaseCache, Cache, None] = None) -> None:
        """
        Depends on credentials providing region that matches the S3 bucket.
        :param src: String. S3 url of the prefix containing the runtime public vcfs
        :param cache: Cache instance. Defaults to use a new SimpleCache.
        """

        split_url = urlparse(src)
        self.bucket = split_url.netloc
        self.prefix = split_url.path.lstrip('/')
        self.suffix = "bravo.pub.vcf.gz"
        self.location = S3PubVcfSource._get_bucket_location(self.bucket)
        self.is_on_ec2 = S3PubVcfSource._is_running_in_ec2()

        if cache is None:
            self.cache = SimpleCache(threshold=10)
        else:
            self.cache = cache

        self.client = S3PubVcfSource._get_region_matched_client(self.location)

        logger.debug(f"S3CramSource: {self.bucket} {self.prefix} {self.suffix}")

    #
    # Static Methods
    #
    @staticmethod
    def _is_running_in_ec2():
        try:
            ec2_metadata
            result = True
        except IOError:
            logger.debug("Timeout waiting for EC2 metadata. Not running in EC2.")
            result = False
        return result

    @staticmethod
    def _get_bucket_location(bucket):
        scout = boto3.client('s3')
        location_resp = scout.get_bucket_location(Bucket=bucket)
        bucket_location = location_resp['LocationConstraint']
        logger.debug(f"S3CramSource Region: {bucket_location}")

        return bucket_location

    @staticmethod
    def _generate_session(bucket_location):
        try:
            role_arn = ec2_metadata.instance_profile_arn
            role_sess_name = f"{ec2_metadata.instance_id}-{os.getpid()}"

            assume_role_kwargs = {
                'RoleArn': role_arn,
                'RoleSessionName': role_sess_name,
                'DurationSeconds': 900,
            }
            session = brs.RefreshableSession(
                defer_refresh=False,
                assume_role_kwargs=assume_role_kwargs,
                region_name=bucket_location,
            )
        except IOError:
            logger.debug("Timeout waiting for EC2 metadata. Not running in EC2.")
            session = boto3.session.Session()

        return session

    @staticmethod
    def _get_region_matched_client(bucket_location):
        session = S3PubVcfSource._generate_session(bucket_location)
        client = session.client(service_name='s3',
                                config=Config(signature_version="s3v4",
                                              region_name=bucket_location))

        return client

    @staticmethod
    def _extract_chr(s3_key: str) -> Union[str, None]:
        chr_patt = r'chr[0-9X]{1,2}'
        hit = re.search(chr_patt, s3_key)
        if hit is not None:
            return s3_key[hit.start():hit.end()]
        return None

    #
    # Instance Methods
    #

    def _generate_url(self, chrom: str) -> Union[str, None]:
        """
        Generate presigned S3 url to retrieve public VCF for given chromosome.
        """
        # 6 hour expiration is max for IAM instance profile
        vcf_key = f"{self.prefix}/{chrom}.{self.suffix}"
        print(f"key: {vcf_key}")
        try:
            resp = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': vcf_key},
                ExpiresIn=900)
        except ClientError as err:
            logger.error(err)
            return None
        return resp

    #
    # ABC Overrides
    #
    def get_url(self, chrom: str, userid: str) -> Union[str, None]:
        """
        Cache and Return S3 url to retrieve public VCF for given chromosome.
        """
        url = self.cache.get(f"{userid}.{chrom}")
        if url:
            return url
        else:
            url = self._generate_url(chrom)
            self.cache.set(f"{userid}.{chrom}", url)

        return url

    def available_vcfs(self) -> list:
        """
        Cache and Return available public VCFs.
        """
        result = []

        try:
            resp = self.client.list_objects(Bucket=self.bucket, Prefix=self.prefix)
            result = [S3PubVcfSource._extract_chr(item["Key"]) for item in resp["Contents"]]
        except ClientError as err:
            logger.error(err)

        return result
