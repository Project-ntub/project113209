<!-- src/components/backend/filters/TextFilter.vue -->
<template>
    <input
      :id="'filter-' + filter.name"
      type="text"
      v-model="internalValue"
      :placeholder="'輸入 ' + (filter.verbose_name || filter.name)"
    />
  </template>
  
  <script>
  import { computed } from 'vue';
  
  export default {
    name: 'TextFilter',
    props: {
      filter: {
        type: Object,
        required: true
      },
      modelValue: {
        type: String,
        default: ''
      }
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const internalValue = computed({
        get: () => props.modelValue,
        set: (val) => emit('update:modelValue', val)
      });
  
      return { internalValue };
    }
  };
  </script>
  
  <style scoped>
  /* 您可以根據需要添加樣式 */
  </style>
  