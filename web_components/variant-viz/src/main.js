import Vue from 'vue'
import App from './App.vue'

import Model from "../../model/src/model.js";
Vue.use(Model);

Vue.config.productionTip = false

new Vue({
  render: h => h(App, {
    props: {
      homepage: "https://bravo.sph.umich.edu/test/",
      api: "https://bravo.sph.umich.edu/test/",
      // variantId: "22-23971765-A-G",
      variantId: "1-55063542-C-A",
      // variantId: "17-38869859-G-A",
      totalSamples: 132345
    }
  }),
}).$mount('#app')
