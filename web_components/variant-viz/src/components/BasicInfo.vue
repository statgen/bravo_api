<template>
  <div class="card shadow-sm" style="min-width: 420px">
    <div class="card-body">
      <div class="container-fluid">
        <div class="row">
          <div class="col-sm-8 text-left text-truncate">Chromosome</div>
          <div class="col-sm-4 text-right">{{ this.variant.chrom }}</div>
        </div>
        <div class="row">
          <div class="col-sm-8 text-left text-truncate">Position</div>
          <div class="col-sm-4 text-right">{{ this.variant.pos.toLocaleString() }}</div>
        </div>
        <div class="row">
          <div class="col-sm-8 text-left text-truncate">Reference allele</div>
          <div class="col-sm-4 text-right">{{ this.variant.variant_id.split("-")[2] }}</div>
        </div>
        <div class="row">
          <div class="col-sm-8 text-left text-truncate">Alternate allele</div>
          <div class="col-sm-4 text-right">{{ this.variant.variant_id.split("-")[3] }}</div>
        </div>
        <div v-if="variant.rsids.length > 0" class="row">
          <div class="col-sm-8 text-left text-truncate">rsID</div>
          <div class="col-sm-4 text-right">
            <span v-for="item in this.variant.rsids" style="margin-right:1px">{{ item }}</span>
          </div>
        </div>
        <div class="row">
          <div class="col-sm-8 text-left text-truncate">Filter</div>
          <div class="col-sm-4 text-right">
            <span v-for="item in this.variant.filter" v-bind:class="{ 'badge badge-success': item == 'PASS', 'badge badge-danger': item != 'PASS' }" style="margin-right:1px">{{ item }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'basicinfo',
  props: ['variant']
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
