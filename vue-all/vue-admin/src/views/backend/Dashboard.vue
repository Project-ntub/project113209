<template> 
  <div class="dashboard-page">
    <TopNavbar title="儀表板管理" />
    <div class="dashboard-container">
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
        <button v-if="canAddChart" @click="openChartModal(false)">新增圖表</button>
        <!-- <button @click="openPreviewModal">預覽角色介面</button> -->
      </div>

      <div class="charts">
        <!-- 渲染篩選後的圖表 -->
        <div v-for="chart in filteredCharts" :key="chart.id" class="chart-wrapper">
          <ChartContainer 
            :chartConfig="chart" 
            @reload-charts="fetchCharts"
            :isFrontend="false"
            :canExport="chart.can_export"
            :canDelete="chart.can_delete"
          >
            <PlotlyChart :chartConfig="chart" />
          </ChartContainer>
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
      @reload-charts="fetchCharts"  
    />

    <!-- 預覽角色介面窗口 -->
    <!-- <UserInterfacePreviewModal v-if="showPreviewModal" @close="closePreviewModal" /> -->
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
import Modal from '@/components/backend/ChartModal.vue';
// import UserInterfacePreviewModal from '@/components/backend/UserInterfacePreviewModal.vue';
import axios from 'axios';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'DashboardManager',
  components: {
    TopNavbar,
    PlotlyChart,
    ChartContainer,
    Modal,
    // UserInterfacePreviewModal,
  },
  data() {
    return {
      charts: [],
      filteredCharts: [], // 用來存放篩選後的圖表
      showChartModal: false,
      // showPreviewModal: false,
      isEditing: false,
      selectedChartId: null,
      filterType: 'all', // 新增一個用來追踪當前的過濾類型
      chartPermissionMap: {
        'sales': '銷售額',
        'revenue': '營業額',
        'inventory': '庫存量',
        // 可以根據需求添加更多的映射
      },
    };
  },
  computed: {
    ...mapGetters(['getPermissions']),
    canAddChart() {
      return this.getPermissions.some(perm => perm.permission_name === '儀表板管理' && perm.can_add);
    },
  },
  mounted() {
    this.fetchCharts();
  },
  methods: {
    ...mapActions(['fetchPermissions']),
    async fetchCharts() {
      try {
        // 確保權限已經被獲取
        await this.fetchPermissions();

        const response = await axios.get('/api/backend/get-chart-configurations/');
        const chartConfigs = response.data.map(chart => ({
          ...chart,
          chartType: chart.chart_type.toLowerCase(), // 確保是小寫
        }));

        // 根據過濾條件選擇圖表
        let filteredConfigs = chartConfigs;
        if (this.filterType !== 'all') {
          const permissionName = this.chartPermissionMap[this.filterType];
          filteredConfigs = chartConfigs.filter(chart => chart.name === permissionName);
        }

        // 為每個圖表呼叫 dynamic-chart-data 並添加 x_data 和 y_data
        const chartsWithData = await Promise.all(filteredConfigs.map(async (chart) => {
          try {
            const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
              table_name: chart.data_source,
              x_field: chart.x_axis_field,
              y_field: chart.y_axis_field,
              filter_conditions: JSON.parse(chart.filter_conditions || '{}'),
              join_fields: chart.join_fields || []
            });
            return {
              ...chart,
              x_data: dataResponse.data.x_data,
              y_data: dataResponse.data.y_data,
              last_updated: dataResponse.data.last_updated,
              can_export: this.hasPermission(chart.name, 'can_export'),
              can_delete: this.hasPermission(chart.name, 'can_delete'),
            };
          } catch (error) {
            console.error(`Error fetching data for chart ID ${chart.id}:`, error);
            return {
              ...chart,
              x_data: [],
              y_data: [],
              last_updated: null,
              error: '無法獲取數據',
              can_export: false,
              can_delete: false,
            };
          }
        }));

        this.charts = chartsWithData;
        this.filteredCharts = chartsWithData; // 由於已經根據 filterType 過濾過

        console.log('Fetched charts with data:', this.charts);
      } catch (error) {
        console.error('Error fetching chart configurations:', error);
      }
    },
    openChartModal(editing, chartId = null) {
      this.isEditing = editing;
      this.selectedChartId = chartId;
      this.showChartModal = true;
    },
    closeChartModal() {
      this.showChartModal = false;
    },
    async showDashboard(type) {
      this.filterType = type;
      await this.fetchCharts();
    },
    async fetchChartConfigMethod(chartId) {
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

        const updatedConfig = {
          ...data,
          x_data: dataResponse.data.x_data,
          y_data: dataResponse.data.y_data,
          last_updated: dataResponse.data.last_updated,
          can_export: this.hasPermission(data.name, 'can_export'),
          can_delete: this.hasPermission(data.name, 'can_delete'),
        };

        return updatedConfig;
      } catch (error) {
        console.error('加載圖表配置時發生錯誤:', error);
        alert('加載圖表配置時發生錯誤，請稍後再試');
        return null;
      }
    },
    hasPermission(permissionName, action) {
      const permission = this.getPermissions.find(perm => perm.permission_name === permissionName);
      return permission ? permission[action] : false;
    },
  },
};
</script>

<style scoped src="@/assets/css/backend/Dashboard.css"></style>
