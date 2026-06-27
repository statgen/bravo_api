import logging
import csv
import io
import pysam
import tempfile
import os
import time
import multiprocessing as mp
from contextlib import contextmanager
from flask_caching import Cache
from cachelib import BaseCache, SimpleCache
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
        self.cram_catalog = FsSvCramSource.load_catalog(self.catalog_path)
        logger.debug(f"Loaded index of {len(self.cram_catalog)} SVs")

        if(cache is None):
            self.cache = SimpleCache(threshold=10)
        else:
            self.cache = cache

    #############
    # Interface #
    #############

    def get_info(self, variant_id):
        return {}

    def get_crai(self, variant_id, sample_no, sample_het):
        pass

    def get_cram(self, variant_id: str, sample_no: int,
                 start_byte: int = None, stop_byte: int = None) -> dict:
        """
        :param variant_id: structvar identifier, e.g. DUP_1:897945-925264
        :return: Dictionary with ByteIO contents of bam file and start,stop,size
            suitable for http Content-Range header.
        """
        # Process structural variant id into components
        primary_split = variant_id[-4].split(':')
        chrom = primary_split[0]
        start, stop = primary_split[1].split('-')
        chrom = FsSvCramSource.normalize_contig_prefix(chrom, self.contigs_chr_prefixed)

        # Lookup cram path from the index
        cram_path = self.variant_idx[variant_id]
        if(not cram_path):
            return {}

        # Extract bam data subset from the cram
        bam_data = self.get_bam_data(cram_path, chrom, start, stop)
        data_size = len(bam_data)

        if start_byte is None or start_byte < 0:
            start_byte = 0

        correct_stop = FsSvCramSource.rectify_stop_byte(start_byte, stop_byte, data_size)

        bam_slice = bam_data[start_byte:correct_stop]
        bam_io = io.BytesIO(bam_slice)

        return {'file_bytes': bam_io, 'start_byte': start_byte,
                'stop_byte': stop_byte, 'file_size': data_size}

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

    @staticmethod
    def load_catalog(path: str) -> dict:
        ret_val = {}
        with open(path, newline='') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                ret_val[row[0]] = row[1]
        return ret_val

    def get_bam_data(self, sv_id, cram_path, chrom, start, stop) -> bytes:
        return(self.get_data(sv_id, "bam", sv_id, cram_path, chrom, start, stop))

    def get_bai_data(self, sv_id, cram_path, chrom, start, stop) -> bytes:
        return(self.get_data(sv_id, "bai", sv_id, cram_path, chrom, start, stop))

    def get_data(self, sv_id, suffix, cram_path, chrom, start, stop) -> bytes:
        cache_key = f"{sv_id}-{suffix}"
        target_data = self.cache.get(cache_key)
        if target_data is None:
            combined_data = FsSvCramSource.extract_bam_subset(cram_path, self.ref_path,
                                                              chrom, start, stop)
            self.cache_combined_data(sv_id, combined_data)
            target_data = combined_data[cache_key]
        return(target_data)

    def cache_combined_data(self, sv_id: str, bam_data: dict) -> None:
        self.cache.set(f'{sv_id}-bam', bam_data['bam'])
        self.cache.set(f'{sv_id}-bai', bam_data['bai'])

    @staticmethod
    def extract_bam_subset(cram_path: str, ref_path: str, chrom: str, start: str, stop: str):
        """
        Pysam requires reading and writing to files due to how the underying htslib is used.
        Using tempfiles to create a bam subset then immediately reading it to memory.
        """
        start = int(start)
        stop = int(stop)

        bam_arr = bytearray()
        bai_arr = bytearray()
        with pysam.AlignmentFile(cram_path, 'rc', reference_filename=ref_path) as icram,\
                tempfile.NamedTemporaryFile(mode='w+b', suffix='.bam', delete=False) as btmp:

            # Write a bam file
            ofile = pysam.AlignmentFile(btmp, 'wb', reference_filename=ref_path,
                                        header=icram.header)
            for read in icram.fetch(chrom, start, stop):
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

    #################
    # From CramTest #
    #################
    @contextmanager
    @staticmethod
    def temp_fifo(*args, **kwargs):
        """
        Create a named pipe, return the path, ensure it gets deleted
        """
        tmp_file_name = f"bravo-{os.getpid()}-{time.time()}.bam"
        tmp_file_path = os.path.join(tempfile.gettempdir(), tmp_file_name)
        try:
            os.mkfifo(tmp_file_path)
            yield tmp_file_path
        finally:
            os.unlink(tmp_file_path)

    @contextmanager
    @staticmethod
    def writing_descriptor(path):
        """
        open path for writing.  Ensure it gets closed.
        Return file descriptor
        """
        try:
            fd = os.open(path, os.O_WRONLY)
            os.set_inheritable(fd, True)
            yield fd
        finally:
            os.close(fd)

    @contextmanager
    @staticmethod
    def reading_descriptor(path):
        """
        open path for non-blocking reading.  Ensure it gets closed.
        Return file descriptor
        """
        try:
            fd = os.open(path, os.O_RDONLY)
            os.set_inheritable(fd, True)
            yield fd
        finally:
            os.close(fd)

    @staticmethod
    def fill_pipe_from_cram(src_cram: str, ref: str, pipe: str, chrom: str, start: int, stop: int):
        """
        Read from a source cram and fill a named pipe fashion.
        """
        with pysam.AlignmentFile(src_cram, 'rc', reference_filename=ref) as icram,\
             pysam.AlignmentFile(pipe, 'wb', reference_filename=ref, header=icram.header) as ocram:
            for read in icram.fetch(chrom, start, stop):
                ocram.write(read)

    def putative_extract_cram(self, chrom="chr11", start=49670000, stop=49673000) -> bytearray:
        MAX_READ_SIZE = 131072
        data = bytearray()

        cram_path = "/mnt/bravo/data/runtime/structvar/crams/chr11_selected_p070.cram"

        with FsSvCramSource.temp_fifo() as fifo_path:
            proc_args = (cram_path, self.ref_path, fifo_path, chrom, start, stop)
            proc = mp.Process(target=FsSvCramSource.fill_pipe_from_cram, args=proc_args)
            proc.start()

            with FsSvCramSource.reading_descriptor(fifo_path) as read_fd:
                while True:
                    byte_str = os.read(read_fd, MAX_READ_SIZE)
                    if len(byte_str) > 0:
                        data += byte_str
                    elif not proc.is_alive():
                        break
        # At this point `data` is ready to be stuffed into a BytesIO for shipping over the wire.
        return(io.BytesIO(data))

    def extract_cram(self, cram_path, chrom="chr11", start=49670000, stop=49673000) -> bytearray:
        MAX_READ_SIZE = 131072
        data = bytearray()

        with FsSvCramSource.temp_fifo() as fifo_path:
            proc_args = (cram_path, self.ref_path, fifo_path, chrom, start, stop)
            proc = mp.Process(target=FsSvCramSource.fill_pipe_from_cram, args=proc_args)
            proc.start()

            with FsSvCramSource.reading_descriptor(fifo_path) as read_fd:
                while True:
                    byte_str = os.read(read_fd, MAX_READ_SIZE)
                    if len(byte_str) > 0:
                        data += byte_str
                    elif not proc.is_alive():
                        break
        return(io.BytesIO(data))

    @staticmethod
    def extract_pos_vals(sv_id: str) -> list:
        """
        Parse chromosome, start, and stop from valid structural variant id
        Prepend "chr" to chromosome value.
        Convert start and stop to integers.
        """
        tx = str.maketrans("_:", "--")
        parts = sv_id.translate(tx).split("-")
        return([f"chr{parts[1]}", int(parts[2]), int(parts[3])])

    def get_cram_data(self, sv_id: str) -> io.BytesIO:
        """
        Extract relevant bam data from cram file given structvar id.
        """
        # lookup cram file for sv
        cram_path = self.catalog[sv_id]
        # resolve list of postion values [chrom, start, stop]
        chrom, start, stop = FsSvCramSource.extract_pos_vals(sv_id)
        # extract data
        return(self.extract_cram(cram_path, chrom, start, stop))
