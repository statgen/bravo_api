<template>
  <div class="card shadow-sm" style="min-width: 300px">
    <div class="card-body">
      <div v-for="count in counts" class="container-fluid">
        <div class="row">
          <div class="col-5 col-sm-7 text-left text-truncate">{{ count.name }}</div>
          <div class="col-7 col-sm-5 text-right">{{ count.value }}</div>
        </div>
        <div class="row" style="margin-bottom:8px;">
          <div class="col-12 col-sm-12">
            <div class="progress" style="height:5px;">
              <div class="progress-bar" role="progressbar" v-bind:style="{ width: count.percent + '%' }" v-bind:aria-valuenow="count.value" v-bind:aria-valuemax="count.max"></div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'counts',
  props: ['variant', 'n_samples'],
  computed: {
    counts: function() {
      return [
        { name: "Samples", value: (this.variant.allele_num / 2).toLocaleString(), percent:  100 * this.variant.allele_num / (2 * this.n_samples), max: this.n_samples },
        { name: "AC (Alternate allele Count)", value: this.variant.allele_count.toLocaleString(), percent: 100 * this.variant.allele_count / (2 * this.n_samples), max: 2 * this.n_samples },
        { name: "AF (Alternate allele Frequency)", value: this.variant.allele_freq.toPrecision(5), percent: 100 * this.variant.allele_freq, max: 1.0 },
        { name: "Heterozygotes", value: this.variant.het_count.toLocaleString(), percent: 100 * this.variant.het_count / this.n_samples, max: this.n_samples },
        { name: "Homozygotes", value: this.variant.hom_count.toLocaleString(), percent: 100 * this.variant.hom_count / this.n_samples, max: this.n_samples }
      ];
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
