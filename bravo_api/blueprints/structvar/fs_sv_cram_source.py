import logging
import csv
import re
from pathlib import Path
from bravo_api.core.cram_source import (CramSource, CramSourceInaccessibleError,
                                        ReferenceInaccessibleError)
from flask_caching import Cache
from cachelib import BaseCache, SimpleCache

logger = logging.getLogger(__name__)


class FsSvCramSource(CramSource):

    id_patt = re.compile(r"^(INV|DUP|DEL)_(\d\d?):\d+-\d+$", re.IGNORECASE)

    def __init__(self, src: str, ref: str, cache: [BaseCache, Cache] = None):
        self.source = Path(src)
        self.seq_dir = self.source.joinpath('crams')
        self.idx_path = self.source.joinpath('sv_cram_index.tsv')
        self.ref_path = Path(ref)

        self.validate()
        self.variant_idx = FsSvCramSource.load_variant_index(self.idx_path)
        logger.debug(f"Loaded index of {len(self.variant_idx)} SVs")

        if(cache is None):
            self.cache = SimpleCache(threshold=10)
        else:
            self.cache = cache

    #############
    # Interface #
    #############

    def get_info(self, variant_id):
        pass

    def get_crai(self, variant_id, sample_no, sample_het):
        pass

    def get_cram(self, variant_id: str, sample_no: int, sample_het: bool,
                 start_byte: int = None, stop_byte: int = None) -> dict:
        """
        :param variant_id: structvar identifier, e.g. DUP_1:897945-925264
        :return: Dictionary with ByteIO contents of bam file and start,stop,size
            suitable for http Content-Range header.
        """
        if(not FsSvCramSource.sv_id_is_well_formed(variant_id)):
            return {}

        primary_split = variant_id[-4].split(':')
        chrom = primary_split[0]
        start, stop = primary_split[1].split('-')

        chrom = FsSvCramSource.normalize_contig_prefix(chrom, self.contigs_chr_prefixed)

        pass

    ##################
    # Implementation #
    ##################

    def validate(self):
        if(not(self.source.is_dir())):
            msg = (f'FS SV Crams source must be an extant directory: {self.source}')
            raise CramSourceInaccessibleError(msg)

        if(not(self.seq_dir.is_dir())):
            msg = (f'FS SV Crams source must contain "crams" directory: {self.seq_dir}')
            raise CramSourceInaccessibleError(msg)

        if(not(self.idx_path.is_file())):
            msg = (f'FS SV Crams source must contain sv_cram_index.tsv: {self.variant_map}')
            raise CramSourceInaccessibleError(msg)

        if(not(self.idx_path.with_suffix('.tsv').is_file())):
            msg = (f'FS SV Crams index must be a tsv: {self.variant_map}.tbi')
            raise CramSourceInaccessibleError(msg)

        if(not(self.ref_path.is_file())):
            msg = (f'Reference file must exist: {self.ref_path}')
            raise ReferenceInaccessibleError(msg)

        if(not(self.ref_path.with_suffix('.fa.fai').is_file())):
            msg = (f'Reference file index must exist: {self.ref_path}.fai')
            raise ReferenceInaccessibleError(msg)
        return True

    def load_variant_index(idx_path: str) -> dict:
        ret_val = {}
        with open(idx_path, newline='') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                ret_val[row[0]] = row[1]
        return ret_val

    @staticmethod
    def sv_id_is_well_formed(id: str) -> bool:
        if re.fullmatch(FsSvCramSource.id_patt):
            return True
        return False
