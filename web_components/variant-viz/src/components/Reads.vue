<template>
  <div class="card shadow-sm">
    <div class="card-body">
      <div v-if="computedHeterozygous.length == 0 && computedHomozygous.length == 0" class="container-fluid">
        <div class="row">
          <div class="col-sm-12">
            <div role="role" class="alert alert-info">
              Can't display raw sequences: no heterozygous or homozygous individuals.
            </div>
          </div>
        </div>
      </div>
      <div v-else class="container-fluid">
        <div v-if="computedHeterozygous.length > 0" class="row mb-1">
          <div class="col-sm-auto">
            Displaying sequences for heterozygous individual:
          </div>
          <div class="col-sm-auto">
            <div class="btn-group" role="group">
              <button v-for="individual in computedHeterozygous" v-bind:id="'btn-het-' + individual.no" type="button" class="btn btn-secondary btn-sm" v-on:click="sequence(true, individual.no, $event)">{{ individual.no }}</button>
            </div>
          </div>
        </div>
        <div v-if="computedHomozygous.length > 0" class="row mb-1">
          <div class="col-sm-auto">
            Displaying sequences for homozygous individual:
          </div>
          <div class="col-sm-auto">
            <div class="btn-group" role="group">
              <button v-for="individual in computedHomozygous" v-bind:id="'btn-hom-' + individual.no" type="button" class="btn btn-secondary btn-sm" v-on:click="sequence(false, individual.no, $event)">{{ individual.no }}</button>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-sm-12">
            <div ref="igv"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import igv from "igv";

export default {
  name: 'reads',
  props: ['variant', 'api'],
  data: function() {
    return { };
  },
  components: {
  },
  methods : {
    load: function() {
    },
    init_tracks: function() {
      if (this.computedHeterozygous.length > 0) {
        this.$el.querySelector('#btn-het-1').click();
      } else if (this.computedHomozygous.length > 0) {
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
    this.options.locus = `${this.variant.chrom}:${this.variant.pos - 100}-${this.variant.pos + 99}`;
    var self = this;
    igv.createBrowser(this.$refs.igv, this.options).then(function(browser) {
      self.init_tracks();
    });
  },
  computed: {
    computedHeterozygous: function() {
      var heterozygous = [];
      for (var i = 0; i < Math.min(5, this.variant.het_count); ++i) {
        heterozygous.push({ no: i + 1 });
      }
      return heterozygous;
    },
    computedHomozygous: function() {
      var homozygous = [];
      for (var i = 0; i < Math.min(5, this.variant.hom_count); ++i) {
        homozygous.push({ no: i + 1 });
      }
      return homozygous;
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
