"""
Coverage bins are:
    Continugous positions with difference in mean and median read depth less than the bin value
    are consolidate together.
"""

from bravo_api.core.coverage_provider import CoverageProvider, CoverageSourceInaccessibleError
import os


class FSCoverageProvider(CoverageProvider):
    # Query lengths corresponding to resolution. Temporarily here for reference.
    # QSIZE = [10_000, 3000, 1000, 300, 0]

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

    def coverage(self, chr, start, stop, bin):
        return([])
