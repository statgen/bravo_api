from flask import current_app
import glob
import rapidjson
import pysam
import time
import os.path


class CoverageFile(object):
    '''handles a single tabixed coverage file with any number of chroms'''
    def __init__(self, path, binned):
        self._tabixfile = pysam.TabixFile(path)
        self._binned = binned

    def is_binned(self):
        return self._binned

    def get_chroms(self):
        return self._tabixfile.contigs

    def get_coverage(self, chrom, start, stop, limit, continue_from = 0):
        total = 0
        last = 0
        data = []
        for row in self._tabixfile.fetch(chrom, max(0, start - 1), stop, parser=pysam.asTuple()):
            if int(row[2]) >= start:
                total += 1
                if total > continue_from and len(data) < limit:
                    last = total
                    data.append(rapidjson.loads(row[3]))
        return { 'total': total, 'data': data, 'last': None if last == total else last }

    def __str__(self):
        return f"<CoverageFile chroms={','.join(self.get_chroms())} path={self._tabixfile.filename}>"

    __repr__ = __str__


class SingleChromCoverageHandler(object):
    '''contains coverage (at multiple binning levels) for one chrom'''
    def __init__(self, chrom):
        self._chrom = chrom
        self._coverage_files = []

    def add_coverage_file(self, coverage_file, min_length_in_bases):
        self._coverage_files.append({'file': coverage_file, 'bp-min-length': min_length_in_bases})
        self._coverage_files.sort(key = lambda d: d['bp-min-length'])

    def get_coverage_file(self, start, stop, length = None):
        if length is None:
            length = stop - start
        for coverage_file in reversed(self._coverage_files):
            if coverage_file['bp-min-length'] <= length:
                return coverage_file['file']
        return None

    def __str__(self):
        return f'<SingleChromCoverageHandler chrom={self._chrom} coverage_files={self._coverage_files}>'

    __repr__ = __str__


class CoverageHandler(object):
    '''contains coverage (at multiple binning levels) for all chroms'''
    def __init__(self, coverage_files):
        self._single_chrom_coverage_handlers = {}
        for cf in coverage_files:
            coverage_file = CoverageFile(cf['path'], cf.get('binned', False))
            for chrom in coverage_file.get_chroms():
                if chrom not in self._single_chrom_coverage_handlers:
                    self._single_chrom_coverage_handlers[chrom] = SingleChromCoverageHandler(chrom)
                self._single_chrom_coverage_handlers[chrom].add_coverage_file(coverage_file, cf.get('bp-min-length', 0))

    def get_coverage_file(self, chrom, start, stop):
        single_chrom_coverage_handler = self._single_chrom_coverage_handlers.get(chrom, None)
        if single_chrom_coverage_handler is not None:
            return single_chrom_coverage_handler.get_coverage_file(start, stop)
        return None


coverage_handler = None

def generate_coverage_files_metadata(coverage_dir):
    cov_files_md = []
    glob_suffix = '*.json.gz'
    full_glob = glob.glob( os.path.join(coverage_dir, 'full', glob_suffix))
    bin25_glob = glob.glob( os.path.join(coverage_dir, 'bin_0.25', glob_suffix))
    bin50_glob = glob.glob( os.path.join(coverage_dir, 'bin_0.50', glob_suffix))
    bin75_glob = glob.glob( os.path.join(coverage_dir, 'bin_0.75', glob_suffix))
    bin1_glob = glob.glob(os.path.join(coverage_dir, 'bin_1.00', glob_suffix))

    cov_files_md.extend({'bp-min-length':0,                  'path':path} for path in full_glob)
    cov_files_md.extend({'bp-min-length':300, 'binned':True, 'path':path} for path in bin25_glob)
    cov_files_md.extend({'bp-min-length':1000, 'binned':True, 'path':path} for path in bin50_glob)
    cov_files_md.extend({'bp-min-length':3000, 'binned':True, 'path':path} for path in bin75_glob)
    cov_files_md.extend({'bp-min-length':10000, 'binned':True, 'path':path} for path in bin1_glob)
    return(cov_files_md)


def init_coverage(coverage_dir):
    global coverage_handler
    coverage_file_metadata = generate_coverage_files_metadata(coverage_dir)
    coverage_handler = CoverageHandler(coverage_file_metadata)


def get_coverage(chrom, start, stop, limit, continue_from = 0):
    result = {
       'limit': 0,
       'total': 0,
       'data': [],
       'last': None
    }
    coverage_file = coverage_handler.get_coverage_file(chrom, start, stop)
    if coverage_file is None:
        return result
    coverage = coverage_file.get_coverage(chrom, start, stop, limit, continue_from)
    result['total'] = coverage['total']
    result['data'] = coverage['data']
    result['last'] = coverage['last']
    return result
