<!-- src/components/backend/filters/DateFilter.vue -->
<template>
    <div class="date-filter">
      <input
        type="date"
        v-model="startDate"
        @change="update"
        placeholder="開始日期"
      />
      <input
        type="date"
        v-model="endDate"
        @change="update"
        placeholder="結束日期"
      />
    </div>
  </template>
  
  <script>
  export default {
    props: {
      filter: Object,
      value: Object // { start: String, end: String }
    },
    data() {
      return {
        startDate: this.value?.start || '',
        endDate: this.value?.end || ''
      };
    },
    methods: {
      update() {
        this.$emit('update', { start: this.startDate, end: this.endDate });
      }
    }
  };
  </script>
  
  <style scoped>
  .date-filter {
    display: flex;
    gap: 5px;
  }
  </style>
  