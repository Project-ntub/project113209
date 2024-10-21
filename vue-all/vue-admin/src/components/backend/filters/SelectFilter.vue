<!-- src/components/backend/filters/SelectFilter.vue -->
<template>
    <select
      :id="'filter-' + filter.name"
      v-model="internalValue"
    >
      <option value="">所有</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </template>
  
  <script>
  import axios from 'axios';
  import { ref, computed } from 'vue';
  
  export default {
    name: 'SelectFilter',
    props: {
      filter: {
        type: Object,
        required: true
      },
      modelValue: {
        type: [String, Array],
        default: ''
      }
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const options = ref([]);
      const internalValue = computed({
        get: () => props.modelValue,
        set: (val) => emit('update:modelValue', val)
      });
  
      // 獲取選項
      if (props.filter.related_model) {
        axios.get(`/api/backend/get-options/${props.filter.related_model}/`)
          .then(response => {
            options.value = response.data.options;
          })
          .catch(error => {
            console.error(`獲取 ${props.filter.related_model} 選項時出錯:`, error);
          });
      } else if (props.filter.choices) {
        options.value = props.filter.choices.map(choice => ({
          value: choice[0],
          label: choice[1]
        }));
      }
  
      return { options, internalValue };
    }
  };
  </script>
  
  <style scoped>
  /* 您可以根據需要添加樣式 */
  </style>
  