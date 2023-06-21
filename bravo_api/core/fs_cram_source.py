from bravo_api.core.cram_source import (CramSource, CramSourceInaccessibleError,
                                        ReferenceInaccessibleError, VariantMapError)
from pathlib import Path
from cachelib import BaseCache, SimpleCache
from flask_caching import Cache
import gzip
import pysam
import io
import os
import hashlib
import tempfile
import logging


log = logging.getLogger(__name__)


class FSCramSource(CramSource):

    def __init__(self, src: str, ref: str, cache: [BaseCache, Cache] = None):
        self.source = Path(src)
        self.seq_dir = self.source.joinpath('sequences')
        self.variant_map = self.source.joinpath('variant_map.tsv.gz')
        self.ref_path = Path(ref)

        self.max_hom_hets = None
        self.contigs = set()
        self.contigs_chr_prefixed = True

        self.validate()
        self.configure_from_variant_map()

        if(cache is None):
            self.cache = SimpleCache(threshold=10)
        else:
            self.cache = cache

    #############
    # Interface #
    #############

    def get_info(self, variant_id):
        chrom, pos, ref, alt = variant_id.split('-')
        chrom = FSCramSource.normalize_contig_prefix(chrom, self.contigs_chr_prefixed)
        if chrom not in self.contigs:
            return []
        else:
            return FSCramSource.get_sequences_info(self.variant_map, chrom, int(pos), ref, alt)

    def get_crai(self, variant_id, sample_no, sample_het):
        """ Index of subset data for individual sample representing a variant

        :param variant_id: chrom-pos-ref-alt identifier of variant.
        :param sample_no: index of the homozygous sample identifier for which to return data.
        :param sample_het: T/F indicating if sample ids should be taken from het column.

        :return: contents of the bai file wrapped in BytesIO instance
        """
        chrom, pos, ref, alt = variant_id.split('-')
        chrom = FSCramSource.normalize_contig_prefix(chrom, self.contigs_chr_prefixed)

        sample_id = self.lookup_sample_id(chrom, pos, ref, alt, sample_het, sample_no)
        cram_path = self.calc_cram_path(sample_id)

        bai_data = self.get_bai_data(cram_path, chrom, pos, ref, alt, sample_het, sample_no)
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
        chrom = FSCramSource.normalize_contig_prefix(chrom, self.contigs_chr_prefixed)

        # Lookup sample_id
        sample_id = self.lookup_sample_id(chrom, pos, ref, alt, sample_het, sample_no)

        # Lookup cram_path
        cram_path = self.calc_cram_path(sample_id)

        # Get bam data from the cram
        bam_data = self.get_bam_data(cram_path, chrom, pos, ref, alt, sample_het, sample_no)

        data_size = len(bam_data)

        if start_byte is None or start_byte < 0:
            start_byte = 0

        correct_stop = FSCramSource.rectify_stop_byte(start_byte, stop_byte, data_size)

        bam_slice = bam_data[start_byte:correct_stop]
        bam_io = io.BytesIO(bam_slice)

        return {'file_bytes': bam_io, 'start_byte': start_byte,
                'stop_byte': stop_byte, 'file_size': data_size}

    ##################
    # Implementation #
    ##################

    @staticmethod
    def extract_max_het_hom(variant_map: Path):
        header_hom_hets = 0
        with gzip.open(str(variant_map), 'rt') as ifile:
            for line in ifile:
                if not line.startswith('#'):
                    break
                if line.startswith('#MAX_RANDOM_HOM_HETS='):
                    header_hom_hets = int(line.rstrip().split('=')[1].strip())

        if header_hom_hets <= 0:
            msg = (f'Invalid value for MAX_RANDOM_HOM_HETS: {header_hom_hets}.'
                   f'In {variant_map} header. #MAX_RANDOM_HOM_HETS=<val> is missing or invalid.')
            raise VariantMapError(msg)

        return(header_hom_hets)

    @staticmethod
    def extract_contigs(variant_map: Path):
        contigs = set()
        with pysam.TabixFile(str(variant_map)) as itabix:
            contigs = set(itabix.contigs)
        return(contigs)

    @staticmethod
    def are_contigs_chr_prefixed(contigs):
        single_val = next(iter(contigs))
        return(single_val.startswith('chr'))

    @staticmethod
    def normalize_contig_prefix(contig, use_chr_prefix):
        if contig.startswith('chr') and not use_chr_prefix:
            return(contig[3:])
        elif not contig.startswith('chr') and use_chr_prefix:
            return(f'chr{contig}')
        else:
            return(contig)

    def configure_from_variant_map(self):
        self.max_hom_hets = FSCramSource.extract_max_het_hom(self.variant_map)
        self.contigs = FSCramSource.extract_contigs(self.variant_map)
        self.contigs_chr_prefixed = FSCramSource.are_contigs_chr_prefixed(self.contigs)

    def validate(self):
        if(not(self.source.is_dir())):
            msg = (f'FS Crams source must be an extant directory: {self.source}')
            raise CramSourceInaccessibleError(msg)

        if(not(self.seq_dir.is_dir())):
            msg = (f'FS Crams source must contain "sequences" directory: {self.seq_dir}')
            raise CramSourceInaccessibleError(msg)

        if(not(self.variant_map.is_file())):
            msg = (f'FS Crams source must contain variant_map: {self.variant_map}')
            raise CramSourceInaccessibleError(msg)

        if(not(self.variant_map.with_suffix('.gz.tbi').is_file())):
            msg = (f'FS Crams source must contain variant_map index: {self.variant_map}.tbi')
            raise CramSourceInaccessibleError(msg)

        if(not(self.ref_path.is_file())):
            msg = (f'Reference file must exist: {self.ref_path}')
            raise ReferenceInaccessibleError(msg)

        if(not(self.ref_path.with_suffix('.fa.fai').is_file())):
            msg = (f'Reference file index must exist: {self.ref_path}.fai')
            raise ReferenceInaccessibleError(msg)

        return True

    @staticmethod
    def get_sequences_info(variant_map, chrom, pos, ref, alt):
        with pysam.TabixFile(str(variant_map), parser=pysam.asTuple()) as itabix:
            return FSCramSource.het_hom_counts(itabix, chrom, pos, ref, alt)

    @staticmethod
    def het_hom_counts(tabix_file, chrom, pos, ref, alt):
        result = []
        for row in tabix_file.fetch(chrom, pos - 1, pos):
            if int(row[1]) == pos and row[2] == ref and row[3] == alt:
                result.append({
                    'n_homozygous': len(row[4].split(',')) if row[4] else 0,
                    'n_heterozygous': len(row[5].split(',')) if row[5] else 0
                })
                break
        return result

    @staticmethod
    def rectify_stop_byte(start: int, stop: int, data_size: int):
        """ Correct stop index so that given stop index is included in returned data.
        """

        if stop is None or stop < 0:
            r_stop = data_size
        elif stop < start:
            r_stop = start
        else:
            r_stop = stop + 1

        return r_stop

    @staticmethod
    def extract_bam_subset(cram_path: str, ref_path: str, chrom: str, pos: str):
        window = 100
        ipos = int(pos)
        bam_arr = bytearray()
        bai_arr = bytearray()
        with pysam.AlignmentFile(cram_path, 'rc', reference_filename=ref_path) as icram,\
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
            combined_data = FSCramSource.extract_bam_subset(cram_path, self.ref_path, chrom, pos)
            self.cache_combined_data(base_key, combined_data)
            target_data = combined_data[key_suffix]
        return(target_data)

    def lookup_sample_id(self, chrom: str, pos: str, ref: str, alt: str,
                         sample_het: bool, sample_no: int) -> str:
        log.debug('lookup id: %s, %s, %s, %s, %s, %i', chrom, pos, ref, alt, sample_het, sample_no)
        sample_id = None
        pos = int(pos)
        with pysam.TabixFile(str(self.variant_map), parser=pysam.asTuple()) as itabix:
            for row in itabix.fetch(chrom, pos - 1, pos):
                sample_id = FSCramSource.extract_sample_id(row, pos, ref, alt,
                                                           sample_het, sample_no)
        return sample_id

    @staticmethod
    def extract_sample_id(row, pos, ref, alt, sample_het, sample_no):
        """ Extract sample_id of variant from variant map row

        :param row: Tuple of variant map row
        :param sample_het: T/F indicating if sample ids should be taken from het column.
        :param sample_no: 1-based index of the id to select from the het or hom column.
        """
        sample_id = None
        if int(row[1]) == pos and row[2] == ref and row[3] == alt:
            samples = row[5] if sample_het else row[4]
            if samples:
                samples = samples.split(',')
            if len(samples) >= sample_no:
                sample_id = samples[sample_no - 1]
        return(sample_id)

    def calc_cram_path(self, sample_id) -> str:
        cram_path = os.path.join(self.seq_dir, hashlib.md5(sample_id.encode()).hexdigest()[:2],
                                 sample_id + '.cram')
        return(cram_path)

    def is_sample_no_sample_het_valid(self, sample_no, sample_het) -> bool:
        self.max_hom_hets = None
        if sample_no > self.max_hom_hets:
            return False

        if sample_het and sample_no > self.max_hom_hets:
            return None
        if not sample_het and sample_no > self.max_hom_hets:
            return None
