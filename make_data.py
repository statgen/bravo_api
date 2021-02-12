#!/usr/bin/env python

import os
import bgzip
import math
import json


def main():
    SEQUENCE_LENGTH = 10000
    print("---begin")
    # Make directories
    base_dir = os.path.join("data")
    # assumed subdirectory of SEQUENCES_DIR of config
    sequences_dir = os.path.join(base_dir, "crams", "demo", "sequences")
    # SEQUENCES_DIR of the config
    variants_dir = os.path.join(base_dir, "crams", "demo")
    coverage_dir = os.path.join(base_dir, "coverage", "bin_1")
    reference_dir = os.path.join(base_dir, "reference")

    mode = 0o755
    os.makedirs(sequences_dir, mode, True)
    os.makedirs(coverage_dir, mode, True)
    os.makedirs(reference_dir, mode, True)
    os.makedirs(os.path.join(base_dir, "cache"), mode, True)

    # Write dummy data
    #   a tsv with a json object last field. Needs tabix
    variant_file = os.path.join(variants_dir, "variant_map.tsv.gz")
    coverage_file = os.path.join(coverage_dir, "coverage.json.gz")
    #   needs cram conversion
    reference_file = os.path.join(reference_dir, "chr77.fa")

    sequences_file = os.path.join(sequences_dir, "reads.sam")

    write_ref(SEQUENCE_LENGTH, reference_file)
    write_coverage(SEQUENCE_LENGTH, coverage_file)
    write_sam(SEQUENCE_LENGTH, sequences_file)
    write_variant_map(SEQUENCE_LENGTH, variant_file)

    print("---post process")
    # Post process data
    cram_file = os.path.splitext(sequences_file)[0] + ".cram"
    cram_cmd = (f"samtools view --reference {reference_file} --output-fmt cram,version=3.0 "
                f"{sequences_file} > {cram_file}")
    print(cram_cmd)
    os.system(cram_cmd)

    cram_index_cmd = f"samtools index {cram_file}"
    print(cram_index_cmd)
    os.system(cram_index_cmd)

    os.unlink(sequences_file)

    tabix_variant_cmd = f"tabix -s 1 -b 2 -e 2 {variant_file}"
    print(tabix_variant_cmd)
    os.system(tabix_variant_cmd)

    tabix_coverage_cmd = f"tabix -s 1 -b 2 -e 3 {coverage_file}"
    print(tabix_coverage_cmd)
    os.system(tabix_coverage_cmd)

    print("---done")


def write_variant_map(seq_len, out_file):
    HEADER = ("#RANDOM_SEED=1\n"
              "#MAX_RANDOM_HOM_HETS=5\n"
              "#SAMPLES_USED=1000\n"
              "#CHROM\tPOS\tREF\tALT\tHOM\tHET\n")
    SHORT_ARM_START = math.floor(seq_len * 0.20)
    SHORT_ARM_END = math.floor(seq_len * 0.30)
    LONG_ARM_START = math.floor(seq_len * 0.40)
    LONG_ARM_END = math.floor(seq_len * 0.90)
    MUT_INC = 100

    seq_gen = sequence_generator(seq_len)

    lines = bytearray()
    lines.extend(HEADER.encode())
    # Advance through sequence generator
    for pos in range(0, SHORT_ARM_START):
        next(seq_gen)

    for pos in range(SHORT_ARM_START, SHORT_ARM_END, MUT_INC):
        for i in range(0, MUT_INC-1):
            next(seq_gen)
        lines.extend(variant_line(pos, next(seq_gen)).encode())

    for pos in range(SHORT_ARM_END, LONG_ARM_START):
        next(seq_gen)

    for pos in range(LONG_ARM_START, LONG_ARM_END, MUT_INC):
        for i in range(0, MUT_INC-1):
            next(seq_gen)
        lines.extend(variant_line(pos, next(seq_gen)).encode())

    print(out_file)
    with open(out_file, "wb") as ofile:
        with bgzip.BGZipWriter(ofile) as zip:
            zip.write(lines)


def variant_line(pos, ref_base):
    if(ref_base is None):
        return None
    # inversions
    alt_base = {"C": "T", "T": "C", "G": "A", "A": "G"}[ref_base]
    return(f"chr77\t{pos}\t{ref_base}\t{alt_base}\t\t100\n")


def write_sam(seq_len, out_file):
    SHORT_ARM_START = math.floor(seq_len * 0.20)
    SHORT_ARM_END = math.floor(seq_len * 0.30)
    LONG_ARM_START = math.floor(seq_len * 0.40)
    LONG_ARM_END = math.floor(seq_len * 0.90)
    INC = 151

    # Use same sequence as reference
    seq_gen = sequence_generator(seq_len)

    lines = []
    # Advance through sequence generator
    for pos in range(0, SHORT_ARM_START):
        next(seq_gen)

    for pos in range(SHORT_ARM_START, SHORT_ARM_END, INC):
        lines.append(sam_line(pos, seq_gen, INC))

    for pos in range(SHORT_ARM_END, LONG_ARM_START):
        next(seq_gen)

    for pos in range(LONG_ARM_START, LONG_ARM_END, INC):
        lines.append(sam_line(pos, seq_gen, INC))

    with open(out_file, "w") as ofile:
        ofile.writelines(lines)


def sam_line(pos, gen, increment):
    seq_arr = bytearray(increment)
    for i in range(0, increment):
        seq_arr[i] = ord(next(gen))
        sam_line = (f"demotmplt{pos}\t99\tchr77\t{pos}\t0\t151M\t=\t{pos+300}\t451\t"
                    f"{seq_arr.decode()}\t{'?'*increment}\tMD:Z:151\tNM:i:0\n")
    return(sam_line)


def write_coverage(seq_len, out_file):
    SHORT_ARM_START = math.floor(seq_len * 0.20)
    SHORT_ARM_END = math.floor(seq_len * 0.30)
    LONG_ARM_START = math.floor(seq_len * 0.40)
    LONG_ARM_END = math.floor(seq_len * 0.90)

    rows = static_coverage(SHORT_ARM_START, SHORT_ARM_END)
    rows.extend(static_coverage(LONG_ARM_START, LONG_ARM_END))

    with open(out_file, "wb") as ofile:
        with bgzip.BGZipWriter(ofile) as zip:
            zip.write(rows)


# Create list of coverage incrementing 50bp at a time.
def static_coverage(begin, end):
    CHROM = "77"
    STATIC_STATS = {"1": 0.750, "10": 0.25, "100": 0, "15": 0.125, "20": 0.100,
                    "25": 0.050, "30": 0.025, "5": 0.350, "50": 0.001, "chrom": CHROM,
                    "mean": 8.25, "median": 4}
    INC = 50
    result = bytearray()

    for pos in range(begin, end, INC):
        stats = STATIC_STATS.copy()
        stats['start'] = pos+1
        stats['end'] = pos+INC
        result.extend(f"{CHROM}\t{stats['start']}\t{stats['end']}\t{json.dumps(stats)}\n".encode())
    # handle any remainder smaller than INC size.
    if(pos < end):
        stats = STATIC_STATS.copy()
        stats['start'] = pos+1
        stats['end'] = end
        result.extend(f"{CHROM}\t{stats['start']}\t{stats['end']}\t{json.dumps(stats)}\n".encode())

    return(result)


def write_ref(seq_len, out_file):
    LINE_LENGTH = 50
    SEQUENCE_LINES = seq_len // LINE_LENGTH
    REF_HEADER = f">chr77  LN:{seq_len}  rl:Chromosome  AS:DemoAssembly\n"

    seq_gen = sequence_generator(seq_len)

    with open(out_file, "w") as ofile:
        ofile.write(REF_HEADER)
        for line in range(SEQUENCE_LINES):
            for char in range(LINE_LENGTH):
                ofile.write(next(seq_gen))
            ofile.write("\n")


# Approximate structure of a chromosome ref
def sequence_generator(seq_len):
    FAKEGENE = "TTCGCCAAGGAGGCCGAGAACGAG"
    i = 0
    # 20% N's
    while i < seq_len * 0.20:
        yield("N")
        i += 1
    # 10% FAKEGENE (TTC GCC AAG GAG GCC GAG AAC GAG)
    while i < seq_len * 0.30:
        for char in FAKEGENE:
            yield(char)
            i += 1
    # 10% N's
    while i < seq_len * 0.40:
        yield("N")
        i += 1
    # 50% FAKEGENE (TTC GCC AAG GAG GCC GAG AAC GAG)
    while i < seq_len * 0.90:
        for char in FAKEGENE:
            yield(char)
            i += 1
    # 10 % N and all subequent calls.
    while True:
        yield("N")


if __name__ == "__main__":
    main()
