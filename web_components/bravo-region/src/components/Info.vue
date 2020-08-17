/* eslint-disable */

<template>
  <div class="child-component">
    <div class="container-fluid">
      <div class="row">
        <div class="col-12">
          <div v-if="computedRegion.gene != null">
            <h1 class="display-5"><i>{{computedRegion.gene.gene_name}}</i></h1>
            <h6>{{computedRegion.gene.full_gene_name}}</h6>
            <ul class="list-inline">
              <li class="list-inline-item">Ensembl ID: <a v-bind:href="'http://www.ensembl.org/Homo_sapiens/geneview?gene=' + computedRegion.gene.gene_id">{{computedRegion.gene.gene_id}}</a> |</li>
              <li class="list-inline-item">Gene type: <span style="color:#85144b;">{{computedRegion.gene.gene_type}}</span> |</li>
              <li class="list-inline-item">Region: <a v-on:click="$emit('goto_region', computedRegion.gene.chrom, computedRegion.gene.start, computedRegion.gene.stop)" href="#">{{computedRegion.gene.chrom}}:{{computedRegion.gene.start.toLocaleString()}}-{{computedRegion.gene.stop.toLocaleString()}}</a> |</li>
              <li class="list-inline-item">Total length: {{(computedRegion.gene.stop - computedRegion.gene.start + 1).toLocaleString()}} bp | </li>
              <li class="list-inline-item">Exonic length: {{ computedRegion.gene.coding_regions.reduce((total, entry) => total + entry[1] - entry[0] + 1, 0).toLocaleString() }} bp</li>
              <li class="list-inline-item"> | <a v-bind:href="'http://pheweb.sph.umich.edu/SAIGE-UKB/gene/' + computedRegion.gene.gene_name">UK Biobank PheWeb</a></li>
              <li v-if="computedRegion.gene.omim_accession" class="list-inline-item"> | <a v-bind:href="'https://omim.org/entry/' + computedRegion.gene.omim_accession">OMIM</a></li>
              <li class="list-inline-item"> | <a v-bind:href="'https://www.genecards.org/cgi-bin/carddisp.pl?gene=' + computedRegion.gene.gene_id">GeneCards</a></li>
              <li class="list-inline-item"> | <a v-bind:href="'https://genome.ucsc.edu/cgi-bin/hgTracks?db=GRCh38&position=' + computedRegion.gene.chrom + ':' + computedRegion.gene.start + '-' + computedRegion.gene.stop">UCSC Browser</a></li>
            </ul>
          </div>
          <div v-if="(computedRegion.gene == null) && (computedRegion.regionChrom != null) && (computedRegion.regionStart != null) && (computedRegion.regionStop != null)">
            <h1 class="display-5">{{computedRegion.regionChrom}}:{{computedRegion.regionStart.toLocaleString()}}-{{computedRegion.regionStop.toLocaleString()}}</h1>
            <ul class="list-inline">
              <li class="list-inline-item">Region length: {{(computedRegion.regionStop - computedRegion.regionStart + 1).toLocaleString()}} bp</li>
              <li class="list-inline-item"> | <a v-bind:href="'https://genome.ucsc.edu/cgi-bin/hgTracks?db=GRCh38&position=' + computedRegion.regionChrom + ':' + computedRegion.regionStart + '-' + computedRegion.regionStop">UCSC Browser</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "info",
    props: {
      'region': {
        type: Object
      }
    },
    components: {
    },
    data: function() {
      return {
      }
    },
    methods: {
    },
    beforeCreate: function() {
      // initialize non reactive data
    },
    created: function() {
    },
    mounted: function() {
    },
    computed: {
      computedRegion: function() {
        return JSON.parse(JSON.stringify(this.region));
      }
    },
    watch: {
    }
  }
</script>

<style scoped>
.child-component {
  position: relative;
  min-height: 50px;
  margin-top: 5px;
}
</style>
