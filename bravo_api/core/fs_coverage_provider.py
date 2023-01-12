"""
Coverage bins are:
    Continugous positions with difference in mean and median read depth less than the bin value
    are consolidate together.
"""
from bravo_api.core.coverage_provider import CoverageProvider, CoverageSourceInaccessibleError
from pathlib import Path
import rapidjson
import pysam
import os


class FSCoverageProvider(CoverageProvider):

    def __init__(self, src):
        self.source = Path(src)
        self.validate_source()
        self.catalog = self.discover_files()

    def validate_source(self):
        extant = self.source.exists()
        directory = self.source.is_dir()
        readable = os.access(self.source, os.R_OK)

        if(not(extant and directory and readable)):
            msg = (f'FS Coverage soure must be extant: {extant},'
                   f'a directory: {directory}, and readable: {readable}.')
            raise CoverageSourceInaccessibleError(msg)
        return(True)

    def evaluate_chrom_representation(self):
        """
        All chromosomes expected to be represented in all coverage bins
        """
        msgs = []
        for bin_name, cov_bin in self.catalog.items():
            missing_chroms = [chrom for chrom in self._chroms if chrom not in cov_bin.keys()]
            if(missing_chroms):
                msgs.append(f'Coverage {bin_name} missing chroms: {missing_chroms}')
        return(msgs)

    def evaluate_chrom_readability(self):
        """
        All coverage files expected to be readable
        """
        msgs = []
        for cbin in self.catalog.values():
            for path in cbin.values():
                if(not os.access(path, os.R_OK)):
                    msgs.append(f'Coverage file {path} unreadable')
                index_path = path.parent / (path.name + '.tbi')
                if(not os.access(index_path, os.R_OK)):
                    msgs.append(f'Coverage file index {index_path} unreadable')
        return(msgs)

    def evaluate_catalog(self):
        warn_msgs = []
        warn_msgs.extend(self.evaluate_chrom_representation())
        warn_msgs.extend(self.evaluate_chrom_readability())
        return(warn_msgs)

    def discover_files(self):
        """
        Find and organize the chrN.bin_X.YZ.tar.gz coverage files into a dictionary organized by
        bin then chromosome.
        """
        result = {}
        for bin_name in self._bins:
            bin_dir = self.source.joinpath(bin_name)
            bin_files = bin_dir.glob('*.tsv.gz')

            bin_by_chr = {}
            for bfile in bin_files:
                filename_chr = bfile.name.replace('chr', '').split('.', maxsplit=1)[0]
                bin_by_chr[filename_chr] = bfile

            result[bin_name] = bin_by_chr
        return(result)

    def lookup_coverage_path(self, cov_bin, chrom):
        """
        Return path to a coverage file or None
        """
        return(self.catalog.get(cov_bin, {}).get(chrom))

    def coverage(self, cov_bin, chrom, start, stop):
        """
        Provide list of dicts of from the json data of appropriate coverate file
        """
        result = []

        # Get path from catalog
        cov_path = self.lookup_coverage_path(cov_bin, chrom)

        # Handle no path by returning no data.
        if(not cov_path):
            return(result)

        tabixfile = pysam.TabixFile(cov_path.as_posix())

        for row in tabixfile.fetch(chrom, max(1, start - 1), stop, parser=pysam.asTuple()):
            result.append(rapidjson.loads(row[3]))

        return(result)
