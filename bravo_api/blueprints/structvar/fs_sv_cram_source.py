import logging
import csv
from pathlib import Path
from bravo_api.core.cram_source import (CramSource, CramSourceInaccessibleError,
                                        ReferenceInaccessibleError)
from flask_caching import Cache
from cachelib import BaseCache, SimpleCache

logger = logging.getLogger(__name__)


class FsSvCramSource(CramSource):

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
