<template>
  <div :class="['home-page', { 'sidebar-open': isSidebarOpen }]">
    <TopNavbar title="儀表板管理" />

    <!-- 並排顯示下拉選單和新增圖表按鈕 -->
    <div class="top-controls">
      <select @change="showDashboard($event.target.value)">
        <option value="all">所有圖表</option>
        <option value="sales">銷售額</option>
        <option value="revenue">營業額</option>
        <option value="inventory">庫存量</option>
      </select>
      <!-- <button @click="openChartModal(false)">新增圖表</button> -->
    </div>

    <div class="charts">
      <!-- 渲染篩選後的圖表 -->
      <div v-for="chart in filteredCharts" :key="chart.id" class="chart-wrapper">
        <ChartContainer 
          :chartConfig="chart" 
          @reload-charts="fetchCharts"
          :isFrontend="true"
          :canExport="chart.can_export"
          :canDelete="chart.can_delete"
          :canEdit="chart.can_edit"
        />
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
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
import Modal from '@/components/backend/ChartModal.vue';
import axios from 'axios';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'HomePage',
  components: {
    TopNavbar,
    ChartContainer,
    Modal,
  },
  data() {
    return {
      charts: [],
      filteredCharts: [],
      showChartModal: false,
      isEditing: false,
      selectedChartId: null,
      filterType: 'all',
      isSidebarOpen: localStorage.getItem('sidebarOpen') === 'true',
    };
  },
  computed: {
    ...mapGetters(['getPermissions']),
    canAddChart() {
      return Array.isArray(this.getPermissions) && this.getPermissions.some(perm => perm.permission_name === '儀表板管理' && perm.can_add);
    },
  },
  mounted() {
    this.fetchCharts().then(() => {
      this.applyFilter(); // 初始載入時應用過濾
    });
  },
  methods: {
    ...mapActions(['fetchPermissions']),
    async fetchCharts() {
      try {
        await this.fetchPermissions();

        const response = await axios.get('/api/backend/charts/');
        const chartConfigs = response.data.map(chart => ({
          ...chart,
          chartType: chart.chartType ? chart.chartType.toLowerCase() : 'bar',
          dataSource: chart.dataSource || '',
          xAxisField: chart.xAxisField || '',
          yAxisField: chart.yAxisField || '',
        }));

        const chartsWithData = await Promise.all(chartConfigs.map(async (chart) => {
          try {
            const filterConditions = typeof chart.filter_conditions === 'string' 
              ? JSON.parse(chart.filter_conditions || '{}') 
              : chart.filter_conditions || {};

            const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
              table_name: chart.dataSource,
              x_field: chart.xAxisField,
              y_field: chart.yAxisField,
              filter_conditions: filterConditions,
              join_fields: chart.joinFields || []
            });

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
            console.error(`Error fetching data for chart ID ${chart.id}:`, error);
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

        this.charts = chartsWithData;
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
      this.applyFilter(); // 在 fetchCharts 之後應用過濾
    },
    applyFilter() {
      if (this.filterType === 'all') {
        this.filteredCharts = this.charts.filter(chart => this.canViewChart(chart.name));
      } else {
        const typeMap = {
          sales: '銷售',
          revenue: '營業',
          inventory: '庫存'
        };
        const expectedName = typeMap[this.filterType];
        this.filteredCharts = this.charts.filter(chart => 
          chart.name.includes(expectedName) && this.canViewChart(chart.name)
        );
      }
    },
    canViewChart(chartName) {
      return this.getPermissions.some(perm => perm.permission_name === chartName && perm.can_view);
    },
  },
  watch: {
    filterType() {
      this.applyFilter();
    }
  }
};
</script>

<style scoped src="@/assets/css/frontend/HomePage.css"></style>
