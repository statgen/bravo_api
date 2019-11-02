/* eslint-disable */

<template>
  <div class="child-component">
    <div class="container-fluid">
      <div class="row">
        <div class="col-12">
          <div class="btn-group mr-1">
            <button class="btn btn-outline-primary btn-sm dropdown-toggle" type="button" id="qualityFilterDropdownButton" data-boundary="window" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Quality
            </button>
            <div class="dropdown-menu shadow" @click.stop="">
              <form class="p-2">
                <ul style="list-style-type: none; padding-left: 0;">
                  <li>
                    <div class="custom-control custom-checkbox">
                      <input class="custom-control-input" type="checkbox" value="" id="defaultCheck1">
                      <label class="custom-control-label" for="defaultCheck1">Variants which pass QC</label>
                    </div>
                    <ul style="list-style-type: none; padding-left: 1rem; padding-top: 0.2rem;">
                      <li>
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" value="" id="defaultCheck2">
                          <label class="custom-control-label" for="defaultCheck2">PASS</label>
                          <small class="form-text text-muted">All filters passed</small>
                        </div>
                      </li>
                    </ul>
                  </li>
                  <li>
                    <div class="custom-control custom-checkbox">
                      <input class="custom-control-input" type="checkbox" value="" id="defaultCheck2">
                      <label class="custom-control-label" for="defaultCheck2">Variants which failed QC</label>
                    </div>
                    <ul style="list-style-type: none; padding-left: 1rem; padding-top: 0.2rem;">
                      <li>
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" value="" id="defaultCheck2">
                          <label class="custom-control-label" for="defaultCheck2">SVM</label>
                          <small class="form-text text-muted">Variant failed SVM filter.</small>
                        </div>
                      </li>
                      <li>
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" value="" id="defaultCheck2">
                          <label class="custom-control-label" for="defaultCheck2">DISC</label>
                          <small class="form-text text-muted">Mendelian or duplicate genotype discordance is high.</small>
                        </div>
                      </li>
                      <li>
                        <div class="custom-control custom-checkbox">
                          <input class="custom-control-input" type="checkbox" value="" id="defaultCheck2">
                          <label class="custom-control-label" for="defaultCheck2">EXHET</label>
                          <small class="form-text text-muted">Excess heterozygosity.</small>
                        </div>
                      </li>
                    </ul>
                  </li>
                </ul>
                <hr/>
                <div class="form-row">
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-secondary btn-sm" disabled>Clear</button>
                  </div>
                  <div class="col mr-auto">
                    <button type="button" class="btn btn-primary btn-sm float-right" v-on:click="saveQualityFilters">Save</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
          <!-- <div class="btn-group">
            <button class="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" id="qualityFilterDropdownButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Consequence
            </button>
            <form class="dropdown-menu p-2">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" value="" id="defaultCheck3">
                <label class="form-check-label" for="defaultCheck3">Synonymous</label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="checkbox" value="" id="defaultCheck4">
                <label class="form-check-label" for="defaultCheck4">Non-synonymous</label>
              </div>
              <button type="submit" class="btn btn-secondary btn-sm" disabled>Clear</button>
              <button type="submit" class="btn btn-primary btn-sm">Save</button>
            </form>
          </div> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "snvfilter",
    props: {
    },
    components: {
    },
    data: function() {
      return {
      }
    },
    methods: {
      saveQualityFilters: function() {
        $(this.$el.querySelector('#qualityFilterDropdownButton')).dropdown('hide');
      }
    },
    beforeCreate: function() {
      // initialize non reactive data
    },
    created: function() {
    },
    mounted: function() {
    },
    computed: {
    },
    watch: {
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
