"""
Provide Crams from S3 Bucket.
"""
import logging
import boto3
import re
import gzip
import pysam
import io
import hashlib
import tempfile
from bravo_api.core.cram_source import (CramSource, CramSourceInaccessibleError,
                                        ReferenceInaccessibleError)
from pathlib import Path
from flask_caching import Cache
from cachelib import BaseCache, SimpleCache
from urllib.parse import urlparse
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class S3CramSource(CramSource):

    def __init__(self, src: str, ref: str, cache: [BaseCache, Cache] = None):
        """
        :param src: S3 url of the prefix containing the runtime data as a string
            E.g. s3://mybucket/data/runtime/crams
        """
        self.client = boto3.client('s3')
        self.source = src.rstrip('/')
        self.varmap_url = f'{self.source}/variant_map.tsv.gz'
        self.ref_path = Path(ref)

        self.max_hom_hets = None
        self.contigs = set()
        self.contigs_chr_prefixed = True

        # self.validate()
        self.configure_from_variant_map()

        logger.debug('S3CramSource initialized Logged')

        if(cache is None):
            self.cache = SimpleCache(threshold=10)
        else:
            self.cache = cache

    #############
    # Interface #
    #############

    def get_info(self, variant_id):
        """
        :param variant_id: chrom-pos-ref-alt identifier of variant.
        """
        chrom, pos, ref, alt = variant_id.split('-')
        chrom = CramSource.normalize_contig_prefix(chrom, self.contigs_chr_prefixed)
        if chrom not in self.contigs:
            return []
        else:
            return S3CramSource.get_sequences_info(self.varmap_url, chrom, int(pos), ref, alt)

    def get_crai(self, variant_id, sample_no: int, sample_het: bool) -> io.BytesIO:
        """ Crai for data of individual sample that is representative of given variant

        :param variant_id: chrom-pos-ref-alt identifier of variant.
        :param sample_no: index of the homozygous sample identifier for which to return data.
        :param sample_het: T/F indicating if sample ids should be taken from het column.

        :return: contents of the bai file wrapped in BytesIO instance
        """
        chrom, pos, ref, alt = variant_id.split('-')
        chrom = CramSource.normalize_contig_prefix(chrom, self.contigs_chr_prefixed)

        sample_id = S3CramSource.lookup_sample_id(self.varmap_url, chrom, pos, ref, alt,
                                                sample_het, sample_no)
        logger.debug('sample_id: %s', sample_id)
        cram_url = self.calc_cram_url(sample_id)

        bai_data = self.get_bai_data(cram_url, chrom, pos, ref, alt, sample_het, sample_no)
        return(io.BytesIO(bai_data))

    def get_cram(self, variant_id: str, sample_no: int, sample_het: bool,
                 start_byte: int = None, stop_byte: int = None) -> dict:
        """ Subset cram data for individual sample representing a variant.

        :param variant_id: chrom-pos-ref-alt identifier of variant.
        :param sample_no: index of the homozygous sample identifier for which to return data.
        :param sample_het: T/F indicating if sample ids should be taken from het column.
        :param start_byte: position from Content-Header Range. Position should be included in data.
        :param stop_byte: position from Content-Header Range. Position should be included in data.

        :return: Dictionary with ByteIO contents of bam file and start,stop,size
            suitable for http Content-Range header.
        """
        chrom, pos, ref, alt = variant_id.split('-')
        chrom = CramSource.normalize_contig_prefix(chrom, self.contigs_chr_prefixed)

        # Lookup sample_id
        sample_id = S3CramSource.lookup_sample_id(self.varmap_url, chrom, pos, ref, alt,
                                                sample_het, sample_no)

        # Lookup cram_path
        cram_url = self.calc_cram_url(sample_id)

        # Get bam data from the cram
        bam_data = self.get_bam_data(cram_url, chrom, pos, ref, alt, sample_het, sample_no)

        data_size = len(bam_data)

        if start_byte is None or start_byte < 0:
            start_byte = 0

        correct_stop = CramSource.rectify_stop_byte(start_byte, stop_byte, data_size)

        bam_slice = bam_data[start_byte:correct_stop]
        bam_io = io.BytesIO(bam_slice)

        return {'file_bytes': bam_io, 'start_byte': start_byte,
                'stop_byte': stop_byte, 'file_size': data_size}

    def validate(self):
        """
        Validate that the bucket, prefix, and objects are accessible.
        """
        S3CramSource.validate_ref_path(self.ref_path)
        S3CramSource.validate_bucket_varmap(self.source, self.client)
        S3CramSource.validate_bucket_crams(self.source, self.client)

        return True

    ##################
    # Implementation #
    ##################

    def configure_from_variant_map(self):
        self.max_hom_hets = S3CramSource.extract_max_het_hom(self.varmap_url, self.client)
        self.contigs = S3CramSource.extract_contigs(self.varmap_url)
        self.contigs_chr_prefixed = S3CramSource.are_contigs_chr_prefixed(self.contigs)

    def calc_cram_url(self, sample_id) -> str:
        id_hash = hashlib.md5(sample_id.encode()).hexdigest()[:2]
        return(f'{self.source}/sequences/{id_hash}/{sample_id}.cram')

    def get_bai_data(self, cram_url, chrom, pos, ref, alt, sample_no, sample_het=None) -> bytes:
        return(self.get_data('bai', cram_url, chrom, pos, ref, alt, sample_no, sample_het))

    def get_data(self, key_suffix: str, cram_url: str, chrom: str, pos: int, ref: str, alt: str,
                 sample_no, sample_het=None) -> bytes:
        base_key = f'{chrom}-{pos}-{ref}-{alt}-{sample_het}-{sample_no}'
        target_data = self.cache.get(f'{base_key}-{key_suffix}')
        if target_data is None:
            combined_data = S3CramSource.extract_bam_subset(cram_url, self.ref_path, chrom, pos)
            self.cache_combined_data(base_key, combined_data)
            target_data = combined_data[key_suffix]
        return(target_data)

    def cache_combined_data(self, base_key: str, bam_data: dict) -> None:
        self.cache.set(f'{base_key}-bam', bam_data['bam'])
        self.cache.set(f'{base_key}-bai', bam_data['bai'])

    def get_bam_data(self, cram_path, chrom, pos, ref, alt, sample_no, sample_het=None) -> bytes:
        return(self.get_data('bam', cram_path, chrom, pos, ref, alt, sample_no, sample_het))

    def get_bai_data(self, cram_path, chrom, pos, ref, alt, sample_no, sample_het=None) -> bytes:
        return(self.get_data('bai', cram_path, chrom, pos, ref, alt, sample_no, sample_het))

    def get_data(self, key_suffix, cram_path, chrom, pos, ref, alt,
                 sample_no, sample_het=None) -> bytes:
        base_key = f'{chrom}-{pos}-{ref}-{alt}-{sample_het}-{sample_no}'
        target_data = self.cache.get(f'{base_key}-{key_suffix}')
        if target_data is None:
            combined_data = S3CramSource.extract_bam_subset(cram_path, self.ref_path, chrom, pos)
            self.cache_combined_data(base_key, combined_data)
            target_data = combined_data[key_suffix]
        return(target_data)

    @staticmethod
    def extract_bam_subset(cram_url: str, ref_path: str, chrom: str, pos: str):
        window = 100
        ipos = int(pos)
        bam_arr = bytearray()
        bai_arr = bytearray()
        with pysam.AlignmentFile(cram_url, 'rc', reference_filename=ref_path) as icram,\
                tempfile.NamedTemporaryFile(mode='w+b', suffix='.bam', delete=False) as btmp:

            # Write a bam file
            ofile = pysam.AlignmentFile(btmp, 'wb', reference_filename=ref_path,
                                        header=icram.header)
            for read in icram.fetch(chrom, max(0, ipos - window), ipos + window):
                ofile.write(read)
            ofile.close()

            # Read bamfile back into memory (pysam requires file name)
            btmp.seek(0, io.SEEK_SET)
            bam_arr = bytearray(btmp.read(-1))

            # Index the bam file
            pysam.index(btmp.name)

            # Read the contents of index (pysam requires file name)
            with open(f'{btmp.name}.bai', 'rb') as ifile:
                bai_arr = bytearray(ifile.read(-1))

        return {'bam': bam_arr, 'bai': bai_arr}

    @staticmethod
    def lookup_sample_id(varmap_url: str, chrom: str, pos: str, ref: str, alt: str,
                         het: bool, sample_no: int) -> str:
        logger.debug(f'lookup id: {varmap_url}, {chrom}, {pos}, {ref}, {alt}, {het}, {sample_no}')
        id = None
        pos = int(pos)
        with pysam.TabixFile(varmap_url, parser=pysam.asTuple()) as itabix:
            for row in itabix.fetch(chrom, pos - 1, pos):
                id = S3CramSource.extract_sample_id(row, pos, ref, alt, het, sample_no)
                if id is not None:
                    break
        return id

    @staticmethod
    def get_sequences_info(varmap_url, chrom, pos, ref, alt):
        with pysam.TabixFile(varmap_url, parser=pysam.asTuple()) as itabix:
            return CramSource.het_hom_counts(itabix, chrom, pos, ref, alt)

    @staticmethod
    def extract_contigs(varmap_url: str):
        """
        :param varmap_url: S3 url to variant_map.tsv.gz
        """
        contigs = set()
        with pysam.TabixFile(varmap_url) as itabix:
            contigs = set(itabix.contigs)
        return(contigs)

    @staticmethod
    def extract_max_het_hom(varmap_url, client):
        """
        :param varmap_url: S3 url to variant_map.tsv.gz
        """
        split_url = urlparse(varmap_url)
        bucket = split_url.netloc
        key = split_url.path.lstrip('/')

        header_hom_hets = None

        try:
            resp = client.get_object(Bucket=bucket, Key=key)
        except ClientError as err:
            msg = err.response['Error']['Message']
            raise CramSourceInaccessibleError(f'Error while reading header of variant map: {msg}')

        body = resp.get('Body', b'')
        with gzip.open(body, 'rt') as ifile:
            for line in ifile:
                if not line.startswith('#'):
                    break
                if line.startswith('#MAX_RANDOM_HOM_HETS='):
                    header_hom_hets = int(line.rstrip().split('=')[1].strip())
        return(header_hom_hets)

    @staticmethod
    def validate_ref_path(ref_path: Path):
        if(not(ref_path.is_file())):
            msg = (f'Reference file must exist: {ref_path}')
            raise ReferenceInaccessibleError(msg)

        if(not(ref_path.with_suffix('.fa.fai').is_file())):
            msg = (f'Reference file index must exist: {ref_path}.fai')
            raise ReferenceInaccessibleError(msg)

        return True

    @staticmethod
    def validate_bucket_varmap(url, client):
        split_url = urlparse(url)
        bucket = split_url.netloc
        prefix = split_url.path.lstrip('/')

        varmap_key = f'{prefix}/variant_map.tsv.gz'
        varmap_idx_key = f'{prefix}/variant_map.tsv.gz.tbi'

        # Verify expected protocol.
        if split_url.scheme != "s3":
            raise CramSourceInaccessibleError('Url scheme is not s3')

        try:
            client.head_object(Bucket=bucket, Key=varmap_key)
            varmap_present = True
        except ClientError as err:
            if err.response['Error']['Code'] == '404':
                varmap_present = False
            else:
                msg = err.response['Error']['Message']
                raise CramSourceInaccessibleError(f'Error while checking for variant map: {msg}')

        try:
            client.head_object(Bucket=bucket, Key=varmap_idx_key)
            varmap_idx_present = True
        except ClientError as err:
            if err.response['Error']['Code'] == '404':
                varmap_idx_present = False
            else:
                msg = err.response['Error']['Message']
                raise CramSourceInaccessibleError(
                    f'Error while checking for variant map index: {msg}')

        if not varmap_present:
            raise CramSourceInaccessibleError(f'Missing variant map: {varmap_key}')

        if not varmap_idx_present:
            raise CramSourceInaccessibleError(f'Missing variant map index: {varmap_idx_key}')

        return True

    @staticmethod
    def validate_bucket_crams(url, client):
        """
        :param url: S3 url to the crams prefix without trailing slash.
        """
        split_url = urlparse(url)
        bucket = split_url.netloc
        prefix = split_url.path.lstrip('/')

        # prefix to the sequences "directory" under than crams prefix
        seq_prefix = f'{prefix}/sequences/'

        try:
            resp = client.list_objects_v2(Bucket=bucket, Prefix=seq_prefix, MaxKeys=20)
        except ClientError as err:
            msg = err.response['Error']['Message']
            raise CramSourceInaccessibleError(f'{split_url.netloc}: {msg}')

        if resp['KeyCount'] == 0:
            raise CramSourceInaccessibleError(f'{bucket}/{seq_prefix} is empty')

        seq_keys = [item['Key'] for item in resp['Contents']]

        cram_patt = r'.*\.cram$'
        cram_matches = [re.search(cram_patt, item) is not None for item in seq_keys]

        if not any(cram_matches):
            raise CramSourceInaccessibleError(
                f'No cram files found in first 20 keys under: {bucket}/{seq_prefix}')

        return True
