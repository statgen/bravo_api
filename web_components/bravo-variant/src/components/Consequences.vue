<template>
  <div class="card shadow-sm">
    <div class="card-body">
      <div class="container-fluid">
        <div class="row">
          <div class="col-sm-12">
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th scope="col" style="border-top:none;">Variant effect</th>
                    <th scope="col" style="border-top:none;">LOFTEE</th>
                    <th scope="col" style="border-top:none;">HGVS description</th>
                    <th scope="col" style="border-top:none;">Gene</th>
                    <th scope="col" style="border-top:none;">Transcript</th>
                    <th scope="col" style="border-top:none;">Type</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="consequence in consequences" v-bind:key="consequence.transcript">
                    <td>
                      <span v-for="effect in consequence.effects" v-bind:key="effect" class="badge badge-light" v-bind:style="{ 'color': $DOMAIN_DICTIONARY['consequence'][effect].color, 'margin-right': '1px' }">{{ $DOMAIN_DICTIONARY["consequence"][effect].text }}</span>
                    </td>
                    <td><span class="badge" v-bind:class="{ 'badge-success': consequence.lof == $DOMAIN_DICTIONARY['lof']['HC'].text, 'badge-warning': consequence.lof == $DOMAIN_DICTIONARY['lof']['LC'].text }">{{ consequence.lof }}</span></td>
                    <td>
                      <span v-for="hgvs in consequence.hgvs" v-bind:key="hgvs" style="margin-right:5px">{{ hgvs }}</span>
                    </td>
                    <td><a v-bind:href="homepage + `/gene/snv/${consequence.gene}`" class="text-info">{{ consequence.gene }} <span v-if="consequence.gene_other_name">(<i>{{ consequence.gene_other_name }}</i>)</span></a></td>
                    <td>{{ consequence.transcript }}</td>
                    <td><span class="badge">{{ consequence.biotype }}</span></td>
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
export default {
  name: 'consequences',
  props: ['homepage', 'variant'],
  computed: {
    consequences: function() {
      var consequences = [];
      this.variant.annotation.genes.forEach( gene => {
        gene.transcripts.forEach( transcript => {
          var effects = [];
          transcript.consequence.forEach(e => {
            effects.push(e);
          });
          var lof = null;
          if ("lof" in transcript) {
            lof = this.$DOMAIN_DICTIONARY["lof"][transcript.lof].text;
          }
          var hgvs = [];
          if ('HGVSp' in transcript) { hgvs.push(transcript.HGVSp); }
          if ('HGVSc' in transcript) { hgvs.push(transcript.HGVSc); }
          consequences.push({
            gene: gene.name,
            gene_other_name: gene.other_name,
            transcript: transcript.name,
            biotype: transcript.biotype.replace("_", " "),
            hgvs: hgvs,
            effects: effects,
            lof:  lof});
        });
      });
      return consequences;
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
