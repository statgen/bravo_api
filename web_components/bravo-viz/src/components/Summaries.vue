/* eslint-disable */

<template>
  <div class="child-component">
    <button class="close-button" v-on:click="$emit('close')">
      <font-awesome-icon style="background-color: transparent;" :icon="closeIcon"></font-awesome-icon>
    </button>

    <div class="container-fluid">
      <div class="cards">
        <div v-if="computedRegion.gene != null" class="card shadow-sm small" style="min-width: 400px">
          <div class="card-body">
            <div class="container-fluid">
              <div class="row">
                <div class="col-sm-4 text-left text-truncate">Gene name</div>
                <div class="col-sm-8 text-right"><i>{{computedRegion.gene.gene_name}}</i></div>
              </div>
              <div class="row">
                <div class="col-sm-4 text-left text-truncate">Ensembl ID</div>
                <div class="col-sm-8 text-right">{{computedRegion.gene.gene_id}}</div>
              </div>
              <div class="row">
                <div class="col-sm-4 text-left text-truncate">Gene type</div>
                <div class="col-sm-8 text-right">{{computedRegion.gene.gene_type}}</div>
              </div>
              <div class="row">
                <div class="col-sm-4 text-left text-truncate">Gene full name</div>
                <div class="col-sm-8 text-right">{{computedRegion.gene.full_gene_name}}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="computedRegion.gene != null" class="card shadow-sm small" style="min-width: 400px">
          <div class="card-body">
            <div class="container-fluid">
              <div class="row">
                <div class="col-sm-4 text-left text-truncate">Region</div>
                <div class="col-sm-8 text-right">{{computedRegion.gene.chrom}}:{{computedRegion.gene.start.toLocaleString()}}-{{computedRegion.gene.stop.toLocaleString()}}</div>
              </div>
              <div class="row">
                <div class="col-sm-5 text-left text-truncate">Total length (bp)</div>
                <div class="col-sm-7 text-right">{{(computedRegion.gene.stop - computedRegion.gene.start + 1).toLocaleString()}}</div>
              </div>
              <div class="row">
                <div class="col-sm-6 text-left text-truncate">Exonic length (bp)</div>
                <div class="col-sm-6 text-right">{{ computedRegion.gene.coding_regions.reduce((total, entry) => total + entry[1] - entry[0] + 1, 0).toLocaleString() }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="(computedRegion.gene == null) && (computedRegion.regionChrom != null) && (computedRegion.regionStart != null) && (computedRegion.regionStop != null)" class="card shadow-sm small" style="min-width: 400px">
          <div class="card-body">
            <div class="container-fluid">
              <div class="row">
                <div class="col-sm-3 text-left text-truncate">Region</div>
                <div class="col-sm-8 text-right">{{computedRegion.regionChrom}}:{{computedRegion.regionStart.toLocaleString()}}-{{computedRegion.regionStop.toLocaleString()}}</div>
              </div>
              <div class="row">
                <div class="col-sm-4 text-left text-truncate">Length (bp)</div>
                <div class="col-sm-7 text-right">{{(computedRegion.regionStop - computedRegion.regionStart + 1).toLocaleString()}}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="summary != null" class="card shadow-sm small" style="min-width: 400px">
          <div class="card-body">
            <div class="container-fluid">
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
        <div v-if="summary != null" class="card shadow-sm small" style="min-width: 400px">
          <div class="card-body">
            <div class="container-fluid">
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
        <div v-if="summary != null" class="card shadow-sm small" style="min-width: 400px">
          <div class="card-body">
            <div class="container-fluid">
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
        <div v-if="summary != null" class="card shadow-sm small" style="min-width: 400px">
          <div class="card-body">
            <div class="container-fluid">
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
        summary: null
      }
    },
    methods: {
      load: function() {
        if ((this.region.regionChrom == null) || (this.region.regionStart == null) || (this.region.regionStop == null)) {
          return;
        }
        if (this.region.gene != null) {
          var url = `${this.api}variants/gene/snv/${this.region.gene.gene_id}/summary`;
        } else {
          var url = `${this.api}variants/region/snv/${this.region.regionChrom}-${this.region.regionStart}-${this.region.regionStop}/summary`;
        }
        axios
          .post(url)
          .then(response => {
            var payload = response.data;
            this.summary = payload['data'];
          })
          .catch(error => {
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
      }
    },
    beforeCreate: function() {
      // initialize non reactive data
    },
    created: function() {
    },
    mounted: function() {
      this.load();
    },
    computed: {
      computedRegion: function() {
        return JSON.parse(JSON.stringify(this.region));
      }
    },
    watch: {
      computedRegion: {
        handler: function(newValue, oldValue) {
          if ((newValue.gene != oldValue.gene)) {
            this.load();
          } else if (newValue.gene == null) {
            if ((newValue.regionChrom != oldValue.regionChrom) || (newValue.regionStart != oldValue.regionStart) || (newValue.regionStop != oldValue.regionStop)) {
              this.load();
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
  z-index: 9999;
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
