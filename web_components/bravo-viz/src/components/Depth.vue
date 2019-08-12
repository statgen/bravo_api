/* eslint-disable */

<template>
<div class="child-component">
  <button class="close-button" v-on:click="$emit('close')">
    <font-awesome-icon style="background-color:transparent;" :icon="closeIcon"></font-awesome-icon>
  </button>
  <p v-if="failed" class="bravo-message">Error while loading depth</p>
  <p v-else-if="loading" class="bravo-message">Depth is loading...</p>
  <p v-else-if="loaded_data_size == 0" class="bravo-message">No depth data for this region</p>
</div>
</template>

<script>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import axios from "axios";
import * as d3 from "d3";

export default {
  name: "depth",
  props: {
    'api': {
      type: String
    },
    'region': {
      type: Object
    },
    'dimensions': {
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
      failed: false,
      loaded_data_size: 0,
      closeIcon: faTimes,
    }
  },
  methods: {
    load_cycle: function(url, size, next, draw) {
      axios
        .post(url, {
          size: size,
          next: next,
        })
        .then(response => {
          var payload = response.data;
          this.loaded_data_size += payload.data.length;
          draw = draw.then( () => {
            if (payload.data.length > 0) {
              // this.coverage_stats = this.coverage_stats.concat(payload.data); -- visualizations doesn't work when making new array copy
              // payload.data.forEach(d => {
              //   this.coverage_stats.push(d);
              // });
              this.coverage_stats.push(...payload.data); // ECMA6
              this.initializeCoverageSVG();
              this.draw();
            }
          });
          if (payload.next != null) {
            this.load_cycle(`${this.api}coverage/${this.region.regionChrom}-${this.region.regionStart}-${this.region.regionStop}`, size, payload.next, draw);
          } else {
            this.loading = false;
          }
        })
        .catch(error => {
          this.failed = true;
        });
    },
    load: function() {
      this.loading = true;
      this.coverage_stats = [];
      this.loaded_data_size = 0;
      this.load_cycle(`${this.api}coverage/${this.region.regionChrom}-${this.region.regionStart}-${this.region.regionStop}`, 10000, null, new Promise( resolve => resolve()));
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
          .attr("id", "depth-clip")
        .append("rect")
          .attr("x", 0)
          .attr("y", 0);
      this.drawing = this.svg.append("g");
      this.depth_g = this.drawing.append("g");
      this.y_axis_g = this.drawing.append("g")
        .style("font-size", "9px");
      this.drawing.append("text")
          .attr("transform", `translate(${-this.dimensions.margin.left + 11},${this.height/2}) rotate(-90)`)
          .style("font-size", "11px")
          .style("text-anchor", "middle")
          .text("Avg. Depth");
      this.x_scale = d3.scaleLinear();
      this.y_axis = d3.axisLeft();
      this.y_scale = d3.scaleLinear();
    },
    initializeCoverageSVG: function() {
      var path = this.depth_g.selectAll("path")
        .data([this.coverage_stats])
        .enter()
        .append("path")
          .style("fill", this.color)
          .style("stroke-width", 0.1)
          .style("stroke", "black");
    },
    draw: function () {
      this.svg.attr("width", this.dimensions.width).attr("height", this.height + this.dimensions.margin.top + this.dimensions.margin.bottom);
      this.drawing.attr("transform", `translate(${this.dimensions.margin.left}, ${this.dimensions.margin.top})`);
      this.drawing_clip
        .attr("width", this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right)
        .attr("height", this.height);
      this.x_scale.range(this.region.segments.plot).domain(this.region.segments.region);
      this.y_scale.range([this.height, 0]).domain([0, d3.max(this.coverage_stats, function(d) { return d.mean; })]);
      this.y_axis.scale(this.y_scale).ticks(4).tickFormat(this.format_y_ticks);
      this.y_axis_g.call(this.y_axis);
      var area = d3.area()
        .x( d => this.x_scale(d.start) )
        .y0(d => 0)
        .y1(d => 0)
        .y0( d => this.height )
        .y1( d => this.y_scale(d.mean) )
        .curve(d3.curveStepAfter);
      this.drawing.selectAll("g>path:last-child")
        .attr("clip-path", "url(#depth-clip)")
        .attr("d", area);
    },
    highlight: function() {
      this.drawing.selectAll(".highlight_line").remove();
      if ((this.hoveredVariant.index != null) && (this.hoveredVariant.hovered)) {
        this.drawing.append("line")
          .attr("class", "highlight_line")
          .attr("x1", this.x_scale(this.hoveredVariant.data.pos))
          .attr("y1", 0)
          .attr("x2", this.x_scale(this.hoveredVariant.data.pos))
          .attr("y2", this.height)
          .attr("stroke-width", 2)
          .attr("stroke-linecap", "round")
          .attr("stroke", "#e77f00");
      }
    }
  },
  beforeCreate() {
    // initialize non-reactive data
    this.height = 70;
    this.color = '#ffa37c';
    this.svg = null;
    this.drawing = null;
    this.drawing_g = null;
    this.x_scale = null;
    this.y_axis = null;
    this.y_scale = null;
    this.y_axis_g = null;
    this.coverage_stats = [];
  },
  created: function() {
  },
  mounted: function() {
    this.initializeSVG();
    if ((this.region.regionChrom != null) && (this.region.regionStart != null) && (this.region.regionStop != null) &&
      (this.region.segments.region.every(d => d != null)) && (this.region.segments.plot.every(d => d != null))) {
      this.load();
    }
  },
  watch: {
    region: {
      handler: function(newValue, oldValue) {
        if ((newValue.regionChrom == oldValue.regionChrom) && (newValue.regionStart == oldValue.regionStart) && (newValue.regionStop == oldValue.regionStop)) {
          if ((!this.loading) && (!this.failed) && (this.loaded_data_size > 0)) {
            this.draw();
            this.highlight();
          }
        } else {
          this.load();
        }
      },
      deep: true
    },
    hoveredVariant: function(newValue, oldValue) {
      if ((!this.loading) && (!this.failed) && (this.loaded_data_size > 0)) {
        this.highlight();
      }
    }
  }
}
</script>

<style scoped>
.child-component {
  position: relative;
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
.bravo-message {
  position: absolute;
  top: 50%;
  left: 50%;
  -webkit-transform: translateX(-50%) translateY(-50%);
  transform: translateX(-50%) translateY(-50%);
  border: 1px solid black;
  padding: 5px;
  background-color: white;
  opacity: 0.8;
}
</style>
