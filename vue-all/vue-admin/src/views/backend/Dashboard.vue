<!-- src/views/backend/Dashboard.vue -->
<template>
  <div class="dashboard-page">
    <!-- 頂部導航欄，顯示標題 -->
    <TopNavbar title="儀表板管理" />
    <div class="dashboard-container">
      <br>
      <br>
      <!-- 下拉選單來選擇圖表類型 -->
      <div class="top-left-controls">
        <select @change="showDashboard($event.target.value)">
          <option value="all">所有圖表</option>
          <option value="sales">銷售額</option>
          <option value="revenue">營業額</option>
          <option value="inventory">庫存量</option>
        </select>
      </div>

      <!-- 新增圖表和預覽角色介面按鈕 -->
      <div class="button-group">
        <!-- 新增圖表按鈕，只有有權限的用戶才能看到 -->
        <button v-if="canAddChart" @click="openChartModal(false)">新增圖表</button>
        <!-- 預覽角色介面按鈕 -->
        <button @click="openPreviewModal">預覽角色介面</button>
        <!-- 用戶介面預覽模態視窗 -->
        <UserInterfacePreviewModal v-if="showPreviewModal" @close="showPreviewModal = false" />
      </div>

      <div class="charts">
        <!-- 渲染篩選後的圖表 -->
        <div v-for="chart in filteredCharts" :key="chart.id" class="chart-wrapper">
          <!-- 判斷是否為前台 -->
          <ChartContainer 
            :chartConfig="chart" 
            @reload-charts="fetchCharts"
            :isFrontend="false"
            :canExport="chart.can_export"
            :canDelete="chart.can_delete"
            :canEdit="chart.can_edit"
          />
        </div>
      </div>
    </div>

    <!-- 新增圖表窗口 -->
    <Modal 
      v-if="showChartModal" 
      :isEditing="isEditing" 
      :chartId="selectedChartId" 
      :fetchChartConfig="fetchChartConfigMethod"
      @close="closeChartModal"
    />
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
import Modal from '@/components/backend/ChartModal.vue';
import UserInterfacePreviewModal from '@/components/backend/UserInterfacePreviewModal.vue'; 
import axios from 'axios';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'DashboardManager',
  components: {
    TopNavbar,
    ChartContainer,
    Modal,
    UserInterfacePreviewModal
  },
  data() {
    return {
      charts: [], // 儲存所有圖表配置
      filteredCharts: [], // 儲存經過篩選的圖表
      showChartModal: false, // 控制新增圖表模態視窗的顯示與隱藏
      showPreviewModal: false, // 控制預覽角色介面模態視窗的顯示與隱藏
      isEditing: false, // 判斷是否為編輯模式
      selectedChartId: null, // 選定的圖表ID，若為新增則為 null
      filterType: 'all', // 當前的篩選類型
    };
  },
  computed: {
    ...mapGetters(['getPermissions']),
    // 計算用戶是否有新增圖表的權限
    canAddChart() {
      return Array.isArray(this.getPermissions) && this.getPermissions.some(perm => perm.permission_name === '儀表板管理' && perm.can_add);
    },
  },
  mounted() {
    // 組件掛載後獲取圖表配置，並應用初始篩選
    this.fetchCharts().then(() => {
      this.applyFilter(); // 初始載入時應用過濾
    });
  },
  methods: {
    ...mapActions(['fetchPermissions']),
    async fetchCharts() {
      // 獲取圖表配置的函數
      try {
        await this.fetchPermissions(); // 獲取用戶權限

        // 發送請求到後端獲取所有圖表配置
        const response = await axios.get('/api/backend/charts/');
        // 處理圖表配置，確保圖表類型和欄位名稱為正確格式
        const chartConfigs = response.data.map(chart => ({
          ...chart,
          chartType: chart.chartType ? chart.chartType.toLowerCase() : 'bar',
          dataSource: chart.dataSource || '',
          xAxisField: chart.xAxisField || '',
          yAxisField: chart.yAxisField || '',
        }));

        console.log('獲取到的圖表配置:', chartConfigs);

        // 為每個圖表配置獲取相應的圖表數據
        const chartsWithData = await Promise.all(chartConfigs.map(async (chart) => {
          try {
            // 處理過濾條件
            const filterConditions = typeof chart.filter_conditions === 'string' 
              ? JSON.parse(chart.filter_conditions || '{}') 
              : chart.filter_conditions || {};

            // 發送請求到後端獲取動態圖表數據
            const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
              table_name: chart.dataSource,
              x_field: chart.xAxisField,
              y_field: chart.yAxisField,
              filter_conditions: filterConditions,
              join_fields: chart.joinFields || []
            });

            console.log(`圖表 ID ${chart.id} 的數據:`, dataResponse.data);

            return {
              ...chart,
              x_data: dataResponse.data.x_data,
              y_data: dataResponse.data.y_data,
              last_updated: dataResponse.data.last_updated,
              can_export: chart.can_export,
              can_delete: chart.can_delete,
              can_edit: chart.can_edit,
            };
          } catch (error) {
            console.error(`獲取圖表 ID ${chart.id} 的數據時出錯:`, error);
            return {
              ...chart,
              x_data: [],
              y_data: [],
              last_updated: null,
              error: '無法獲取數據',
              can_export: false,
              can_delete: false,
              can_edit: false,
            };
          }
        }));

        console.log('包含數據的圖表配置:', chartsWithData);

        this.charts = chartsWithData; // 儲存獲取到的圖表配置及數據
        this.applyFilter(); // 應用篩選條件
        console.log('圖表數量:', this.charts.length);
        console.log('圖表詳細:', this.charts);
      } catch (error) {
        console.error('獲取圖表配置時出錯:', error);
      }
    },
    openPreviewModal() {
      // 打開預覽角色介面的模態視窗
      this.showPreviewModal = true;
    },
    openChartModal(editing, chartId = null) {
      // 打開新增或編輯圖表的模態視窗
      this.isEditing = editing;
      this.selectedChartId = chartId;
      this.showChartModal = true;
    },
    closeChartModal() {
      // 關閉新增或編輯圖表的模態視窗
      this.showChartModal = false;
    },
    async showDashboard(type) {
      // 根據選擇的類型顯示相應的圖表
      this.filterType = type;
      await this.fetchCharts(); // 獲取圖表配置
      this.applyFilter(); // 應用篩選條件
    },
    async fetchChartConfigMethod(chartId) {
      // 獲取圖表配置的方法
      if (!chartId) {
        console.error('chartId is undefined');
        alert('無效的圖表 ID，無法加載圖表配置');
        return null;
      }
      try {
        const response = await axios.get(`/api/backend/charts/${chartId}/`);
        const data = response.data;

        // 呼叫 dynamic-chart-data 以獲取 x_data 和 y_data
        const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
          table_name: data.data_source,
          x_field: data.x_axis_field,
          y_field: data.y_axis_field,
          filter_conditions: JSON.parse(data.filter_conditions || '{}'),
          join_fields: data.join_fields || []
        });

        // 更新圖表配置
        const updatedConfig = {
          ...data,
          chartType: data.chart_type ? data.chart_type.toLowerCase() : 'bar', // 添加 chartType
          x_data: dataResponse.data.x_data,
          y_data: dataResponse.data.y_data,
          last_updated: dataResponse.data.last_updated ? new Date(dataResponse.data.last_updated) : null,
          can_export: this.hasPermission(data.name, 'can_export'),
          can_delete: this.hasPermission(data.name, 'can_delete'),
          can_edit: this.hasPermission(data.name, 'can_edit'),
        };

        return updatedConfig;
      } catch (error) {
        console.error('獲取圖表配置時發生錯誤:', error);
        alert('獲取圖表配置時發生錯誤，請稍後再試');
        return null;
      }
    },
    getChartNameByType(type) {
      // 根據圖表類型映射到對應的中文名稱
      const typeMap = {
        'sales': '銷售',      // 修改為 "銷售"
        'revenue': '營業',    // 修改為 "營業"
        'inventory': '庫存',  // 修改為 "庫存"
      };
      return typeMap[type] || null;
    },
    applyFilter() {
      // 根據當前的篩選類型過濾圖表
      console.log('正在應用篩選條件:', this.filterType);
      if (this.filterType === 'all') {
        // 顯示所有圖表，前提是用戶有查看權限
        this.filteredCharts = this.charts.filter(chart => {
          const hasPermission = this.hasPermission(chart.name, 'can_view');
          console.log(`圖表: ${chart.name}, 是否有權限: ${hasPermission}`);
          return hasPermission;
        });
      } else {
        // 根據篩選類型映射到圖表名稱的一部分
        const expectedName = this.getChartNameByType(this.filterType);
        if (!expectedName) {
          console.error(`未知的 filterType: ${this.filterType}`);
          this.filteredCharts = [];
          return;
        }
        // 篩選圖表名稱包含對應類型名稱且用戶有查看權限的圖表
        this.filteredCharts = this.charts.filter(chart => {
          const isTypeMatch = chart.name.includes(expectedName); // 使用包含來匹配名稱
          const hasPermission = this.hasPermission(chart.name, 'can_view');
          console.log(`圖表: ${chart.name}, 類型匹配: ${isTypeMatch}, 是否有權限: ${hasPermission}`);
          return isTypeMatch && hasPermission;
        });
      }
      console.log('應用篩選後的圖表:', this.filteredCharts);
    },
    hasPermission(permissionName, action) {
      // 檢查用戶是否有特定權限
      const permission = this.getPermissions.find(perm => perm.permission_name === permissionName);
      return permission ? permission[action] : false;
    },
    slugify(text) {
      // 將文本轉換為 slug 格式
      return text.toString().toLowerCase()
        .replace(/\s+/g, '-') // 替換空格為連字符
        .replace(/[^\w-]+/g, '')
        .replace(/--+/g, '-')
        .replace(/^-+/, '')
        .replace(/-+$/, '');
    },
    async onReloadCharts() {
      // 重新載入圖表配置的函數
      await this.fetchCharts();
    }
  },
  watch: {
    filterType() { // 監視 filterType 的變化
      this.applyFilter();
    }
  }
};
</script>

<style scoped src="@/assets/css/backend/Dashboard.css"></style>
