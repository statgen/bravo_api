<template>
  <div class="token-main-div" v-bind:class="{ 'token-main-div-freeze': isReady }">
    <input class="token-input" v-bind:class="{ 'token-input-freeze': isReady }" placeholder="Add filter" autocomplete="off" />
    <button type="button" class="token-close-button" v-bind:class="{ 'close-button-show': isReady }" v-on:click="tokenclose">
      <font-awesome-icon style="background-color: transparent;" :icon="closeIcon"></font-awesome-icon>
    </button>
  </div>
</template>

<script>
import $ from 'jquery';
import _ from 'devbridge-autocomplete';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTimesCircle } from '@fortawesome/free-regular-svg-icons';

export default {
  name: 'Token',
  components: {
    FontAwesomeIcon
  },
  props: {
    'suggestions': {
      type: Object
    },
    'id': {
      type: Number
    },
    'filter': {
      type: Object
    }
  },
  data: function() {
    return {
      tokenFilter: this.filter != null ? JSON.parse(JSON.stringify(this.filter)) : null,
      closeIcon: faTimesCircle,
      isReady: false
    }
  },
  methods: {
    tokenclose: function(event) {
      this.isReady = false;
      this.$emit('tokenclose', this.id);
    },
    initialize: function() {
      if (this.tokenFilter == null) {
        return;
      }
      var input = this.$el.querySelector('input');
      input.value = `${this.tokenFilter.title}:${this.tokenFilter.text}`;
      this.freeze();
    },
    freeze: function() {
      var input = this.$el.querySelector('input');
      input.readOnly = true;
      this.isReady = true;
      // compute exact text width in pixels
      var textwidth = document.getElementById("textwidth");
      if (textwidth === null) {
        textwidth = document.createElement("div");
        textwidth.setAttribute("id", "textwidth");
        this.$el.appendChild(textwidth);
      }
      textwidth.style.fontFamily = $(input).css("font-family");
      textwidth.style.fontSize = $(input).css("font-size");
      textwidth.style.fontStyle = $(input).css("font-style");
      textwidth.style.fontWeight = 700; // corresponds to bold;
      textwidth.innerHTML = input.value;
      $(input).attr('size', input.value.length);
      $(input).css('width', textwidth.clientWidth + 2); // +2 just to avoid making it super tight
    },
    hasFilter: function() {
      return this.isReady;
    },
    getFilter: function() {
      return this.tokenFilter != null ? this.tokenFilter.tabulator_filter : null;
    }
  },
  mounted: function() {
    var self = this;
    var input_el = this.$el.querySelector('input');

    $(input_el).autocomplete({
      minChars: 0,
      delimiter: ':',
      width: 'flex',
      groupBy: 'category',
      lookup: function(query, done) {
        var input = input_el.value.split(':');
        var result = {suggestions: []};
        if (input.length == 1) {
          Object.keys(self.suggestions).forEach(function(key) {
            if (key.startsWith(query)) {
              result.suggestions.push(self.suggestions[key]);
            }
          });
        } else {
          var suggestions = self.suggestions[input[0]].data.items;
          Object.keys(suggestions).forEach(function(key) {
            if (key.startsWith(query)) {
              result.suggestions.push(suggestions[key]);
            }
          });
        }
        done(result);
      },
      onSelect: function(suggestion) {
        var input = this.value.split(':');
        if (self.isReady) { // is already tokenized. don't handle any events other than close button.
          return;
        }
        if (input.length == 1) {
          this.value += ':';
          this.dispatchEvent(new Event("input"));
        } else {
          if (suggestion.data.category == 'By Group') {
            var filters = [];
            suggestion.data.filters.forEach(f => {
              filters.push(f);
            });
            self.$emit('tokenexpand', filters);
          } else {
            self.tokenFilter = {
              title: input[0],
              text: input[1],
              tabulator_filter: suggestion.data.tabulator_filter
            };
            self.freeze();
            self.$emit('tokenready');
          }
        }
      },
      appendTo: this.$el
    });
    this.initialize();
  },
  beforeDestroy: function() {
    var input_el = this.$el.querySelector('input');
    $(input_el).off('focus');
    $(input_el).off('focusout');
    $(input_el).autocomplete().hide();
    $(input_el).autocomplete().dispose();
    this.isReady = false;
  }
}
</script>

<style scoped>
.token-main-div {
   position: relative;
   flex-grow: 1;
   white-space: nowrap;
   padding: 0px;
   margin: 1px;
   border: 1px solid white;
}
.token-main-div-freeze {
  flex-grow: 0;
  border: 1px solid #85afd0;
  border-radius: 0.5rem 0.5rem 0.5rem 0.5rem;
  background-color: #dae7f1;
}
.token-input {
  display: inline-block;
  width: 100%;
  min-width: auto;
  background-color: transparent;
  border: none;
  box-shadow: none;
  outline: none;
}
.token-input:focus {
  border: none;
  box-shadow: none;
  outline: none;
}
.token-input-freeze {
  width: auto;
  min-width: auto;
  color: #2d5f8f;
  font-weight: bold;
}
.token-close-button {
  display: none;
  padding: 0px 2px 0px 2px;
  margin: 0px;
  background-color: transparent;
  color: #2d5f8f;
  border: none;
  outline: none;
  cursor: pointer;
}
.token-close-button:focus {
   border: none;
   box-shadow: none;
   outline: none;
}
.close-button-show {
  display: inline-block;
}
.token-main-div >>> .autocomplete-suggestions {
  background-color: white;
  border: 1px solid #ced4da;
  overflow: auto;
}
.token-main-div >>> .autocomplete-suggestion {
  padding: 2px 5px;
  white-space: nowrap;
  overflow: hidden;
}
.token-main-div >>> .autocomplete-selected {
  background: #dae7f1;
}
.token-main-div >>> .autocomplete-suggestions strong {
  font-weight: normal; color: #3399FF;
}
.token-main-div >>> .autocomplete-group {
  font-size: 0.8rem;
  font-style: normal;
  color: darkmagenta;
  padding: 2px 2px;
}
.token-main-div >>> #textwidth {
  position: absolute;
  visibility: hidden;
  height: auto;
  width: auto;
  white-space: nowrap;
  margin: 0px;
  padding: 0px;
  border: 0px;
}
</style>
