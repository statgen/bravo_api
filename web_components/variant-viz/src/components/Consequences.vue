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
                    <th scope="col" style="border-top:none;">Loss-of-Function (LoF)</th>
                    <th scope="col" style="border-top:none;">HGVS description</th>
                    <th scope="col" style="border-top:none;">Gene</th>
                    <th scope="col" style="border-top:none;">Transcript</th>
                    <th scope="col" style="border-top:none;">Type</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="consequence in consequences">
                    <td>
                      <span v-for="effect in consequence.effects" class="badge badge-light" v-bind:style="{ 'color': effect.color, 'margin-right': '1px', }">{{ effect.text }}</span>
                    </td>
                    <td><span class="badge" v-bind:class="{ 'badge-success': consequence.lof == 'High Confidence', 'badge-warning': consequence.lof == 'Low Confidence' }">{{ consequence.lof }}</span></td>
                    <td>{{ consequence.hgvs }}</td>
                    <td>{{ consequence.gene }}</td>
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
import { Model } from '../mixins/model.js'

export default {
  mixins: [ Model ],
  name: 'consequences',
  props: ['variant'],
  computed: {
    consequences: function() {
      var consequences = [];
      this.variant.annotation.genes.forEach( gene => {
        gene.transcripts.forEach( transcript => {
          var effects = [];
          transcript.consequence.forEach(e => {
            effects.push(this.domain_dictionary["annotation.region.consequence"][e]);
          });
          var lof = null;
          if ("lof" in transcript) {
            lof = this.domain_dictionary["annotation.region.lof"][transcript.lof].text;
          }
          consequences.push({
            gene: gene.name,
            transcript: transcript.name,
            biotype: transcript.biotype.replace("_", " "),
            hgvs: transcript.HGVS,
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
