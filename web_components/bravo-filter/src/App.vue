<template>
  <form id="bravofilter" class="bravofilter"  @submit="handleSubmit">
    <div style="vertical-align: middle; padding-left: 2px; padding-right: 2px;">
      <font-awesome-icon style="vertical-align: inherit; color: #757575;" :icon="filterIcon"></font-awesome-icon>
    </div>
    <token v-bind:suggestions="suggestions" v-for="filter in activeFilters" :key="filter.id" v-bind:id="filter.id" v-bind:filter="filter.filter" v-on:tokenready="tokenReady" v-on:tokenexpand="tokenExpand" v-on:tokenclose="tokenClose"></token>
  </form>
</template>

<script>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faFilter } from '@fortawesome/free-solid-svg-icons';
import token from './components/Token.vue';

export default {
  name: "bravofilter",
  components: {
    FontAwesomeIcon,
    token
  },
  props: {
    suggestions: {
      type: Object
    },
    filters: {
      type: Array
    }
  },
  data: function() {
    return {
      activeFilters: [],
      filterIcon: faFilter
    }
  },
  methods: {
    tokenReady: function() {
      var id = this.activeFilters[this.activeFilters.length - 1].id + 1;
      this.activeFilters.push({ id: id, filter: null });
      this.$emit("filter", this.collectFilters());
    },
    tokenClose: function(value) {
      this.activeFilters.splice(this.activeFilters.findIndex(f => f.id == value), 1);
      this.$emit("filter", this.collectFilters());
    },
    tokenExpand: function(new_filters) {
      var id = this.activeFilters[this.activeFilters.length - 1].id + 1;
      this.activeFilters.splice(this.activeFilters.length - 1, 1);
      new_filters.forEach( f => {
        this.activeFilters.push({ id: id, filter: JSON.parse(JSON.stringify(f)) });
        id += 1;
      });
      this.activeFilters.push({ id: id, filter: null });
      this.$nextTick(function() {
        this.$emit("filter", this.collectFilters());
      });
    },
    collectFilters: function() {
      var filters = [];
      for (var i = 0; i < this.$children.length; ++i) {
        if (this.$children[i].hasFilter()) {
          filters.push({ tabulator_filter: this.$children[i].getFilter() });
        }
      }
      return filters;
    },
    setFilters: function(new_filters) {
      if (this.activeFilters.length > 0) {
        var id = this.activeFilters[this.activeFilters.length - 1].id + 1;
        this.activeFilters.splice(0, activeFilters.filters.length);
      } else {
        var id = 0;
      }
      new_filters.forEach( f => {
        this.activeFilters.push({ id: id, filter: JSON.parse(JSON.stringify(f)) });
        id += 1;
      });
      this.activeFilters.push({ id: id, filter: null });
    },
    handleSubmit: function(e) {
      e.preventDefault();
    }
  },
  created: function() {
    this.setFilters(this.filters);
  },
  mounted: function() {
  }
}
</script>

<style>
.bravofilter {
  border: 1px solid #ced4da;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin: 0px;
  padding: 2px 0px 2px 0px;
}
</style>
