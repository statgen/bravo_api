from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class CramSourceInaccessibleError(Exception):
    """
    Exception class indicating the CramSource data could not be read.
    """
    pass


class VariantMapError(Exception):
    """
    Exception class indicating a problem with the variant map data.
    """
    pass


class ReferenceInaccessibleError(Exception):
    """
    Exception class indicating the CramSource reference could not be read.
    """
    pass


class CramSource(ABC):
    """
    Validate and provide read from crams files.
    """

    _window_bp = 100

    def __init__(self, src, ref):
        pass

    @abstractmethod
    def get_info(self, variant_id):
        pass

    @abstractmethod
    def get_crai(self, variant_id, sample_no, sample_het):
        pass

    @abstractmethod
    def get_cram(self, variant_id, sample_no, sample_het, start_byte, stop_byte):
        pass

    @abstractmethod
    def validate(self):
        pass

    ##########################
    # Shared utility methods #
    ##########################

    @staticmethod
    def extract_sample_id(row, pos, ref, alt, sample_het, sample_no):
        """ Extract sample_id of variant from variant map row

        :param row: Tuple of variant map row
        :param sample_het: T/F indicating if sample ids should be taken from het column.
        :param sample_no: 1-based index of the id to select from the het or hom column.
        """
        logger.debug(f'variant map val: {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}')
        logger.debug(f'comp sample val: {pos}, {ref}, {alt}, {sample_het}, {sample_no}')

        sample_id = None
        if int(row[1]) == pos and row[2] == ref and row[3] == alt:
            samples = row[5] if sample_het else row[4]
            if samples:
                samples = samples.split(',')
            if len(samples) >= sample_no:
                sample_id = samples[sample_no - 1]
        return(sample_id)

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
