/* eslint-disable */

<template>
  <div class="child-component">
    <div class="container-fluid">
      <div class="row">
        <div class="col-12" style="padding-left: 0px; padding-top: 2px; padding-bottom: 2px;">
          <div class="btn-group mr-1 mt-1" id="qualityFilter">
            <button class="btn btn-sm dropdown-toggle" v-bind:class="{'btn-primary': savedQualityFilters.length > 0, 'btn-outline-primary': savedQualityFilters.length == 0}" type="button" id="qualityFilterDropdownButton" data-boundary="window" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Quality <span v-if="savedQualityFilters.length > 0">({{savedQualityFilters.length}})</span>
            </button>
            <div class="dropdown-menu shadow" @click.stop="">
              <form class="p-2">
                <ul style="list-style-type: none; padding-left: 0;">
                  <li>
                    <div class="custom-control custom-checkbox">
                      <input class="custom-control-input" type="checkbox" value="" id="allPassedQC" v-on:change="changedAllPassedCheckbox">
                      <label class="custom-control-label" for="allPassedQC">All variants which pass QC</label>
                    </div>
                    <ul style="list-style-type: none; padding-left: 1rem; padding-top: 0.2rem;">
                      <li>
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" value="PASS" id="PASS" v-model="qualityFilters">
                          <label class="custom-control-label" for="PASS">PASS</label>
                          <small class="form-text text-muted">All filters passed</small>
                        </div>
                      </li>
                    </ul>
                  </li>
                  <li>
                    <div class="custom-control custom-checkbox">
                      <input class="custom-control-input" type="checkbox" value="" id="allFailedQC" v-on:change="changedAllFailedCheckbox">
                      <label class="custom-control-label" for="allFailedQC">All variants which failed QC</label>
                    </div>
                    <ul style="list-style-type: none; padding-left: 1rem; padding-top: 0.2rem;">
                      <li>
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" value="SVM" id="SVM" v-model="qualityFilters">
                          <label class="custom-control-label" for="SVM">SVM</label>
                          <small class="form-text text-muted">Variant failed SVM filter.</small>
                        </div>
                      </li>
                      <li>
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" value="DISC" id="DISC" v-model="qualityFilters">
                          <label class="custom-control-label" for="DISC">DISC</label>
                          <small class="form-text text-muted">Mendelian or duplicate genotype discordance is high.</small>
                        </div>
                      </li>
                      <li>
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" value="EXHET" id="EXHET" v-model="qualityFilters">
                          <label class="custom-control-label" for="EXHET">EXHET</label>
                          <small class="form-text text-muted">Excess heterozygosity.</small>
                        </div>
                      </li>
                    </ul>
                  </li>
                </ul>
                <hr/>
                <div class="form-row">
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-secondary btn-sm" v-on:click="clearQualityFilters" :disabled="qualityFilters.length == 0">Clear</button>
                  </div>
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-primary btn-sm float-right" v-on:click="applyQualityFilters">Save</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
          <div class="btn-group mr-1 mt-1" id="consequenceFilter">
            <button class="btn btn-sm dropdown-toggle" v-bind:class="{'btn-primary': savedConsequenceFilters.length > 0, 'btn-outline-primary': savedConsequenceFilters.length == 0}" type="button" id="consequenceFilterDropdownButton" data-boundary="window" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Consequence <span v-if="savedConsequenceFilters.length > 0">({{savedConsequenceFilters.length}})</span>
            </button>
            <div class="dropdown-menu shadow" @click.stop="">
              <form class="p-2">
                <div class="overflow-auto" style="min-width: 260px; max-height: 370px;">
                    <ul style="list-style-type: none; padding-left: 0;">
                      <div class="custom-control custom-checkbox">
                        <input class="custom-control-input" type="checkbox" value="" id="allSynonymous" v-on:change="changedAllSynonymousCheckbox">
                        <label class="custom-control-label" for="allSynonymous">Synonymous</label>
                      </div>
                      <ul style="list-style-type: none; padding-left: 1rem; padding-top: 0.2rem;">
                      <li v-for="item in consequenceFiltersInputs.synonymous">
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" v-bind:value="item" v-bind:key="item" v-bind:id="item" v-model="consequenceFilters">
                          <label class="custom-control-label" v-bind:for="item">{{item}}</label>
                          <!-- <small class="form-text text-muted"></small> -->
                        </div>
                      </li>
                      </ul>
                    </ul>
                    <ul style="list-style-type: none; padding-left: 0;">
                      <div class="custom-control custom-checkbox">
                        <input class="custom-control-input" type="checkbox" value="" id="allNonsynonymous" v-on:change="changedAllNonsynonymousCheckbox">
                        <label class="custom-control-label" for="allNonsynonymous">Non-synonymous</label>
                      </div>
                      <ul style="list-style-type: none; padding-left: 1rem; padding-top: 0.2rem;">
                      <li v-for="item in consequenceFiltersInputs.nonsynonymous">
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" v-bind:value="item" v-bind:key="item" v-bind:id="item" v-model="consequenceFilters">
                          <label class="custom-control-label" v-bind:for="item">{{item}}</label>
                          <!-- <small class="form-text text-muted"></small> -->
                        </div>
                      </li>
                      </ul>
                    </ul>
                    <button type="button" class="btn btn-link btn-sm" button v-on:click="expandedConsequenceFilters = !expandedConsequenceFilters">
                      <span v-if="expandedConsequenceFilters">Show less</span><span v-else>Show more</span>
                    </button>
                    <ul v-if="expandedConsequenceFilters" style="list-style-type: none; padding-left: 0;">
                      <li v-for="item in consequenceFiltersInputs.others">
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" v-bind:value="item" v-bind:key="item" v-bind:id="item" v-model="consequenceFilters">
                          <label class="custom-control-label" v-bind:for="item">{{item}}</label>
                        </div>
                      </li>
                    </ul>
                </div>
                <hr/>
                <div class="form-row">
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-secondary btn-sm" v-on:click="clearConsequenceFilters" :disabled="consequenceFilters.length == 0">Clear</button>
                  </div>
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-primary btn-sm float-right" v-on:click="applyConsequenceFilters">Save</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
          <div class="btn-group mr-1 mt-1" id="lofFilter">
            <button class="btn btn-sm dropdown-toggle" v-bind:class="{'btn-primary': savedLofFilters.length > 0, 'btn-outline-primary': savedLofFilters.length == 0}" type="button" id="lofFilterDropdownButton" data-boundary="window" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              pLoF <span v-if="savedLofFilters.length > 0">({{savedLofFilters.length}})</span>
            </button>
            <div class="dropdown-menu shadow" @click.stop="">
              <form class="p-2">
                <ul style="list-style-type: none; padding-left: 0;">
                  <div class="custom-control custom-checkbox">
                    <input class="custom-control-input" type="checkbox" value="" id="allLoF" v-on:change="changedAllLoFCheckbox">
                    <label class="custom-control-label" for="allLoF">Putative Loss-of-Function</label>
                  </div>
                  <ul style="list-style-type: none; padding-left: 1rem; padding-top: 0.2rem;">
                  <li v-for="item in consequenceFiltersInputs.lof">
                    <div class="custom-control custom-checkbox">
                      <input class="custom-control-input" type="checkbox" v-bind:value="item" v-bind:key="item" v-bind:id="item" v-model="lofFilters">
                      <label class="custom-control-label" v-bind:for="item">{{item}}</label>
                      <!-- <small class="form-text text-muted"></small> -->
                    </div>
                  </li>
                  </ul>
                </ul>
                <hr/>
                <div class="form-row">
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-secondary btn-sm" v-on:click="clearLofFilters" :disabled="lofFilters.length == 0">Clear</button>
                  </div>
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-primary btn-sm float-right" v-on:click="applyLofFilters">Save</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
          <div class="btn-group mr-1 mt-1" id="frequencyFilter">
            <button class="btn btn-sm dropdown-toggle" v-bind:class="{'btn-primary': (savedMinFrequency > 0) || (savedMaxFrequency < 100), 'btn-outline-primary': (savedMinFrequency == 0) && (savedMaxFrequency == 100)}" type="button" id="frequencyFilterDropdownButton" data-boundary="window" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Frequency <span v-if="(savedMinFrequency > 0) || (savedMaxFrequency < 100)">({{(savedMinFrequency > 0) + (savedMaxFrequency < 100)}})</span>
            </button>
            <div class="dropdown-menu shadow" @click.stop="">
              <form class="p-2">
                <h6>Alternate allele frequency (%)</h6>
                <div class="form-group row">
                  <label for="minFrequency" class="col-sm-2 col-form-label">Min</label>
                  <div class="col-sm-10">
                    <input class="form-control" id="minFrequency" type="number" name="" min="0" max="100" step="0.01" v-model="minFrequency" required>
                  </div>
                </div>
                <div class="form-group row">
                  <label for="maxFrequency" class="col-sm-2 col-form-label">Max</label>
                  <div class="col-sm-10">
                    <input class="form-control" id="maxFrequency" type="number" name="" min="0" max="100" step="0.01" v-model="maxFrequency" required>
                  </div>
                </div>
                <hr/>
                <div class="form-row">
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-secondary btn-sm" v-on:click="clearFrequencyFilters" :disabled="(minFrequency == 0) && (maxFrequency == 100)">Clear</button>
                  </div>
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-primary btn-sm float-right" v-on:click="applyFrequencyFilters" :disabled="(minFrequency === '') || (maxFrequency === '') || (minFrequency < 0) || (minFrequency > 100) || (maxFrequency < 0) || (maxFrequency > 100) || (minFrequency > maxFrequency)">Save</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
          <div class="btn-group mr-1 mt-1" id="rsFilter">
            <button class="btn btn-sm dropdown-toggle" v-bind:class="{'btn-primary': savedRsFilters.length > 0, 'btn-outline-primary': savedRsFilters.length == 0}" type="button" id="rsFilterDropdownButton" data-boundary="window" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              rsID <span v-if="savedRsFilters.length > 0">(1)</span>
            </button>
            <div class="dropdown-menu shadow" @click.stop="">
              <form class="p-2">
                <div class="form-group">
                  <label for="inputRs">Variant rsID</label>
                  <input type="text" class="form-control" id = "inputRs" placeholder="Enter rs identifier" v-model="rsFilters">
                </div>
                <hr/>
                <div class="form-row">
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-secondary btn-sm" v-on:click="clearRsFilters" :disabled="rsFilters.length == 0">Clear</button>
                  </div>
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-primary btn-sm float-right" v-on:click="applyRsFilters">Save</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "snvfilter",
    props: {
      suggestions: {
        type: Object
      },
      filters: {
        type: Array
      }
    },
    components: {
    },
    data: function() {
      return {
        qualityFilters: [],
        savedQualityFilters: [],
        consequenceFiltersInputs: {},
        consequenceFilters: [],
        savedConsequenceFilters: [],
        expandedConsequenceFilters: false,
        lofFilters: [],
        savedLofFilters: [],
        minFrequency: 0,
        maxFrequency: 100,
        savedMinFrequency: 0,
        savedMaxFrequency: 100,
        rsFilters: "",
        savedRsFilters: ""
      }
    },
    methods: {
      emitFilters: function() {
        var newActiveFilters = [];
        this.savedQualityFilters.forEach(filter => {
          newActiveFilters.push({ tabulator_filter: { field: 'filter', type: '=', value: filter}});
        });
        this.savedConsequenceFilters.forEach(filter => {
          newActiveFilters.push({tabulator_filter: {
            field: this.consequenceFiltersMap[filter].field,
            type: this.consequenceFiltersMap[filter].type,
            value: this.consequenceFiltersMap[filter].value
          }});
        });
        this.savedLofFilters.forEach(filter => {
          newActiveFilters.push({tabulator_filter: {
            field: this.consequenceFiltersMap[filter].field,
            type: this.consequenceFiltersMap[filter].type,
            value: this.consequenceFiltersMap[filter].value
          }});
        });
        if ((this.savedMinFrequency > 0) || (this.savedMaxFrequency < 100)) {
          var newFrequencyFilters = [];
          if (this.savedMinFrequency > 0) {
            newFrequencyFilters.push({field: 'allele_freq', type: '>', value: this.savedMinFrequency / 100});
          }
          if (this.savedMaxFrequency < 100) {
            newFrequencyFilters.push({field: 'allele_freq', type: '<', value: this.savedMaxFrequency / 100});
          }
          newActiveFilters.push({tabulator_filter: newFrequencyFilters});
        }
        if (this.savedRsFilters.length > 0) {
          newActiveFilters.push({tabulator_filter: { field: 'rsids', type: '=', value: this.savedRsFilters }});
        }
        this.$emit("filter", newActiveFilters);
      },
      doNotChangeQualityFilters: function() {
        this.qualityFilters = JSON.parse(JSON.stringify(this.savedQualityFilters));
      },
      changeQualityFilters: function() {
        this.savedQualityFilters = JSON.parse(JSON.stringify(this.qualityFilters));
      },
      applyQualityFilters: function() {
        var nochange = true;
        if (this.qualityFilters.length != this.savedQualityFilters.length) {
          nochange = false;
        } else {
          for (var i = 0; i < this.qualityFilters.length; ++i) {
            if (!this.savedQualityFilters.includes(this.qualityFilters[i])) {
              nochange = false;
            }
          }
        }
        if (!nochange) {
          this.changeQualityFilters();
          this.emitFilters();
        }
        $(this.$el.querySelector('#qualityFilterDropdownButton')).dropdown('hide'); // we assume that bootstrap with its jquery was loaded externally
      },
      clearQualityFilters: function() {
        this.qualityFilters = [];
      },
      doNotChangeConsequenceFilters: function() {
        this.consequenceFilters = JSON.parse(JSON.stringify(this.savedConsequenceFilters));
      },
      changeConsequenceFilters: function() {
        this.savedConsequenceFilters = JSON.parse(JSON.stringify(this.consequenceFilters));
      },
      applyConsequenceFilters: function() {
        var nochange = true;
        if (this.consequenceFilters.length != this.savedConsequenceFilters.length) {
          nochange = false;
        } else {
          for (var i = 0; i < this.consequenceFilters.length; ++i) {
            if (!this.savedConsequenceFilters.includes(this.consequenceFilters[i])) {
              nochange = false;
            }
          }
        }
        if (!nochange) {
          this.changeConsequenceFilters();
          this.emitFilters();
        }
        $(this.$el.querySelector('#consequenceFilterDropdownButton')).dropdown('hide'); // we assume that bootstrap with its jquery was loaded externally
      },
      clearConsequenceFilters: function() {
        this.consequenceFilters = [];
      },

      doNotChangeLofFilters: function() {
        this.lofFilters = JSON.parse(JSON.stringify(this.savedLofFilters));
      },
      changeLofFilters: function() {
        this.savedLofFilters = JSON.parse(JSON.stringify(this.lofFilters));
      },
      applyLofFilters: function() {
        var nochange = true;
        if (this.lofFilters.length != this.savedLofFilters.length) {
          nochange = false;
        } else {
          for (var i = 0; i < this.lofFilters.length; ++i) {
            if (!this.savedLofFilters.includes(this.lofFilters[i])) {
              nochange = false;
            }
          }
        }
        if (!nochange) {
          this.changeLofFilters();
          this.emitFilters();
        }
        $(this.$el.querySelector('#lofFilterDropdownButton')).dropdown('hide'); // we assume that bootstrap with its jquery was loaded externally
      },
      clearLofFilters: function() {
        this.lofFilters = [];
      },
      doNotChangeFrequencyFilters: function() {
        this.minFrequency = this.savedMinFrequency;
        this.maxFrequency = this.savedMaxFrequency;
      },
      changeFrequencyFilters: function() {
        this.savedMinFrequency = this.minFrequency;
        this.savedMaxFrequency = this.maxFrequency;
      },
      applyFrequencyFilters: function() {
        var nochange = true;
        if (this.minFrequency != this.savedMinFrequency) {
          nochange = false;
        }
        if (this.maxFrequency != this.savedMaxFrequency) {
          nochange = false;
        }
        if (!nochange) {
          this.changeFrequencyFilters();
          this.emitFilters();
        }
        $(this.$el.querySelector('#frequencyFilterDropdownButton')).dropdown('hide'); // we assume that bootstrap with its jquery was loaded externally
      },
      clearFrequencyFilters: function() {
        this.minFrequency = 0;
        this.maxFrequency = 100;
      },
      doNotChangeRsFilters: function() {
        this.rsFilters = JSON.parse(JSON.stringify(this.savedRsFilters));
      },
      changeRsFilters: function() {
        this.savedRsFilters = JSON.parse(JSON.stringify(this.rsFilters));
      },
      applyRsFilters: function() {
        var nochange = true;
        if (this.rsFilters.length != this.savedRsFilters.length) {
          nochange = false;
        } else {
          for (var i = 0; i < this.rsFilters.length; ++i) {
            if (!this.savedRsFilters.includes(this.rsFilters[i])) {
              nochange = false;
            }
          }
        }
        if (!nochange) {
          this.changeRsFilters();
          this.emitFilters();
        }
        $(this.$el.querySelector('#rsFilterDropdownButton')).dropdown('hide'); // we assume that bootstrap with its jquery was loaded externally
      },
      clearRsFilters: function() {
        this.rsFilters = [];
      },
      changedAllPassedCheckbox: function(e) {
        if (e.target.checked) {
          if (!this.qualityFilters.includes('PASS')) {
            this.qualityFilters.push('PASS');
          }
        } else {
          var i = this.qualityFilters.indexOf('PASS');
          if (i >= 0) {
              this.qualityFilters.splice(i, 1);
          }
        }
      },
      changedAllFailedCheckbox: function(e) {
        var filters = ['SVM', 'DISC', 'EXHET'];
        if (e.target.checked) {
          filters.forEach(filter => {
            if (!this.qualityFilters.includes(filter)) {
              this.qualityFilters.push(filter);
            }
          });
        } else {
          filters.forEach(filter => {
            var i = this.qualityFilters.indexOf(filter);
            if (i >= 0) {
                this.qualityFilters.splice(i, 1);
            }
          });
        }
      },
      changedAllLoFCheckbox: function(e) {
        if (e.target.checked) {
          this.lof.forEach(filter => {
            if (!this.lofFilters.includes(filter)) {
              this.lofFilters.push(filter);
            }
          });
        } else {
          this.lof.forEach(filter => {
            var i = this.lofFilters.indexOf(filter);
            if (i >= 0) {
              this.lofFilters.splice(i, 1);
            }
          });
        }
      },
      changedAllSynonymousCheckbox: function(e) {
        if (e.target.checked) {
          this.synonymous.forEach(filter => {
            if (!this.consequenceFilters.includes(filter)) {
              this.consequenceFilters.push(filter);
            }
          });
        } else {
          this.synonymous.forEach(filter => {
            var i = this.consequenceFilters.indexOf(filter);
            if (i >= 0) {
              this.consequenceFilters.splice(i, 1);
            }
          });
        }
      },
      changedAllNonsynonymousCheckbox: function(e) {
        if (e.target.checked) {
          this.nonsynonymous.forEach(filter => {
            if (!this.consequenceFilters.includes(filter)) {
              this.consequenceFilters.push(filter);
            }
          });
        } else {
          this.nonsynonymous.forEach(filter => {
            var i = this.consequenceFilters.indexOf(filter);
            if (i >= 0) {
              this.consequenceFilters.splice(i, 1);
            }
          });
        }
      }
    },
    beforeCreate: function() {
      // initialize non reactive data
      this.consequenceFiltersMap = {};
      this.lof = ['High Confidence', 'Low Confidence'];
      this.synonymous = ['synonymous', 'start retained', 'stop retained'];
      this.nonsynonymous = ['missense', 'start lost', 'stop lost', 'stop gained', 'frameshift', 'inframe insertion', 'inframe deletion'];
    },
    created: function() {
      this.filters.forEach(filter => {
        if (filter.title == 'Quality') {
          this.qualityFilters.push(filter.tabulator_filter.value);
          this.savedQualityFilters.push(filter.tabulator_filter.value);
        }
      });
    },
    mounted: function() {
      $(this.$el.querySelector('#qualityFilter')).on('hide.bs.dropdown', this.doNotChangeQualityFilters);
      $(this.$el.querySelector('#consequenceFilter')).on('hide.bs.dropdown', this.doNotChangeConsequenceFilters);
      $(this.$el.querySelector('#lofFilter')).on('hide.bs.dropdown', this.doNotChangeLofFilters);
      $(this.$el.querySelector('#frequencyFilter')).on('hide.bs.dropdown', this.doNotChangeFrequencyFilters);
      $(this.$el.querySelector('#rsFilter')).on('hide.bs.dropdown', this.doNotChangeRsFilters);
    },
    computed: {
    },
    watch: {
      suggestions: function(newSuggestions, oldSuggestions) {
        this.consequenceFiltersInputs = {
          'lof': [],
          'synonymous': [],
          'nonsynonymous': [],
          'others': []
        };
        this.consequenceFiltersMap = {};

        var lof = newSuggestions.LoF;
        for (var name in lof.data.items) {
          if (lof.data.items.hasOwnProperty(name)) {
            var item = lof.data.items[name];
            if (item.data.category != 'By Value') {
              continue;
            }
            this.consequenceFiltersInputs.lof.push(item.value);
            this.consequenceFiltersMap[item.value] = item.data.tabulator_filter;
          }
        }

        var consequences = newSuggestions.Consequence;
        for (var name in consequences.data.items) {
          if (consequences.data.items.hasOwnProperty(name)) {
              var item = consequences.data.items[name];
              if (item.data.category != 'By Value') {
                continue;
              }
              if (this.synonymous.includes(item.value)) {
                this.consequenceFiltersInputs.synonymous.push(item.value);
                this.consequenceFiltersMap[item.value] = item.data.tabulator_filter;
              } else if (this.nonsynonymous.includes(item.value)) {
                this.consequenceFiltersInputs.nonsynonymous.push(item.value);
                this.consequenceFiltersMap[item.value] = item.data.tabulator_filter;
              } else {
                this.consequenceFiltersInputs.others.push(item.value);
                this.consequenceFiltersMap[item.value] = item.data.tabulator_filter;
              }
          }
        }
      },
      qualityFilters: function(newFilters, oldFilters) {
        var failedFilters = ['SVM', 'DISC', 'EXHET'];
        if (failedFilters.every(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allFailedQC').indeterminate = false;
          this.$el.querySelector('#allFailedQC').checked = true;
        } else if (failedFilters.some(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allFailedQC').indeterminate = true;
          this.$el.querySelector('#allFailedQC').checked = false;
        } else {
          this.$el.querySelector('#allFailedQC').indeterminate = false;
          this.$el.querySelector('#allFailedQC').checked = false;
        }
        var passedFilters = ['PASS'];
        if (passedFilters.every(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allPassedQC').indeterminate = false;
          this.$el.querySelector('#allPassedQC').checked = true;
        } else if (passedFilters.some(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allPassedQC').indeterminate = true;
          this.$el.querySelector('#allPassedQC').checked = false;
        } else {
          this.$el.querySelector('#allPassedQC').indeterminate = false;
          this.$el.querySelector('#allPassedQC').checked = false;
        }
      },
      consequenceFilters: function(newFilters, oldFilters) {
        if (this.synonymous.every(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allSynonymous').indeterminate = false;
          this.$el.querySelector('#allSynonymous').checked = true;
        } else if (this.synonymous.some(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allSynonymous').indeterminate = true;
          this.$el.querySelector('#allSynonymous').checked = false;
        } else {
          this.$el.querySelector('#allSynonymous').indeterminate = false;
          this.$el.querySelector('#allSynonymous').checked = false;
        }
        if (this.nonsynonymous.every(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allNonsynonymous').indeterminate = false;
          this.$el.querySelector('#allNonsynonymous').checked = true;
        } else if (this.nonsynonymous.some(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allNonsynonymous').indeterminate = true;
          this.$el.querySelector('#allNonsynonymous').checked = false;
        } else {
          this.$el.querySelector('#allNonsynonymous').indeterminate = false;
          this.$el.querySelector('#allNonsynonymous').checked = false;
        }
      },
      lofFilters: function(newFilters, oldFilters) {
        if (this.lof.every(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allLoF').indeterminate = false;
          this.$el.querySelector('#allLoF').checked = true;
        } else if (this.lof.some(filter => newFilters.includes(filter))) {
          this.$el.querySelector('#allLoF').indeterminate = true;
          this.$el.querySelector('#allLoF').checked = false;
        } else {
          this.$el.querySelector('#allLoF').indeterminate = false;
          this.$el.querySelector('#allLoF').checked = false;
        }
      }
    }
  }
</script>

<style scoped>
.child-component {
  /* position: relative; */
  /* min-height: 50px; */
  /* margin-top: 5px; */
}
</style>
