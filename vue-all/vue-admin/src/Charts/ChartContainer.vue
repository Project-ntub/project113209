<template>
    <div>
      <div class="chart-container">
        <div class="chart-header">
          <div class="menu-button">
            <button class="menu-icon" @click="toggleMenu">⋮</button>
            <div v-if="showMenu" class="menu">
              <!-- 如果不是前台模式，則顯示編輯功能 -->
              <template v-if="!isFrontend">
                <button @click="editChart">編輯圖表</button>
                <button @click="openPermissionModal">編輯權限</button>
              </template>
              <!-- 匯出功能無論前台還是後台都顯示 -->
              <button @click="exportChart('csv')">匯出為 CSV</button>
              <button @click="exportChart('excel')">匯出為 Excel</button>
              <button @click="exportChart('pdf')">匯出為 PDF</button>
            </div>
          </div>
        </div>
        <slot></slot>
      </div>

      <!-- 只有後台才顯示編輯模態窗口 -->
      <PermissionModal v-if="!isFrontend && isPermissionModalVisible" @close="isPermissionModalVisible = false" />
      <ChartModal v-if="!isFrontend && isChartModalVisible" :isEditing="true" @close="isChartModalVisible = false" />
    </div>
</template>

<script>
import axios from 'axios';
import PermissionModal from '@/components/backend/PermissionModal.vue';
import ChartModal from '@/components/backend/ChartModal.vue';

export default {
  components: {
    PermissionModal,
    ChartModal
  },
  props: {
    chartConfig: Object,
    isFrontend: Boolean // 接收從外部傳入的是否為前台的判斷
  },
  data() {
    return {
      showMenu: false,
      isPermissionModalVisible: false,
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
    openPermissionModal() {
      this.isPermissionModalVisible = true;
      this.showMenu = false;
    },
    async exportChart(format) {
      let apiUrl = '';
      if (format === 'csv') {
        apiUrl = '/api/backend/export-data-csv/';
      } else if (format === 'excel') {
        apiUrl = '/api/backend/export-data-excel/';
      } else if (format === 'pdf') {
        apiUrl = '/api/backend/export-data-pdf/';
      }

      // 確保 chartConfig 包含所需數據
      console.log("chartConfig in ChartContainer.vue: ", this.chartConfig);
       // 打印 chartConfig 以確認其內容

      if (!this.chartConfig || !this.chartConfig.data || this.chartConfig.data.length === 0) {
        alert("圖表配置無效，無法導出！");
        return;
      }

      try {
        console.log("API URL: ", apiUrl);
        console.log("Data being sent: ", this.chartConfig);  // 確認即將發送的數據

        const response = await axios.post(apiUrl, { chartConfig: this.chartConfig }, {
          responseType: 'blob'
        });

        console.log("Response received: ", response);
      } catch (error) {
        console.error('Error exporting data:', error);
        alert('匯出失敗，請檢查數據並重試。');
      }
    },
    onResize() {
      // 處理圖表大小調整
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
