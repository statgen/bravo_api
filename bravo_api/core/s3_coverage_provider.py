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
from functools import reduce


class S3CoverageProvider(CoverageProvider):

    def __init__(self, src):
        self.client = boto3.client('s3')
        self.src = src
        split_url = urlparse(self.src)
        self.bucket = split_url.netloc
        self.prefix = split_url.path.lstrip('/')
        self.validate_source()
        self.catalog = self.discover_files()

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
            obj_resp = self.client.list_objects_v2(Bucket=self.bucket,
                                                   Prefix=self.prefix,
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
        Return list of messages to the contrary.
        """
        messages = []
        for bin_name, cov_bin in self.catalog.items():
            missing_chroms = [chrom for chrom in self._chroms if chrom not in cov_bin.keys()]
            if(missing_chroms):
                messages.append(f'Coverage {bin_name} missing chroms: {missing_chroms}')
        return(messages)

    @staticmethod
    def simple_dict_flat(acc, d):
        """
        Helper function for reducing list of non-nested dicts to list of values
        """
        acc.extend(list(d.values()))
        return(acc)

    def evaluate_chrom_readability(self):
        """
        All coverage files expected to be readable.
        Return list of messages to the contrary.
        """
        messages = []
        all_paths = reduce(S3CoverageProvider.simple_dict_flat, self.catalog.values(), [])

        for path in all_paths:
            try:
                self.client.head_object(Bucket=self.bucket, Key=path)
            except ClientError as err:
                err_msg = err.response['Error']['Message']
                messages.append(f'{self.bucket}/{path}: {err_msg}')
        return(messages)

    def evaluate_catalog(self):
        warn_msgs = []
        warn_msgs.extend(self.evaluate_chrom_representation())
        warn_msgs.extend(self.evaluate_chrom_readability())
        return(warn_msgs)

    def discover_files(self):
        """
        Find and organize the chrN.bin_X.YZ.tar.gz coverage files into a dictionary organized by
        bin then chromosome. Form of bin-chr-file index will be:
        {
          'bin_0.25': {'chr1': 's3://bucket/prefix/chr1.bin_0.25.tsv.gz',
                      ...,
                      'chr22': 's3://bucket/prefix/chr22.bin_0.25.tsv.gz'},
          ....
          'bin_full': {...}
        }
        """
        split_url = urlparse(self.src)
        bucket = split_url.netloc
        prefix = split_url.path.lstrip('/')

        obj_resp = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        all_keys = [item['Key'] for item in obj_resp['Contents']]

        chr_patt = re.compile(r'.*chr([0-9X]{1,2})')
        result = {}
        for bin_name in self._bins:
            result[bin_name] = {}
            bin_keys = [item for item in all_keys if item.startswith(f'{prefix}/{bin_name}')]

            for key in bin_keys:
                chr = chr_patt.match(key).group(1)
                result[bin_name][chr] = key
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
