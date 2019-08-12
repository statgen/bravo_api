<template>
  <input class="search-box-input" name="value" type="text" autocomplete="off" placeholder="Search for gene or region" v-bind:autofocus="autofocus"/>
</template>

<script>
import $ from "jquery";
import _ from 'devbridge-autocomplete';

export default {
  name: 'autocomplete',
  props: ['autocompleteapi', 'searchapi', 'width', 'autofocus'],
  data: function() {
    return {
      ready: false
    };
  },
  methods: {
    isEmpty: function() {
      return (this.$el.value.trim() == "");
    }
  },
  mounted: function() {
    var self = this;
    $(this.$el).focus(function() {
      self.$emit('inputfocus');
    });
    $(this.$el).focusout(function() {
      self.$emit('inputfocusout');
    });
    $(this.$el).autocomplete({
      serviceUrl: self.autocompleteapi,
      dataType: "json",
      width: this.width,
      maxHeight: 250,
      appendTo: this.$parent.$el,
      triggerSelectOnValidInput: false,
      formatResult: function(suggestion, currentValue) {
          var value = "<div class='autocomplete-suggestion-item'>";
          value += "<div>" + $.Autocomplete.defaults.formatResult(suggestion, currentValue) + "</div>"
          value += "<div style='font-size: 0.75em; color: #85144b'>" + suggestion.data.type + "</div>"
          var chrom = suggestion.data.chrom;
          if (chrom.substring(0, 3) != "chr") {
            chrom = "chr" + chrom;
          }
          value += "<div style='font-size: 0.75em;'>" + chrom +
          ":" + parseInt(suggestion.data.start).toLocaleString() +
          "-" + parseInt(suggestion.data.stop).toLocaleString() + "</div>"
          value += "</div>"
          return value;
      },
      beforeRender: function(container, suggestions) {
      },
      onSearchComplete: function(query, suggestions) {
        if (suggestions.length > 0) {
          self.$emit('dropdownopen');
        }
      },
      onHide: function() {
        self.$emit('dropdownclose');
      },
      onSelect: function (suggestion) {
        window.location.assign(self.searchapi + "?value=" + suggestion.value + "&chrom=" + suggestion.data.chrom + "&start=" + suggestion.data.start + "&stop=" + suggestion.data.stop);
      }
    });
    this.ready = true;
  },
  beforeDestroy: function() {
    $(this.$el).off("focus");
    $(this.$el).off("focusout");
    $(this.$el).autocomplete().hide();
    $(this.$el).autocomplete().dispose();
    this.ready = false;
  },
  watch: {
    width: function(newValue, oldValue) {
      if (this.ready) {
        $(this.$el).autocomplete().setOptions({
          width: this.width
        });
      }
    }
  }
}
</script>

<style scoped>
.search-box-input {
   flex-grow: 1;
   min-width: 16px;
   margin-left: 8px;
   font-size: 16px;
   border: none;
   outline: none;
}
.search-box-input:focus {
   border: none;
   box-shadow: none;
   outline: none;
}
</style>
