<!-- src/Charts/ChartContainer.vue -->
<template>
  <div>
    <div class="chart-container">
      <div class="chart-header">
        <div class="menu-button">
          <button class="menu-icon" @click="toggleMenu">⋮</button>
          <div v-if="showMenu" class="menu">
            <template v-if="!isFrontend">
              <button @click="editChart">編輯圖表</button>
            </template>
            <button @click="exportChart('csv')">匯出為 CSV</button>
            <button @click="exportChart('excel')">匯出為 Excel</button>
            <button @click="exportChart('pdf')">匯出為 PDF</button>
          </div>
        </div>
      </div>
      <slot></slot>
    </div>
    <ChartModal v-if="!isFrontend && isChartModalVisible" :isEditing="true" @close="isChartModalVisible = false" />
  </div>
</template>

<script>
import axios from 'axios';
import ChartModal from '@/components/backend/ChartModal.vue';

export default {
  components: {
    ChartModal
  },
  props: {
    chartConfig: Object,
    isFrontend: Boolean
  },
  data() {
    return {
      showMenu: false,
      isChartModalVisible: false
    };
  },
  methods: {
    toggleMenu() {
      this.showMenu = !this.showMenu;
    },
    editChart() {
      this.isChartModalVisible = true;
      this.showMenu = false;
    },
    async exportChart(format) {
      const apiUrl = `/api/backend/export-data-${format}/`;

      if (!this.chartConfig || !this.chartConfig.data || this.chartConfig.data.length === 0) {
        alert("圖表配置無效，無法導出！");
        return;
      }

      try {
        const response = await axios.post(apiUrl, { chartConfig: this.chartConfig }, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `exported-file.${format}`);
        document.body.appendChild(link);
        link.click();
      } catch (error) {
        console.error('匯出數據時出錯:', error);
        alert('匯出失敗，請檢查數據並重試。');
      }
    }
  }
};
</script>

<style scoped>
.chart-container {
  position: relative;
  padding: 10px;
  border-radius: 10px;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
.chart-header {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 10;
}
.menu-button {
  position: relative;
  z-index: 11;
}
.menu-icon {
  background: rgba(255, 255, 255, 0.8);
  border: none;
  color: black;
  padding: 8px;
  font-size: 20px;
  cursor: pointer;
  border-radius: 50%;
}
.menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #3498db;
  border: 1px solid #2980b9;
  border-radius: 5px;
  width: 150px;
  z-index: 12;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
.menu button {
  display: block;
  width: 100%;
  padding: 8px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  color: white;
}
.menu button:hover {
  background-color: #2980b9;
}
</style>
