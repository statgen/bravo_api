from flask import current_app
import os
import random
import string
import pysam
import fcntl
import time
import re
import gzip
import hashlib
from intervaltree import IntervalTree


class SequencesClient(object):
    '''Manages CRAMS for all chromosomes. Assumes one CRAM per chromosome.'''
    def __init__(self, crams_dir, reference_path, cache_dir, window_bp):
        self._variant_map_file = os.path.join(crams_dir, 'variant_map.tsv.gz')
        if not os.path.exists(self._variant_map_file):
            raise Exception('Provided CRAM directory doesn\'t contain "variant_map.tsv.gz" file.')
        if not os.path.exists(self._variant_map_file + '.tbi'):
            raise Exception('Provided CRAM directory doesn\'t contain "variant_map.tsv.gz.tbi" file.')
        self._sequences_dir = os.path.join(crams_dir, 'sequences')
        if not os.path.exists(self._sequences_dir):
            raise Exception('Provided CRAM directory doesn\'t contain "sequences" directory.')
        if not os.path.isdir(self._sequences_dir):
            raise Exception('Provided CRAM directory contains "sequences" which is not a directory.')
        self._crams_dir = crams_dir
        self._reference_path = reference_path
        if not os.path.exists(cache_dir):
            raise Exception('Provided CRAM cache path does not exist.')
        if not os.path.isdir(cache_dir):
            raise Exception('Provided CRAM cache path must be a directory.')
        try: # check if can write to cache directory
            filename = os.path.join(cache_dir, f'test_{SequencesClient.get_random_filename(10)}')
            f = open(filename, 'w')
        except:
            raise Exception(f'Error while writing to the CRAM cache directory {cache_dir}.')
        else:
            f.close()
            os.remove(filename)
        self._cache_dir = cache_dir
        self._window_bp = window_bp
        self._max_hom = 0
        self._max_het = 0
        with gzip.open(self._variant_map_file, 'rt') as ifile:
            for line in ifile:
                if not line.startswith('#'):
                    break
                if line.startswith('#MAX_RANDOM_HOM_HETS='):
                    self._max_hom = self._max_het = int(line.rstrip().split('=')[1].strip())
        if self._max_hom <= 0 or self._max_het <= 0:
            raise Exception(f'Invalid values for MAX_HOM and MAX_HET ({self._max_hom} and {self._max_het}).')
        self._starts_with_chr = False
        self._contigs = set()
        with pysam.TabixFile(self._variant_map_file) as itabix:
            for contig in itabix.contigs:
                self._contigs.add(contig)
        for contig in self._contigs:
            if contig.startswith('chr'):
                self._starts_with_chr = True
                break

    @property
    def max_hom(self):
        return self._max_hom

    @property
    def max_het(self):
        return self._max_het

    @staticmethod
    def get_random_filename(length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(length))

    def normalize_chrom(self, chrom):
        if self._starts_with_chr:
            if not chrom.startswith('chr'):
                return f'chr{chrom}'
        else:
            if chrom.startswith('chr'):
                return chrom[3:]
        return chrom

    def get_sequences_info(self, chrom, pos, ref, alt):
        results = []
        chrom = self.normalize_chrom(chrom)
        if chrom in self._contigs:
            with pysam.TabixFile(self._variant_map_file, parser = pysam.asTuple()) as itabix:
                for row in itabix.fetch(chrom, pos - 1, pos):
                    if int(row[1]) == pos and row[2] == ref and row[3] == alt:
                        results.append({
                           'n_homozygous': len(row[4].split(',')) if row[4] else 0,
                           'n_heterozygous': len(row[5].split(',')) if row[5] else 0
                        })
                        break
        return results

    def get_sequences(self, chrom, pos, ref, alt, sample_no, sample_het):
        chrom = self.normalize_chrom(chrom)
        sample_id = None
        with pysam.TabixFile(self._variant_map_file, parser = pysam.asTuple()) as itabix:
            for row in itabix.fetch(chrom, pos - 1, pos):
                if int(row[1]) == pos and row[2] == ref and row[3] == alt:
                    samples = row[5] if sample_het else row[4]
                    if samples:
                        samples = samples.split(',')
                    if len(samples) >= sample_no:
                        sample_id = samples[sample_no - 1]
        if not sample_id:
            return None

        qname = f'{pos}:{ref}:{alt}:{"" if sample_het else "0"}{sample_no}'
        cram = os.path.join(self._sequences_dir, hashlib.md5(sample_id.encode()).hexdigest()[:2], sample_id + '.cram')

        cached_cram = os.path.join(self._cache_dir, f'{chrom}-{qname.replace(":", "-")}.bam')
        cached_cram_index = f'{cached_cram}.bai'
        if os.path.exists(cached_cram):
            with open(cached_cram, 'r') as ifile:
                unlocked = False
                for i in range(10): # locked file means it is still being written. so, we wait.
                    try:
                        fcntl.flock(ifile, fcntl.LOCK_SH | fcntl.LOCK_NB)
                        unlocked = True
                        break
                    except:
                        time.sleep(0.2)
                        continue
                if not unlocked:
                    return None
        else:
            with pysam.AlignmentFile(cram, 'rc', reference_filename = self._reference_path) as icram, open(cached_cram, 'wb') as ofile:
                ocram = pysam.AlignmentFile(ofile, 'wb', reference_filename = self._reference_path, header = icram.header)
                try:
                    fcntl.flock(ofile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except:
                    return None # file is already locked. this situation is abnormal and we expect it to happen very rarely (maybe when app is stopped abnormally and the file remains locked)
                n_reads = 0
                for read in icram.fetch(chrom, max(0, pos - self._window_bp), pos + self._window_bp):
                    if read.query_name.startswith(qname + ':'):
                        n_reads += 1
                        ocram.write(read)
                ocram.close()
                fcntl.flock(ofile, fcntl.LOCK_UN) # ofile fill be unlocked automatically after "with" context, but just in case we still do flock.LOCK_UN
            if n_reads == 0:
                os.remove(cached_cram)
                return None
            pysam.index(cached_cram)
        return { 'cram': cached_cram, 'crai': cached_cram_index }


sequences_handler = None


def init_sequences(sequences_dir, reference_sequence, sequences_cache_dir):
    global sequences_handler
    sequences_handler = SequencesClient(sequences_dir, reference_sequence, sequences_cache_dir, 100)


def get_info(variant_id):
    chrom, pos, ref, alt = variant_id.split('-')
    return sequences_handler.get_sequences_info(chrom, int(pos), ref, alt)


def get_crai(variant_id, sample_no, sample_het):
    if sample_het and sample_no > sequences_handler.max_het:
        return None
    if not sample_het and sample_no > sequences_handler.max_hom:
        return None
    chrom, pos, ref, alt = variant_id.split('-')
    sequences = sequences_handler.get_sequences(chrom, int(pos), ref, alt, sample_no, sample_het)
    if sequences:
        return sequences['crai']
    return None


def get_cram(variant_id, sample_no, sample_het, start_byte, stop_byte):
    if sample_het and sample_no > sequences_handler.max_het:
        return None
    if not sample_het and sample_no > sequences_handler.max_hom:
        return None
    chrom, pos, ref, alt = variant_id.split('-')
    sequences = sequences_handler.get_sequences(chrom, int(pos), ref, alt, sample_no, sample_het)
    if not sequences:
        return None
    file_size = os.path.getsize(sequences['cram'])
    if start_byte is None or start_byte < 0:
        start_byte = 0
    if stop_byte is None or stop_byte < 0:
        length = file_size - start_byte
    else:
        length = stop_byte - start_byte
    with open(sequences['cram'], 'rb') as ifile:
        ifile.seek(start_byte)
        file_bytes = ifile.read(length)
    return { 'file_bytes': file_bytes, 'start_byte': start_byte, 'stop_byte': start_byte + length - 1, 'file_size': file_size }
