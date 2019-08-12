/* eslint-disable */

<template>
<div class="child-component">
  <div class="bravo-tooltip">
    <div v-html="tooltipHtml"></div>
  </div>
  <button class="close-button" v-on:click="$emit('close')">
    <font-awesome-icon style="background-color: transparent;" :icon="closeIcon"></font-awesome-icon>
  </button>
  <p v-if="loading" class="bravo-message">Loading variants</p>
  <p v-else-if="empty" class="bravo-message">No variants in this region</p>
</div>
</template>

<script>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import * as d3 from "d3";

export default {
  name: "sv",
  props: {
    chrom: {
      type: String,
      required: true
    },
    start: {
      type: Number,
      required: true
    },
    stop:{
      type: Number,
      required: true
    },
    width: {
      type: Number,
      required: true
    },
    getData: {
      type: Function,
      required: true
    }
  },
  components: {
    FontAwesomeIcon,
  },
  data: function() {
    return {
      loading: false,
      empty: true,
      tooltipHtml: "",
      closeIcon: faTimes
    }
  },
  methods: {
    setData: function(data, append) {
      this.loading = true;
      this.empty = false;
      new Promise( resolve => resolve() )
      .then( () => {
        if (!append) {
          this.erase()
        }
        if (data.length > 0) {
          this.variants = this.variants.concat(data); // concat should be the fastest, although new array is created
          // this.variants.push(...data);
          this.initializeVariantsSVG();
          this.draw();
          this.loading = false;
          this.empty = false;
        } else {
          this.loading = false;
          this.empty = true;
        }
      });
    },
    scrolled: function(event) {
      var scrollDiv = event.target;
      var scrollDivPosition = scrollDiv.scrollTop - 12; // account for g element translated by 12 px;
      var scrollDivHeight = scrollDiv.clientHeight;
      var top_visible_variant = 0;
      if (scrollDivPosition > 0) {
        top_visible_variant = Math.floor(scrollDivPosition / this.variantLineHeight); // for sure are out of view;
        if (scrollDivPosition - (top_visible_variant * this.variantLineHeight) >= this.variantRectHeight) { // here we check if variant rectangle is completely out of view.
          top_visible_variant += 1;
        }
      }
      scrollDivPosition += scrollDivHeight;
      var bottom_visible_variant = Math.floor(scrollDivPosition / this.variantLineHeight);
      if (scrollDivPosition - (bottom_visible_variant * this.variantLineHeight) <= this.variantRectHeight) { // here we check if variant rectangle is completely out of view.
        bottom_visible_variant -= 1;
      }
      this.$emit("scroll", top_visible_variant, bottom_visible_variant);
    },
    scrollTo: function(top_variant, bottom_variant) {
      var scrollDiv = this.$el.querySelector("#scroll");
      scrollDiv.removeEventListener("scroll", this.scrolled); // temporarly remove our own scroll event listener to avoid event loops.
      scrollDiv.addEventListener("scroll", () => {
        scrollDiv.addEventListener("scroll", this.scrolled);
      });
      scrollDiv.scrollTop = top_variant * this.variantLineHeight;
    },
    hover: function(variant, hovered) {
      var rects = this.drawing.selectAll("rect");
      rects.style("fill", (d, i) => {
        if (i == variant ) {
          return hovered ? this.color.Hovered : this.color[d.type];
        }
        return this.color[d.type];
      });
    },
    erase: function() {
      this.variants = [];
      var div_scroll = this.$el.querySelector("#scroll");
      div_scroll.removeEventListener("scroll", this.scrolled); // temporarly remove our own scroll event listener to avoid event loops.
      div_scroll.addEventListener("scroll", () => {
        div_scroll.addEventListener("scroll", this.scrolled);
      });
      div_scroll.scrollTop = 0;
      d3.select(div_scroll).style("display", "none");
      this.drawing.selectAll("rect").remove();
    },
    initializeSVG: function () {
      this.svg = d3.select(this.$el)
        .append("div")
          .attr("id", "scroll")
          .style("max-height", `${this.height}px`)
          .style("display", "none")
          .style("overflow-y", "scroll")
          .style("overflow-x", "hidden")
        .append("svg")
          .style("display", "block");
      this.drawing_clip = this.svg
        .append("clipPath")
          .attr("id", "sv-clip")
        .append("rect")
          .attr("x", 0)
          .attr("y", 0);
      this.drawing = this.svg.append("g");
      this.x_scale = d3.scaleLinear();
    },
    initializeVariantsSVG: function () {
      var rects = this.drawing.selectAll("rect")
        .data(this.variants)
        .enter()
        .append("rect")
          .style("stroke-width", 0.2)
          .style("stroke", "black")
          .style("rx", 3)
          .style("ry", 3)
          .attr("rx", 3) // for firefox & safari
          .attr("ry", 3) // for firefox & safari
          .style("fill", d => this.color[d.type]);
      var self = this;
      rects.on('mouseover', function(d, i) {
        d3.select(this).style("fill", self.color.Hovered);
        var s = d.pos < self.start ? self.start : d.pos;
        var e = d.stop > self.stop ? self.stop : d.stop;
        var x_mid = self.x_scale(s + (e - s) / 2.0) + self.margin.left ;
        var y_mid = this.getAttribute("y") - // get Y coordinate of the rectangle (its linear 1-to-1 mapping to pixel)
          self.$el.querySelector("#scroll").scrollTop - // substruct scroll position of the parent div
          self.margin.top - // substruct drawing area margin
          7;
        d3.select(self.$el.querySelector(".bravo-tooltip"))
          .style("display", "block")
          .style("left", x_mid + "px")
          .style("top", y_mid + "px");
        self.tooltipHtml = `<ul><li>${d.variant_id}</li><li>${d.type}</li><li>${d.chrom}:${d.pos.toLocaleString()}-${d.stop.toLocaleString()}</li><ul>`;
        self.$emit("hover", i, true);
      });
      rects.on('mouseout', function(d, i) {
        d3.select(self.$el.querySelector(".bravo-tooltip"))
          .style("display", "none");
        self.tooltipHtml = "";
        d3.select(this).style("fill", d => self.color[d.type] );
        self.$emit("hover", i, false);
      });
    },
    draw: function () {
      d3.select(this.$el.querySelector("#scroll")).style("display", "block");
      this.svg
        .attr("width", this.width)
        .attr("height", this.variantLineHeight * this.variants.length);
      this.drawing
        .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`);
      this.drawing_clip
        .attr("width", this.width - this.margin.left - this.margin.right)
        .attr("height", this.variantLineHeight * this.variants.length);
      this.x_scale.range([0, this.width - this.margin.left - this.margin.right]).domain([ this.start,  this.stop]);
      this.drawing.selectAll("rect")
        .attr("clip-path", "url(#sv-clip)")
        .attr("x", d => this.x_scale(d.pos))
        .attr("width", d => this.x_scale(d.stop + 1) - this.x_scale(d.pos))
        .attr("y", (d, i) => i * this.variantLineHeight)
        .attr("height", this.variantRectHeight);
    }
  },
  beforeCreate() {
    // initialize non reactive data
    this.variants = [];
    this.height = 200;
    this.margin = {
      left: 25,
      right: 25,
      top: 12,
      bottom: 18
    };
    this.color = {
      Hovered: "orange",
      Deletion: "#a6cee3",
      Inversion: "#1f78b4",
      Duplication: "#b2df8a"
    };
    this.svg = null;
    this.drawing = null;
    this.drawing_clip = null;
    this.x_scale = null;
    this.variantRectHeight = 6; // height of the rectangle which represents variant
    this.variantLineHeight = 9; // how much each variant occupies. this includes veriant rectangle height and margins
    this.tip = null;
  },
  created: function() {
  },
  mounted: function() {
    this.initializeSVG();
    this.$el.querySelector("#scroll").addEventListener("scroll", this.scrolled);
    this.setData(this.getData()); // TODO:here we will need to load not only data from table, but also the scroll state!
  },
  beforeDestroy: function() {
  },
  watch: {
    width: function(newValue, oldValue) {
      if ((!this.loading) && (this.variants.length > 0)) {
        this.draw();
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
  padding: 0px 2px 0px 2px;
  color: black;
  font-size: 11px;
  outline: none;
  background-color: #eeeeee;
  border: 1px solid #cccccc;
  border-radius: 5px;
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
