<template>
  <div id="bravoviz">
    <info v-bind:region="region" v-on:goto_region="redirectToRegion"/>
    <div class="parent-menu">
      <button class="parent-menu-button" v-on:click="showMenuDropDown = !showMenuDropDown">
        Panels <font-awesome-icon style="background-color: transparent; display: inline-block; vertical-align: middle" :icon="panelsIcon"></font-awesome-icon>
      </button>
      <div v-if="showMenuDropDown" class="parent-menu-dropdown">
        <div>
          <a href="#" v-on:click.prevent="showSummaries = !showSummaries; showMenuDropDown = !showMenuDropDown">Summary Display <div style="display: inline" v-if="showSummaries">On</div><div style="display: inline" v-else>Off</div></a>
        </div>
        <div>
          <a href="#" v-on:click.prevent="showDepth = !showDepth; showMenuDropDown = !showMenuDropDown">Depth Display <div style="display: inline" v-if="showDepth">On</div><div style="display: inline" v-else>Off</div></a>
        </div>
        <div v-if="!gene_view">
          <a href="#" v-on:click.prevent="showGenes = !showGenes; showMenuDropDown = !showMenuDropDown">Genes Display <div style="display: inline" v-if="showGenes">On</div><div style="display: inline" v-else>Off</div></a>
        </div>
        <div v-if="gene_view">
          <a href="#" v-on:click.prevent="showGene = !showGene; showMenuDropDown = !showMenuDropDown">Transcripts Display <div style="display: inline" v-if="showGene">On</div><div style="display: inline" v-else>Off</div></a>
        </div>
        <div>
          <a href="#" v-on:click.prevent="showSNV = !showSNV; showMenuDropDown = !showMenuDropDown">Variants Display <div style="display: inline" v-if="showSNV">On</div><div style="display: inline" v-else>Off</div></a>
        </div>
      </div>
      <button v-if="gene_view" class="parent-menu-button" v-on:click="toggleIntrons()">
        <div v-if="showIntrons">Shows introns <font-awesome-icon style="background-color: transparent; display: inline-block; vertical-align: middle" :icon="showIntronsIcon"></font-awesome-icon></div>
        <div v-else>Hides introns <font-awesome-icon style="background-color: transparent; display: inline-block; vertical-align: middle" :icon="hideIntronsIcon"></font-awesome-icon></div>
      </button>
    </div>
  <div style="position: relative; min-height: 20px">
    <summaries v-if="showSummaries" v-on:close="showSummaries = false" v-bind:api="api" v-bind:region="region"/>
    <depth v-if="showDepth" v-on:close="showDepth = false" v-bind:api="api" v-bind:region="region" v-bind:dimensions="dimensions" v-bind:hoveredVariant="hoveredVariant"/>
    <genes v-if="showGenes && !gene_view" v-on:close="showGenes = false" v-on:click="genesClick" v-bind:api="api" v-bind:region="region" v-bind:dimensions="dimensions" v-bind:hoveredVariant="hoveredVariant"/>
    <gene v-if="showGene && gene_view" v-on:close="showGene = false" v-bind:region="region" v-bind:dimensions="dimensions" v-bind:hoveredVariant="hoveredVariant"/>
    <snv v-if="showSNV" v-on:close="showSNV = false" v-bind:api="api" v-bind:region="region" v-bind:dimensions="dimensions" v-bind:filters="activeFilters" v-bind:visibleVariants="visibleVariants" v-bind:hoveredVariant="hoveredVariant"/>
    <coordinates v-bind:region="region" v-bind:dimensions="dimensions"/>

    <div>
      <button type="button" class="download-button" v-on:click="download++">Download
        <font-awesome-icon style="background-color: transparent; display: inline-block; vertical-align: middle" :icon="downloadIcon"></font-awesome-icon>
      </button>
      <bravofilter ref="filter" v-bind:suggestions="filterSuggestions" v-on:filter="onFilterChange" v-bind:filters="activeFilters"/>
    </div>
    <snvtable ref="snvtable" v-on:suggestions="onFilterSuggestionsChange" v-on:scroll="variantsScroll" v-on:hover="variantHover" v-bind:region="region" v-bind:api="api" v-bind:filters="activeFilters" v-bind:paginationSize="paginationSize" v-bind:download="download"/>
  </div>
</div>
</template>

<script>
import axios from "axios";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faWindowRestore, faEyeSlash, faEye, faDownload } from '@fortawesome/free-solid-svg-icons';
import { Model } from './mixins/model.js'
import coordinates from './components/Coordinates.vue';
import depth from './components/Depth.vue';
import genes from './components/Genes.vue';
import gene from './components/Gene.vue';
import snv from './components/SNV.vue';
import snvtable from './components/SNVTable.vue';
import sv from './components/SV.vue';
import svtable from './components/SVTable.vue';
import summaries from './components/Summaries.vue';
import info from './components/Info.vue';
import bravofilter from 'bravo-filter/src/App.vue'; // used "npm link"

export default {
  name: "bravoviz",
  mixins: [ Model ],
  components: {
    FontAwesomeIcon,
    coordinates,
    depth,
    genes,
    gene,
    snv,
    snvtable,
    sv,
    svtable,
    bravofilter,
    summaries,
    info
  },
  props: {
    homepage: {
      type: String
    },
    api: {
      type: String
    },
    paginationSize: {
      type: Number
    },
    chrom: {
      type: String
    },
    start: {
      type: Number
    },
    stop: {
      type: Number
    },
    gene_name: {
      type: String
    },
    filters: {
      type: Array,
      default: function() {
        return [ { title: "Quality", text: "PASS", tabulator_filter: { field: "filter", type: "=", value: "PASS" }} ];
      }
    }
  },
  computed: {
    gene_view() {
      return (this.gene_name != null);
    }
  },
  data: function() {
    return {
      dimensions: {
        width: 300, // arbitrary initial value. will be changed on "mounted" hook
        margin: {
          left: 40,
          right: 15,
          top: 12,
          bottom: 5
        }
      },

      region: {
        regionChrom: this.chrom,
        regionStart: this.start,
        regionStop: this.stop,
        gene: null,
        introns: true,
        segments: {
          region: [this.start, this.stop],
          plot: [0, 300], // arbitrary initial value. will be changed on "mounted" hook
        }
      },

      activeFilters: JSON.parse(JSON.stringify(this.filters)),
      filterSuggestions: {},

      showSummaries: true,
      showDepth: true,
      showGenes: this.gene_name == null,
      showGene: this.gene_name != null,
      showSNV: true,
      showMenuDropDown: false,
      showIntrons: true,
      panelsIcon: faWindowRestore,
      hideIntronsIcon: faEyeSlash,
      showIntronsIcon: faEye,
      downloadIcon: faDownload,

      hoveredVariant: {
        index: null,
        data: null,
        hovered: null
      },
      visibleVariants: {
        start_index: null,
        stop_index: null,
        data: null
      },

      download: 0,

    }
  },
  methods: {
    unwindGeneExons: function (gene) {
      gene.exons = [];
      gene.cds = [];
      gene.coding_regions = [];
      gene.features.sort((a, b) => a.start - b.start);
      gene.features.forEach(d => {
        if (d.feature_type == 'exon') {
          d.transcript_type = gene.transcripts.find(t => t.transcript_id == d.transcript_id).transcript_type;
          gene.exons.push(d);
        } else if (d.feature_type == 'CDS'){
          d.transcript_type = gene.transcripts.find(t => t.transcript_id == d.transcript_id).transcript_type;
          gene.cds.push(d);
        }
      });
      gene.exons.forEach(d => {
        if (gene.coding_regions.length == 0) {
          gene.coding_regions.push([d.start, d.stop]);
        } else {
          var last = gene.coding_regions[gene.coding_regions.length - 1];
          if (last[1] >= d.start) {
            if (last[1] < d.stop) {
              last[1] = d.stop;
            }
          } else {
            gene.coding_regions.push([d.start, d.stop]);
          }
        }
      });
    },
    domain2range: function(show_introns) {
      if (!show_introns) {
        const gap_width = 5; // 5 pixels for a gap between axis breaks
        const range_width = this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right - (this.region.gene.coding_regions.length - 1) * gap_width;
        const domain_width = this.region.gene.coding_regions.reduce((length, region) => length + region[1] - region[0] + 1, 0);
        var domain = [];
        var range = [];
        this.region.gene.coding_regions.forEach((region, i) => {
          domain.push(region[0]);
          domain.push(region[1]);
          if (i == 0) {
            range.push(0);
            range.push(Math.floor(range_width * (region[1] - region[0]) / domain_width));
          } else if (i == this.region.gene.coding_regions.length - 1) {
            range.push(range[range.length - 1] + gap_width);
            range.push(this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right);
          } else {
            range.push(range[range.length - 1] + gap_width);
            range.push(range[range.length - 1] + Math.floor(range_width * (region[1] - region[0]) / domain_width));
          }
        });
        this.region.introns = false;
        this.region.segments = {
          region: domain,
          plot: range
        };
      } else {
        this.region.introns = true;
        this.region.segments = {
          region: [this.region.regionStart, this.region.regionStop],
          plot: [0, this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right]
        };
      }
    },
    loadGene: function() {
      axios
        .get(`${this.api}genes/api/${this.gene_name}`)
        .then( response => {
          var payload = response.data;
          if (payload.data.length > 0) {
            payload.data.forEach(d => {
              if ((d.gene_name == this.gene_name) || (d.gene_id == this.gene_name)) {
                this.unwindGeneExons(d);
                this.region = {
                  regionChrom: d.chrom,
                  regionStart: d.start,
                  regionStop: d.stop,
                  gene: d,
                  introns: true,
                  segments: {
                    region: [d.start, d.stop],
                    plot: [0, this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right]
                  }
                }
              }
            });
          }
        })
        .catch( error => {
        });
    },
    toggleIntrons() {
      this.domain2range(!this.showIntrons);
      this.showIntrons = !this.showIntrons;
    },
    onResize(event) {
      this.dimensions.width = this.$el.clientWidth;
      if (this.gene_view) {
        this.domain2range(this.showIntrons);
      } else {
        this.region.segments.plot = [0, this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right];
      }
    },
    redirectToRegion(chrom, start, stop) {
      window.location.href = this.homepage + `region/snv/${chrom}-${start}-${stop}`;
    },
    genesClick(gene) {
      window.location.href = this.homepage + `gene/snv/${gene.gene_id}`;
    },
    variantsScroll(top_variant_idx, bottom_variant_idx, variants) {
      this.visibleVariants = {
        start_index: top_variant_idx,
        stop_index: bottom_variant_idx,
        data: variants
      }
    },
    variantHover(variant_idx, variant_data, hovered) {
      this.hoveredVariant = {
        index: variant_idx,
        data: variant_data,
        hovered: hovered
      }
    },
    onFilterSuggestionsChange(suggestions) {
      this.filterSuggestions = suggestions;
    },
    onFilterChange(filters) {
      this.activeFilters = filters;
    },
  },
  beforeCreate: function() {
  },
  created: function() {
  },
  mounted: function() {
    this.dimensions.width = this.$el.clientWidth;
    if (this.gene_view) {
      this.loadGene();
    } else {
      this.region.segments.plot = [0, this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right];
    }
    window.addEventListener('resize', this.onResize);
  },
  beforeDestroy: function() {
    window.removeEventListener('resize', this.onResize);
  }
}
</script>

<style scoped>
.parent-menu {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  display: inline-block;
  font-size: 13px;
}
.parent-menu-button {
  outline: none;
  padding: 0px 7px 0px 7px;
  margin: 0px 1px 0px 1px;
  color: white;
  background-color: #007bff;
  border: 1px solid #007bff;
  border-radius: 2px;
  box-shadow: none;
}
.parent-menu-button:hover {
  background-color: #0062cc;
  border-color: #0062cc;
}
.parent-menu-dropdown {
  display: block;
  position: absolute;
  background-color: #eeeeee;
  min-width: 140px;
  overflow: auto;
  box-shadow: 0px 4px 8px 0px rgba(0,0,0,0.2);
  border: 1px solid #cbcacb;
  z-index: 999;
}
.parent-menu-dropdown a {
  display: block;
  padding: 4px 2px;
  color: black;
  text-align: left;
  text-decoration: none;
}
.parent-menu-dropdown a:hover {
  background-color: #cccccc;
}
.download-button {
  float: left;
  background-color: #eeeeee;
  outline: none;
  padding: 0px 7px 0px 7px;
  margin: 0px 1px 0px 1px;
  border: 1px solid #cccccc;
  height: 36px;
}

#app {
  /* border: 1px solid red; */
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  position: relative;
  text-align: center;
  color: #2c3e50;
  /* margin-top: 60px; */
}
</style>
