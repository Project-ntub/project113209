<template>
  <div>
    <div class="chart-container">
      <div class="chart-header">
        <div class="menu-button">
          <button class="menu-icon" @click="toggleMenu">⋮</button>
          <div v-if="showMenu" class="menu">
            <template v-if="!isFrontend">
              <button @click="editChart">編輯圖表</button>
              <button @click="deleteChart">刪除圖表</button> <!-- v-if="localCanDelete" -->
            </template>
            <div class="export-button"> <!-- v-if="localCanExport" -->
              <button @click="exportChart('csv')">匯出為 CSV</button>
              <button @click="exportChart('excel')">匯出為 Excel</button>
              <button @click="exportChart('pdf')">匯出為 PDF</button>
            </div>
          </div>
        </div>
      </div>
      <PlotlyChart :chartConfig="localChartConfig" @update-chart-config="updateChartConfig"></PlotlyChart>
    </div>
    <ChartModal v-if="!isFrontend && isChartModalVisible" :isEditing="true" @close="isChartModalVisible = false" />
  </div>
</template>

<script>
import axios from 'axios';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartModal from '@/components/backend/ChartModal.vue';

export default {
  components: {
    PlotlyChart,
    ChartModal
  },
  props: {
    chartConfig: Object,
    isFrontend: Boolean,
    canExport: Boolean,
    canDelete: Boolean // 接收刪除權限
  },
  data() {
    return {
      showMenu: false,
      isChartModalVisible: false,
      localChartConfig: { ...this.chartConfig }, // 使用本地副本
      localCanExport: false,
      localCanDelete: false, // 本地刪除權限
      chartPermissions: {} // 用來存放每個圖表的權限信息
    };
  },
  mounted() {
    this.localCanExport = this.canExport; // 初始化本地匯出權限
    this.localCanDelete = this.canDelete; // 初始化本地刪除權限
    if (!this.localChartConfig || !this.localChartConfig.data) {
      console.error("localChartConfig 或 data 未定義");
      return;
    }
    this.fetchUserPermissions(); // 確保加載權限
  },
  methods: {
    toggleMenu() {
      this.showMenu = !this.showMenu;
    },
    editChart() {
      this.isChartModalVisible = true;
      this.showMenu = false;
    },
    async deleteChart() {
      console.log('Chart ID:', this.localChartConfig.id); // Add this to check chart ID
      const confirmation = confirm('確定要隱藏此圖表嗎？');
      if (confirmation) {
        try {
          if (!this.localChartConfig.id) {
            alert('圖表ID無效，無法刪除');
            return;
          }
          const response = await axios.post(`/api/backend/delete-chart/${this.localChartConfig.id}/`);
          alert(response.data.message || '圖表已被隱藏');
          this.$emit('reload-charts');
        } catch (error) {
          console.error('隱藏圖表時出錯:', error);
          alert('隱藏失敗，請稍後再試。');
        }
      }
    },
    updateChartConfig(updatedConfig) {
      this.localChartConfig = updatedConfig; // 更新本地變量
      console.log('Updated chartConfig:', this.localChartConfig);
    },
   fetchUserPermissions() {
    axios.get('/api/backend/permissions/')
      .then(response => {
        const permissions = response.data;
        this.localCanExport = permissions.some(perm => perm.permission_name === this.localChartConfig.name && perm.can_export);
        this.localCanDelete = permissions.some(perm => perm.permission_name === '圖表管理' && perm.can_delete); // 假設這是刪除權限的名字

        console.log("Permissions:", permissions); // 確認返回的權限
        console.log("Local Can Export:", this.localCanExport); // 檢查匯出權限
        console.log("Local Can Delete:", this.localCanDelete); // 檢查刪除權限
      })
      .catch(error => {
        console.error('無法獲取權限:', error);
      });
  },
    async exportChart(format) {
      const apiUrl = `/api/backend/export-data-${format}/`; // 確保這裡的API路徑正確

      // 確認 localChartConfig.data 是否存在並包含數據
      if (!this.localChartConfig || !this.localChartConfig.data || this.localChartConfig.data.length === 0) {
        alert("圖表配置無效，無法導出！");
        return;
      }

      try {
        const response = await axios.post(apiUrl, { chartConfig: this.localChartConfig }, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');

        // 以圖表名稱為基礎生成檔案名
        const fileName = `${this.localChartConfig.label || 'exported-file'}.${format}`;
        link.href = url;
        link.setAttribute('download', fileName); // 使用圖表名稱生成檔案名
        document.body.appendChild(link);
        link.click();
      } catch (error) {
        console.error('匯出數據時出錯:', error);
        alert('匯出失敗，請檢查數據並重試。');
      }
    }
  },
};
</script>

<style scoped>
.chart-container {
  position: relative;
  padding: 10px;
  background-color: white;
  border-radius: 10px;
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