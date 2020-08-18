<template>
  <div class="card shadow-sm" style="width: 300px;">
    <div class="card-body">
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: 'depth',
  props: ['variant'],
  methods: {
    initializeSVG: function() {
      this.svg = d3.select(this.$el.querySelector('.card-body'))
        .append("svg")
          .style("display", "block")
          .attr("width", this.width)
          .attr("height", this.height);
      this.drawing = this.svg.append("g");
      this.legend = this.svg.append("g");

      this.all_dp_histogram = this.drawing.append("g");
      this.alt_dp_histogram = this.drawing.append("g");

      this.x_axis_g = this.drawing.append("g")
        .style("font-size", "11px");
      this.x_axis = d3.axisBottom();
      this.x_scale = d3.scaleLinear();

      this.y_axis_g = this.drawing.append("g")
        .style("font-size", "11px");
      this.y_axis = d3.axisLeft();
      this.y_scale = d3.scaleLinear();

      this.drawing.append("text")
        .attr("transform", `translate(-32, ${this.margin.top + (this.height - this.margin.top - this.margin.bottom) / 2}) rotate(-90)`)
          .style("font-size", "12px")
          .style("text-anchor", "middle")
          .style("font-weight", "bold")
          .text("Proportion of individuals");

      this.drawing.append("text")
        .attr("transform", `translate(${(this.width - this.margin.left - this.margin.right) / 2}, ${this.height - this.margin.bottom + 28})`)
          .style("font-size", "12px")
          .style("text-anchor", "middle")
          .style("font-weight", "bold")
          .text("Sequencing depth");
    },
    draw: function() {
      var x_extent = d3.extent(this.bins);
      x_extent[0] -= this.bin_width / 2;
      x_extent[1] += this.bin_width / 2;

      var total_dp_1 = d3.sum(this.variant.dp_hist);
      var total_dp_2 = d3.sum(this.variant.dp_hist_alt);
      var y_extent_1 = d3.extent(this.variant.dp_hist, function(d) { return d / total_dp_1; });
      var y_extent_2 = d3.extent(this.variant.dp_hist_alt, function(d) { return d / total_dp_2});

      var y_extent = [ Math.min(y_extent_1[0], y_extent_2[0]), Math.max(y_extent_1[1], y_extent_2[1]) ]

      this.drawing.attr("transform", `translate(${this.margin.left}, ${this.margin.top})`);

      this.x_scale.range([0, this.width - this.margin.left - this.margin.right]).domain(x_extent);
      this.y_scale.range([this.height - this.margin.top - this.margin.bottom, 0]).domain(y_extent);

      this.x_axis.scale(this.x_scale);
      this.x_axis_g.attr("transform", `translate(0, ${this.height - this.margin.top - this.margin.bottom})`).call(this.x_axis);

      this.y_axis.scale(this.y_scale);
      this.y_axis_g.call(this.y_axis);

      this.all_dp_histogram.selectAll("rect").remove();
      this.all_dp_histogram.selectAll("rect")
        .data(this.variant.dp_hist)
        .enter()
        .append("rect")
        .attr("width", this.x_scale(this.bin_width))
        .attr("height", d => this.height - this.margin.top - this.margin.bottom - this.y_scale(d / total_dp_1) )
        .attr("transform", (d, i) => `translate(${this.x_scale(this.bins[i] - this.bin_width / 2)},${this.y_scale(d / total_dp_1)})`)
        .attr("shape-rendering", "crispEdges") // to avoid white space between adjacent rectangles
        .attr("stroke-width", 1)
        .attr("stroke", "lightsteelblue")
        .attr("fill", "lightsteelblue")
        .attr("fill-opacity", "0.50");

      this.alt_dp_histogram.selectAll("rect").remove();
      this.alt_dp_histogram.selectAll("rect")
        .data(this.variant.dp_hist_alt)
        .enter()
        .append("rect")
        .attr("width", this.x_scale(this.bin_width))
        .attr("height", d => this.height - this.margin.top - this.margin.bottom - this.y_scale(d / total_dp_2) )
        .attr("transform", (d, i) => `translate(${this.x_scale(this.bins[i] - this.bin_width / 2)},${this.y_scale(d / total_dp_2)})`)
        .attr("shape-rendering", "crispEdges") // to avoid white space between adjacent rectangles
        .attr("stroke-width", 1)
        .attr("stroke", "lightpink")
        .attr("fill", "lightpink")
        .attr("fill-opacity", "0.50");
    },
    drawLegend: function() {
      this.legend.selectAll("rect").remove();
      this.legend.selectAll("text").remove();
      this.legend.attr("transform", `translate(${this.margin.left}, ${this.height - this.margin.bottom + 42})`)
      this.legend.append("rect")
        .attr("width", 12)
        .attr("height", 12)
        .attr("stroke-width", 1)
        .attr("stroke", "lightsteelblue")
        .attr("fill", "lightsteelblue")
        .attr("fill-opacity", "0.50");
      this.legend.append("text")
        .attr("x", 15)
        .attr("text-anchor", "start")
        .attr("dominant-baseline", "text-before-edge")
        .attr("font-size", 12)
        .text("All individuals");
      this.legend.append("rect")
        .attr("y", 15)
        .attr("width", 11)
        .attr("height", 11)
        .attr("stroke-width", 1)
        .attr("stroke", "lightpink")
        .attr("fill", "lightpink")
        .attr("fill-opacity", "0.50");
      this.legend.append("text")
        .attr("x", 15)
        .attr("y", 15)
        .attr("text-anchor", "start")
        .attr("dominant-baseline", "text-before-edge")
        .attr("font-size", 12)
        .text("Alternate allele carriers");
    }
  },
  beforeCreate: function() {
    // initialize non-reactive data
    this.width = 260;
    this.height = 300;
    this.margin = {
      left: 42,
      right: 10,
      top: 5,
      bottom: 70
    };
    this.svg = null;
    this.drawing = null;

    this.all_dp_histogram = null;
    this.alt_dp_histogram = null;
    this.legend = null;

    this.x_axis_g = null;
    this.x_axis = null;
    this.x_scale = null;

    this.y_axis_g = null;
    this.y_axis = null;
    this.y_scale = null;

    this.bins = [ 2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5, 87.5, 92.5, 97.5 ];
    this.bin_width = 5;
  },
  mounted: function() {
    this.initializeSVG();
    this.draw();
    this.drawLegend();
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
