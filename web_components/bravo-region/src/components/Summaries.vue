/* eslint-disable */

<template>
  <div class="child-component">
    <div class="control-buttons">
      <button v-if="hasLeftScroll || hasRightScroll" class="control-button" v-on:click="collapsed = !collapsed">
        <div style="display: inline" v-if="collapsed">Expand <font-awesome-icon style="background-color: transparent;" :icon="expandIcon"></font-awesome-icon></div>
        <div style="display: inline" v-else>Collapse <font-awesome-icon style="background-color: transparent;" :icon="collapseIcon"></font-awesome-icon></div>
      </button>
      <button class="control-button" v-on:click="$emit('close')">
        <font-awesome-icon style="background-color: transparent;" :icon="closeIcon"></font-awesome-icon>
      </button>
    </div>
    <button v-if="collapsed && hasLeftScroll" class="hscroll-button scroll-left" v-on:click="scroll(-200)">
      <font-awesome-icon style="background-color: transparent;" :icon="scrollLeftIcon"></font-awesome-icon>
    </button>
    <button v-if="collapsed && hasRightScroll" class="hscroll-button scroll-right" v-on:click="scroll(200)">
      <font-awesome-icon style="background-color: transparent;" :icon="scrollRightIcon"></font-awesome-icon>
    </button>
    <div class="container-fluid">
      <div v-bind:class="{ 'cards': collapsed, 'card-columns': !collapsed }">
        <div class="card shadow-sm small">

          <div class="card-body">

            <div v-if="loading" class="container-fluid">
              <div class="row">
                <div class="col-sm-12 text-center">
                  <div class="spinner-border spinner-border-sm text-primary ml-auto" role="status" aria-hidden="true"></div>
                  <strong>&nbsp;Loading...</strong>
                </div>
              </div>
            </div>
            <div v-if="failed" class="container-fluid">
              <div class="row">
                <div class="col-sm-12 text-center">
                  Error while loading data
                </div>
              </div>
            </div>
            <div v-if="loaded" class="container-fluid">
              <div class="row">
                <div class="col-sm-12">
                  <div class="table-responsive">
                    <table class="table table-sm">
                      <thead>
                        <tr>
                          <th scope="col" style="border-top:none;">Variant type</th>
                          <th scope="col" class="d-md-table-cell text-right" style="border-top:none;">Number</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>All</td>
                          <td class="d-md-table-cell text-right">{{(summary.all['total'] || 0).toLocaleString()}}</td>
                        </tr>
                        <tr>
                          <td>SNVs</td>
                          <td class="d-md-table-cell text-right">{{(summary.all['snv'] || 0).toLocaleString()}}</td>
                        </tr>
                        <tr>
                          <td>Indels</td>
                          <td class="d-md-table-cell text-right">{{(summary.all['indels'] || 0).toLocaleString()}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm small">
          <div class="card-body">
            <div v-if="loading" class="container-fluid">
              <div class="row">
                <div class="col-sm-12 text-center">
                  <div class="spinner-border spinner-border-sm text-primary ml-auto" role="status" aria-hidden="true"></div>
                  <strong>&nbsp;Loading...</strong>
                </div>
              </div>
            </div>
            <div v-if="failed" class="container-fluid">
              <div class="row">
                <div class="col-sm-12 text-center">
                  Error while loading data
                </div>
              </div>
            </div>
            <div v-if="loaded" class="container-fluid">
              <div class="row">
                <div class="col-sm-12">
                  <div class="table-responsive">
                    <table class="table table-sm">
                      <thead>
                        <tr>
                          <th scope="col" style="border-top:none;">SNVs</th>
                          <th scope="col" class="d-md-table-cell text-right" style="border-top:none;">Number</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>Synonymous</td>
                          <td class="d-md-table-cell text-right">{{this.count_synonymous('all')}}</td>
                        </tr>
                        <tr>
                          <td>Non-synonymous</td>
                          <td class="d-md-table-cell text-right">{{this.count_nonsynonymous('all')}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm small">
          <div class="card-body">
            <div v-if="loading" class="container-fluid">
              <div class="row">
                <div class="col-sm-12 text-center">
                  <div class="spinner-border spinner-border-sm text-primary ml-auto" role="status" aria-hidden="true"></div>
                  <strong>&nbsp;Loading...</strong>
                </div>
              </div>
            </div>
            <div v-if="failed" class="container-fluid">
              <div class="row">
                <div class="col-sm-12 text-center">
                  Error while loading data
                </div>
              </div>
            </div>
            <div v-if="loaded" class="container-fluid">
              <div class="row">
                <div class="col-sm-12">
                  <div class="table-responsive">
                    <table class="table table-sm">
                      <thead>
                        <tr>
                          <th scope="col" style="border-top:none;">Indels</th>
                          <th scope="col" class="d-md-table-cell text-right" style="border-top:none;">Number</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>Frameshifts</td>
                          <td class="d-md-table-cell text-right">{{this.count_frameshifts('all')}}</td>
                        </tr>
                        <tr>
                          <td>Inframe deletions</td>
                          <td class="d-md-table-cell text-right">{{this.count_inframe_deletions('all')}}</td>
                        </tr>
                        <tr>
                          <td>Inframe insertions</td>
                          <td class="d-md-table-cell text-right">{{this.count_inframe_insertions('all')}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm small">
          <div class="card-body">
            <div v-if="loading" class="container-fluid">
              <div class="row">
                <div class="col-sm-12 text-center">
                  <div class="spinner-border spinner-border-sm text-primary ml-auto" role="status" aria-hidden="true"></div>
                  <strong>&nbsp;Loading...</strong>
                </div>
              </div>
            </div>
            <div v-if="failed" class="container-fluid">
              <div class="row">
                <div class="col-sm-12 text-center">
                  Error while loading data
                </div>
              </div>
            </div>
            <div v-if="loaded" class="container-fluid">
              <div class="row">
                <div class="col-sm-12">
                  <div class="table-responsive">
                    <table class="table table-sm">
                      <thead>
                        <tr>
                          <th scope="col" style="border-top:none;">Putative Loss-of-Function (pLoF)</th>
                          <th scope="col" class="d-none d-md-table-cell text-right" style="border-top:none;">Number</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>High Confidence (HC)</td>
                          <td class="d-md-table-cell text-right">{{(summary.all['LoF (HC)'] || 0).toLocaleString()}}</td>
                        </tr>
                        <tr>
                          <td>Low Confidence (LC)</td>
                          <td class="d-md-table-cell text-right">{{(summary.all['LoF (LC)'] || 0).toLocaleString()}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
  import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
  import { faTimes } from '@fortawesome/free-solid-svg-icons';
  import { faAngleRight } from '@fortawesome/free-solid-svg-icons';
  import { faAngleLeft } from '@fortawesome/free-solid-svg-icons';
  import { faPlusSquare, faMinusSquare } from '@fortawesome/free-solid-svg-icons';

  import axios from "axios";

  export default {
    name: "summaries",
    props: {
      'api': {
        type: String
      },
      'region': {
        type: Object
      },
      'filters': {
        type: Array
      },
    },
    components: {
        FontAwesomeIcon,
    },
    data: function() {
      return {
        tooltipHtml: "",
        closeIcon: faTimes,
        scrollRightIcon: faAngleRight,
        scrollLeftIcon: faAngleLeft,
        expandIcon: faPlusSquare,
        collapseIcon: faMinusSquare,
        hasLeftScroll: false,
        hasRightScroll: false,
        loading: false,
        loaded: false,
        failed: false,
        collapsed: true,
        summary: null
      }
    },
    methods: {
      load: function() {
        if ((this.region.regionChrom == null) || (this.region.regionStart == null) || (this.region.regionStop == null)) {
          return;
        }
        var url = "";
        if (this.region.gene != null) {
          url = `${this.api}variants/gene/snv/${this.region.gene.gene_id}/summary`;
        } else {
          url = `${this.api}variants/region/snv/${this.region.regionChrom}-${this.region.regionStart}-${this.region.regionStop}/summary`;
        }
        this.summary = null;
        this.loaded = false;
        this.failed = false;
        this.loading = true;
        axios
          .post(url, {
            filters: this.computedFilters,
            introns: this.computedRegion.introns,
          })
          .then(response => {
            var payload = response.data;
            this.summary = payload['data'];
            this.loading = false;
            this.failed = false;
            this.loaded = true;
            this.$nextTick(() => {
              this.updateHorizontalScroll();
            });
          })
          .catch(error => {
            this.loading = false;
            this.loaded = false;
            this.failed = true;
            this.summary = null;
          })
          .finally(() => {
          });
      },
      count_synonymous: function(category) {
        return (this.summary[category]['synonymous_variant'] || 0) +
          (this.summary[category]['start_retained_variant'] || 0) +
          (this.summary[category]['stop_retained_variant'] || 0);
      },
      count_nonsynonymous: function(category) {
        return (this.summary[category]['missense_variant'] || 0) +
          (this.summary[category]['start_lost'] || 0) +
          (this.summary[category]['stop_gained'] || 0) +
          (this.summary[category]['stop_lost'] || 0);
      },
      count_frameshifts: function(category) {
        return this.summary[category]['frameshift_variant'] || 0;
      },
      count_inframe_insertions: function(category) {
        return (this.summary[category]['inframe_insertion'] || 0);
      },
      count_inframe_deletions: function(category) {
        return (this.summary[category]['inframe_deletion'] || 0);
      },
      updateHorizontalScroll: function() {
        var cards = this.$el.querySelector(".cards");
        this.hasLeftScroll = cards.scrollLeft != 0;
        this.hasRightScroll = Math.abs(cards.scrollWidth - cards.clientWidth - cards.scrollLeft) > 1;
      },
      scroll: function(value) {
        var cards = this.$el.querySelector(".cards");
        cards.scrollLeft = cards.scrollLeft + value;
      }
    },
    beforeCreate: function() {
      // initialize non reactive data
    },
    created: function() {
    },
    mounted: function() {
      this.load();
      this.$el.querySelector(".cards").onscroll = this.updateHorizontalScroll;
    },
    computed: {
      computedRegion: function() {
        return JSON.parse(JSON.stringify(this.region));
      },
      computedFilters: function() {
        var filters = [];
        this.filters.forEach(f => {
          filters.push(f.tabulator_filter);
        });
        return filters;
      }
    },
    watch: {
      computedRegion: {
        handler: function(newValue, oldValue) {
          if (newValue.gene != null) {
            if ((oldValue.gene == null) || (oldValue.gene.gene_id != newValue.gene.gene_id) || (oldValue.introns != newValue.introns)) {
              this.load();
            }
          } else if (newValue.gene == null) {
            if (oldValue.gene != null) {
              this.load();
            } else if ((newValue.regionChrom != oldValue.regionChrom) || (newValue.regionStart != oldValue.regionStart) || (newValue.regionStop != oldValue.regionStop) || (oldValue.introns != newValue.introns)) {
              this.load();
            }
          }
          this.updateHorizontalScroll();
        },
        deep: true
      },
      filters: function(newValue, oldValue) {
        this.load();
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
.control-buttons {
  position: absolute;
  margin: 0px;
  top: 0px;
  right: 0px;
  font-size: 12px;
  z-index: 999;
}
.control-button {
  padding: 0px 4px 0px 4px;
  margin-left: 1px;
  color: white;
  outline: none;
  background-color: #007bff;
  border: 1px solid #007bff;
  border-radius: 2px;
  box-shadow: none;
}
.hscroll-button {
  padding: 0px;
  width: 32px;
  height: 32px;
  color: #007bff;
  font-size: 20px;
  outline: none;
  background-color: #ffffff;
  border: 2px solid #007bff;
  border-radius: 50%;
  box-shadow: none;
  z-index: 998;
}
.hscroll-button:hover {
  box-shadow: 0px 0px 8px 0px rgba(0,0,0,.3);
  color: #0062cc;
  border-color: #0062cc;
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
.control-button:hover {
  background-color: #0062cc;
  border-color: #0062cc;
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
@media (max-width: 575.98px) {
  .card-columns {
    column-count: 1;
  }
}
@media (min-width: 576px) and (max-width: 767.98px) {
  .card-columns {
    column-count: 1;
  }
}
@media (min-width: 768px) and (max-width: 991.98px) {
  .card-columns {
    column-count: 2;
  }
}
@media (min-width: 992px) and (max-width: 1199.98px) {
  .card-columns {
    column-count: 3;
  }
}
@media (min-width: 1200px) {
  .card-columns {
    column-count: 3;
  }
}
</style>
