<template>
  <div class="card shadow-sm">
    <div class="card-body">
      <div v-if="this.loading" class="text-muted text-center">Loading...</div>
      <div v-else-if="this.failed" class="text-muted text-center">Error while retrieving sequence data.</div>
      <div v-else-if="this.counts.n_hets == 0 && this.counts.n_homs == 0" class="container-fluid">
        <div class="row">
          <div class="col-sm-12">
            <div role="role" class="alert alert-info">
              Raw sequences in heterozygous/homozygous individual(s) are not available at this variant.
            </div>
          </div>
        </div>
      </div>
      <div v-else class="container-fluid">
        <div class="table-responsive">
          <table class="table table-sm table-borderless">
            <tbody>
              <tr v-if="this.counts.n_hets > 0">
                <td class="text-left" style="width: 45%;">Displaying sequences for heterozygous individual:</td>
                <td class="text-left">
                  <div class="btn-group" role="group">
                    <button v-for="individual in this.counts.n_hets" v-bind:id="'btn-het-' + individual" type="button" class="btn btn-secondary btn-sm" v-on:click="sequence(true, individual, $event)">{{ individual }}</button>
                  </div>
                </td>
              </tr>
              <tr v-if="this.counts.n_homs > 0">
                <td class="text-left" style="width: 45%;">Displaying sequences for homozygous individual:</td>
                <td class="text-left">
                  <div class="btn-group" role="group">
                    <button v-for="individual in this.counts.n_homs" v-bind:id="'btn-hom-' + individual" type="button" class="btn btn-secondary btn-sm" v-on:click="sequence(false, individual, $event)">{{ individual }}</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="row">
          <div class="col-12 col-sm-12">
            <div ref="igv"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import igv from "igv";

export default {
  name: 'reads',
  props: ['variant', 'api'],
  data: function() {
    return {
      loading: true,
      failed: false,
      counts: {
        n_hets: 0,
        n_homs: 0
      }
    };
  },
  components: {
  },
  methods : {
    load: function() {
    },
    init_tracks: function() {
      if (this.counts.n_hets > 0) {
        this.$el.querySelector('#btn-het-1').click();
      } else if (this.counts.n_homs > 0) {
        this.$el.querySelector('#btn-hom-1').click();
      }
    },
    sequence: function(heterozygous, sample_no, event) {
      const name = `${heterozygous ? "Heterozygous" : "Homozygous"} individual #${sample_no}`;
      if (event.target.classList.contains('active')) {
        event.target.classList.remove('active');
        igv.browser.removeTrackByName(name);
      } else {
        event.target.classList.add('active');
        igv.browser.loadTrack({
          type: "alignment",
          format: "bam",
          name: name,
          colorBy: "strand",
          url: `${this.api}variant/api/snv/cram/${this.variant.variant_id}-${heterozygous ? 1 : 0}-${sample_no}`,
          indexURL: `${this.api}variant/api/snv/crai/${this.variant.variant_id}-${heterozygous ? 1 : 0}-${sample_no}`
        });
      }
    }
  },
  beforeCreate() {
    // initialize non-reactive data
    this.igv_browser = null;
    this.options = {
      reference: {
        fastaURL: "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa",
        indexURL: "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa.fai",
        cytobandURL: "https://s3.amazonaws.com/igv.org.genomes/hg38/annotations/cytoBandIdeo.txt.gz"
      },
      locus: "",
      showNavigation: true,
      showChromosomeWidget: false,
      showSVGButton: true,
      showCenterGuide: true,
      showRuler: true,
    };
  },
  created: function() {

  },
  mounted: function() {
    axios
      .get(`${this.api}variant/api/snv/cram/summary/${this.variant.variant_id}`)
      .then( response => {
        var result = response.data;
        if (result.data.length > 0) {
          var counts = result.data[0];
          this.counts.n_homs = counts.n_homozygous;
          this.counts.n_hets = counts.n_heterozygous;
        }
        this.loading = false;
        this.$nextTick(function () {
          this.options.locus = `${this.variant.chrom}:${this.variant.pos - 100}-${this.variant.pos + 99}`;
          var self = this;
          igv.createBrowser(this.$refs.igv, this.options).then(function() {
            self.init_tracks();
          });
        })
      })
      .catch( error => {
        this.loading = false;
        this.failed = true;
      });
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
