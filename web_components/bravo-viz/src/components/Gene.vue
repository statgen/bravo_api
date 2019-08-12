/* eslint-disable */

<template>
<div class="child-component">
  <div class="bravo-tooltip">
    <div v-html="tooltipHtml"></div>
  </div>
  <button class="close-button" v-on:click="$emit('close')">
    <font-awesome-icon style="background-color: transparent;" :icon="closeIcon"></font-awesome-icon>
  </button>
  <div v-if="region.gene != null" class="bravo-info-message">
    Displaying {{ this.region.gene.transcripts.length }} transcript(s)
  </div>
  <p v-if="region.gene == null" class="bravo-message">No gene transcripts</p>
</div>
</template>

<script>
  import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
  import { faTimes } from '@fortawesome/free-solid-svg-icons';
  import * as d3 from "d3";

  export default {
    name: "gene",
    props: {
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
        tooltipHtml: "",
        closeIcon: faTimes,
      }
    },
    methods: {
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
        this.drawing = this.svg.append("g");
        this.x_scale = d3.scaleLinear();
      },
      initializeTranscriptsSVG: function() {
        this.rects_box = this.drawing.append("g").selectAll("rect")
           .data(this.region.gene.transcripts)
           .enter()
           .append("rect")
           .attr("height", Math.max(this.cds_height, this.exon_height) + this.font_size + 1)
           .attr("shape-rendering", "geometricPrecision")
           .style("fill", "white")
           .style("stroke", "none")
           .style("stroke-width", 0)
           .style("rx", 3)
           .style("ry", 3)
           .attr("rx", 3) // for firefox & safari
           .attr("ry", 3); // for firefox & safari

        this.rects_transcripts = this.drawing.append("g").selectAll("rect")
          .data(this.region.gene.transcripts)
          .enter()
          .append("rect")
          .attr("height", this.transcript_height)
          .attr("shape-rendering", "crispEdges")
          .style("pointer-events", "none")
          .style("fill", d => this.color[d.transcript_type] || '#999999');

        this.rects_cds = this.drawing.append("g").selectAll("rect")
          .data(this.region.gene.cds)
          .enter()
          .append("rect")
          .attr("height", this.cds_height)
          .attr("shape-rendering", "crispEdges")
          .style("pointer-events", "none")
          .style("fill", d => this.color[d.transcript_type] || '#999999');

        this.rects_exons = this.drawing.append("g").selectAll("rect")
          .data(this.region.gene.exons)
          .enter()
          .append("rect")
          .attr("height", this.exon_height)
          .attr("shape-rendering", "crispEdges")
          .style("pointer-events", "none")
          .style("fill", d => this.color[d.transcript_type] || '#999999');

        this.text_transcripts = this.drawing.selectAll("text")
          .data(this.region.gene.transcripts)
          .enter()
          .append("text")
          .style("pointer-events", "none");

        var self = this;
        this.rects_box.on("mouseover", function(transcript) {
          d3.select(this)
            .style("fill", "#eeeeee")
            .style("stroke", "black")
            .style("stroke-width", "1px")
            .style("cursor", "pointer");
          var x_mid = transcript.x_start + (transcript.x_stop - transcript.x_start) / 2.0 + self.dimensions.margin.left;
          var y_mid = this.getAttribute("y") - // get Y coordinate of the rectangle (its linear 1-to-1 mapping to pixel)
                self.$el.querySelector("#scroll").scrollTop - // substruct scroll position of the parent div
                self.dimensions.margin.top - // substruct drawing area margin
                8;
          d3.select(self.$el.querySelector(".bravo-tooltip"))
            .style("display", "block")
            .style("left", x_mid + "px")
            .style("top", y_mid + "px");
          self.tooltipHtml = `<ul><li>${transcript.transcript_id} (${transcript.strand})</li><li style='color: #85144b'>${transcript.transcript_type}</li><li>${self.region.chrom}:${transcript.start.toLocaleString()}-${transcript.stop.toLocaleString()}</li><ul>`;
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
      },
      draw: function () {
        this.x_scale.range(this.region.segments.plot).domain(this.region.segments.region);
        this.region.gene.transcripts.forEach((transcript, i) => {
          transcript.x_start = this.x_scale(transcript.start);
          transcript.x_stop = this.x_scale(transcript.stop);
          transcript.y = i + 1;
          // very trivial calculation of text box size given that we use 11px font size (assume 0.7 ratio of height to width) of known font style! if you change font style or size, change this line as well.
          var label_width = (transcript.transcript_id.length + 2) * this.font_size * 0.7;
          var padding = label_width - (transcript.x_stop - transcript.x_start);
          padding = padding < 0 ? 0 : padding / 2.0;
          transcript.box_left = transcript.x_start - padding - 2;
          transcript.box_right = transcript.x_stop + padding + 2;
          this.region.gene.exons.forEach( exon => {
            if (exon.transcript_id == transcript.transcript_id) {
              exon.x_start = this.x_scale(exon.start);
              exon.x_stop = this.x_scale(exon.stop);
              exon.y = transcript.y;
            }
          });
          this.region.gene.cds.forEach( cds => {
            if (cds.transcript_id == transcript.transcript_id) {
              cds.x_start = this.x_scale(cds.start);
              cds.x_stop = this.x_scale(cds.stop);
              cds.y = transcript.y;
            }
          });
        });
        this.svg
          .attr("width", this.dimensions.width)
          .attr("height", this.dimensions.margin.top + this.region.gene.transcripts.length * this.step + (this.cds_height - this.transcript_height) / 2 + 2);
        this.drawing.attr("transform", `translate(${this.dimensions.margin.left}, ${this.dimensions.margin.top})`);
        this.rects_transcripts
          .attr("x", d => d.x_start)
          .attr("width", d => d.x_stop - d.x_start)
          .attr("y", d => d.y * this.step - this.transcript_height);
        this.rects_cds
          .attr("x", d => d.x_start)
          .attr("width", d => d.x_stop - d.x_start)
          .attr("y", d => d.y * this.step - this.transcript_height - (this.cds_height - this.transcript_height) / 2);
        this.rects_exons
          .attr("x", function(d) { return d.x_start; })
          .attr("width", function(d) { return d.x_stop - d.x_start; })
          .attr("y", d => d.y * this.step - this.transcript_height - (this.exon_height - this.transcript_height) / 2);
        this.text_transcripts
          .attr("x", d => d.x_start + (d.x_stop - d.x_start) / 2.0)
          .attr("y", d => d.y * this.step - this.transcript_height - (Math.max(this.cds_height, this.exon_height) - this.transcript_height) / 2 - 1)
          .attr("text-anchor", "middle")
          .attr("alignment-baseline", "alphabetic")
          .style("font-family", "sans-serif")
          .style("font-size", "11px")
          .html(function(d) {
            if (d.strand == '+') {
              return d.transcript_id + "<tspan style=\"font-style: normal;\"> &rarr;</tspan>"
            } else {
              return "<tspan style=\"font-style: normal;\">&larr; </tspan>" + d.transcript_id;
            }
          });
        this.rects_box
          .attr("x", function(d) { return d.box_left; })
          .attr("width", function(d) { return d.box_right - d.box_left; })
          .attr("y", d => d.y * this.step - this.transcript_height - (Math.max(this.cds_height, this.exon_height) - this.transcript_height) / 2 - this.font_size);
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
      this.height = 200;
      this.step = 25; // distance between transcripts on y-axis (measured from the center)
      this.transcript_height = 3;
      this.cds_height = 11;
      this.exon_height = 7;
      this.font_size = 11;
      this.color = {
        'protein_coding': '#373994'
      };
      this.svg = null;
      this.drawing = null;
      this.drawing_x_axis = null;
      this.x_scale = null;
      this.rects_transcripts = null;
      this.text_transcripts = null;
      this.rects_cds = null;
      this.rects_exons = null;
      this.rects_box = null;
    },
    created: function() {
    },
    mounted: function() {
      this.initializeSVG();
      if ((this.region.gene != null) && (this.region.segments.region.every(d => d != null)) && (this.region.segments.plot.every(d => d != null))) {
        this.initializeTranscriptsSVG();
        this.draw();
      }
    },
    watch: {
      region: {
        handler: function(newValue, oldValue) {
          if ((this.region.gene != null) && (this.region.segments.region.every(d => d != null)) && (this.region.segments.plot.every(d => d != null))) {
            if ((oldValue.gene == null) || (oldValue.gene.gene_id !=newValue.gene.gene_id)) {
              this.initializeTranscriptsSVG();
            }
            this.draw();
            this.highlight();
          }
        },
        deep: true
      },
      hoveredVariant: function(newValue, oldValue) {
        if ((this.region.gene != null) && (this.region.segments.region.every(d => d != null)) && (this.region.segments.plot.every(d => d != null))) {
          this.highlight();
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
  border: 1px solid black;
  padding: 5px;
  background-color: white;
  opacity: 0.8;
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
