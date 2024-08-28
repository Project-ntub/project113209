<template>
  <div class="chart-modal-container">
    <div class="chart-modal">
      <div class="chart-modal-header">
        <h2>{{ isEditing ? '編輯圖表' : '新增圖表' }}</h2>
        <button @click="closeModal" class="close-btn">×</button>
      </div>
      <div class="chart-modal-body">
        <div class="chart-settings">
          <!-- 圖表類型 -->
          <div class="setting">
            <label for="chart-style">圖表類型</label>
            <select id="chart-style" v-model="chartData.style">
              <option value="bar">柱狀圖</option>
              <option value="line">折線圖</option>
              <option value="pie">圓餅圖</option>
              <option value="radar">雷達圖</option>
              <option value="scatter">散點圖</option>
              <!-- 加入更多圖表類型 -->
            </select>
          </div>
          <!-- 圖表名稱輸入 -->
          <div class="setting">
            <label for="chart-name">圖表名稱</label>
            <input id="chart-name" v-model="chartData.name" type="text" placeholder="輸入圖表名稱" />
          </div>
          <!-- 顯示數據標籤切換 -->
          <div class="setting">
            <label for="show-labels">顯示數據標籤</label>
            <input id="show-labels" type="checkbox" v-model="chartData.showLabels" />
          </div>
          <!-- 圖表顏色 -->
          <div class="setting">
            <label for="chart-color">圖表顏色</label>
            <input id="chart-color" type="color" v-model="chartData.color" />
          </div>
          <!-- X軸標籤 -->
          <div class="setting">
            <label for="x-axis-label">X軸標籤</label>
            <input id="x-axis-label" v-model="chartData.xAxisLabel" type="text" placeholder="輸入X軸標籤" />
          </div>
          <!-- Y軸標籤 -->
          <div class="setting">
            <label for="y-axis-label">Y軸標籤</label>
            <input id="y-axis-label" v-model="chartData.yAxisLabel" type="text" placeholder="輸入Y軸標籤" />
          </div>
          <!-- 更多設定 -->
        </div>
        <!-- 圖表預覽 -->
        <div class="chart-preview">
          <h3>預覽</h3>
          <div id="chart-container">
            <!-- 在這裡整合你的圖表庫 -->
          </div>
        </div>
      </div>
      <div class="chart-modal-footer">
        <button class="btn-save" @click="saveChart">{{ isEditing ? '保存變更' : '新增圖表' }}</button>
        <button class="btn-cancel" @click="closeModal">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    isEditing: Boolean,
  },
  data() {
    return {
      chartData: {
        style: 'bar',
        name: '',
        showLabels: true,
        color: '#007BFF',
        xAxisLabel: '',
        yAxisLabel: '',
        // 其他圖表設定
      },
    };
  },
  methods: {
    saveChart() {
      if (this.isEditing) {
        // 編輯圖表的邏輯
        console.log('保存圖表變更');
      } else {
        // 新增圖表的邏輯
        console.log('新增新圖表');
      }
      this.closeModal();
    },
    closeModal() {
      this.$emit('close');
    },
  },
};
</script>

<style scoped>
.chart-modal-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}
.chart-modal {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  width: 80%;
  max-width: 600px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.chart-modal-header,
.chart-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chart-modal-body {
  display: flex;
  gap: 20px;
}
.chart-settings,
.chart-preview {
  flex: 1;
}
.setting {
  margin-bottom: 15px;
}
.btn-save,
.btn-cancel {
  background-color: #007BFF;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
</style>
