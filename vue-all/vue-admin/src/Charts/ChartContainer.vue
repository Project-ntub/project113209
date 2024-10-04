<template>
  <div>
    <div class="chart-container">
      <div class="chart-header">
        <div class="menu-button">
          <button class="menu-icon" @click="toggleMenu">⋮</button>
          <div v-if="showMenu" class="menu">
            <template v-if="!isFrontend">
              <button @click="editChart">编辑图表</button>
              <button v-if="localCanDelete" @click="deleteChart">删除图表</button>
            </template>
            <div v-if="localCanExport" class="export-button">
              <button @click="exportChart('csv')">导出为 CSV</button>
              <button @click="exportChart('excel')">导出为 Excel</button>
              <button @click="exportChart('pdf')">导出为 PDF</button>
            </div>
          </div>
        </div>
      </div>
      <!-- 點擊圖表，打开查看圖表的視窗 -->
      <div @click="openChartModal">
        <PlotlyChart :chartConfig="localChartConfig" />
      </div>

      <!-- 查看圖表的視窗 -->
      <div v-if="isChartModalVisible" class="chart-modal-overlay" @click.self="closeChartModal">
        <div class="chart-modal-content">
          <PlotlyChart :chartConfig="localChartConfig" />
          <button class="close-btn" @click="closeChartModal">×</button>
        </div>
      </div>
    </div>
    <!-- 编辑圖表的視窗 -->
    <ChartModal v-if="!isFrontend && isEditModalVisible" :isEditing="true" :chartId="localChartConfig.id" @close="closeEditModal" />
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
    canDelete: Boolean
  },
  data() {
    return {
      showMenu: false,
      isChartModalVisible: false,
      isEditModalVisible: false,
      localChartConfig: { ...this.chartConfig },
      localCanExport: false,
      localCanDelete: false,
    };
  },
  mounted() {
    this.localCanExport = this.canExport; // 初始化匯出權限
    this.localCanDelete = this.canDelete; // 初始化刪除權限
    this.fetchUserPermissions();
    
  },
  methods: {
    toggleMenu() {
      this.showMenu = !this.showMenu;
    },
    openChartModal() {
      this.isChartModalVisible = true;
    },
    closeChartModal() {
      this.isChartModalVisible = false;
    },
    editChart() {
      this.isEditModalVisible = true;
      this.showMenu = false;
    },
    closeEditModal() {
      this.isEditModalVisible = false;
    },
    async deleteChart() {
      if (!this.localChartConfig.id) {
        alert('圖表ID無效，無法刪除');
        return;
      }
      const confirmation = confirm('確定要隱藏此圖表嗎？');
      if (confirmation) {
        try {
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
      this.localChartConfig = updatedConfig;
    },
    fetchUserPermissions() {
      axios.get('/api/backend/permissions/')
        .then(response => {
          const permissions = response.data;

          // 依據圖表名稱確認權限
          this.localCanExport = permissions.some(perm => 
            perm.permission_name === this.localChartConfig.label && perm.can_export === true
          );
          this.localCanDelete = permissions.some(perm => 
            perm.permission_name === this.localChartConfig.label && perm.can_delete === true
          );
        })
        .catch(error => {
          console.error('無法獲取權限:', error);
        });
    },
    async exportChart(format) {
      if (!this.localChartConfig.data || this.localChartConfig.data.length === 0) {
        alert("圖表配置無效，無法導出！");
        return;
      }

      try {
        const response = await axios.post(`/api/backend/export-data-${format}/`, { chartConfig: this.localChartConfig }, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${this.localChartConfig.label || 'exported-file'}.${format}`);
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
.chart-modal-overlay {
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
.chart-modal-content {
  position: relative;
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  max-width: 80%;
  max-height: 80%;
  overflow: auto;
}
.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
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
