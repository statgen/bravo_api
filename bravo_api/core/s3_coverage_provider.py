"""
Provide coverage bin data backed by an S3 object.
"""
from bravo_api.core.coverage_provider import CoverageProvider, CoverageSourceInaccessibleError
from urllib.parse import urlparse
import rapidjson
import pysam
import re
import boto3
from botocore.exceptions import ClientError


class S3CoverageProvider(CoverageProvider):

    def __init__(self, src):
        self.client = boto3.client('s3')
        self.src = src
        self.validate_source()
        # self.catalog = self.discover_files()

    def validate_source(self):
        """
        Validate that the bucket, prefix, and objects are accessible.
        """
        split_url = urlparse(self.src)

        # Verify expected protocol.
        if split_url.scheme != "s3":
            raise CoverageSourceInaccessibleError('Url scheme is not s3')

        # Check that objects exists in bucket at prefix.
        try:
            obj_resp = self.client.list_objects_v2(Bucket=split_url.netloc,
                                                   Prefix=split_url.path.lstrip('/'),
                                                   MaxKeys=10)
        except ClientError as err:
            msg = err.response['Error']['Message']
            raise CoverageSourceInaccessibleError(f'{split_url.netloc}: {msg}')

        # Check that a tsv.gz or tsv.gz.tbi accessible in first few keys
        patt = re.compile(r'.*gz(\.tbi)?$')
        obj_keys = [item['Key'] for item in obj_resp['Contents']]

        matches = map(patt.match, obj_keys)
        num_matches = sum(item is not None for item in matches)

        if num_matches < 1:
            raise CoverageSourceInaccessibleError('Did not find coverage (.gz) files.')

        return(True)

    def evaluate_chrom_representation(self):
        """
        All chromosomes expected to be represented in all coverage bins
        """
        msgs = []
        return(msgs)

    def evaluate_chrom_readability(self):
        """
        All coverage files expected to be readable
        """
        msgs = []
        return(msgs)

    def evaluate_catalog(self):
        warn_msgs = []
        warn_msgs.extend(self.evaluate_chrom_representation())
        warn_msgs.extend(self.evaluate_chrom_readability())
        return(warn_msgs)

    def discover_files(self):
        """
        Find and organize the chrN.bin_X.YZ.tar.gz coverage files into a dictionary organized by
        bin then chromosome.
        """
        result = {}
        return(result)

    def lookup_coverage_path(self, cov_bin, chrom):
        """
        Return path to a coverage file or None
        """
        return(self.catalog.get(cov_bin, {}).get(chrom))

    def coverage(self, cov_bin, chrom, start, stop):
        """
        Provide list of dicts of from the json data of appropriate coverate file
        """
        result = []

        # Get path from catalog
        cov_path = self.lookup_coverage_path(cov_bin, chrom)

        # Handle no path by returning no data.
        if(not cov_path):
            return(result)

        tabixfile = pysam.TabixFile(cov_path)

        for row in tabixfile.fetch(chrom, max(1, start - 1), stop, parser=pysam.asTuple()):
            result.append(rapidjson.loads(row[3]))

        return(result)
