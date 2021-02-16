

def make_xpos(chrom, pos):
    chromosomes = [ str(x) for x in range(1, 23) ]  + [ 'X', 'Y', 'M' ]
    if chrom.startswith('chr'): chrom = chrom[3:]
    return { chrom: i + 1 for  i, chrom in enumerate(chromosomes) }[chrom] * int(1e9) + pos
