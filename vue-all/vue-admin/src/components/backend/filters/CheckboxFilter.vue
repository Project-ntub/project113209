<!-- src/components/backend/filters/CheckboxFilter.vue -->
<template>
    <div class="checkbox-filter">
      <div v-for="option in options" :key="option.value">
        <input
          type="checkbox"
          :id="'filter-' + filter.name + '-' + option.value"
          :value="option.value"
          v-model="internalValue"
        />
        <label :for="'filter-' + filter.name + '-' + option.value">{{ option.label }}</label>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { ref, computed } from 'vue';
  
  export default {
    name: 'CheckboxFilter',
    props: {
      filter: {
        type: Object,
        required: true
      },
      modelValue: {
        type: Array,
        default: () => []
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
  .checkbox-filter {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  </style>
  