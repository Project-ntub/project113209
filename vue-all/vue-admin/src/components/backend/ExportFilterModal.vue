<!-- ExportFilterModal.vue -->
<template>
    <div class="modal-overlay">
      <div class="modal-content">
        <h3>匯出篩選條件</h3>
        <form @submit.prevent="submitFilters">
          <!-- 例如：日期範圍選擇 -->
          <div class="form-group">
            <label for="startDate">開始日期：</label>
            <input type="date" v-model="filters.startDate" id="startDate">
          </div>
          <div class="form-group">
            <label for="endDate">結束日期：</label>
            <input type="date" v-model="filters.endDate" id="endDate">
          </div>
          <!-- 可以根據需要添加更多篩選條件 -->
          <!-- ... -->
  
          <div class="modal-buttons">
            <button type="button" @click="$emit('close')">取消</button>
            <button type="submit">匯出</button>
          </div>
        </form>
        <button class="close-modal-btn" @click="$emit('close')">×</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      chartConfig: Object
    },
    data() {
      return {
        filters: {
          startDate: '',
          endDate: '',
          // 可以添加更多的篩選條件
        }
      };
    },
    methods: {
      submitFilters() {
        // 將篩選條件傳遞給父組件
        this.$emit('export', this.filters);
      }
    }
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  .modal-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 400px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
  }
  .close-modal-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
  }
  .form-group {
    margin-bottom: 15px;
  }
  .modal-buttons {
    display: flex;
    justify-content: flex-end;
  }
  .modal-buttons button {
    margin-left: 10px;
  }
  </style>
  