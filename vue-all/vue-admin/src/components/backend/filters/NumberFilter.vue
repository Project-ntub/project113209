<!-- src/components/backend/filters/NumberFilter.vue -->
<template>
    <div class="number-filter">
      <input
        type="number"
        v-model.number="min"
        @input="update"
        placeholder="最小值"
      />
      <input
        type="number"
        v-model.number="max"
        @input="update"
        placeholder="最大值"
      />
    </div>
  </template>
  
  <script>
  export default {
    props: {
      filter: Object,
      value: Object // { min: Number, max: Number }
    },
    data() {
      return {
        min: this.value?.min || '',
        max: this.value?.max || ''
      };
    },
    methods: {
      update() {
        this.$emit('update', { min: this.min, max: this.max });
      }
    }
  };
  </script>
  
  <style scoped>
  .number-filter {
    display: flex;
    gap: 5px;
  }
  </style>
  