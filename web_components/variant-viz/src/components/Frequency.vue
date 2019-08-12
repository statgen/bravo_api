<template>
  <div class="card shadow-sm" style="min-width: 420px">
    <div class="card-body">
      <div class="container-fluid">
        <div class="row">
          <div class="col-12">
            <h5>Allele frequency in {{ ds.ds }}</h5>
          </div>
        </div>
      </div>
      <div v-for="frequency in frequencies" class="container-fluid">
        <div class="row">
          <div class="col-sm-7 text-left text-truncate">{{ frequency.name }}</div>
          <div class="col-sm-5 text-right">{{ frequency.value }}</div>
        </div>
        <div class="row" style="margin-bottom:8px;">
          <div class="col-sm-12">
            <div class="progress" style="height:5px;">
              <div class="progress-bar" role="progressbar" v-bind:style="{ width: frequency.percent + '%' }" v-bind:aria-valuenow="frequency.value" v-bind:aria-valuemax="frequency.max"></div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { Model } from '../mixins/model.js'

export default {
  mixins: [ Model ],
  name: 'frequency',
  props: ['ds'],
  computed: {
    frequencies: function() {
      var frequencies = [];
      for (const key in this.ds) {
        if (key != 'ds') {
          frequencies.push({ name: `${this.domain_dictionary.populations[key]} (${key})`, value: this.ds[key], percent: this.ds[key] * 100, max: 1.0 });
        }
      }
      return frequencies;
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
