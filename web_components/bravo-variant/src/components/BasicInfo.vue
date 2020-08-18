<template>
  <div class="card shadow-sm" style="min-width: 300px">
    <div class="card-body">
      <div class="container-fluid">
        <div class="row">
          <div class="col-6 col-sm-7 text-left text-truncate">Chromosome</div>
          <div class="col-6 col-sm-5 text-right">{{ this.variant.chrom }}</div>
        </div>
        <div class="row">
          <div class="col-5 col-sm-7 text-left text-truncate">Position</div>
          <div class="col-7 col-sm-5 text-right">{{ this.variant.pos.toLocaleString() }}</div>
        </div>
        <div class="row">
          <div class="col-7 col-sm-7 text-left text-truncate">Reference allele</div>
          <div class="col-5 col-sm-5 text-right text-truncate">{{ this.variant.variant_id.split("-")[2] }}</div>
        </div>
        <div class="row">
          <div class="col-7 col-sm-7 text-left text-truncate">Alternate allele</div>
          <div class="col-5 col-sm-5 text-right text-truncate">{{ this.variant.variant_id.split("-")[3] }}</div>
        </div>
        <div v-if="variant.rsids.length > 0" class="row">
          <div class="col-5 col-sm-6 text-left text-truncate">rsID</div>
          <div class="col-7 col-sm-6 text-right">
            <span v-for="item in this.variant.rsids" style="margin-left:5px">
              <a :href="'https://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=' + item">{{ item }}</a>
            </span>
          </div>
        </div>
        <div class="row">
          <div class="col-4 col-sm-8 text-left text-truncate">Filter</div>
          <div class="col-8 col-sm-4 text-right">
            <span v-for="item in this.variant.filter" v-bind:class="{ 'badge badge-success': item == 'PASS', 'badge badge-danger': item != 'PASS' }" style="margin-right:1px">{{ item }}</span>
          </div>
        </div>
        <div class="row">
          <div class="col-4 col-sm-8 text-left text-truncate">ClinVar</div>
          <div class="col-8 col-sm-4 text-right">
            <span v-if="clinvar_loading" class="text-muted">Checking...</span>
            <span v-else-if="clinvar_error" class="text-muted">Unavailable</span>
            <span v-else-if="this.clinvar_links.length == 0" class="text-muted">None</span>
            <span v-else v-for="link in this.clinvar_links" style="margin-left:5px">
              <a :href="link">Open</a>
            </span>
          </div>
        </div>
        <div class="row">
          <div class="col-4 col-sm-8 text-left text-truncate">PubMed</div>
          <div class="col-8 col-sm-4 text-right">
            <span v-if="pubmed_loading">Checking...</span>
            <span v-else-if="pubmed_error">Unavailable</span>
            <span v-else-if="this.pubmed_links.length == 0" class="text-muted">None</span>
            <span v-else v-for="link in this.pubmed_links" style="margin-left:5px">
              <a :href="link">Open</a>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: 'basicinfo',
  props: ['variant'],
  data: function() {
    return {
      clinvar_loading: true,
      clinvar_error: false,
      clinvar_links: [],
      pubmed_loading: true,
      pubmed_error: false,
      pubmed_links: []
    }
  },
  methods: {
    checkClinVar: function() {
      var queries = [];
      for (const rsid of this.variant.rsids) {
        queries.push(axios.get(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=${rsid}&retmode=json`));
      }
      axios
        .all(queries)
        .then( responses => {
          for (var i = 0; i < responses.length; ++i) {
            if (responses[i].data.esearchresult.count > 0) {
              this.clinvar_links.push(`https://www.ncbi.nlm.nih.gov/clinvar?term=${this.variant.rsids[i]}`);
            }
          }
          if (this.clinvar_links.length == 0) { // try chrom and position query
            axios
              .get(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=${this.variant.chrom}[chr]%20AND%20${this.variant.pos}[chrpos]&retmode=json`)
              .then( response => {
                if (response.data.esearchresult.count > 0) {
                  this.clinvar_links.push(`https://www.ncbi.nlm.nih.gov/clinvar?term=${this.variant.chrom}[chr]%20AND%20${this.variant.pos}[chrpos]`);
                }
                this.clinvar_loading = false;
              })
              .catch( error => {
                this.clinvar_error = true;
                this.clinvar_loading = false;
              });
          } else {
            this.clinvar_loading = false;
          }
        })
        .catch( errors => {
          this.clinvar_error = true;
          this.clinvar_loading = false;
        });
    },
    checkPubMed: function() {
      var queries = [];
      for (const rsid of this.variant.rsids) {
        queries.push(axios.get(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=${rsid}&retmode=json`));
      }
      axios
        .all(queries)
        .then( responses => {
          for (var i = 0; i < responses.length; ++i) {
            if (responses[i].data.esearchresult.count > 0) {
              this.pubmed_links.push(`https://www.ncbi.nlm.nih.gov/pubmed?term=${this.variant.rsids[i]}`);
            }
          }
          this.pubmed_loading = false;
        })
        .catch( errors => {
          this.pubmed_error = true;
          this.pubmed_loading = false;
        });

    }
  },
  mounted: function() {
    this.checkClinVar();
    this.checkPubMed();
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
