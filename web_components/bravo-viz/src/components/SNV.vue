/* eslint-disable */

<template>
<div class="child-component">
  <button class="close-button" v-on:click="$emit('close')">
    <font-awesome-icon style="background-color: transparent;" :icon="closeIcon"></font-awesome-icon>
  </button>
  <div v-if="loading" class="d-flex align-items-center bravo-message">
    <div class="spinner-border spinner-border-sm text-primary ml-auto" role="status" aria-hidden="true"></div>
    <strong>&nbsp;Loading...</strong>
  </div>
  <div v-if="failed" class="bravo-message">Error while loading variants count</div>
  <div v-if="this.loaded && (this.variants >  0)" class="bravo-info-message">
    Displaying {{ this.variants.toLocaleString() }} variant(s)
  </div>
  <div v-if="this.loaded && (this.variants == 0)" class="bravo-info-message">
    No variants
  </div>
</div>
</template>

<script>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import axios from "axios";
import * as d3 from "d3";

export default {
  name: "snv",
  props: {
    'region': {
      type: Object
    },
    'dimensions': {
      type: Object
    },
    'api': {
      type: String
    },
    'filters': {
      type: Array
    },
    'visibleVariants': {
      type: Object
    },
    'hoveredVariant': {
      type: Object
    }
  },
  components: {
    FontAwesomeIcon,
  },
  data: function() {
    return {
      loading: false,
      loaded: false,
      failed: false,
      variants: 0,
      closeIcon: faTimes
    }
  },
  methods: {
    load: function() {
      if ((this.region.regionChrom == null) || (this.region.regionStart == null) || (this.region.regionStop == null)) {
        return;
      }
      if (this.region.gene != null) {
        var url = `${this.api}variants/gene/snv/${this.region.gene.gene_id}/histogram`;
      } else {
        var url = `${this.api}variants/region/snv/${this.region.regionChrom}-${this.region.regionStart}-${this.region.regionStop}/histogram`;
      }

      this.clearDrawing();

      this.failed = false;
      this.loaded = false;
      this.loading = true;

      var timestamp = Date.now();
      this.timestamp = timestamp;
      axios
        .post(url, {
          filters: this.computedFilters,
          introns: this.computedRegion.introns,
          windows: this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right
        })
        .then(response => {
          var payload = response.data;
          if (timestamp == this.timestamp) {
            this.histogram_window_size = payload.data["window-size"];
            this.histogram_data = payload.data.windows;
            this.variants = this.histogram_data.reduce((total, entry) => total + entry.count, 0);
            this.draw();
            this.drawHistogram();
            this.drawVariants();
          }
          this.loaded = true;
        })
        .catch(error => {
          this.loaded = false;
          this.failed = true;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    format_y_ticks: function(value) {
      return d3.format('d')(value) + "x";
    },
    initializeSVG: function () {
      this.svg = d3.select(this.$el)
        .append("svg")
          .style("display", "block")
          .attr("width", this.dimensions.width)
          .attr("height", this.height + this.dimensions.margin.top + this.dimensions.margin.bottom);
      this.drawing_clip = this.svg
        .append("clipPath")
          .attr("id", "snv-clip")
        .append("rect")
          .attr("x", 0)
          .attr("y", 0);
      this.drawing = this.svg.append("g");

      this.histogram_g = this.drawing.append("g")
        .attr("clip-path", "url(#snv-clip)");
      this.variant_pointers_g = this.drawing.append("g");
      this.y_axis_g = this.drawing.append("g")
        .style("font-size", "9px");

      this.drawing.append("text")
        .attr("transform", `translate(${-this.dimensions.margin.left + 11},${(this.height - 10)/2}) rotate(-90)`)
        .style("font-size", "11px")
        .style("text-anchor", "middle")
        .text("Variants Count");

      this.x_scale = d3.scaleLinear();
      this.y_axis = d3.axisLeft();
      this.y_scale = d3.scaleLinear();
    },
    draw: function () {
      this.drawing.selectAll("text").attr("opacity", 1);
      this.svg.attr("width", this.dimensions.width).attr("height", this.height + this.dimensions.margin.top + this.dimensions.margin.bottom);
      this.drawing.attr("transform", `translate(${this.dimensions.margin.left}, ${this.dimensions.margin.top})`);
      this.drawing_clip
        .attr("width", this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right)
        .attr("height", this.height);

      this.x_scale.range(this.region.segments.plot).domain(this.region.segments.region);

      var max_count = d3.max(this.histogram_data, function(d) { return d.count; });
      this.y_scale.range([this.height - 10, 0]).domain([0, max_count]);
      this.y_axis.scale(this.y_scale).ticks(Math.min(max_count, 4)).tickFormat(d3.format(".0s"));
      this.y_axis_g.call(this.y_axis);
    },
    highlightVariant: function() {
      // this.drawing.selectAll("line").remove();
      // if ((this.hoveredVariant.index != null) && (this.hoveredVariant.hovered)) {
      //   this.drawing.append("line")
      //     .attr("x1", this.x_scale(this.hoveredVariant.data.pos))
      //     .attr("y1", 0)
      //     .attr("x2", this.x_scale(this.hoveredVariant.data.pos))
      //     .attr("y2", this.height)
      //     .attr("stroke-width", 2)
      //     .attr("stroke-linecap", "round")
      //     .attr("stroke", "#e77f00");
      // }
    },
    drawHistogram: function() {
      this.histogram_g.selectAll("rect").remove();
      this.histogram_g.selectAll("rect")
        .data(this.histogram_data)
        .enter()
        .append("rect")
        .attr("x", 0)
        .attr("width", d => this.x_scale(d.start + this.histogram_window_size) - this.x_scale(d.start))
        .attr("height", d => this.height - 10 - this.y_scale(d.count))
        .attr("transform", d => `translate(${this.x_scale(d.start)},${this.y_scale(d.count)})`)
        .attr("stroke-width", 1)
        .attr("stroke", "lightsteelblue")
        .attr("fill", "lightsteelblue");
    },
    drawVariants: function() {
      this.variant_pointers_g.selectAll("path").remove();
      if (this.visibleVariants.data != null) {
        this.variant_pointers_g.selectAll("path")
          .data(this.visibleVariants.data)
          .enter()
          .append("path")
          .attr("d", d3.symbol().size(40).type(d3.symbolTriangle))
          .attr("transform", d => `translate(${this.x_scale(d.pos)},${this.height - 4})`)
          .attr("stroke", "black")
          .attr("fill", "green")
          .attr("opacity", 0.2);
      }
    },
    clearDrawing: function() {
      this.y_axis_g.selectAll("*").remove();
      this.histogram_g.selectAll("rect").remove();
      this.variant_pointers_g.selectAll("path").remove();
      this.drawing.selectAll("text").attr("opacity", 0);
    }
  },
  beforeCreate: function() {
    // initialize non-reactive data
    this.timestamp = null;
    this.histogram_data = [];
    this.histogram_window_size = 0;
    this.height = 70;
    this.color = '#ffa37c';
    this.svg = null;
    this.drawing = null;
    this.histogram_g = null;
    this.variant_pointers_g = null;
    this.x_scale = null;
    this.y_axis = null;
    this.y_scale = null;
    this.y_axis_g = null;
  },
  created: function() {
  },
  mounted: function() {
    this.initializeSVG();
    this.load();
  },
  watch: {
    computedRegion: {
      handler: function(newValue, oldValue) {
        if ((newValue.regionChrom == oldValue.regionChrom) && (newValue.regionStart == oldValue.regionStart) && (newValue.regionStop == oldValue.regionStop) && (newValue.introns == oldValue.introns)) {
          if (newValue.segments.plot[1] - newValue.segments.plot[0] > oldValue.segments.plot[1] - oldValue.segments.plot[0]) {
            this.load();
          } else if ((!this.loading) && (!this.failed) && (this.histogram_data.length > 0)) {
            this.draw();
            this.drawHistogram();
            this.drawVariants();
            // this.highlight();
          }
        } else {
          this.load();
        }
      },
      deep: true
    },
    filters: function(newValue, oldValue) {
      this.load();
    },
    hoveredVariant: function(newValue, oldValue) {
      // if ((!this.loading) && (!this.failed)) {
        // if (this.loaded_data_size > 0) {
          // this.highlight();
        // }
      // }
    },
    visibleVariants: function(newValue, oldValue) {
      this.drawVariants();
    }
  },
  computed: {
    computedRegion: function() {
      return JSON.parse(JSON.stringify(this.region));
    },
    computedFilters: function() {
      var filters = [];
      this.filters.forEach(f => {
        filters.push(f.tabulator_filter);
      });
      return filters;
    }
  }
}
</script>

<style scoped>
.child-component {
  position: relative;
  /* border: 1px solid black; */
  min-height: 50px;
  margin-top: 5px;
}
.close-button {
  position: absolute;
  top: 0px;
  right: 0px;
  padding: 0px 4px 0px 4px;
  color: black;
  font-size: 11px;
  outline: none;
  background-color: #eeeeee;
  border: 1px solid #cccccc;
  border-radius: 2px;
  box-shadow: none;
  opacity: 0.5;
}
.close-button:hover {
  background-color: #cccccc;
  opacity: 1.0;
}
.bravo-info-message {
  position: absolute;
  top: 0%;
  left: 50%;
  font-size: 11px;
  -webkit-transform: translateX(-50%);
  transform: translateX(-50%);
  background-color: white;
  opacity: 0.8;
}
.bravo-message {
  position: absolute;
  top: 50%;
  left: 50%;
  -webkit-transform: translateX(-50%) translateY(-50%);
  transform: translateX(-50%) translateY(-50%);
  border: 1px solid gray;
  padding: 5px;
  background-color: white;
  opacity: 1.0;
  border-radius: 5%;
}
</style>
