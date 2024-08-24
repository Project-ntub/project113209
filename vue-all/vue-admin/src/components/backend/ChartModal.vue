<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>新增圖表</h3>
        <button class="close-button" @click="close">×</button>
      </div>
      <div class="modal-body">
        <!-- 選擇圖表類型 -->
        <div class="form-group">
          <label for="chart-type">圖表類型:</label>
          <select v-model="chartData.chartType" id="chart-type" class="form-control">
            <option value="bar">柱狀圖</option>
            <option value="line">折線圖</option>
            <option value="pie">圓餅圖</option>
          </select>
        </div>

        <!-- 輸入圖表名稱 -->
        <div class="form-group">
          <label for="chart-name">圖表名稱:</label>
          <input v-model="chartData.chartName" id="chart-name" type="text" class="form-control" />
        </div>

        <!-- 配置圖表數據 -->
        <div class="form-group">
          <label for="chart-data">圖表數據:</label>
          <textarea v-model="chartData.chartData" id="chart-data" class="form-control" placeholder="請輸入圖表數據（例如：{'x': [1,2,3], 'y': [4,5,6]}）"></textarea>
        </div>

        <!-- 預覽圖表 -->
        <div class="form-group">
          <label for="chart-preview">圖表預覽:</label>
          <div id="chart-preview">
            <!-- 這裡可以集成一個圖表庫來顯示預覽，例如 ECharts 或 Chart.js -->
            <p>預覽將顯示在這裡（請集成圖表庫來顯示）</p>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary" @click="saveChart">保存</button>
        <button class="btn btn-secondary" @click="close">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChartModal',
  data() {
    return {
      chartData: {
        chartType: 'bar', // 默認為柱狀圖
        chartName: '',
        chartData: '',
      },
    };
  },
  methods: {
    close() {
      this.$emit('close');
    },
    saveChart() {
      // 這裡你可以添加保存圖表的邏輯，例如發送請求到後端
      console.log('保存圖表資料:', this.chartData);
      // 發送資料給父組件或者 API
      this.$emit('save', this.chartData);
      // 關閉模態框
      this.close();
    },
  },
};
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
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
    max-width: 90%;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
  }
  
  .modal-body {
    padding: 10px 0;
  }
  
  .modal-footer {
    padding-top: 10px;
    text-align: right;
    border-top: 1px solid #eee;
  }
  
  .close-button {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
  }
</style>
