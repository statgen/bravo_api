/* eslint-disable */

<template>
<div class="child-component">
  <div class="bravo-tooltip">
    <div v-html="tooltipHtml"></div>
  </div>
  <button class="close-button" v-on:click="$emit('close')">
    <font-awesome-icon style="background-color: transparent;" :icon="closeIcon"></font-awesome-icon>
  </button>
  <div v-if="loading" class="d-flex align-items-center bravo-message">
    <div class="spinner-border spinner-border-sm text-primary ml-auto" role="status" aria-hidden="true"></div>
    <strong>&nbsp;Loading...</strong>
  </div>
  <div v-if="failed" class="bravo-message">Error while loading genes data</div>
  <div v-if="loaded && (genes.length > 0)" class="bravo-info-message">Displaying {{ genes.length }} gene(s)</div>
  <div v-if="loaded && (genes.length == 0)" class="bravo-message">No genes in this region</div>
</div>
</template>

<script>
  import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
  import { faTimes } from '@fortawesome/free-solid-svg-icons';
  import axios from "axios";
  import * as d3 from "d3";

  export default {
    name: "genes",
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
      'hoveredVariant':{
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
        tooltipHtml: "",
        closeIcon: faTimes,
      }
    },
    methods: {
      load: function() {
        this.failed = false;
        this.loaded = false;
        this.loading = true;
        axios
          .get(`${this.api}genes/${this.region.regionChrom}-${this.region.regionStart}-${this.region.regionStop}`)
          .then( response => {
            var payload = response.data;
            if (payload.data.length > 0) {
              this.genes = payload.data;
              this.unwind_exons();
              this.initializeGenesSVG();
              this.draw();
            }
            this.loading = false;
            this.loaded = true;
          })
          .catch( error => {
            this.failed = true;
            this.loaded = false;
          });
      },
      unwind_exons: function () {
        this.exons = [];
        this.genes.forEach(function (gene) {
          gene.features.sort( function(a, b) { return a.start - b.start; });
          var last = { start: 0, stop: 0 };
          gene.features.forEach(function(feature) {
            if (feature.feature_type == 'exon') {
              if ((last.start != feature.start) || (last.stop != feature.stop)) { // remove identical regions e.g from different transcripts
                feature.gene_type = gene.gene_type;
                this.exons.push(feature);
                last = feature;
              }
            }
          }, this);
        }, this);
      },
      arrange_genes: function () {
        var buckets = [{ genes: [] }];
        var intersect = function(gene, start, stop) {
          if ((gene.box_right >= start) && (gene.box_left <= stop)) {
            return Math.min(gene.box_left, stop) - Math.max(gene.box_right, start) + 1;
          }
          return 0;
        }
        var put = function(gene) {
          for (var i = 0; i < buckets.length; ++i) {
            if (buckets[i].genes.length == 0) {
              gene.y = i;
              buckets[i].genes.push(gene);
              return;
            } else if (buckets[i].genes.every(function(gene2) { return intersect(gene, gene2.box_left, gene2.box_right) == 0; })) {
              gene.y = i;
              buckets[i].genes.push(gene);
              return;
            }
          }
          gene.y = buckets.length + 1;
          buckets.push({ genes: [gene] });
        }
        this.genes.forEach(function(gene) {
          // very trivial calculation of text box size given that we use 11px font size (assume 0.7 ratio of height to width) of known font style! if you change font style or size, change this line as well.
          var label_width = (gene.gene_name.length + 2) * 11 * 0.7;
          var padding = label_width - (gene.x_stop - gene.x_start);
          padding = padding < 0 ? 0 : padding / 2.0;
          gene.box_left = gene.x_start - padding - 2;
          gene.box_right = gene.x_stop + padding + 2;
          put(gene);
          gene.features.forEach(function(feature) {
            feature.y = gene.y;
          });
        });
      },
      initializeSVG: function () {
        this.svg = d3.select(this.$el)
          .append("div")
            .attr("id", "scroll")
            .style("max-height", `${this.height}px`)
            .style("display", "block")
            .style("overflow-y", "scroll")
            .style("overflow-x", "hidden")
          .append("svg")
            .style("display", "block");
        this.drawing_clip = this.svg
          .append("clipPath")
            .attr("id", "genes-clip")
          .append("rect")
            .attr("x", 0)
            .attr("y", 0);
        this.drawing = this.svg.append("g");
        this.x_scale = d3.scaleLinear();
      },
      initializeGenesSVG: function() {
        this.rects_box = this.drawing.selectAll("rec")
          .data(this.genes)
          .enter()
          .append("rect")
          .attr("height", 21)
          .attr("shape-rendering", "geometricPrecision")
          .style("fill", "white")
          .style("stroke", "none")
          .style("stroke-width", 0)
          .style("rx", 3)
          .style("ry", 3)
          .attr("rx", 3) // for firefox & safari
          .attr("ry", 3); // for firefox & safari
        this.rects_genes = this.drawing.selectAll("rec")
          .data(this.genes)
          .enter()
          .append("rect")
          .attr("height", 3)
          .attr("shape-rendering", "crispEdges")
          .style("pointer-events", "none")
          .style("fill", d => this.color[d.gene_type] || '#999999');
        this.rects_exons = this.drawing.selectAll("rec")
          .data(this.exons)
          .enter()
          .append("rect")
          .attr("height", 7)
          .attr("shape-rendering", "crispEdges")
          .style("pointer-events", "none")
          .style("fill", d => this.color[d.gene_type] || '#999999');
        this.text_genes = this.drawing.selectAll("text")
          .data(this.genes)
          .enter()
          .append("text")
          .style("pointer-events", "none");

        var self = this;
        this.rects_box.on("mouseover", function(gene) {
          d3.select(this)
            .style("fill", "#eeeeee")
            .style("stroke", "black")
            .style("stroke-width", "1px")
            .style("cursor", "pointer");
          var s = gene.start < self.region.regionStart ? self.region.regionStart : gene.start;
          var e = gene.stop > self.region.regionStop ? self.region.regionStop : gene.stop;
          var x_mid = self.x_scale(s + (e - s) / 2.0) + self.dimensions.margin.left ;
          var y_mid = this.getAttribute("y") - // get Y coordinate of the rectangle (its linear 1-to-1 mapping to pixel)
                self.$el.querySelector("#scroll").scrollTop - // substruct scroll position of the parent div
                self.dimensions.margin.top - // substruct drawing area margin
                16;
          d3.select(self.$el.querySelector(".bravo-tooltip"))
            .style("display", "block")
            .style("left", x_mid + "px")
            .style("top", y_mid + "px");
          self.tooltipHtml = `<ul><li><i>${gene.gene_name}</i> (${gene.strand})</li><li>${gene.gene_id}</li><li style='color: #85144b'>${gene.gene_type}</li><li>${gene.chrom}:${gene.start.toLocaleString()}-${gene.stop.toLocaleString()}</li><ul>`;
        });
        this.rects_box.on("mouseout", function(d) {
          d3.select(self.$el.querySelector(".bravo-tooltip"))
            .style("display", "none");
          self.tooltipHtml = "";
          d3.select(this)
            .style("fill", "white")
            .style("stroke", "none")
            .style("stroke-width", 0)
            .style("cursor", "default");
        });
        this.rects_box.on("click", d => this.$emit("click", d));
      },
      draw: function () {
        this.x_scale.range(this.region.segments.plot).domain(this.region.segments.region);
        this.genes.forEach(function(gene) {
          gene.x_start = this.x_scale(gene.start);
          gene.x_stop = this.x_scale(gene.stop);
          gene.features.forEach(function(feature) {
            feature.x_start = this.x_scale(feature.start);
            feature.x_stop = this.x_scale(feature.stop);
          }, this);
        }, this);
        this.arrange_genes();
        var max_y = d3.max(this.genes, function(gene) { return gene.y; }) + 1;
        this.svg
          .attr("width", this.dimensions.width)
          .attr("height", this.dimensions.margin.top + max_y * 22 + 2);
        this.drawing
          .attr("transform", `translate(${this.dimensions.margin.left}, ${this.dimensions.margin.top})`);
        this.drawing_clip
          .attr("width", this.dimensions.width - this.dimensions.margin.left - this.dimensions.margin.right)
          .attr("height", max_y * 22 + 2);
        this.rects_genes
          .attr("clip-path", "url(#genes-clip)")
          .attr("x", function(d) { return d.x_start; })
          .attr("width", function(d) { return d.x_stop - d.x_start; })
          .attr("y", function(d) { return d.y * 22 + 22 - 3 - 2; });
        this.rects_exons
            .attr("clip-path", "url(#genes-clip)")
            .attr("x", function(d) { return d.x_start; })
            .attr("width", function(d) { return d.x_stop - d.x_start; })
            .attr("y", function(d) { return d.y * 22 + 22 - 5 - 2; });
        this.text_genes
          .attr("clip-path", "url(#genes-clip)")
          .attr("x", d => {
            var s = Math.max(this.region.regionStart, d.start);
            var e = Math.min(this.region.regionStop, d.stop);
            return this.x_scale(s + (e - s) / 2.0);
          })
          .attr("y", function(d) { return d.y * 22 + 22 - 3 - 2 - 3; })
          .attr("text-anchor", "middle")
          .attr("alignment-baseline", "alphabetic")
          .style("font-family", "sans-serif")
          .style("font-style", "italic")
          .style("font-size", "11px")
          .html(function(d) {
            if (d.strand == '+') {
              return d.gene_name + "<tspan style=\"font-style: normal;\"> &rarr;</tspan>"
            } else {
              return "<tspan style=\"font-style: normal;\">&larr; </tspan>" + d.gene_name;
            }
          });
        this.rects_box
          .attr("clip-path", "url(#genes-clip)")
          .attr("x", function(d) { return d.box_left; })
          .attr("width", function(d) { return d.box_right - d.box_left; })
          .attr("y", function(d) { return d.y * 22 + 22 - 18 - 2; });
      },
      highlight: function() {
        this.drawing.selectAll("line").remove();
        if ((this.hoveredVariant.index != null) && (this.hoveredVariant.hovered)) {
          this.drawing.append("line")
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
    beforeCreate: function() {
      // initialize non reactive data
      this.genes = [];
      this.exons = [];
      this.height = 200;
      this.color = {
        'protein_coding': '#373994'
      };
      this.svg = null;
      this.drawing = null;
      this.drawing_clip = null;
      this.drawing_x_axis = null;
      this.x_scale = null;
      this.rects_genes = null;
      this.rects_exons = null;
      this.rects_box = null;
      this.tip = null;
    },
    created: function() {
    },
    mounted: function() {
      this.initializeSVG();
      this.load();
    },
    watch: {
      region: {
        handler: function(newValue, oldValue) {
          if ((!this.loading) && (!this.failed)) {
            if ((this.genes.length > 0) && (this.region.segments.region.every(d => d != null)) && (this.region.segments.plot.every(d => d != null))) {
              this.draw();
              this.highlight();
            }
          }
        },
        deep: true
      },
      hoveredVariant: function(newValue, oldValue) {
        if ((!this.loading) && (!this.failed)) {
          if (this.genes.length > 0) {
            this.highlight();
          }
        }
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
  border: 1px solid grey;
  padding: 5px;
  background-color: white;
  opacity: 1.0;
  border-radius: 5%;
}
.bravo-tooltip {
  position: absolute;
  display: none;
  pointer-events: none;
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  color: black;
  font-size: 11px;
  background-color: #eeeeee;
  border: 1px solid black;
  border-radius: 5px;
  box-shadow: 0px 4px 8px 0px rgba(0,0,0,0.2);
  z-index: 1;
  -webkit-transform: translateX(-50%) translateY(-50%);
  transform: translateX(-50%) translateY(-50%);
  z-index: 9999;
  opacity: 1;
}
.bravo-tooltip >>> div {
  padding: 3px 3px 0px 3px;
}
.bravo-tooltip >>> ul  {
  list-style-type: none;
  margin: 0;
  padding: 0;
  white-space: nowrap;
}
.bravo-tooltip::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: black transparent transparent transparent;
}
</style>
