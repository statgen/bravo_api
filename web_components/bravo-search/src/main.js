import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false

new Vue({
  render: h => h(App, {
    props: {
      autocompleteapi: "https://bravo.sph.umich.edu/test/autocomplete",
      searchapi: "https://bravo.sph.umich.edu/test/search",
      autofocus: false
    }
  }),
}).$mount('#app');
