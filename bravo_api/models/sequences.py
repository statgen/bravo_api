from flask import current_app
import os
import random
import string
import pysam
import fcntl
import time
import re
from intervaltree import IntervalTree


class SequencesClient(object):
   '''Manages CRAMS for all chromosomes. Assumes one CRAM per chromosome.'''
   def __init__(self, crams_dir, reference_path, cache_dir, window_bp):
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
      self._crams = dict()
      self._max_hom = 0
      self._max_het = 0
      for path in os.walk(self._crams_dir):
         for cram_file in (x for x in path[2] if x.endswith('.cram')):
            cram_path = os.path.join(path[0], cram_file)
            chrom = None
            start_bp = None
            stop_bp = None
            max_hom = None
            max_het = None
            with pysam.AlignmentFile(cram_path, 'rc', reference_filename = self._reference_path) as cram:
               for line in cram.header['CO']:
                  m = re.match(r'MAX_HOM=(\d+);MAX_HET=(\d+)', line)
                  if m:
                     max_hom, max_het = m.groups()
                  else:
                     m = re.match(r'REGION=(\w+):(\d+)-(\d+)', line)
                     if m:
                        chrom, start_bp, stop_bp = m.groups()
               if chrom is None or start_bp is None or stop_bp is None:
                  raise Exception('REGION tag was not found in CRAM SO header lines.')
               if max_hom is None or max_het is None:
                  raise Exception('MAX_HOM and MAX_HET tags were not found in CRAM SO header lines.')
               self._max_hom = max(self._max_hom, int(max_hom))
               self._max_het = max(self._max_het, int(max_het))
               t = self._crams.setdefault(chrom, IntervalTree())
               if t.overlap(int(start_bp), int(stop_bp) + 1):
                  raise Exception('Two or more CRAM files with overlapping regions were detected.')
               t.addi(int(start_bp), int(stop_bp) + 1, { 'header': {'HD': cram.header['HD'], 'SQ': cram.header['SQ']}, 'path': cram_path })

   @property
   def max_hom(self):
      return self._max_hom

   @property
   def max_het(self):
      return self._max_het

   @staticmethod
   def get_random_filename(length):
      return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(length))

   def get_sequences(self, chrom, pos, qname):
      interval_crams = self._crams.get(chrom, None)
      if interval_crams is None:
         chrom = chrom[3:] if chrom.startswith('chr') else f'chr{chrom}'
         interval_crams = self._crams.get(chrom, None)
         if interval_crams is None:
            return None
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
         interval_cram = interval_crams.at(pos)
         if len(interval_cram) != 1:
            return None
         cram = interval_cram.pop().data
         with pysam.AlignmentFile(cram['path'], 'rc', reference_filename = self._reference_path) as icram, open(cached_cram, 'wb') as ofile: 
            ocram = pysam.AlignmentFile(ofile, 'wb', reference_filename = self._reference_path, header = cram['header'])
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


def get_crai(variant_id, sample_no, sample_het):
   if sample_het and sample_no > sequences_handler.max_het:
      return None
   if not sample_het and sample_no > sequences_handler.max_hom:
      return None
   chrom, pos, ref, alt = variant_id.split('-')
   qname = f'{pos}:{ref}:{alt}:{"" if sample_het else "0"}{sample_no}'
   sequences = sequences_handler.get_sequences(chrom, int(pos), qname)
   if sequences:
      return sequences['crai']
   return None


def get_cram(variant_id, sample_no, sample_het, start_byte, stop_byte):
   if sample_het and sample_no > sequences_handler.max_het:
      return None
   if not sample_het and sample_no > sequences_handler.max_hom:
      return None
   chrom, pos, ref, alt = variant_id.split('-')
   qname = f'{pos}:{ref}:{alt}:{"" if sample_het else "0"}{sample_no}'
   sequences = sequences_handler.get_sequences(chrom, int(pos), qname)
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
