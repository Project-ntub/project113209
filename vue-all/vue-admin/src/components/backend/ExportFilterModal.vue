<!-- src\components\backend\ExportFilterModal.vue -->
<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <h3>匯出篩選條件</h3>
      <form @submit.prevent="submitFilters">
        <!-- 日期範圍選擇 -->
        <div class="form-group">
          <label for="startDate">開始日期：</label>
          <input type="date" v-model="filters.startDate" id="startDate">
        </div>
        <div class="form-group">
          <label for="endDate">結束日期：</label>
          <input type="date" v-model="filters.endDate" id="endDate">
        </div>

        <!-- 商品名稱篩選 -->
        <div class="form-group">
          <label for="productName">商品名稱包含：</label>
          <select v-model="filters.productName" id="productName">
            <option value="">--請選擇商品--</option>
            <option v-for="p in allProductNames" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>

        <!-- 店名篩選 -->
        <div class="form-group">
          <label for="storeName">店名包含：</label>
          <select v-model="filters.storeName" id="storeName">
            <option value="">--請選擇店名--</option>
            <option v-for="s in allStoreNames" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>

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
import axios from 'axios';


export default {
props: {
  chartConfig: Object
},
data() {
  return {
    filters: {
      startDate: '',
      endDate: '',
      productName: '',
      storeName: '',
      // 可再擴充更多條件
    },
    allProductNames: [],
    allStoreNames:[]
  };
},
async mounted() {
  try {
    const productRes = await axios.get('/api/backend/get-product-names/');
    this.allProductNames = productRes.data || [];
      
    const storeRes = await axios.get('/api/backend/get-store-names/');
    this.allStoreNames = storeRes.data || [];
  } catch (error) {
    console.error('取得清單失敗:', error);
  }
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
  