import Vue from 'vue'
import App from './App.vue'

import Model from "../../bravo-model/src/model.js";
Vue.use(Model);

Vue.config.productionTip = false

new Vue({
  render: h => h(App, {
    props: {
      homepage: "https://bravo.sph.umich.edu/test/",
      api: "https://bravo.sph.umich.edu/test/",
      paginationSize: 100,
      // chrom: "22",
      // start: 23970365,
      // stop: 23981469,
      // chrom: "1",
      // start: 55039548,
      // stop: 55064852,

      // no genes in this region
      // chrom: "22",
      // start: 26976872,
      // stop: 26991421,


      // gene_name: 'DAB1',
      gene_name: 'PCSK9',
      // gene_name: 'M1AP',
      // gene_name: 'JADE1',
      // gene_name: 'LARGE1',
      // gene_name: 'U6'
      // gene_name: 'ENSG00000276138',
      // gene_name: 'ENSG00000278188'
    }
  }),
}).$mount('#app')
