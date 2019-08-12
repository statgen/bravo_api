import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false


new Vue({
  render: h => h(App, {
    props: {
      api: "https://bravo.sph.umich.edu/dev/",
      variantId: "22-23971765-A-G",
      totalSamples: 132345
    }
  }),
}).$mount('#app')
