import logging
import csv
import io
import os
from flask_caching import Cache
from cachelib import BaseCache
from pathlib import Path
from bravo_api.core.cram_source import (CramSource, CramSourceInaccessibleError,
                                        ReferenceInaccessibleError)

logger = logging.getLogger(__name__)


class FsSvCramSource(CramSource):
    CATALOG_FILENAME = "sv_cram_index.tsv"
    CRAMS_DIRNAME = "crams"

    def __init__(self, src: str, ref: str, cache: [BaseCache, Cache] = None):
        self.source = Path(src)
        self.seq_dir = self.source.joinpath(FsSvCramSource.CRAMS_DIRNAME)
        self.catalog_path = self.source.joinpath(FsSvCramSource.CATALOG_FILENAME)
        self.ref_path = Path(ref)

        self.validate()
        self.catalog = FsSvCramSource.load_catalog(self.catalog_path)
        logger.debug(f"Loaded index of {len(self.catalog)} SVs")

    #############
    # Interface #
    #############

    def get_info(self, variant_id):
        return {}

    def get_crai(self, variant_id, sample_no=0, sample_het=False):
        """ Index of subset data for individual sample representing a variant

        :param variant_id: chrom-pos-ref-alt identifier of variant.
        :param sample_no: integer unused in this implementation.
        :param sample_het: boolean unused in this implementation.

        :return: contents of the bai file wrapped in BytesIO instance
        """
        cram_file = self.catalog.get(variant_id)
        if not cram_file:
            return(io.BytesIO(b""))

        cram_path = os.path.join(self.seq_dir, cram_file)
        try:
            with open(f'{cram_path}.crai', 'rb') as ifile:
                bai_arr = bytearray(ifile.read(-1))
        except FileNotFoundError:
            return(io.BytesIO(b""))

        return(io.BytesIO(bai_arr))

    def get_cram(self, variant_id: str, sample_no: int,
                 start_byte: int = None, stop_byte: int = None) -> dict:
        """
        :param variant_id: structvar identifier, e.g. DUP_1:897945-925264
        :return: Dictionary of file_bytes, start_byte, stop_byte, file_size
            with ByteIO contents of cram file and start, stop, size suitable for http Content-Range.
        """
        cram_file = self.catalog.get(variant_id)
        if not cram_file:
            return(None)

        cram_path = os.path.join(self.seq_dir, cram_file)
        try:
            file_size = os.stat(cram_path).st_size
            with open(cram_path, 'rb') as ifile:
                ifile.seek(start_byte, 0)
                n_bytes = 1 + stop_byte - start_byte
                file_bytes = ifile.read(n_bytes)
        except OSError:
            return(None)

        return {'file_bytes': io.BytesIO(file_bytes), 'start_byte': start_byte,
                'stop_byte': stop_byte, 'file_size': file_size}

    ##################
    # Implementation #
    ##################

    @staticmethod
    def load_catalog(path: str) -> dict:
        ret_val = {}
        with open(path, newline='') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                ret_val[row[0]] = row[1]
        return ret_val

    def validate(self):
        if(not(self.source.is_dir())):
            msg = (f'FS SV Crams source must be an extant directory: {self.source}')
            raise CramSourceInaccessibleError(msg)

        if(not(self.seq_dir.is_dir())):
            msg = (f'FS SV Crams source must contain "crams" directory: {self.seq_dir}')
            raise CramSourceInaccessibleError(msg)

        if(not(self.catalog_path.is_file())):
            msg = (f'FS SV Crams source must contain sv_cram_index.tsv: {self.variant_map}')
            raise CramSourceInaccessibleError(msg)

        if(not(self.catalog_path.with_suffix('.tsv').is_file())):
            msg = (f'FS SV Crams index must be a tsv: {self.variant_map}.tbi')
            raise CramSourceInaccessibleError(msg)

        if(not(self.ref_path.is_file())):
            msg = (f'Reference file must exist: {self.ref_path}')
            raise ReferenceInaccessibleError(msg)

        if(not(self.ref_path.with_suffix('.fa.fai').is_file())):
            msg = (f'Reference file index must exist: {self.ref_path}.fai')
            raise ReferenceInaccessibleError(msg)
        return True
