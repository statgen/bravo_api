def chrom_position_offsets():
    chromosomes = [str(x) for x in range(1, 23)] + ['X', 'Y', 'M']
    offsets = {f"{chrom}": (count + 1) * int(1e9) for count, chrom in enumerate(chromosomes)}
    return offsets


CHROMOSOMES_OFFSETS = chrom_position_offsets()


def make_xpos(chrom, pos, offsets=CHROMOSOMES_OFFSETS):
    if chrom.startswith('chr'):
        chrom = chrom[3:]

    if chrom in offsets:
        return offsets[chrom] + pos
    else:
        return -1
