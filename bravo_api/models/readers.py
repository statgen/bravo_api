from bravo_api.models.utils import make_xpos
from urllib.parse import unquote
import pysam
import gzip
import json
import logging
import sys

def read_sv(filename):
    with pysam.VariantFile(filename) as ifile:
        for x in ['SVTYPE', 'SUPP', 'AVGLEN', 'END', 'STRANDS', 'CIEND', 'CIPOS']:
            if x not in ifile.header.info:
                raise Exception(f'Missing {x} INFO field.')
        for record in ifile.fetch():
            svtype = record.info['SVTYPE']
            if svtype not in {'DEL', 'DUP', 'INV'}: # we don't use insertions and translocations
                continue
            chrom = record.contig[3:] if record.contig.startswith('chr') else record.contig
            cipos = list(map(int, record.info['CIPOS']))
            ciend = list(map(int, record.info['CIEND']))
            #maxlen = max(0, (record.stop + ciend[1]) - (record.pos + cipos[0])) + 1
            #minlen = max(0, (record.stop + ciend[0]) - (record.pos + cipos[1])) + 1
            variant = {
               'variant_id': record.id,
               'chrom': chrom,
               'pos': record.pos,
               'xpos': make_xpos(chrom, record.pos),
               'filter': record.filter.keys(),
               'qual': record.qual,
               'type': { 'DEL': 'Deletion', 'DUP': 'Duplication', 'INV': 'Inversion' }[svtype],
               'support': int(record.info['SUPP']),
               'stop': record.stop,
               'xstop': make_xpos(chrom, record.stop),
               'cipos': cipos,
               'ciend': ciend,
               'avglen': record.info['AVGLEN']
            }
            yield variant


def rs_from_effects(allele_effects):
    rs = set()
    for effect in allele_effects:
        rs.update(x for x in effect['Existing_variation'].split('&') if x.startswith('rs'))
    return list(rs)


# based on Ensembl VEP calculated vatiant consequences (https://useast.ensembl.org/info/genome/variation/prediction/predicted_data.html)
snv_consequence2code = { name: i for i, name in enumerate(reversed([
   'transcript_ablation',
   'splice_acceptor_variant',
   'splice_donor_variant',
   'stop_gained',
   'frameshift_variant',
   'stop_lost',
   'start_lost',
   'transcript_amplification',
   'inframe_insertion',
   'inframe_deletion',
   'missense_variant',
   'protein_altering_variant',
   'splice_region_variant',
   'incomplete_terminal_codon_variant',
   'start_retained_variant',
   'stop_retained_variant',
   'synonymous_variant',
   'coding_sequence_variant',
   'mature_miRNA_variant',
   '5_prime_UTR_variant',
   '3_prime_UTR_variant',
   'non_coding_transcript_exon_variant',
   'intron_variant',
   'NMD_transcript_variant',
   'non_coding_transcript_variant',
   'upstream_gene_variant',
   'downstream_gene_variant',
   'TFBS_ablation',
   'TFBS_amplification',
   'TF_binding_site_variant',
   'regulatory_region_ablation',
   'regulatory_region_amplification',
   'feature_elongation',
   'regulatory_region_variant',
   'feature_truncation',
   'intergenic_variant'
]), 1)}

snv_lof2code = {name: i for i, name in enumerate(reversed(['HC', 'LC']), 1)}

# we require the same bins for all histograms. Rationale: if all bins are the same, then we don't
# need to store their boundaries for each variant and we save several hundreds GB of storage +
# reduce document size (which may allow to keep in RAM more documents).
hist_bins = [2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5,
             72.5, 77.5, 82.5, 87.5, 92.5, 97.5]


def annotation_from_effects(allele_effects):
    region = {}
    genes = {}
    regulators = []
    motifs = []
    for effect in allele_effects:
        consequences = sorted(effect['Consequence'].split('&'), key = lambda x: snv_consequence2code[x], reverse = True)
        consequences_coded = [ snv_consequence2code[x] for x in consequences ]
        if 'LoF' in effect and effect['LoF'] != '':
            lof = effect['LoF']
        else:
            lof = None
        if lof is not None:
            lof_coded = snv_lof2code[lof]
        region.setdefault('consequence', set()).update(consequences)
        region.setdefault('_consequence', set()).update(consequences_coded)
        if lof is not None:
            region.setdefault('lof', set()).add(lof)
            region.setdefault('_lof', set()).add(lof_coded)
        if effect['Feature_type'] == 'Transcript':
            gene = genes.setdefault(effect['Gene'], { 'transcripts': [] })
            gene.setdefault('consequence', set()).update(consequences)
            gene.setdefault('_consequence', set()).update(consequences_coded)
            transcript = {
               'name': effect['Feature'],
               'biotype': effect['BIOTYPE'],
               'consequence': consequences,
               '_consequence': consequences_coded
            }
            hgvs_c = unquote(effect['HGVSc']).split(':', 1)[-1]
            hgvs_p = unquote(effect['HGVSp']).split(':', 1)[-1]
            hgvs = None
            if hgvs_p:
                transcript['HGVSp'] = hgvs_p
                if '=' not in hgvs_p: # ie. non-synonymous
                    hgvs = hgvs_p
            if hgvs_c:
                transcript['HGVSc'] = hgvs_c
                if hgvs is None:
                    hgvs = hgvs_c
            if hgvs is not None:
                for consequence_code in consequences_coded:
                    region.setdefault('hgvs', dict()).setdefault(consequence_code, set()).add(hgvs)
                    gene.setdefault('hgvs', dict()).setdefault(consequence_code, set()).add(hgvs)
            if lof is not None:
                gene.setdefault('lof', set()).add(lof)
                gene.setdefault('_lof', set()).add(lof_coded)
                transcript['lof'] = lof
                if effect['LoF_filter'] != '':
                    transcript['lof_filter'] = effect['LoF_filter']
                if effect['LoF_flags'] != '':
                    transcript['lof_flags'] = effect['LoF_flags']
                transcript['_lof'] = lof_coded
            gene['transcripts'].append(transcript)
        elif effect['Feature_type'] == 'RegulatoryFeature':
            regulators.append({
               'name': effect['Feature'],
               'biotype': effect['BIOTYPE']
            })
        elif effect['Feature_type'] == 'MotifFeature':
            motifs.append({
               'name': effect['Feature']
            })
    annotations = {}
    for key, value in region.items():
        if key == '_consequence' or key == '_lof':
            region[key] = sorted(value, reverse = True)
        elif key == 'consequence':
            region[key] = sorted(value, key = lambda x: snv_consequence2code[x], reverse = True)
        elif key == 'lof':
            region[key] = sorted(value, key = lambda x: snv_lof2code[x], reverse = True)
        elif key == 'hgvs':
            region[key] = []
            for _, hgvss in sorted(value.items(), reverse = True):
                for hgvs in hgvss:
                    if hgvs not in region[key]:
                        region[key].append(hgvs)
    annotations['region'] = region
    if genes:
        annotations['genes'] = []
        for gene_name, gene_values in genes.items():
            gene = { 'name': gene_name }
            for key, value in gene_values.items():
                if key == '_consequence' or key == '_lof':
                    gene[key] = sorted(value, reverse = True)
                elif key == 'consequence':
                    gene[key] = sorted(value, key = lambda x: snv_consequence2code[x], reverse = True)
                elif key == 'lof':
                    gene[key] = sorted(value, key = lambda x: snv_lof2code[x], reverse = True)
                elif key == 'transcripts':
                    gene[key] = value
                elif key == 'hgvs':
                    gene[key] = []
                    for _, hgvss in sorted(value.items(), reverse = True):
                        for hgvs in hgvss:
                            if hgvs not in gene[key]:
                                gene[key].append(hgvs)
            annotations['genes'].append(gene)
    if regulators:
        annotations['regulatory'] = regulators
    if motifs:
        annotations['motifs'] = motifs
    return annotations


def get_pub_freqs(allele_effects):
    pub_freqs = {}
    for effect in allele_effects:
        af = effect.get('AF', '')
        if af != '':
            db = pub_freqs.setdefault('1000G', { 'ALL': float(af.split('&')[0]) })
            for pop in ['AFR', 'AMR', 'EAS', 'EUR', 'SAS']:
                af = effect.get(pop + '_AF', '')
                if af != '':
                    db[pop] = float(af.split('&')[0])
        af = effect.get('gnomAD_AF', '')
        if af != '':
            db = pub_freqs.setdefault('gnomAD', {'ALL': float(af.split('&')[0]) })
            for pop in ['AFR', 'AMR', 'ASJ', 'EAS', 'FIN', 'NFE', 'OTH', 'SAS']:
                af = effect.get('gnomAD_' + pop + '_AF', '')
                if af != '':
                    db[pop] = float(af.split('&')[0])
    return [{'ds': key, **value} for key, value in pub_freqs.items()]


def read_snv(filename):
    with pysam.VariantFile(filename) as ifile:
        #for x in ['AC', 'AN', 'AF', 'Hom', 'CADD_PHRED', 'AVGDP', 'AVGDP_R', 'AVGGQ', 'AVGGQ_R', 'DP_HIST', 'DP_HIST_R', 'GQ_HIST', 'GQ_HIST_R', 'CSQ']:
        for x in ['AC', 'AN', 'AF', 'Hom', 'CADD_PHRED', 'AVGDP', 'AVGDP_R', 'DP_HIST', 'DP_HIST_R', 'CSQ']:
            if not x in ifile.header.info:
                logging.error(f'Missing {x} INFO field meta-information.')
                sys.exit(1)
        vep_field_names = ifile.header.info['CSQ'].description.split(':', 1)[-1].strip().split('|')
        for x in ['DP_HIST', 'DP_HIST_R']:
        #for x in ['DP_HIST', 'DP_HIST_R', 'GQ_HIST', 'GQ_HIST_R']:
            if list(map(float, ifile.header.info[x].description.split(':', 1)[-1].strip().split('|'))) != hist_bins:
                logging.error(f'Incorrect histogram bins size in {x} INFO field meta-information.')
                sys.exit(1)

        # we assume that all INFO fields with _PCTL suffix (and storing 2 floats: percentile lower bound, percentile upper bound) are percentiles of quality metrics
        qc_metric_names = []
        for meta_key, meta_description in ifile.header.info.items():
            if meta_key.endswith('_PCTL') and meta_description.type == 'Float' and meta_description.number == 2:
                qc_metric = meta_key[:-5]
                if qc_metric in ifile.header.info or qc_metric == 'QUAL':
                    qc_metric_names.append((qc_metric, meta_key))

        for record in ifile.fetch():
            effects = dict()
            # parse VEP predicter allele specific effects on each transcript
            for effect in record.info['CSQ']:
                effect = effect.split('|')
                assert len(vep_field_names) == len(effect), (vep_field_names, effect)
                effect = dict(zip(vep_field_names, effect))
                effects.setdefault(int(effect['ALLELE_NUM']) - 1, []).append(effect)
            chrom = record.contig[3:] if record.contig.startswith('chr') else record.contig
            for i, alt_allele in enumerate(record.alts): # each alternate allele generates separate entry/vatiant in database
                if record.info['AN'] == 0: # skip if all genotypes are missing
                    continue
                if record.info['AC'][i] == 0: # skip monomorphic
                    continue
                allele_effects = effects[i]
                try:
                    variant = {
                       'chrom': chrom,
                       'pos': record.pos,
                       'xpos': make_xpos(chrom, record.pos),
                       'stop': record.stop, # TODO: check if pysam generates this correctly
                       'xstop': make_xpos(chrom, record.stop),
                       'variant_id': f'{chrom}-{record.pos}-{record.ref}-{alt_allele}',
                       'rsids': rs_from_effects(allele_effects),
                       'site_quality': record.qual,
                       'filter': sorted(record.filter.keys()),
                       'allele_count': record.info['AC'][i],
                       'allele_num': record.info['AN'],
                       'allele_freq': record.info['AF'][i],
                       'hom_count': record.info['Hom'][i],
                       'het_count': record.info['AC'][i] - 2 * record.info['Hom'][i],
                       'cadd_phred': record.info['CADD_PHRED'][i] if 'CADD_PHRED' in record.info else None,
                       'annotation': annotation_from_effects(allele_effects),
                       'avg_dp': record.info['AVGDP'],
                       'avg_dp_alt': record.info['AVGDP_R'][i + 1],
                       #'avg_gq': record.info['AVGGQ'],
                       #'avg_gq_alt': record.info['AVGGQ_R'][i + 1],
                       'dp_hist': list(map(int, record.info['DP_HIST'].split('|'))),
                       'dp_hist_alt': list(map(int, record.info['DP_HIST_R'][i + 1].split('|'))),
                       #'gq_hist': list(map(int, record.info['GQ_HIST'].split('|'))),
                       #'gq_hist_alt': list(map(int, record.info['GQ_HIST_R'][i + 1].split('|'))),
                       'qc_metrics': { metric: [record.qual if metric == 'QUAL' else record.info[metric], record.info[percentiles][0], record.info[percentiles][1]] for metric, percentiles in qc_metric_names }
                    }
                    pub_freqs = get_pub_freqs(allele_effects)
                    if pub_freqs:
                        variant['pub_freq'] = pub_freqs
                except:
                    logging.exception(f'Failed to process {chrom}-{record.pos}-{record.ref}-{alt_allele} variant.')
                    continue
                yield variant


def read_canonical_transcripts(filename):
    with gzip.open(filename, 'rt') as ifile:
        for line in ifile:
            gene, transcript = line.strip().split()
            yield (gene, transcript)


def read_omim(filename):
    with gzip.open(filename, 'rt') as ifile:
        header = ifile.readline().rstrip('\n').split('\t')
        for line in ifile:
            fields = line.rstrip('\n').split('\t')
            assert len(header) == len(fields), f'len({header}) != len({fields})'
            fields = dict(zip(header, fields))
            if not fields['MIM gene accession'] or not fields['MIM gene description']:
                continue
            yield (fields['Gene stable ID'], fields['Transcript stable ID'], fields['MIM gene accession'], fields['MIM gene description'])


def read_hgnc(filename):
    with gzip.open(filename, 'rt') as ifile:
        header = ifile.readline().rstrip('\n').split('\t')
        for line in ifile:
            fields = line.rstrip('\n').split('\t')
            assert len(header) == len(fields), f'len({header}) != len({fields})'
            fields = dict(zip(header, fields))
            if not fields['ensembl_gene_id']:
                continue
            other_names = fields['alias_symbol'].strip('"').split('|') if fields['alias_symbol'] else []
            if fields['prev_symbol'] and fields['prev_symbol'] not in other_names:
                for name in fields['prev_symbol'].strip('"').split('|'):
                    other_names.append(name)
            yield (fields['symbol'], fields['ensembl_gene_id'], fields['name'], other_names)


def read_gencode(filename, region_types):
    with gzip.open(filename, 'rt') as ifile:
        for line in ifile:
            if line.startswith('#'):
                continue
            fields = line.rstrip().split('\t')
            feature_type = fields[2]
            if feature_type not in region_types:
                continue
            chrom = fields[0][3:] if fields[0].startswith('chr') else fields[0]
            start, stop = map(int, fields[3:5])
            attributes = dict(map(lambda x: x.strip('"'), x.strip().split()) for x in fields[8].split(';') if x != '')
            region = {
               'chrom': chrom,
               'start': start,
               'stop': stop,
               'strand': fields[6],
               'xstart': make_xpos(chrom, start),
               'xstop': make_xpos(chrom, stop),
               'gene_id': attributes['gene_id'].split('.')[0]
            }
            if 'gene' in region_types:
                region['gene_name'] = attributes['gene_name']
                region['gene_type'] = attributes['gene_type']
            if 'transcript' in region_types:
                region['transcript_id'] = attributes['transcript_id'].split('.')[0]
                region['transcript_type'] = attributes['transcript_type']
                region['unconfirmed'] = any(x in ['cds_end_NF', 'cds_start_NF', 'mRNA_end_NF', 'mRNA_start_NF'] for x in attributes.get('tag', []))
            if 'exon' in region_types or 'CDS' in region_types or 'UTR' in region_types:
                if 'transcript_id' not in region:
                    region['transcript_id'] = attributes['transcript_id'].split('.')[0]
                if 'unconfirmed' not in region:
                    region['unconfirmed'] = any(x in ['cds_end_NF', 'cds_start_NF', 'mRNA_end_NF', 'mRNA_start_NF'] for x in attributes.get('tag', []))
                region['feature_type'] = feature_type
            yield region


def read_qc_metrics(filename):
    with gzip.open(filename, 'rt') as ifile:
        for line in ifile:
            metric = json.loads(line)
            yield metric
