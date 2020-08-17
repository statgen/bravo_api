/* eslint-disable */

<template>
<div class="child-component" v-on:click-annotations="showAnnotationsModal">

  <div class="modal" id="modalAnnotations" role="dialog" data-backdrop="false" style="z-index:99999;">
    <div class="modal-dialog modal-dialog-centered modal-sm" role="document">
       <div class="modal-content">
         <div class="modal-header">
           <h5 class="modal-title">{{ selectedVariantId }}</h5>
           <button type="button" class="close" data-dismiss="modal" aria-label="Close">
             <span aria-hidden="true">&times;</span>
           </button>
         </div>
          <div class="modal-body">
            <small>
              <div id="accordion">
                <div v-for="(c, index) in selectedVariantAnnotations" :key="c.consequence">
                  <span class="badge badge-light" v-bind:style="'color:' + $DOMAIN_DICTIONARY.consequence[c.consequence].color + ';font-weight:bold;-webkit-text-stroke: 0.15px black;'">&#9632;</span><a data-toggle="collapse" v-bind:href="'#collapse' + index">{{ $DOMAIN_DICTIONARY.consequence[c.consequence].text }}</a>
                  <div v-if="c.transcripts.length > 0" v-bind:id="'collapse' + index" v-bind:class="index == 0 ? 'collapse show' : 'collapse'" data-parent="#accordion">
                    <ul class="list-unstyled">
                      <li v-for="transcript in c.transcripts">
                        {{ transcript.gene_name }}: {{ transcript.transcript_name }}
                        <ul>
                          <li><span style="color: #85144b;">{{ transcript.biotype }}</span></li>
                          <li v-if="transcript.HGVSc">HGVSc: <b>{{ transcript.HGVSc }}</b></li>
                          <li v-if="transcript.HGVSp">HGVSp: <b>{{ transcript.HGVSp}}</b></li>
                        </ul>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </small>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-primary" data-dismiss="modal">Close</button>
          </div>
      </div>
    </div>
  </div>

  <div v-if="loading" class="d-flex align-items-center bravo-message">
    <div class="spinner-border spinner-border-sm text-primary ml-auto" role="status" aria-hidden="true"></div>
    <strong>&nbsp;Loading...</strong>
  </div>
  <div v-if="loaded && empty" class="bravo-message">No variants</div>
  <div v-if="failed" class="bravo-message">Error while loading variants</div>
  <div ref="snvtable" class="table-sm">


  </div>

</div>
</template>

<script>
// import { Model } from '../mixins/model.js'
import axios from "axios";
import Tabulator from "tabulator-tables";
import 'tabulator-tables/dist/css/bootstrap/tabulator_bootstrap4.min.css';

export default {
  // mixins: [ Model ],
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
    },
    'showColumnVariantID': {
      type: Boolean
    },
    'showColumnRsID': {
      type: Boolean
    },
    'showColumnConsequence': {
      type: Boolean
    },
    'showColumnAnnotation': {
      type: Boolean
    },
    'showColumnLOFTEE': {
      type: Boolean
    },
    'showColumnQuality': {
      type: Boolean
    },
    'showColumnCADD': {
      type: Boolean
    },
    'showColumnNAlleles': {
      type: Boolean
    },
    'showColumnHet': {
      type: Boolean
    },
    'showColumHomAlt': {
      type: Boolean
    },
    'showColumnFrequency': {
      type: Boolean
    }
  },
  data: function() {
    return {
      loading: false,
      loaded: false,
      empty: true,
      failed: false,
      selectedVariantId: "",
      selectedVariantAnnotations: [],
    };
  },
  methods: {
    showAnnotationsModal: function(e) {
      if (this.tabulator != null) {
        var maxTitleLength = 17;
        var data = this.tabulator.getData()[e.detail];
        if (data.variant_id.length >= maxTitleLength) {
          this.selectedVariantId = data.variant_id.substring(0, maxTitleLength) + '...';
        } else {
          this.selectedVariantId = data.variant_id;
        }
        var all_consequences_nosort = {};
        var all_consequences_sorted = [];
        if ("gene" in data.annotation) {
          data.annotation.gene.transcripts.forEach(transcript => {
            var entry = { "gene_name": data.annotation.gene.name, "transcript_name": transcript.name, "biotype": transcript.biotype };
            if ('HGVSc' in transcript) { entry['HGVSc'] = transcript.HGVSc; }
            if ('HGVSp' in transcript) { entry['HGVSp'] = transcript.HGVSp; }
            transcript.consequence.forEach(consequence => {
              if (!(consequence in all_consequences_nosort)) {
                all_consequences_nosort[consequence] = [];
              }
              all_consequences_nosort[consequence].push(entry);
            });
          });
          // order by severity
          data.annotation.gene.consequence.forEach(consequence => {
            all_consequences_sorted.push({ 'consequence': consequence, 'transcripts':  all_consequences_nosort[consequence]});
          });
        } else if ("region" in data.annotation) {
          if ("genes" in data.annotation) {
            data.annotation.genes.forEach(gene => {
              gene.transcripts.forEach(transcript => {
                var entry = { "gene_name": gene.name, "transcript_name": transcript.name, "biotype": transcript.biotype };
                if ('HGVSc' in transcript) { entry['HGVSc'] = transcript.HGVSc; }
                if ('HGVSp' in transcript) { entry['HGVSp'] = transcript.HGVSp; }
                transcript.consequence.forEach(consequence => {
                  if (!(consequence in all_consequences_nosort)) {
                    all_consequences_nosort[consequence] = [];
                  }
                  all_consequences_nosort[consequence].push(entry);
                });
              });
            });
          }
          // order by severity
          data.annotation.region.consequence.forEach(consequence => {
            if (consequence in all_consequences_nosort) {
              var consequence_transcripts = all_consequences_nosort[consequence];
            } else {
              var consequence_transcripts = [];
            }
            all_consequences_sorted.push({ 'consequence': consequence, 'transcripts':  consequence_transcripts });
          });
        }
        this.selectedVariantAnnotations.splice(0, this.selectedVariantAnnotations.length, ...all_consequences_sorted);
        $('#modalAnnotations').modal('show');
      }
    },
    createAnnotationColumnDefinition: function(region_type) {
      return {
        title: "Annotation <a class='text-info' onclick='event.stopPropagation();' data-toggle='tooltip' title='Variant annotation (defined by Sequence Onthology) with most severe effect (total number of annotations).'>?</a>",
        titleDownload: "Annotation",
        field: `annotation.${region_type}.consequence`,
        hozAlign: "left",
        minWidth: 120,
        visible: this.showColumnAnnotation,
        formatter: (cell, params, onrendered) => {
          var html = "";
          var annotations = cell.getValue();
          if (annotations.length > 0) {
            var aes = this.$DOMAIN_DICTIONARY.consequence[annotations[0]];
            html += `<span class="badge badge-light" style="margin-right:1px;color:${aes.color};font-weight:bold;-webkit-text-stroke: 0.15px black;">${aes.text}</span>`;
            html += ` <a href="javascript:void(0)" role="button" onclick='this.dispatchEvent(new CustomEvent("click-annotations", { "bubbles": true, "detail": ${cell.getRow().getPosition()} }))'>(${annotations.length})</a>` // we emit here an Event intead of directly calling Bootstrap modal, because we want to do all modal's dynamics through VueJs.
          }
          return html;
        },
        accessorDownload: (value) => {
          if (value != null) {
            return value.join(';');
          } else {
            return "";
          }
        }
      };
    },
    createLOFTEEColumnDefinition: function(region_type) {
      return {
        title: "LOFTEE <a class='text-info' onclick='event.stopPropagation();' data-toggle='tooltip' title='Variant was predicted to be Loss-of-Function by LOFTEE.'>?</a>",
        titleDownload: "LOFTEE",
        field: `annotation.${region_type}.lof`,
        hozAlign: "left",
        minWidth: 95,
        visible: this.showColumnLOFTEE,
        formatter: (cell, params, onrendered) => {
          var html = "";
          if (cell.getValue() != undefined) {
              cell.getValue().forEach(v => {
                var badge_type = v == "HC" ? "success" : "warning";
                var text = this.$DOMAIN_DICTIONARY.lof[v].text;
                html += `<span class="badge badge-${badge_type}" style="margin-right:1px">${text}</span>`;
              });
          }
          return html;
        },
        accessorDownload: (value) => {
          if (value != null) {
            return value.join(';');
          } else {
            return "";
          }
        }
      };
    },
    createConsequenceColumnDefinition: function(region_type) {
      return {
        title: "Consequence <a class='text-info' onclick='event.stopPropagation();' data-toggle='tooltip' title='HGVSc/HGVSp nomenclature for the most severe variant effect (total number of HGVSc/HGVSp).'>?</a>",
        titleDownload: "Consequence",
        field: `annotation.${region_type}.hgvs`,
        hozAlign: "left",
        headerSort: false,
        minWidth: 120,
        visible: this.showColumnConsequence,
        formatter: (cell, params, onrendered) => {
          if ((cell.getValue() != undefined) && (cell.getValue().length > 0)) {
            return cell.getValue()[0] + ` <a href="javascript:void(0)" role="button" onclick='this.dispatchEvent(new CustomEvent("click-annotations", { "bubbles": true, "detail": ${cell.getRow().getPosition()} }))'>(${cell.getValue().length})</a>`
          } else {
            return "";
          }
        },
        accessorDownload: (value) => {
          if (value != null) {
            return value.join(';');
          } else {
            return ""
          }
        }
      };
    },
    loadData: function() {
      if (this.region.gene != null) {
        ['annotation.region.hgvs', 'annotation.region.consequence', 'annotation.region.lof'].forEach(v => {
          if (this.tabulator.columnManager.findColumn(v)) {
            this.tabulator.deleteColumn(v);
          }
        });
        if (!this.tabulator.columnManager.findColumn('annotation.gene.hgvs')) {
          this.tabulator.addColumn(this.createConsequenceColumnDefinition('gene'), false, 'rsids');
        }
        if (!this.tabulator.columnManager.findColumn('annotation.gene.consequence')) {
          this.tabulator.addColumn(this.createAnnotationColumnDefinition('gene'), false, 'annotation.gene.hgvs');
        }
        if (!this.tabulator.columnManager.findColumn('annotation.gene.lof')) {
          this.tabulator.addColumn(this.createLOFTEEColumnDefinition('gene'), false, 'annotation.gene.consequence');
        }
        $(this.$el.querySelectorAll('[data-toggle="tooltip"]')).tooltip();
        this.tabulator.setData(`${this.api}variants/gene/snv/${this.region.gene.gene_id}`);
      } else if ((this.region.regionChrom != null) && (this.region.regionStart !=null) && (this.region.regionStop != null)) {
        ['annotation.gene.hgvs', 'annotation.gene.consequence', 'annotation.gene.lof'].forEach(v => {
          if (this.tabulator.columnManager.findColumn(v)) {
            this.tabulator.deleteColumn(v);
          }
        });
        if (!this.tabulator.columnManager.findColumn('annotation.region.hgvs')) {
          this.tabulator.addColumn(this.createConsequenceColumnDefinition('region'), false, 'rsids');
        }
        if (!this.tabulator.columnManager.findColumn('annotation.region.consequence')) {
          this.tabulator.addColumn(this.createAnnotationColumnDefinition('region'), false, 'annotation.region.hgvs');
        }
        if (!this.tabulator.columnManager.findColumn('annotation.region.lof')) {
          this.tabulator.addColumn(this.createLOFTEEColumnDefinition('region'), false, 'annotation.region.consequence');
        }
        $(this.$el.querySelectorAll('[data-toggle="tooltip"]')).tooltip();
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
                { title: 'Consequence', text: this.$VALUE2TEXT[`${annotation_field}.consequence`]('synonymous_variant'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'synonymous_variant' }},
                { title: 'Consequence', text: this.$VALUE2TEXT[`${annotation_field}.consequence`]('start_retained_variant'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'start_retained_variant' }},
                { title: 'Consequence', text: this.$VALUE2TEXT[`${annotation_field}.consequence`]('stop_retained_variant'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'stop_retained_variant' }}
              ]
            }
          };

          suggestions['Consequence'].data.items['Non-synonymous'] = {
            value: 'Non-synonymous',
            data: {
              category: 'By Group',
              filters: [
                { title: 'Consequence', text: this.$VALUE2TEXT[`${annotation_field}.consequence`]('missense_variant'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'missense_variant' }},
                { title: 'Consequence', text: this.$VALUE2TEXT[`${annotation_field}.consequence`]('start_lost'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'start_lost' }},
                { title: 'Consequence', text: this.$VALUE2TEXT[`${annotation_field}.consequence`]('stop_gained'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'stop_gained' }},
                { title: 'Consequence', text: this.$VALUE2TEXT[`${annotation_field}.consequence`]('stop_lost'), tabulator_filter: { field: `${annotation_field}.consequence`, type: '=', value: 'stop_lost' }},
              ]
            }
          };

          payload.data['consequence'].forEach ( v => {
            var text_value = this.$VALUE2TEXT[`${annotation_field}.consequence`](v.value);
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
                { title: 'LoF', text: this.$VALUE2TEXT[`${annotation_field}.lof`]('HC'), tabulator_filter: { field: `${annotation_field}.lof`, type: '=', value: 'HC' }},
                { title: 'LoF', text: this.$VALUE2TEXT[`${annotation_field}.lof`]('LC'), tabulator_filter: { field: `${annotation_field}.lof`, type: '=', value: 'LC' }}
              ]
            }
          };
          payload.data['lof'].forEach ( v => {
            var text_value = this.$VALUE2TEXT[`${annotation_field}.lof`](v.value);
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
                { title: 'Quality', text: this.$VALUE2TEXT['filter']('PASS'), tabulator_filter: { field: 'filter', type: '=', value: 'PASS' }}
              ]
            }
          };
          suggestions['Quality'].data.items['Failed'] = {
            value: 'Failed',
            data: {
              category: 'By Group',
              filters: [
                { title: 'Quality', text: this.$VALUE2TEXT['filter']('SVM'), tabulator_filter: {field: 'filter', type: '=', value: 'SVM' }},
                { title: 'Quality', text: this.$VALUE2TEXT['filter']('DISC'), tabulator_filter: {field: 'filter', type: '=', value: 'DISC' }},
                { title: 'Quality', text: this.$VALUE2TEXT['filter']('EXHET'), tabulator_filter: {field: 'filter', type: '=', value: 'EXHET' }}
              ]
            }
          };
          payload.data['filter'].forEach ( v => {
            var text_value = this.$VALUE2TEXT['filter'](v.value);
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
        // if (this.region.gene != null) { // gene mode
        //   if ((this.hoveredRowPosition != null) && ((this.hoveredRowPosition < visible.firstVisibleRowIndex) || (this.hoveredRowPosition > visible.lastVisibleRowIndex))) { // # we need explicitelt hide popover when scrolling on mobile touch screen
        //     var row = this.tabulator.getRowFromPosition(this.hoveredRowPosition);
        //     var cell = row.getCell('annotation.gene.consequence');
        //     if (cell) {
        //       $(cell.getElement().querySelector('.cell-button')).popover('hide');
        //     }
        //   }
        // }
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
    this.hoveredRowPosition = null;
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
          // console.log(data);
          this.empty = data.length == 0;
        }
      },
      renderComplete: (data) => {
        if (this.tabulator != null) {
          var visible = this.getVisibleVariants();

          if (this.hoveredRowPosition != null) { // make sure that row is hovered after re-rendering on mobile touch screen
            var row = this.tabulator.getRowFromPosition(this.hoveredRowPosition);
            row.getElement().classList.add('row-hovered');
            // if (this.region.gene != null) { //gene mode
            //   var cell = row.getCell('annotation.gene.consequence');
            //   if (cell) {
            //     cell.getElement().querySelector('.cell-button').style.display = 'block';
            //   }
            // }
          }
          this.$emit("scroll", visible.firstVisibleRowIndex, visible.lastVisibleRowIndex, visible.data);
        }
      },
      paginationSize: this.paginationSize,
      height: "600px",
      layout: "fitColumns",
      columns: [
        {
          title: this.$GET_FIELD_TITLE("variant_id") + " <a class='text-info' onclick='event.stopPropagation();' data-html='true' data-toggle='tooltip' title='(1) Chromosome<br>(2) Position<br>(3) Reference allele<br>(4) Alternate allele<br>'>?</a>",
          titleDownload: this.$GET_FIELD_TITLE("variant_id"),
          width: 130,
          field: "variant_id",
          visible: this.showColumnVariantID,
          formatter: (cell) => { return `<a href='${this.api}variant/snv/${cell.getValue()}'>${cell.getValue()}</a>`; }
        },
        {
          title: this.$GET_FIELD_TITLE("rsids"),
          titleDownload: this.$GET_FIELD_TITLE("rsids"),
          width: 100,
          field: "rsids",
          visible: this.showColumnRsID,
          formatter: (cell) => {
            var html = "";
            cell.getValue().forEach(v => {
              html += `<a href='${this.api}variant/snv/${v}'>${v}</a>`;
            });
            return html;
          },
          accessorDownload: (value) => {
            if (value != null) {
              return value.join(';');
            } else {
              return "";
            }
          }
        },
        {
          title: this.$GET_FIELD_TITLE("filter"),
          titleDownload: this.$GET_FIELD_TITLE("filter"),
          field: "filter",
          width: 78,
          hozAlign: "left",
          visible: this.showColumnQuality,
          formatter: (cell, params, onrendered) => {
            var html = "";
            cell.getValue().forEach( v => {
              var badge_type = v == "PASS" ? "success" : "danger";
              html += `<span class="badge badge-${badge_type}" style="margin-right:1px">${v}</span>`;
            });
            return html;
          },
          accessorDownload: (value) => {
            if (value != null) {
              return value.join(';');
            } else {
              return "";
            }
          }
        },
        {
          title: this.$GET_FIELD_TITLE("cadd_phred") + " <a class='text-info' onclick='event.stopPropagation();' data-toggle='tooltip' title='Variant deleteriousness score (PHRED-like scaled) computed with Combined Annoation Dependent Depletion (CADD) tool.'>?</a>",
          titleDownload: this.$GET_FIELD_TITLE("cadd_phred"),
          field: "cadd_phred",
          width: 80,
          hozAlign: "left",
          visible: this.showColumnCADD,
          formatter: (cell, params, onrendered) =>  this.$VALUE2TEXT["cadd_phred"](cell.getValue())
        },
        {
          title: this.$GET_FIELD_TITLE("allele_num"),
          titleDownload: this.$GET_FIELD_TITLE("allele_num"),
          field: "allele_num",
          width: 88,
          hozAlign: "left",
          visible: this.showColumnNAlleles,
          formatter: (cell, params, onrendered) => this.$VALUE2TEXT["allele_num"](cell.getValue())
        },
        {
          title: this.$GET_FIELD_TITLE("het_count") + " <a class='text-info' onclick='event.stopPropagation();' data-toggle='tooltip' title='Number of heterozygotes.'>?</a>",
          titleDownload: this.$GET_FIELD_TITLE("het_count"),
          field: "het_count",
          width: 80,
          hozAlign: "left",
          visible: this.showColumnHet,
          formatter: (cell, params, onrendered) => this.$VALUE2TEXT["het_count"](cell.getValue())
        },
        {
          title: this.$GET_FIELD_TITLE("hom_count") + " <a class='text-info' onclick='event.stopPropagation();' data-toggle='tooltip' title='Number of homozygotes for alternate allele.'>?</a>",
          titleDownload: this.$GET_FIELD_TITLE("hom_count"),
          field: "hom_count",
          width: 90,
          hozAlign: "left",
          visible: this.showColumHomAlt,
          formatter: (cell, params, onrendered) => this.$VALUE2TEXT["hom_count"](cell.getValue())
        },
        {
          title: this.$GET_FIELD_TITLE("allele_freq"),
          titleDownload: this.$GET_FIELD_TITLE("allele_freq"),
          field: "allele_freq",
          width: 125,
          hozAlign: "left",
          visible: this.showColumnFrequency,
          formatter: (cell, params, onrendered) => this.$VALUE2TEXT["allele_freq"](cell.getValue())
        },
      ],
      initialSort: [
        { column: "variant_id", dir: "asc" }
      ],
      initialFilter: this.computedFilters,
      rowMouseEnter: (e, row) => {
        if ((this.hoveredRowPosition != null) && (this.hoveredRowPosition != row.getPosition())) { // row was hovered from before and mouseleave was never called
          var hoveredRow = this.tabulator.getRowFromPosition(this.hoveredRowPosition);
          hoveredRow.getElement().classList.remove('row-hovered');
          // if (this.region.gene != null) { // gene mode
          //   $(hoveredRow.getCell('annotation.gene.consequence').getElement().querySelector('.cell-button')).popover('hide');
          //   hoveredRow.getCell('annotation.gene.consequence').getElement().querySelector('.cell-button').style.display = 'none';
          // }
          this.$emit("hover", hoveredRow.getPosition(), hoveredRow.getData(), false);
          this.hoveredRowPosition = null;
        }

        this.hoveredRowPosition = row.getPosition();
        row.getElement().classList.add('row-hovered');
        // if (this.region.gene != null) { // gene mode
        //   row.getCell('annotation.gene.consequence').getElement().querySelector('.cell-button').style.display = 'block';
        // }
        this.$emit("hover", row.getPosition(), row.getData(), true);
      },
      rowMouseLeave: (e, row) => {
        row.getElement().classList.remove('row-hovered');
        // if (this.region.gene != null) { // gene mode
        //   $(row.getCell('annotation.gene.consequence').getElement().querySelector('.cell-button')).popover('hide');
        //   row.getCell('annotation.gene.consequence').getElement().querySelector('.cell-button').style.display = 'none';
        // }
        this.$emit("hover", row.getPosition(), row.getData(), false);
        this.hoveredRowPosition = null;
      }
    });
    this.$el.querySelector(".tabulator-tableHolder").addEventListener("scroll", this.scrolled);
    this.loadFilterSuggestions();
    this.loadData();
    $(this.$el.querySelectorAll('[data-toggle="tooltip"]')).tooltip(); // not needed?
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
    },
    showColumnVariantID: function() {
      if (this.tabulator != null) {
        this.tabulator.toggleColumn('variant_id');
        this.tabulator.redraw();
      }
    },
    showColumnRsID: function() {
      if (this.tabulator != null) {
        this.tabulator.toggleColumn('rsids');
        this.tabulator.redraw();
      }
    },
    showColumnConsequence: function() {
      if (this.tabulator != null) {
        if (this.region.gene != null) {
          this.tabulator.toggleColumn(`annotation.gene.hgvs`);
          this.tabulator.redraw();
        } else if ((this.region.regionChrom != null) && (this.region.regionStart !=null) && (this.region.regionStop != null)) {
          this.tabulator.toggleColumn(`annotation.region.hgvs`);
          this.tabulator.redraw();
        }
      }
    },
    showColumnAnnotation: function() {
      if (this.tabulator != null) {
        if (this.region.gene != null) {
          this.tabulator.toggleColumn(`annotation.gene.consequence`);
          this.tabulator.redraw();
        } else if ((this.region.regionChrom != null) && (this.region.regionStart !=null) && (this.region.regionStop != null)) {
          this.tabulator.toggleColumn(`annotation.region.consequence`);
          this.tabulator.redraw();
        }
      }
    },
    showColumnLOFTEE: function() {
      if (this.tabulator != null) {
        if (this.region.gene != null) {
          this.tabulator.toggleColumn(`annotation.gene.lof`);
          this.tabulator.redraw();
        } else if ((this.region.regionChrom != null) && (this.region.regionStart !=null) && (this.region.regionStop != null)) {
          this.tabulator.toggleColumn(`annotation.region.lof`);
          this.tabulator.redraw();
        }
      }
    },
    showColumnQuality: function() {
      if (this.tabulator != null) {
        this.tabulator.toggleColumn('filter');
        this.tabulator.redraw();
      }
    },
    showColumnCADD: function() {
      if (this.tabulator != null) {
        this.tabulator.toggleColumn('cadd_phred');
        this.tabulator.redraw();
      }
    },
    showColumnNAlleles: function() {
      if (this.tabulator != null) {
        this.tabulator.toggleColumn('allele_num');
        this.tabulator.redraw();
      }
    },
    showColumnHet: function() {
      if (this.tabulator != null) {
        this.tabulator.toggleColumn('het_count');
        this.tabulator.redraw();
      }
    },
    showColumHomAlt: function() {
      if (this.tabulator != null) {
        this.tabulator.toggleColumn('hom_count');
        this.tabulator.redraw();
      }
    },
    showColumnFrequency: function () {
      if (this.tabulator != null) {
        this.tabulator.toggleColumn('allele_freq');
        this.tabulator.redraw();
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
/* BEGIN. :hover doesn't behave as expected on mobile device, so we mannually append our own row-hovered css class */
.child-component >>> .tabulator .tabulator-row.tabulator-selectable.row-hovered {
  background-color: orange;
  cursor: default;
}
.child-component >>> .tabulator .tabulator-row.tabulator-selectable:hover {
}
/* END. */
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
.child-component >>> .cell-button {
  position: absolute;
  top: 0;
  right: 0;
  outline: none;
  padding: 0px 7px 0px 7px;
  margin: 0px 1px 0px 1px;
  color: white;
  background-color: #007bff;
  border: 1px solid #007bff;
  border-radius: 2px;
  box-shadow: none;
}
.child-component >>> .cell-button:hover {
  background-color: #0062cc;
  border-color: #0062cc;
}
</style>
