
export const Model = {
  methods: {
    getField(title, isGene) {
      var main_fields = Object.keys(this.field2title);
      var feature = isGene ? 'gene' : 'region';
      for (var i = 0; i < main_fields.length; ++i) {
        let main_field = main_fields[i];
        if (typeof this.field2title[main_field] === "object") {
          if (feature in this.field2title[main_field]) {
            let nested_field = Object.keys(this.field2title[main_field][feature]).find( nested_field => this.field2title[main_field][feature][nested_field] == title);
            if (nested_field) {
              return `${main_field}.${feature}.${nested_field}`;
            }
          }
        } else if (this.field2title[main_field] == title) {
          return main_field;
        }
      }
      return null;
    },
    getTitle(field) {
      var title = field.split('.').reduce((obj, key) => (obj && obj[key] !== undefined) ? obj[key] : undefined, this.field2title);
      return title ? title : field;
    }
  },
  beforeCreate() {
    this.field2title = {
      "variant_id": "ID (rsID)",
      "pos": "Position",
      "filter": "Quality",
      "cadd_phred": "CADD",
      "allele_num": "N Alleles",
      "het_count": "Het",
      "hom_count": "HomAlt",
      "allele_freq": "Frequency (%)",
      "annotation": {
        "region": {
          "consequence": "Consequence",
          "lof": "LoF",
        },
        "gene": {
          "consequence": "Consequence",
          "lof": "LoF",
        }
      }
    };
    this.text2value = {
      'filter': (text) => text,
    },
    this.value2text = {
      'pos': (value) => value.toLocaleString(),
      'filter': (value) => `${value}`,
      'cadd_phred': (value) => value != null ? `${value.toFixed(2)}` : null,
      'allele_num': (value) => value.toLocaleString(),
      'het_count': (value) => value.toLocaleString(),
      'hom_count': (value) => value.toLocaleString(),
      'allele_freq': (value) => `${(value * 100).toPrecision(3)}%`,
      'annotation.region.consequence': (value) => this.domain_dictionary.consequence[value].text,
      'annotation.region.lof': (value) => this.domain_dictionary.lof[value].text,
      'annotation.gene.consequence': (value) => this.domain_dictionary.consequence[value].text,
      'annotation.gene.lof': (value) => this.domain_dictionary.lof[value].text
    },
    this.domain_dictionary = {
      'lof': {
        'HC': { 'text': 'high-confidence', 'color': 'black', 'desc': 'Variants which pass all LOFTEE filters' },
        'LC': { 'text': 'low-confidence', 'color': 'black', 'desc': 'Variants which fail at least one LOFTEE filter' },
      },
      'consequence': {
        'transcript_ablation': { 'text': 'transcript ablation', 'color': '#fb0007', 'desc': 'A feature ablation whereby the deleted region includes a transcript feature' },
        'splice_acceptor_variant': { 'text': 'splice acceptor', 'color': '#fc4016', 'desc': 'A splice variant that changes the 2 base region at the 3\' end of an intron' },
        'splice_donor_variant': { 'text': 'splice donor', 'color': '#fc4016', 'desc': 'A splice variant that changes the 2 base region at the 5\' end of an intron' },
        'stop_gained': { 'text': 'stop gained', 'color': '#fb0007', 'desc': 'A sequence variant whereby at least one base of a codon is changed, resulting in a premature stop codon, leading to a shortened transcript' },
        'frameshift_variant': { 'text': 'frameshift', 'color': '#8000c9', 'desc': 'A sequence variant which causes a disruption of the translational reading frame, because the number of nucleotides inserted or deleted is not a multiple of three' },
        'stop_lost': { 'text': 'stop lost', 'color': '#fb0007', 'desc': 'A sequence variant where at least one base of the terminator codon (stop) is changed, resulting in an elongated transcript' },
        'start_lost': { 'text': 'start lost', 'color': '#d8b60a', 'desc': 'A codon variant that changes at least one base of the canonical start codon' },
        'transcript_amplification': { 'text': 'transcript amplification', 'color': '#fc4ca5', 'desc': 'A feature amplification of a region containing a transcript' },
        'inframe_insertion': { 'text': 'inframe insertion', 'color': '#fc4ca5', 'desc': 'An inframe non synonymous variant that inserts bases into in the coding sequence' },
        'inframe_deletion': { 'text': 'inframe deletion', 'color': '#fc4ca5', 'desc': 'An inframe non synonymous variant that deletes bases from the coding sequence' },
        'missense_variant': { 'text': 'missense', 'color': '#d8b60a', 'desc': 'A sequence variant, that changes one or more bases, resulting in a different amino acid sequence but where the length is preserved' },
        'protein_altering_variant': { 'text': 'protein altering', 'color': '#fb006d', 'desc': 'A sequence_variant which is predicted to change the protein encoded in the coding sequence' },
        'splice_region_variant': { 'text': 'splice region', 'color': '#fc6940', 'desc': 'A sequence variant in which a change has occurred within the region of the splice site, either within 1-3 bases of the exon or 3-8 bases of the intron' },
        'incomplete_terminal_codon_variant': { 'text': 'incomplete terminal codon', 'color': '#fb00ff', 'desc': 'A sequence variant where at least one base of the final codon of an incompletely annotated transcript is changed' },
        'start_retained_variant': { 'text': 'start retained', 'color': '#68f007', 'desc': 'A sequence variant where at least one base in the start codon is changed, but the start remains'},
        'stop_retained_variant': { 'text': 'stop retained', 'color': '#68f007', 'desc': 'A sequence variant where at least one base in the terminator codon is changed, but the terminator remains'},
        'synonymous_variant': { 'text': 'synonymous', 'color': '#68f007', 'desc': 'A sequence variant where there is no resulting change to the encoded amino acid'},
        'coding_sequence_variant': { 'text': 'coding sequence', 'color': '#387b02', 'desc': 'A sequence variant that changes the coding sequence' },
        'mature_miRNA_variant': { 'text': 'mature miRNA', 'color': '#387b02', 'desc': 'A transcript variant located with the sequence of the mature miRNA' },
        '5_prime_UTR_variant': { 'text': '5\' UTR', 'color': '#69b9c2', 'desc': 'A UTR variant of the 5\' UTR' },
        '3_prime_UTR_variant': { 'text': '3\' UTR', 'color': '#69b9c2', 'desc': 'A UTR variant of the 3\' UTR' },
        'non_coding_transcript_exon_variant': { 'text': 'non-coding transcript exon', 'color': '#2fc726', 'desc': 'A sequence variant that changes non-coding exon sequence in a non-coding transcript' },
        'intron_variant': { 'text': 'intron', 'color': '#09458a', 'desc': 'A transcript variant occurring within an intron' },
        'NMD_transcript_variant': { 'text': 'NMD transcript', 'color': '#fc2c07', 'desc': 'A variant in a transcript that is the target of NMD' },
        'non_coding_transcript_variant': { 'text': 'non-coding transcript', 'color': '#2fc726', 'desc': 'A transcript variant of a non coding RNA gene' },
        'upstream_gene_variant': { 'text': 'upstream', 'color': '#91a5c2', 'desc': 'A sequence variant located 5\' of a gene' },
        'downstream_gene_variant': { 'text': 'downstream', 'color': '#91a5c2', 'desc': 'A sequence variant located 3\' of a gene' },
        'TFBS_ablation': { 'text': 'TFBS ablation', 'color': '#921a20', 'desc': 'A feature ablation whereby the deleted region includes a transcription factor binding site'},
        'TFBS_amplification': { 'text': 'TFBS amplification', 'color': '#921a20', 'desc': 'A feature amplification of a region containing a transcription factor binding site' },
        'TF_binding_site_variant': { 'text': 'TF binding site', 'color': '#921a20', 'desc': 'A sequence variant located within a transcription factor binding site' },
        'regulatory_region_ablation': { 'text': 'regulatory region ablation', 'color': '#921a20', 'desc': 'A feature ablation whereby the deleted region includes a regulatory region' },
        'regulatory_region_amplification': { 'text': 'regulatory region amplification', 'color': '#921a20', 'desc': 'A feature amplification of a region containing a regulatory region' },
        'feature_elongation': { 'text': 'feature elongation', 'color': '#6c6c6c', 'desc': 'A sequence variant that causes the extension of a genomic feature, with regard to the reference sequence' },
        'regulatory_region_variant': { 'text': 'regulatory region', 'color': '#921a20', 'desc': 'A sequence variant located within a regulatory region' },
        'feature_truncation': { 'text': 'feature truncation', 'color': '#6c6c6c', 'desc': 'A sequence variant that causes the reduction of a genomic feature, with regard to the reference sequence' },
        'intergenic_variant': { 'text': 'intergenic', 'color': '#505050', 'desc': 'A sequence variant located in the intergenic region, between genes' },
      }
    };
  }
}
