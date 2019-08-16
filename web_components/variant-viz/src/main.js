import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false


new Vue({
  render: h => h(App, {
    props: {
      homepage: "https://bravo.sph.umich.edu/test/",
      api: "https://bravo.sph.umich.edu/test/",
      variantId: "22-23971765-A-G",
      totalSamples: 132345
    }
  }),
}).$mount('#app')
