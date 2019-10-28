/* eslint-disable */

<template>
  <div class="child-component">
    <button class="close-button" v-on:click="$emit('close')">
      <font-awesome-icon style="background-color: transparent;" :icon="closeIcon"></font-awesome-icon>
    </button>
    <button v-if="hasLeftScroll" class="hscroll-button scroll-left" v-on:click="scroll(-200)">
      <font-awesome-icon style="background-color: transparent;" :icon="scrollLeftIcon"></font-awesome-icon>
    </button>
    <button v-if="hasRightScroll" class="hscroll-button scroll-right" v-on:click="scroll(200)">
      <font-awesome-icon style="background-color: transparent;" :icon="scrollRightIcon"></font-awesome-icon>
    </button>

    <div class="container-fluid">
      <div class="cards">
        <div class="card shadow-sm small" style="min-width: 400px">
          <div class="card-body">
            <div v-if="loading" class="container-fluid">
              <div class="row">
                <div class="col-sm-12 text-center">
                  <div class="spinner-border spinner-border-sm text-primary ml-auto" role="status" aria-hidden="true"></div>
                  <strong>&nbsp;Loading...</strong>
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
                          <th scope="col" class="text-right" style="border-top:none;">Passed QC</th>
                          <th scope="col" class="text-right" style="border-top:none;">Failed QC</th>
                          <th scope="col" class="text-right" style="border-top:none;">All</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>All</td>
                          <td class="text-right">{{(summary.passed['total'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.failed['total'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.all['total'] || 0).toLocaleString()}}</td>
                        </tr>
                        <tr>
                          <td>SNVs</td>
                          <td class="text-right">{{(summary.passed['snv'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.failed['snv'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.all['snv'] || 0).toLocaleString()}}</td>
                        </tr>
                        <tr>
                          <td>Indels</td>
                          <td class="text-right">{{(summary.passed['indels'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.failed['indels'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.all['indels'] || 0).toLocaleString()}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="card shadow-sm small" style="min-width: 400px">
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
                          <th scope="col" class="text-right" style="border-top:none;">Passed QC</th>
                          <th scope="col" class="text-right" style="border-top:none;">Failed QC</th>
                          <th scope="col" class="text-right" style="border-top:none;">All</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>Synonymous</td>
                          <td class="text-right">{{this.count_synonymous('passed')}}</td>
                          <td class="text-right">{{this.count_synonymous('failed')}}</td>
                          <td class="text-right">{{this.count_synonymous('all')}}</td>
                        </tr>
                        <tr>
                          <td>Non-synonymous</td>
                          <td class="text-right">{{this.count_nonsynonymous('passed')}}</td>
                          <td class="text-right">{{this.count_nonsynonymous('failed')}}</td>
                          <td class="text-right">{{this.count_nonsynonymous('all')}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="card shadow-sm small" style="min-width: 400px">
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
                          <th scope="col" style="border-top:none;">Loss-of-Function (LoF)</th>
                          <th scope="col" class="text-right" style="border-top:none;">Passed QC</th>
                          <th scope="col" class="text-right" style="border-top:none;">Failed QC</th>
                          <th scope="col" class="text-right" style="border-top:none;">All</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>High Confidence (HC)</td>
                          <td class="text-right">{{(summary.passed['LoF (HC)'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.failed['LoF (HC)'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.all['LoF (HC)'] || 0).toLocaleString()}}</td>
                        </tr>
                        <tr>
                          <td>Low Confidence (LC)</td>
                          <td class="text-right">{{(summary.passed['LoF (LC)'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.failed['LoF (LC)'] || 0).toLocaleString()}}</td>
                          <td class="text-right">{{(summary.all['LoF (LC)'] || 0).toLocaleString()}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="card shadow-sm small" style="min-width: 400px">
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
                          <th scope="col" class="text-right" style="border-top:none;">Passed QC</th>
                          <th scope="col" class="text-right" style="border-top:none;">Failed QC</th>
                          <th scope="col" class="text-right" style="border-top:none;">All</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>Frameshifts</td>
                          <td class="text-right">{{this.count_frameshifts('passed')}}</td>
                          <td class="text-right">{{this.count_frameshifts('failed')}}</td>
                          <td class="text-right">{{this.count_frameshifts('all')}}</td>
                        </tr>
                        <tr>
                          <td>Inframe deletions</td>
                          <td class="text-right">{{this.count_inframe_deletions('passed')}}</td>
                          <td class="text-right">{{this.count_inframe_deletions('failed')}}</td>
                          <td class="text-right">{{this.count_inframe_deletions('all')}}</td>
                        </tr>
                        <tr>
                          <td>Inframe insetions</td>
                          <td class="text-right">{{this.count_inframe_insertions('passed')}}</td>
                          <td class="text-right">{{this.count_inframe_insertions('failed')}}</td>
                          <td class="text-right">{{this.count_inframe_insertions('all')}}</td>
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
  import axios from "axios";

  export default {
    name: "summaries",
    props: {
      'api': {
        type: String
      },
      'region': {
        type: Object
      }
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
        hasLeftScroll: false,
        hasRightScroll: false,
        loading: false,
        loaded: false,
        failed: false,
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
          .post(url)
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
        this.hasRightScroll = cards.scrollLeft < cards.scrollWidth - cards.clientWidth;
      },
      scroll: function(value) {
        var cards = this.$el.querySelector(".cards");
        if (value < 0) {
          cards.scrollLeft = Math.max(cards.scrollLeft + value, 0);
        } else if (value > 0) {
          cards.scrollLeft = Math.min(cards.scrollLeft + value, cards.scrollWidth - cards.clientWidth);
        }
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
      }
    },
    watch: {
      computedRegion: {
        handler: function(newValue, oldValue) {
          if (newValue.gene != null) {
            if ((oldValue.gene == null) || (oldValue.gene.gene_id != newValue.gene.gene_id)) {
              this.load();
            }
          } else if (newValue.gene == null) {
            if (oldValue.gene != null) {
              this.load();
            } else if ((newValue.regionChrom != oldValue.regionChrom) || (newValue.regionStart != oldValue.regionStart) || (newValue.regionStop != oldValue.regionStop)) {
              this.load();
            }
          }
          this.updateHorizontalScroll();
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
