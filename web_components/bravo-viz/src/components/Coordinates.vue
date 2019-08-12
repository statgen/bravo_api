/* eslint-disable */

<template>
<div class="child-component">
</div>
</template>

<script>
  import * as d3 from "d3";

  export default {
    name: "coordinates",
    props: {
      "region": {
        type: Object
      },
      "dimensions": {
        type: Object
      }
    },
    methods: {
      format_position_ticks: function(value) {
        return d3.format('~s')(value) + "bp";
      },
      position_ticks: function() {
        var ticks = [];
        var window_length = this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right;
        for (var px = 0; px < window_length; px += 100) {
          ticks.push(Math.floor(this.x_scale.invert(px)));
        }
        return ticks;
      },
      init: function () {
        this.svg = d3.select(this.$el)
          .append("div")
            .style("max-height", `${this.height}px`)
            .style("display", "block")
            .style("overflow-y", "hidden")
            .style("overflow-x", "hidden")
          .append("svg")
            .style("height", "20px")
            .style("display", "block");
        this.x_axis = d3.axisBottom();
        this.x_axis_g = this.svg.append("g");
        this.x_scale = d3.scaleLinear();
      },
      draw: function () {
        this.svg.attr("width", this.dimensions.width);
        this.x_axis_g.attr("transform", `translate(${this.dimensions.margin.left}, 0)`);
        this.x_scale.range(this.region.segments.plot).domain(this.region.segments.region);
        this.x_axis.scale(this.x_scale).tickValues(this.position_ticks()).tickFormat(this.format_position_ticks);
        this.x_axis_g.call(this.x_axis);
      }
    },
    beforeCreate() {
      // initialize non reactive data
      this.height = 20;
      this.svg = null;
      this.x_axis = null;
      this.x_axis_g = null;
      this.x_scale = null;
    },
    created: function() {
    },
    mounted: function() {
      this.init();
      if ((this.region.segments.region.every(d => d != null)) && (this.region.segments.plot.every(d => d != null))) {
        this.draw();
      }
    },
    watch: {
      region: {
        handler: function(newValue, oldValue) {
          if ((this.region.segments.region.every(d => d != null)) && (this.region.segments.plot.every(d => d != null))) {
            this.draw();
          }
        },
        deep: true
      }
    }
  }
</script>

<style scoped>
.child-component {
  position: relative;
  min-height: 20px;
  margin-top: 5px;
}
</style>
