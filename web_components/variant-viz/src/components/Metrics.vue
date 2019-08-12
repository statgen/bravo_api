<template>
  <div class="card shadow-sm">
    <div class="card-body">
      <div class="container-fluid">

        <div v-if="this.ready" class="row">
          <div class="col-sm-12">
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th scope="col" style="border-top:none;">Quality metric</th>
                    <th scope="col" style="border-top:none;">Description</th>
                    <th scope="col" style="border-top:none;">Value</th>
                    <th scope="col" style="border-top:none;">Percentile</th>
                    <th scope="col" style="border-top:none;"><percentile /></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="metric in metrics">
                    <td>{{ metric.name }}</td>
                    <td>{{ metric.description }}</td>
                    <td>{{ variant.qc_metrics[metric.name][0].toPrecision(4) }}</td>
                    <td>{{ (variant.qc_metrics[metric.name][2] * 100).toFixed(2) }}</td>
                    <td><percentile v-bind:variant="variant" v-bind:metric="metric"/></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import percentile from './Percentile.vue';

export default {
  name: 'metrics',
  components: {
    percentile
  },
  props: ['variant', 'api'],
  data: function () {
    return {
      loading: false,
      failed: false,
      ready: false
    }
  },
  methods: {
    load: function() {
      this.loading = true;
      axios
        .get(`${this.api}qc/api`)
        .then( response => {
          var payload = response.data;
          this.metrics = payload.data;
          this.loading = false;
          this.ready = true;
        })
        .catch( error => {
          this.failed = true;
        });
    }
  },
  beforeCreate() {
    // initialize non-reactive data
    this.metrics = null;
  },
  created: function() {

  },
  mounted: function() {
    this.load();
  },
  computed: {
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
