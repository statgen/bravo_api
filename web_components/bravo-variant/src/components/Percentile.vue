<template>
  <div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: 'percentile',
  props: ['variant', 'metric'],
  methods: {
    initializeSVG: function(legend) {
      this.svg = d3.select(this.$el)
        .append("svg")
          .style("display", "block")
          .attr("width", legend ? this.legend_width : this.width)
          .attr("height", legend ? this.legend_height:  this.height);
      this.drawing = this.svg.append("g");
      this.x_scale = d3.scaleLinear();
      if (legend) {
        this.x_axis_g = this.drawing.append("g")
          .style("font-size", "9px");
          this.x_axis = d3.axisBottom().ticks(5);
      }
    },
    draw: function() {
      this.drawing.selectAll("rect").remove();
      this.drawing.selectAll("g").remove();
      this.drawing.attr("transform", `translate(${this.margin.left},${this.margin.top})`);
      this.x_scale.range([0, this.width - this.margin.left - this.margin.right]).domain([0, 1.0]);
      this.drawing.selectAll("rect")
        .data(this.percentile_bins)
        .enter()
        .append("rect")
        .attr("x", d => this.x_scale(d.previous_probability))
        .attr("y", 0)
        .attr("width", d => this.x_scale(d.probability - d.previous_probability))
        .attr("height", this.height - this.margin.top - this.margin.bottom)
        .style("stroke", "none")
        .style("stroke-width", "0")
        .attr("shape-rendering", "crispEdges") // to avoid white space between adjacent rectangles
        .style("fill", d => {
          if (d.bin_n > 0) {
            return d3.interpolateRdYlBu(d.bin_n_pass / d.bin_n);
          } else {
            return "#a1a1a1";
          }
        });

      /* Draw bounding box */
      this.drawing.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", this.width - this.margin.left - this.margin.right)
        .attr("height", this.height - this.margin.top - this.margin.bottom)
        .style("pointer-events", "none") // to prevent bubbling
        .style("stroke", "#434343")
        .style("stroke-width", "1")
        .attr("shape-rendering", "crispEdges")
        .style("fill", "none");

      const p_low = this.variant.qc_metrics[this.metric.name][1];
      const p_high = this.variant.qc_metrics[this.metric.name][2];
       /* Draw percentile rectangle mark if difference between percentile values is more than 2px. Otherwise, draw triangle. */
      if (Math.round(this.x_scale(p_high - p_low)) >= 3) {
        this.drawing.append("g")
          .attr("transform", `translate(${this.x_scale(p_low)}, ${this.height - this.margin.top -this.margin.bottom + 1})`)
          .append("path")
            .attr("d", d => " M 0 0 L 0 7 L " + this.x_scale(p_high - p_low) + " 7 L " + this.x_scale(p_high - p_low) + " 0 L 0 0")
            .style("stroke", "none")
            .style("stroke-width", "0")
            .attr("shape-rendering", "crispEdges") // to avoid white space between adjacent triangle
            .style("fill", "red");
      } else {
        this.drawing.append("g")
          .attr("transform", `translate(${this.x_scale(p_low)}, ${this.height - this.margin.top - this.margin.bottom + 1})`)
          .append("path")
            .attr("d", d => " M 0 0 L -7 7 L 7 7 L 0 0")
            .style("stroke", "none")
            .style("stroke-width", "0")
            .attr("shape-rendering", "crispEdges") // to avoid white space between adjacent triangle
            .style("fill", "red");
      }
    },
    drawLegend: function() {
      this.drawing.selectAll("rect").remove();

      this.drawing.attr("transform", `translate(${this.legend_margin.left},${this.legend_margin.top})`);

      this.drawing.append("text")
          .attr("x", this.legend_width / 2)
          .attr("y", -this.legend_margin.top)
          .style("text-anchor", "middle")
          .style("dominant-baseline", "text-before-edge")
          .attr("font-size", "11px")
          .text("% of PASS variants");

      this.x_scale.range([0, this.legend_width - this.legend_margin.left - this.legend_margin.right]).domain([0, 100]);
      this.x_axis.scale(this.x_scale);
      this.x_axis_g.attr("transform", `translate(0, ${this.legend_height - this.legend_margin.top - this.legend_margin.bottom})`).call(this.x_axis);

      var colorScale = d3.scaleSequential(d3.interpolateRdYlBu).domain([0, 100]);
      this.drawing.selectAll("rect")
        .data(d3.range(this.legend_width - this.legend_margin.left - this.legend_margin.right))
        .enter()
        .append("rect")
        .attr("x", (d, i) => i)
        .attr("y", 0)
        .attr("height", this.legend_height - this.legend_margin.top - this.legend_margin.bottom)
        .attr("width", 1)
        .attr("shape-rendering", "crispEdges")
        .style("fill", d => colorScale(d));

        /* Draw bounding box */
        this.drawing.append("rect")
          .attr("x", 0)
          .attr("y", 0)
          .attr("width", this.legend_width - this.legend_margin.left - this.legend_margin.right)
          .attr("height", this.legend_height - this.legend_margin.top - this.legend_margin.bottom)
          .attr("shape-rendering", "crispEdges")
          .style("pointer-events", "none") // to prevent bubbling
          .style("stroke", "#434343")
          .style("stroke-width", "1")
          .style("fill", "none");
    }
  },
  beforeCreate: function() {
    // initialize non-reactive data
    this.width = 180;
    this.height = 28;
    this.margin = {
      left: 7,
      right: 7,
      top: 2,
      bottom: 8
    };
    this.legend_width = 180;
    this.legend_height = 45;
    this.legend_margin = {
      left: 7,
      right: 8,
      top: 17,
      bottom: 18
    };
    this.svg = null;
    this.drawing = null;
    this.x_scale = null;
    this.x_axis_g = null;
    this.x_axis = null;
  },
  mounted: function() {
    if (this.percentile_bins != null) {
      this.initializeSVG(false);
      this.draw();
    } else {
          this.initializeSVG(true);
      this.drawLegend();
    }
  },
  computed: {
    percentile_bins: function() {
      if (!this.metric) {
        return null;
      }
      var percentile_bins = JSON.parse(JSON.stringify(this.metric.percentiles)); // deep copy
      percentile_bins.sort((p1, p2) => p1.probability < p2.probability ? -1 : 1);
      var previous_probability = 0;
      var previous_value = null;
      var previous_n = 0;
      var previous_n_pass = 0;
      percentile_bins.forEach(p => {
        p.previous_probability = previous_probability;
        p.previous_value = previous_value;
        p.bin_n = p.n - previous_n;
        p.bin_n_pass = p.n_pass - previous_n_pass;
        previous_probability = p.probability;
        previous_value = p.value;
        previous_n = p.n;
        previous_n_pass = p.n_pass;
      });
      return percentile_bins;
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
