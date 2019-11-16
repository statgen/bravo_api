/* eslint-disable */

<template>
<div class="child-component">
  <div v-if="loading" class="d-flex align-items-center bravo-message">
    <div class="spinner-border spinner-border-sm text-primary ml-auto" role="status" aria-hidden="true"></div>
    <strong>&nbsp;Loading...</strong>
  </div>
  <div v-if="loaded && empty" class="bravo-message">No variants</div>
  <div v-if="failed" class="bravo-message">Error while loading variants</div>

  <div ref="snvtable" class="table-sm"></div>
</div>
</template>

<script>
import { Model } from '../mixins/model.js'
import axios from "axios";
import Tabulator from "tabulator-tables";
import 'tabulator-tables/dist/css/bootstrap/tabulator_bootstrap4.min.css';

export default {
  mixins: [ Model ],
  name: "snvtable",
  props: {
    'region': {
      type: Object
    },
    'filters': {
      type: Array
    },
    'api': {
      type: String
    },
    'paginationSize': {
      type: Number
    },
    'download': {
      type: Number
    }
  },
  components: {
  },
  data: function() {
    return {
      loading: false,
      loaded: false,
      empty: true,
      failed: false,
    };
  },
  methods: {
    createConsequenceColumnDefinition: function(title, field) {
      return {
        title: title,
        field: field,
        align: "left",
        formatter: (cell, params, onrendered) => {
          var html = "<div>";
          cell.getValue().forEach( v => {
            var aes = this.domain_dictionary.consequence[v];
            html += `<span class="badge badge-light" style="margin-right:1px;color:${aes.color};font-weight:bold;-webkit-text-stroke: 0.15px black;">${aes.text}</span>`;
          });
          html += "</div>";
          return html;
        }
      };
    },
    createLoFColumnDefinition: function(title, field) {
      return {
        title: title,
        field: field,
        width: 110,
        align: "left",
        formatter: (cell, params, onrendered) => {
          var html = "<div>";
          if (cell.getValue()) {
            cell.getValue().forEach(v => {
              var badge_type = v == "HC" ? "success" : "warning";
              var text = this.domain_dictionary.lof[v].text;
              html += `<span class="badge badge-${badge_type}" style="margin-right:1px">${text}</span>`;
            });
          }
          html += "</div>";
          return html;
        }
      };
    },
    addAnnotationColumn: function(annotation_name) {
      const json_fields = annotation_name.split('.');
      if ((json_fields.length != 3) || (json_fields[0] != 'annotation')) {
        return;
      }
      if (json_fields[1] == 'region') {
        var old_annotation_name = 'annotation.gene.' + json_fields[2];
      } else if (json_fields[1] == 'gene') {
        var old_annotation_name = 'annotation.region.' + json_fields[2];
      } else {
        return;
      }
      if (this.tabulator.columnManager.findColumn(old_annotation_name)) {
        this.tabulator.deleteColumn(old_annotation_name);
      }
      if (!this.tabulator.columnManager.findColumn(annotation_name)) {
        if (json_fields[2] == 'consequence') {
          this.tabulator.addColumn(this.createConsequenceColumnDefinition(this.getTitle(annotation_name), annotation_name), false, 'variant_id');
        } else if (json_fields[2] == 'lof') {
          this.tabulator.addColumn(this.createLoFColumnDefinition(this.getTitle(annotation_name), annotation_name), false, 'variant_id');
        }
      }
    },
    loadData: function() {
      if (this.region.gene != null) {
        this.addAnnotationColumn('annotation.gene.lof');
        this.addAnnotationColumn('annotation.gene.consequence');
        this.tabulator.setData(`${this.api}variants/gene/snv/${this.region.gene.gene_id}`);
      } else if ((this.region.regionChrom != null) && (this.region.regionStart !=null) && (this.region.regionStop != null)) {
        this.addAnnotationColumn('annotation.region.lof');
        this.addAnnotationColumn('annotation.region.consequence');
        this.tabulator.setData(`${this.api}variants/region/snv/${this.region.regionChrom}-${this.region.regionStart}-${this.region.regionStop}`);
      }
    },
    loadFilterSuggestions: function() {
      var annotation_field = `annotation.${this.computedRegion.gene != null ? 'gene' : 'region'}`;
      return axios
        .get(`${this.api}variants/snv`)
        .then(response => {
          var payload = response.data;
          var suggestions = {};

          suggestions['Consequence'] = { value: 'Consequence', data: { category: 'Field', items: {}}};
          suggestions['Consequence'].data.items['Synonymous'] = {
            value: 'Synonymous',
            data: {
              category: 'By Group',
              filters: [
                { title: 'Consequence', text: this.value2text[`${annotation_field}.consequence`]('synonymous_variant'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'synonymous_variant' }},
                { title: 'Consequence', text: this.value2text[`${annotation_field}.consequence`]('start_retained_variant'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'start_retained_variant' }},
                { title: 'Consequence', text: this.value2text[`${annotation_field}.consequence`]('stop_retained_variant'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'stop_retained_variant' }}
              ]
            }
          };
          suggestions['Consequence'].data.items['Non-synonymous'] = {
            value: 'Non-synonymous',
            data: {
              category: 'By Group',
              filters: [
                { title: 'Consequence', text: this.value2text[`${annotation_field}.consequence`]('missense_variant'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'missense_variant' }},
                { title: 'Consequence', text: this.value2text[`${annotation_field}.consequence`]('start_lost'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'start_lost' }},
                { title: 'Consequence', text: this.value2text[`${annotation_field}.consequence`]('stop_gained'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'stop_gained' }},
                { title: 'Consequence', text: this.value2text[`${annotation_field}.consequence`]('stop_lost'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'stop_lost' }},
              ]
            }
          };

          payload.data['consequence'].forEach ( v => {
            var text_value = this.value2text[`${annotation_field}.consequence`](v.value);
            suggestions['Consequence'].data.items[text_value] = {
              value: text_value,
              data: {
                category: 'By Value',
                tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: v.value }
              }
            };
          });

          suggestions['LoF'] = { value: 'LoF', data: { category: 'Field', items: {}}};
          suggestions['LoF'].data.items['All'] = {
            value: 'All',
            data: {
              category: 'By Group',
              filters: [
                { title: 'LoF', text: this.value2text[`${annotation_field}.lof`]('HC'), tabulator_filter: { field: `${annotation_field}.lof`, type: '=', value: 'HC' }},
                { title: 'LoF', text: this.value2text[`${annotation_field}.lof`]('LC'), tabulator_filter: { field: `${annotation_field}.lof`, type: '=', value: 'LC' }}
              ]
            }
          };
          payload.data['lof'].forEach ( v => {
            var text_value = this.value2text[`${annotation_field}.lof`](v.value);
            suggestions['LoF'].data.items[text_value] = {
              value: text_value,
              data: {
                category: 'By Value',
                tabulator_filter: { field: `${annotation_field}.lof`, type: '=', value: v.value }
              }
            };
          });

          suggestions['Quality'] = { value: 'Quality', data: { category: 'Field', items: {}}};
          suggestions['Quality'].data.items['Passed'] = {
            value: 'Passed',
            data: {
              category: 'By Group',
              filters: [
                { title: 'Quality', text: this.value2text['filter']('PASS'), tabulator_filter: { field: 'filter', type: '=', value: 'PASS' }}
              ]
            }
          };
          suggestions['Quality'].data.items['Failed'] = {
            value: 'Failed',
            data: {
              category: 'By Group',
              filters: [
                { title: 'Quality', text: this.value2text['filter']('SVM'), tabulator_filter: {field: 'filter', type: '=', value: 'SVM' }},
                { title: 'Quality', text: this.value2text['filter']('DISC'), tabulator_filter: {field: 'filter', type: '=', value: 'DISC' }},
                { title: 'Quality', text: this.value2text['filter']('EXHET'), tabulator_filter: {field: 'filter', type: '=', value: 'EXHET' }}
              ]
            }
          };
          payload.data['filter'].forEach ( v => {
            var text_value = this.value2text['filter'](v.value);
            suggestions['Quality'].data.items[text_value] = {
              value: text_value,
              data: {
                category: 'By Value',
                tabulator_filter: { field: 'filter', type: '=', value: v.value }
              }
            };
          });

          suggestions['Frequency (%)'] = { value: 'Frequency (%)', data: { category: 'Field', items: {}}};
          [0.001, 0.005, 0.01, 0.05, 0.1, 1, 5].forEach( value => {
            var text_value = `<${value}%`;
            suggestions['Frequency (%)'].data.items[text_value] = {
              value: text_value,
              data: {
                category: 'By Value',
                tabulator_filter: { field: 'allele_freq', type: '<', value: value / 100.0 }
              }
            };
          });
          this.$emit("suggestions", suggestions);
        })
        .catch(error => {
          console.log("Error while retrieving filters meta-information.")
        });
    },
    getData: function() {
      if (this.tabulator == null) {
        return [];
      }
      return this.tabulator.getData();
    },
    getVisibleVariants: function() {
      var scrollDivHeight = this.tabulator.rowManager.height;
      var scrollDivPosition = this.tabulator.rowManager.scrollTop;
      var lastVisibleRowIndex = this.tabulator.rowManager.vDomBottom;
      var data = []
      while (lastVisibleRowIndex > 0) {
        const rowElement = this.tabulator.rowManager.displayRows[0][lastVisibleRowIndex].element;
        if (rowElement.offsetTop < scrollDivPosition + scrollDivHeight) {
          break;
        }
        lastVisibleRowIndex--;
      }
      var firstVisibleRowIndex = lastVisibleRowIndex;
      while (firstVisibleRowIndex > 0) {
        const rowElement = this.tabulator.rowManager.displayRows[0][firstVisibleRowIndex].element;
        if (rowElement.offsetTop < scrollDivPosition) {
          break;
        }
        firstVisibleRowIndex--;
      }
      if (this.tabulator.rowManager.displayRows[0].length > 0) {
        for (var i = firstVisibleRowIndex; i <= lastVisibleRowIndex; ++i) {
          data.push(this.tabulator.rowManager.displayRows[0][i].data);
        }
      }
      return { firstVisibleRowIndex, lastVisibleRowIndex, data };
    },
    scrolled: function(event) {
      if (this.tabulator.getData().length > 0) {
        var visible = this.getVisibleVariants();
        this.$emit("scroll", visible.firstVisibleRowIndex, visible.lastVisibleRowIndex, visible.data);
      }
    },
    hover: function(variant, hovered) {
      this.tabulator.getRows().forEach(r => { // clean up all elements (just in case)
        r.getElement().classList.remove("hover");
      });
      if (hovered) {
        this.tabulator.getRowFromPosition(variant).getElement().classList.add("hover");
      }
    },
  },
  beforeCreate: function() {
    // DOM-manipulating widgets should store reference statically, not dynamically
    this.tabulator = null;
  },
  created: function() {
  },
  mounted: function() {
    this.tabulator = new Tabulator(this.$refs.snvtable, {
      placeholder: null,
      ajaxURL: "",
      ajaxLoader: false,
      ajaxLoaderLoading: "",
      ajaxLoaderError: "",
      ajaxConfig: {
        method: "POST",
        headers: {
          "Content-type": "application/json; charset=utf-8",
        },
      },
      ajaxContentType: "json",
      ajaxSorting: true,
      ajaxFiltering: true,
      ajaxProgressiveLoad: "scroll",
      ajaxRequesting: (url, params) => {
        if ((url == null) || (url.length == 0)) {
          return false; //abort ajax request
        }
        this.failed = false;
        this.loaded = false;
        this.loading = true;
        return true;
      },
      ajaxURLGenerator: (url, config, params) => {
        if (params.page == 1) { // when 1st page is requested "next" must be null
          params.next = null;

          if ((this.region.gene != null) && (this.region.segments.region.length > 2)) {
            // console.log("without introns");
            params.introns = 0;
          }
        }
        return url;
      },
      ajaxResponse: (url, params, response) => {
        response.last_page = Math.ceil(response.total / response.limit);
        params.next = response.next;
        this.failed = false;
        this.loading = false;
        this.loaded = true;
        return response;
      },
      ajaxError: (xhr, textStatus, errorThrown) => {
        this.loading = false;
        this.loaded = false;
        this.failed = true;
      },
      dataLoaded: (data) => {
        if (this.tabulator != null) {
          this.empty = data.length == 0;
        }
      },
      renderComplete: (data) => {
        if (this.tabulator != null) {
          var visible = this.getVisibleVariants();
          this.$emit("scroll", visible.firstVisibleRowIndex, visible.lastVisibleRowIndex, visible.data);
        }
      },
      paginationSize: this.paginationSize,
      height: "600px",
      layout: "fitColumns",
      columns: [
        { title: this.getTitle("variant_id"), width: 180, field: "variant_id", formatter: (cell, params, onrendered) => {
            var rsids = cell.getData()['rsids'];
            if (rsids.length > 0) {
              return `<a href='${this.api}variant/snv/${cell.getValue()}'>${cell.getValue()}</a></br><span>(${rsids.join(',')})</span>`;
            }
            return `<a href='${this.api}variant/snv/${cell.getValue()}'>${cell.getValue()}</a>`;
        }},
        { title: this.getTitle("filter"), field: "filter", width: 110, align: "left", formatter: (cell, params, onrendered) => {
            var html = "<div>";
            cell.getValue().forEach( v => {
              var badge_type = v == "PASS" ? "success" : "danger";
              html += `<span class="badge badge-${badge_type}" style="margin-right:1px">${v}</span>`;
            });
            html += "</div>";
            return html;
        }},
        { title: this.getTitle("cadd_phred"), field: "cadd_phred", width: 70, align: "left", formatter: (cell, params, onrendered) =>  this.value2text["cadd_phred"](cell.getValue()) },
        { title: this.getTitle("allele_num"), field: "allele_num", width: 90, align: "left", formatter: (cell, params, onrendered) => this.value2text["allele_num"](cell.getValue()) },
        { title: this.getTitle("het_count"), field: "het_count", width: 90, align: "left", formatter: (cell, params, onrendered) => this.value2text["het_count"](cell.getValue()) },
        { title: this.getTitle("hom_count"), field: "hom_count", width: 90, align: "left", formatter: (cell, params, onrendered) => this.value2text["hom_count"](cell.getValue()) },
        { title: this.getTitle("allele_freq"), field: "allele_freq", width: 130, align: "left", formatter: (cell, params, onrendered) => this.value2text["allele_freq"](cell.getValue()) },
      ],
      initialSort: [
        { column: "variant_id", dir: "asc" }
      ],
      initialFilter: this.computedFilters,
      rowMouseEnter: (e, row) => {
        this.$emit("hover", this.tabulator.getRowPosition(row), row.getData(), true);
      },
      rowMouseLeave: (e, row) => {
        this.$emit("hover", this.tabulator.getRowPosition(row), row.getData(), false);
      }
    });
    this.$el.querySelector(".tabulator-tableHolder").addEventListener("scroll", this.scrolled);
    this.loadFilterSuggestions();
    this.loadData();
  },
  beforeDestroy: function() {
  },
  watch: {
    computedFilters: function() {
      this.tabulator.setFilter(this.computedFilters);
    },
    computedRegion: {
      handler: function(newValue, oldValue) {
        if (newValue.gene != null) {
          // we are in gene view
          if (oldValue.gene != null) {
            if (newValue.gene.gene_id != oldValue.gene.gene_id) {
              // gene changed
              this.loadData();
            } else if (newValue.introns != oldValue.introns) {
              // introns added/removed
              this.loadData();
            }
          } else {
            // we switched from the region view to gene view
            this.loadFilterSuggestions();
            this.loadData();
          }
        } else {
          // we are in region view
          if (oldValue.gene == null) {
            if ((newValue.regionChrom != oldValue.regionChrom) || (newValue.regionStart != oldValue.regionStart) || (newValue.regionStop != oldValue.regionStop)) {
              // region changed
              this.loadData();
            }
          } else {
            // we switched from the gene view to region view
            this.loadFilterSuggestions();
            this.loadData();
          }
        }
      },
      deep: true
    },
    download: function() {
      if (this.tabulator != null) {
        var name = 'variants.csv';
        if (this.region.gene != null) {
          name = `variants_${this.region.gene.gene_id}.csv`;
        } else if ((this.region.regionChrom != null) && (this.region.regionStart !=null) && (this.region.regionStop != null)) {
          name = `variants_${this.region.regionChrom}-${this.region.regionStart}-${this.region.regionStop}.csv`;
        }
        this.tabulator.download('csv', name);
      }
    }
  },
  computed: {
    computedRegion: function() {
      return JSON.parse(JSON.stringify(this.region));
    },
    computedFilters: function() {
      var filters = [];
      if (this.filters != null) {
        this.filters.forEach(f => {
          filters.push(f.tabulator_filter);
        });
      }
      return filters;
    }
  }
}
</script>
<style scoped>
.child-component {
  position: relative;
}
.child-component >>> .tabulator {
  font-size: 12px;
}
.child-component >>> .tabulator .tabulator-row:hover {
  background-color: orange;
}
.child-component >>> .tabulator .tabulator-row.hover {
  background-color: orange;
}
.bravo-message {
  position: absolute;
  top: 50%;
  left: 50%;
  -webkit-transform: translateX(-50%) translateY(-50%);
  transform: translateX(-50%) translateY(-50%);
  border: 1px solid gray;
  padding: 5px;
  background-color: white;
  opacity: 1.0;
  border-radius: 5%;
  z-index: 9999;
}
</style>
