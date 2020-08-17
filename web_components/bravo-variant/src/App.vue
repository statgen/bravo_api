<template>
  <div id="variantviz">
    <div v-if="this.ready">
      <div class="container">
        <div class="row">
          <div class="col-12">
            <h1>{{ this.variant.variant_id }}</h1>
          </div>
        </div>
        <div class="row">
          <div class="col-md-6 mt-3">
            <basicinfo v-bind:variant="this.variant"/>
          </div>
          <div class="col-md-6 mt-3">
            <counts v-bind:variant="this.variant" v-bind:n_samples="this.totalSamples"/>
          </div>
        </div>
        <div v-if="'pub_freq' in this.variant" class="row">
          <div v-for="ds in this.variant.pub_freq" class="col-6 mt-3">
            <frequency v-bind:ds="ds"/>
          </div>
        </div>
        <div class="row">
          <div class="col-12 mt-3">
            <consequences v-bind:homepage="this.homepage" v-bind:variant="this.variant"/>
          </div>
        </div>
        <div class="row">
          <div class="col-md-4 mt-3">
            <depth v-bind:variant="this.variant"/>
          </div>
        </div>
        <div class="row">
          <div class="col-12 mt-3">
            <metrics v-bind:variant="this.variant" v-bind:api="this.api"/>
          </div>
        </div>
        <div class="row">
          <div class="col-12 mt-3">
            <reads v-bind:variant="this.variant" v-bind:api="this.api"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import basicinfo from './components/BasicInfo.vue';
import counts from './components/Counts.vue';
import consequences from './components/Consequences.vue';
import depth from './components/Depth.vue';
import metrics from './components/Metrics.vue';
import frequency from './components/Frequency.vue';
import reads from './components/Reads.vue';


export default {
  name: 'bravovariant',
  components: {
    basicinfo,
    counts,
    consequences,
    depth,
    metrics,
    frequency,
    reads
  },
  props: {
    homepage: {
      type: String
    },
    api: {
      type: String
    },
    variantId: {
      type: String
    },
    totalSamples: {
      type: Number
    }
  },
  data: function() {
    return {
      loading: false,
      failed: false,
      ready: false
    }
  },
  methods : {
    load: function() {
      this.loading = true;
      axios
        .get(`${this.api}variant/api/snv/${this.variantId}`)
        .then( response => {
          var payload = response.data;
          this.variant = payload.data[0];
          this.loading = false;
          this.ready = true;
          var datasets = [];
          if ('pub_freq' in this.variant) {
            this.variant.pub_freq.forEach(freqs => {
              datasets.push(freqs.ds);
            });
          } else {
            this.variant['pub_freq'] = [];
          }
          if (!datasets.includes('1000G')) {
            this.variant.pub_freq.push({ 'ds': '1000G' });
          }
          if (!datasets.includes('gnomAD')) {
            this.variant.pub_freq.push({ 'ds': 'gnomAD' });
          }
        })
        .catch( error => {
          this.failed = true;
        });
    }
  },
  beforeCreate() {
    // initialize non-reactive data
    this.variant = null;
    this.consequences = null;
  },
  created: function() {

  },
  mounted: function() {
    this.load();
  }
}
</script>

<style>
#app {
  /* font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50; */
  /* margin-top: 60px; */
}
</style>
