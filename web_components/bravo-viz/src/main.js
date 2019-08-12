import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false

new Vue({
  render: h => h(App, {
    props: {
      // chrom: "22",
      // start: 23970365,
      // stop: 23981469,
      gene_name: 'DDT',
      // gene_name: 'JADE1',
      // gene_name: 'LARGE1',
      // gene_name: 'U6'
      // gene_name: 'ENSG00000276138',
      // gene_name: 'ENSG00000278188'
    }
  }),
}).$mount('#app')
