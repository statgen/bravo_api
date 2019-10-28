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
              <li class="list-inline-item">Ensembl ID: <a v-bind:href="'http://www.ensembl.org/Homo_sapiens/geneview?gene=' + computedRegion.gene.gene_id">{{computedRegion.gene.gene_id}}</a></li>
              <li class="list-inline-item">Gene type: <span style="color:#85144b;">{{computedRegion.gene.gene_type}}</span></li>
              <li class="list-inline-item">Region: {{computedRegion.gene.chrom}}:{{computedRegion.gene.start.toLocaleString()}}-{{computedRegion.gene.stop.toLocaleString()}}</li>
              <li class="list-inline-item">Total length: {{(computedRegion.gene.stop - computedRegion.gene.start + 1).toLocaleString()}} bp</li>
              <li class="list-inline-item">Exonic length: {{ computedRegion.gene.coding_regions.reduce((total, entry) => total + entry[1] - entry[0] + 1, 0).toLocaleString() }} bp</li>
            </ul>
          </div>
          <div v-if="(computedRegion.gene == null) && (computedRegion.regionChrom != null) && (computedRegion.regionStart != null) && (computedRegion.regionStop != null)">
            <h1 class="display-5">{{computedRegion.regionChrom}}:{{computedRegion.regionStart.toLocaleString()}}-{{computedRegion.regionStop.toLocaleString()}}</h1>
            <h6>Region length: {{(computedRegion.regionStop - computedRegion.regionStart + 1).toLocaleString()}} bp</h6>
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
      computedRegion: {
        handler: function(newValue, oldValue) {
          if (newValue.gene != null) {
            if ((oldValue.gene == null) || (oldValue.gene.gene_id != newValue.gene.gene_id)) {
              // this.load();
            }
          } else if (newValue.gene == null) {
            if (oldValue.gene != null) {
              // this.load();
            } else if ((newValue.regionChrom != oldValue.regionChrom) || (newValue.regionStart != oldValue.regionStart) || (newValue.regionStop != oldValue.regionStop)) {
              // this.load();
            }
          }
        },
        deep: true
      },
    }
  }
</script>

<style scoped>
.child-component {
  position: relative;
  min-height: 50px;
  margin-top: 5px;
}
.close-button {
  position: absolute;
  top: 0px;
  right: 0px;
  padding: 0px 4px 0px 4px;
  color: black;
  font-size: 11px;
  outline: none;
  background-color: #eeeeee;
  border: 1px solid #cccccc;
  border-radius: 2px;
  box-shadow: none;
  opacity: 0.5;
  z-index: 999;
}
.hscroll-button {
  padding: 0px;
  width: 32px;
  height: 32px;
  color: #7f7f7f;
  font-size: 20px;
  outline: none;
  background-color: #ffffff;
  border: 1px solid #cccccc;
  border-radius: 50%;
  box-shadow: none;
  z-index: 998;
}
.hscroll-button:hover {
  box-shadow: 0px 0px 4px 0px rgba(0,0,0,.3);
}
.scroll-right {
  position: absolute;
  top: 50%;
  -webkit-transform: translateY(-50%);
  transform: translateY(-50%);
  right: 0px;
}
.scroll-left {
  position: absolute;
  top: 50%;
  -webkit-transform: translateY(-50%);
  transform: translateY(-50%);
  left: 0px;
}
.close-button:hover {
  background-color: #cccccc;
  opacity: 1.0;
}
.cards {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  overflow-x: auto;
  padding-bottom: 5px;
  scroll-behavior: smooth; /* not supported in Safari and Edge */
}
.cards::-webkit-scrollbar { /* don't show horizonal scroll but still allow scrolling */
  display: none;
}
.card {
  height: auto;
  flex: 0 0 auto;
  margin-right: 8px;
  align-self: flex-start;
}
.table {
  margin-bottom: 5px;
}
.card-body {
  padding: 10px;
}
</style>
