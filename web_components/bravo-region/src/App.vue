<template>
  <div id="bravoviz">
    <info v-bind:region="region" v-on:goto_region="redirectToRegion"/>
    <div class="parent-menu">
      <div style="display: inline-block;">
        <button class="parent-menu-button" v-on:click="showMenuDropDown = !showMenuDropDown">
          Panels <font-awesome-icon style="background-color: transparent; display: inline-block; vertical-align: middle" :icon="panelsIcon"></font-awesome-icon>
        </button>
        <div v-if="showMenuDropDown" class="parent-menu-dropdown">
          <div>
            <a href="#" v-on:click.prevent="showSummaries = !showSummaries; showMenuDropDown = !showMenuDropDown"><div v-bind:style="showSummaries ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Summary</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showDepth = !showDepth; showMenuDropDown = !showMenuDropDown"><div v-bind:style="showDepth ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Avg. Depth</a>
          </div>
          <div v-if="!gene_view">
            <a href="#" v-on:click.prevent="showGenes = !showGenes; showMenuDropDown = !showMenuDropDown"><div v-bind:style="showGenes ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Genes</a>
          </div>
          <div v-if="gene_view">
            <a href="#" v-on:click.prevent="showGene = !showGene; showMenuDropDown = !showMenuDropDown"><div v-bind:style="showGene ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Transcripts</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showSNV = !showSNV; showMenuDropDown = !showMenuDropDown"><div v-bind:style="showSNV ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Variants Count</a>
          </div>
        </div>
      </div>
      <div style="display: inline-block;">
        <button class="parent-menu-button" v-on:click="showTableMenuDropDown = !showTableMenuDropDown">
          Columns <font-awesome-icon style="background-color: transparent; display: inline-block; vertical-align: middle" :icon="columnsIcon"></font-awesome-icon>
        </button>
        <div v-if="showTableMenuDropDown" class="parent-menu-dropdown">
          <div>
            <a href="#" v-on:click.prevent="showColumnVariantID = !showColumnVariantID; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnVariantID ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Variant ID</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumnRsID = !showColumnRsID; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnRsID ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> rsID</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumnConsequence = !showColumnConsequence; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnConsequence ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Consequence</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumnAnnotation = !showColumnAnnotation; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnAnnotation ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Annotation</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumnLOFTEE = !showColumnLOFTEE; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnLOFTEE ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> LOFTEE</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumnQuality = !showColumnQuality; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnQuality ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Quality</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumnCADD = !showColumnCADD; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnCADD ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> CADD</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumnNAlleles = !showColumnNAlleles; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnNAlleles ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> N Alleles</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumnHet = !showColumnHet; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnHet ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Het</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumHomAlt = !showColumHomAlt; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumHomAlt ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> HomAlt</a>
          </div>
          <div>
            <a href="#" v-on:click.prevent="showColumnFrequency = !showColumnFrequency; showTableMenuDropDown = !showTableMenuDropDown"><div v-bind:style="showColumnFrequency ? 'display: inline;' : 'display: inline; visibility: hidden;'">&#10004;</div> Frequency (%)</a>
          </div>
        </div>
      </div>
      <div style="display: inline-block;">
        <button v-if="gene_view" class="parent-menu-button" v-on:click="toggleIntrons()">
          <div v-if="showIntrons">Introns <font-awesome-icon style="background-color: transparent; display: inline-block; vertical-align: middle" :icon="showIntronsIcon"></font-awesome-icon></div>
          <div v-else>Introns <font-awesome-icon style="background-color: transparent; display: inline-block; vertical-align: middle" :icon="hideIntronsIcon"></font-awesome-icon></div>
        </button>
      </div>
      <div class="d-none d-sm-inline" style="display: inline-block;"> <!-- don't show download button on mobile devices i.e. devices with very small screens -->
        <button type="button" class="parent-menu-button" v-on:click="download++">CSV
          <font-awesome-icon style="background-color: transparent; display: inline-block; vertical-align: middle" :icon="downloadIcon"></font-awesome-icon>
        </button>
      </div>
    </div>
    <div style="position: relative; min-height: 20px">
      <summaries v-if="showSummaries" v-on:close="showSummaries = false" v-bind:api="api" v-bind:region="region" v-bind:filters="activeFilters"/>
      <depth v-if="showDepth" v-on:close="showDepth = false" v-bind:api="api" v-bind:region="region" v-bind:dimensions="dimensions" v-bind:hoveredVariant="hoveredVariant"/>
      <genes v-if="showGenes && !gene_view" v-on:close="showGenes = false" v-on:click="genesClick" v-bind:api="api" v-bind:region="region" v-bind:dimensions="dimensions" v-bind:hoveredVariant="hoveredVariant"/>
      <gene v-if="showGene && gene_view" v-on:close="showGene = false" v-bind:region="region" v-bind:dimensions="dimensions" v-bind:hoveredVariant="hoveredVariant"/>
      <snv v-if="showSNV" v-on:close="showSNV = false" v-bind:api="api" v-bind:region="region" v-bind:dimensions="dimensions" v-bind:filters="activeFilters" v-bind:visibleVariants="visibleVariants" v-bind:hoveredVariant="hoveredVariant"/>
      <coordinates v-bind:region="region" v-bind:dimensions="dimensions"/>
      <snvfilter ref="filter"
        v-bind:suggestions="filterSuggestions"
        v-bind:filters="activeFilters"
        v-on:filter="onFilterChange"/>
      <snvtable ref="snvtable"
        v-on:suggestions="onFilterSuggestionsChange"
        v-on:scroll="variantsScroll"
        v-on:hover="variantHover"
        v-bind:region="region"
        v-bind:api="api"
        v-bind:filters="activeFilters"
        v-bind:paginationSize="paginationSize"
        v-bind:download="download"
        v-bind:showColumnVariantID="showColumnVariantID"
        v-bind:showColumnRsID="showColumnRsID"
        v-bind:showColumnConsequence="showColumnConsequence"
        v-bind:showColumnAnnotation="showColumnAnnotation"
        v-bind:showColumnLOFTEE="showColumnLOFTEE"
        v-bind:showColumnQuality="showColumnQuality"
        v-bind:showColumnCADD="showColumnCADD"
        v-bind:showColumnNAlleles="showColumnNAlleles"
        v-bind:showColumnHet="showColumnHet"
        v-bind:showColumHomAlt="showColumHomAlt"
        v-bind:showColumnFrequency="showColumnFrequency"/>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faWindowRestore, faEyeSlash, faEye, faDownload, faColumns } from '@fortawesome/free-solid-svg-icons';
import coordinates from './components/Coordinates.vue';
import depth from './components/Depth.vue';
import genes from './components/Genes.vue';
import gene from './components/Gene.vue';
import snv from './components/SNV.vue';
import snvtable from './components/SNVTable.vue';
// import sv from './components/SV.vue';
// import svtable from './components/SVTable.vue';
import summaries from './components/Summaries.vue';
import info from './components/Info.vue';
import snvfilter from './components/SNVFilter.vue';

export default {
  name: "bravoregion",
  components: {
    FontAwesomeIcon,
    coordinates,
    depth,
    genes,
    gene,
    snv,
    snvtable,
    // sv,
    // svtable,
    summaries,
    info,
    snvfilter
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
      columnsIcon: faColumns,
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

      showTableMenuDropDown: false,
      showColumnVariantID: true,
      showColumnRsID: true,
      showColumnConsequence: true,
      showColumnAnnotation: true,
      showColumnLOFTEE: true,
      showColumnQuality: true,
      showColumnCADD: true,
      showColumnNAlleles: false,
      showColumnHet: true,
      showColumHomAlt: true,
      showColumnFrequency: true,

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
        });
    },
    toggleIntrons() {
      this.domain2range(!this.showIntrons);
      this.showIntrons = !this.showIntrons;
    },
    onResize() {
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
    }
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
  font-size: 14px;
}
.parent-menu-button {
  outline: none;
  padding: 0px 7px 0px 7px;
  margin: 1px 1px 1px 1px;
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
