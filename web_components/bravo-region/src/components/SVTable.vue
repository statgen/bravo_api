/* eslint-disable */

<template>
<div class="child-component">
  <div ref="svtable" class="table-sm"></div>
</div>
</template>

<script>
import Tabulator from "tabulator-tables";
import 'tabulator-tables/dist/css/bootstrap/tabulator_bootstrap4.min.css';

export default {
  name: "svtable",
  props: [ 'chrom', 'start', 'stop', 'api', 'paginationSize' ],
  components: {
  },
  data: function() {
    return {
    }
  },
  methods: {
    getData: function() {
      if (this.tabulator == null) {
        return [];
      }
      return this.tabulator.getData();
    },
    scrolled: function(event) {
      var scrollDivHeight = this.tabulator.rowManager.height;
      var scrollDivPosition = this.tabulator.rowManager.scrollTop;
      var rowHeight = this.tabulator.rowManager.vDomRowHeight;
      var top_visible_variant = 0;
      if (scrollDivPosition > 0) {
        top_visible_variant = Math.floor(scrollDivPosition / rowHeight);
        if (scrollDivPosition - (top_visible_variant * rowHeight) >= rowHeight / 2) {
          top_visible_variant += 1;
        }
      }
      scrollDivPosition += scrollDivHeight;
      var bottom_visible_variant = Math.floor(scrollDivPosition / rowHeight);
      if (scrollDivPosition - (bottom_visible_variant * rowHeight) <= rowHeight / 2) {
        bottom_visible_variant -= 1;
      }
      this.$emit("scroll", top_visible_variant, bottom_visible_variant);
    },
    scrollTo: function(top_variant, bottom_variant) {
      // The scrollTo Tabulator method (and similar) don't trigger scroll event and thus progressive data loading on scroll doesn't work.
      // So, we compute scroll position in pixels ourselves and trigger scroll
      this.$el.querySelector(".tabulator-tableHolder").removeEventListener("scroll", this.scrolled); // temporatly remove our own scroll event listener to avoid event loops.
      this.$el.querySelector(".tabulator-tableHolder").addEventListener("scroll", () => {
        this.$el.querySelector(".tabulator-tableHolder").addEventListener("scroll", this.scrolled);
      });
      var rowHeight = this.tabulator.rowManager.vDomRowHeight;
      this.$el.querySelector(".tabulator-tableHolder").scrollTop = rowHeight * top_variant;
    },
    hover: function(variant, hovered) {
      this.tabulator.getRows().forEach(r => { // clean up all elements (just in case)
        r.getElement().classList.remove("hover");
      });
      if (hovered) {
        this.tabulator.getRowFromPosition(variant).getElement().classList.add("hover");
      }
    },
    setFilter: function(filter) {
      this.tabulator.setFilter(filter);
    }
  },
  beforeCreate() {
    // DOM-manipulating widgets should store reference statically, not dynamically
    this.tabulator = null;
  },
  created: function() {
    this.nonreactiveInitialFilter = JSON.parse(JSON.stringify(this.initialFilter)); // copy initial filter value
  },
  mounted: function() {
    this.tabulator = new Tabulator(this.$refs.svtable, {
      ajaxURL: this.api,
      ajaxConfig: {
        method: "POST",
        headers: {
          "Content-type": "application/json; charset=utf-8",
        },
      },
      ajaxContentType: "json",
      ajaxSorting: true,
      ajaxFiltering: true,
      ajaxProgressiveLoad: "scroll",
      ajaxURLGenerator: (url, config, params) => {
        if (params.page == 1) { // when 1st page is requested "next" must be null
          params.next = null;
        }
        return url;
      },
      ajaxResponse: (url, params, response) => {
        response.last_page = Math.ceil(response.total / response.limit);
        if (this.tabulator.getData().length == 0) {
          this.$emit("dataload", response.data, false);
        } else {
          this.$emit("dataload", response.data, true);
        }
        params.next = response.next;
        return response;
      },
      dataLoading: (data) => {
      },
      dataLoaded: (data) => {
      },
      paginationSize: this.paginationSize,
      height: "600px",
      layout: "fitColumns",
      columns: [
        { title: "ID", field: "variant_id", sorter: "string" },
        { title: "Start", field: "pos", sorter: "number", align: "right", formatter: (cell, params, onrendered) => cell.getValue().toLocaleString() },
        { title: "Stop", field: "stop", sorter: "number", align: "right", formatter: (cell, params, onrendered) => cell.getValue().toLocaleString() },
        { title: "Type", field: "type", sorter: "string", align: "center" },
        { title: "Avg. Length", field: "avglen", sorter: "number", align: "right", formatter: (cell, params, onrendered) => cell.getValue().toLocaleString() },
        { title: "Quality", field: "filter", sorter: "string", align: "center" },
        { title: "N", field: "support", sorter: "number", align: "right",  formatter: (cell, params, onrendered) => cell.getValue().toLocaleString() },
        { title: "CI Start", field: "cipos", headerSort: false, align: "right", formatter: (cell, params, onrendered) => "[" + cell.getValue() + "]" },
        { title: "CI Stop", field: "ciend", headerSort: false, align: "right", formatter: (cell, params, onrendered) => "[" + cell.getValue() + "]" }
      ],
      initialSort: [
        { column: "pos", dir: "asc" }
      ],
      initialFilter: [
        { field: "filter", type: "=", value: "PASS" }
      ],
      rowMouseEnter: (e, row) => {
        var variant = this.tabulator.getRowPosition(row);
        this.$emit("hover", variant, true);
      },
      rowMouseLeave: (e, row) => {
        var variant = this.tabulator.getRowPosition(row);
        this.$emit("hover", variant, false);
      }
    });
    this.$el.querySelector(".tabulator-tableHolder").addEventListener("scroll", this.scrolled);
  },
  beforeDestroy: function() {
  },
  watch: {
  }
}
</script>
<style scoped>
.child-component {
  position: relative;
}
.child-component >>> .tabulator {
  font-size: 12px;
}
.child-component >>> .tabulator .tabulator-row:hover {
  background-color: orange;
}
.child-component >>> .tabulator .tabulator-row.hover {
  background-color: orange;
}
</style>
