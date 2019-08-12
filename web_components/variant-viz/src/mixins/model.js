
export const Model = {
  methods: {
    tranlateFilters(filter) {
      var new_filters = [];
      filter.forEach(f => {
        var field = Object.keys(this.field2title).find( key => this.field2title[key] == f.field );
        if (field) {
          var dictionary = this.domain_dictionary[field];
          if (dictionary) {
            var value = Object.keys(dictionary).find( key => dictionary[key].text == f.value );
            new_filters.push({ "field": field, "type": f.type, "value": value });
          } else {
            new_filters.push({ "field": field, "type": f.type, "value": f.value });
          }
        }
      });
      return new_filters;
    }
  },
  beforeCreate() {
    this.field2title = {
      "variant_id": "ID",
      "pos": "Position",
      "annotation.region.consequence": "Consequence",
      "annotation.region.lof": "LoF",
      "filter": "Quality",
      "cadd_phred": "CADD",
      "allele_num": "N Alleles",
      "het_count": "Het",
      "hom_count": "HomAlt",
      "allele_freq": "Frequency (%)"
    };
    this.domain_dictionary = {
      'annotation.region.lof': {
        'HC': { 'text': 'High Confidence', 'color': 'black' },
        'LC': { 'text': 'Low Confidence', 'color': 'black' },
      },
      'annotation.region.consequence': {
        'transcript_ablation': { 'text': 'transcript ablation', 'color': '#fb0007' },
        'splice_acceptor_variant': { 'text': 'splice acceptor', 'color': '#fc4016' },
        'splice_donor_variant': { 'text': 'splice donor', 'color': '#fc4016' },
        'stop_gained': { 'text': 'stop gained', 'color': '#fb0007' },
        'frameshift_variant': { 'text': 'frameshift', 'color': '#8000c9' },
        'stop_lost': { 'text': 'stop lost', 'color': '#fb0007' },
        'start_lost': { 'text': 'start lost', 'color': '#d8b60a' },
        'transcript_amplification': { 'text': 'transcript amplification', 'color': '#fc4ca5' },
        'inframe_insertion': { 'text': 'inframe insetion', 'color': '#fc4ca5' },
        'inframe_deletion': { 'text': 'inframe deletion', 'color': '#fc4ca5' },
        'missense_variant': { 'text': 'missense', 'color': '#d8b60a' },
        'protein_altering_variant': { 'text': 'protein altering', 'color': '#fb006d' },
        'splice_region_variant': { 'text': 'splice region', 'color': '#fc6940' },
        'incomplete_terminal_codon_variant': { 'text': 'incomplete terminal codon', 'color': '#fb00ff' },
        'start_retained_variant': { 'text': 'start retained', 'color': '#68f007' },
        'stop_retained_variant': { 'text': 'stop retained', 'color': '#68f007' },
        'synonymous_variant': { 'text': 'synonymous', 'color': '#68f007' },
        'coding_sequence_variant': { 'text': 'coding sequence', 'color': '#387b02' },
        'mature_miRNA_variant': { 'text': 'mature miRNA', 'color': '#387b02' },
        '5_prime_UTR_variant': { 'text': '5\' UTR', 'color': '#69b9c2' },
        '3_prime_UTR_variant': { 'text': '3\' UTR', 'color': '#69b9c2' },
        'non_coding_transcript_exon_variant': { 'text': 'non-coding transcript exon', 'color': '#2fc726' },
        'intron_variant': { 'text': 'intron', 'color': '#09458a' },
        'NMD_transcript_variant': { 'text': 'NMD transcript', 'color': '#fc2c07' },
        'non_coding_transcript_variant': { 'text': 'non-coding transcript', 'color': '#2fc726' },
        'upstream_gene_variant': { 'text': 'upstream', 'color': '#91a5c2' },
        'downstream_gene_variant': { 'text': 'downstream', 'color': '#91a5c2' },
        'TFBS_ablation': { 'text': 'TFBS ablation', 'color': '#921a20' },
        'TFBS_amplification': { 'text': 'TFBS amplification', 'color': '#921a20' },
        'TF_binding_site_variant': { 'text': 'TF binding site', 'color': '#921a20' },
        'regulatory_region_ablation': { 'text': 'regulatory region ablation', 'color': '#921a20' },
        'regulatory_region_amplification': { 'text': 'regulatory region amplification', 'color': '#921a20' },
        'feature_elongation': { 'text': 'feature elongation', 'color': '#6c6c6c' },
        'regulatory_region_variant': { 'text': 'regulatory region', 'color': '#921a20' },
        'feature_truncation': { 'text': 'feature truncation', 'color': '#6c6c6c' },
        'intergenic_variant': { 'text': 'intergenic', 'color': '#505050' },
      },
      'populations': {
        'ALL': 'All individuals',
        'OTH': 'Others',
        'AFR': 'African',
        'AMR': 'Ad Mixed American',
        'EAS': 'East Asian',
        'ASN': 'Asian',
        'EUR': 'European',
        'SAS': 'South Asian',
        'FIN': 'Finnish',
        'NFE': 'Non-Finnish European',
        'ASJ': 'Ashkenazi Jewish'
      }
    };
  }
}
