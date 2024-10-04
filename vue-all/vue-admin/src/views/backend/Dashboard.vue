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
        <button @click="openChartModal(false)">新增圖表</button>
        <button @click="openPreviewModal">預覽角色介面</button>
      </div>

      <div class="charts">
        <!-- 渲染篩選後的圖表 -->
        <div v-for="chart in filteredCharts" :key="chart.id" class="chart-wrapper">
          <ChartContainer :chartConfig="chart">
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
      @close="closeChartModal" 
    />

    <!-- 預覽角色介面窗口 -->
    <UserInterfacePreviewModal v-if="showPreviewModal" @close="closePreviewModal" />
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import PlotlyChart from '@/Charts/PlotlyChart.vue';
import Modal from '@/components/backend/ChartModal.vue';
import UserInterfacePreviewModal from '@/components/backend/UserInterfacePreviewModal.vue';
import axios from 'axios';

export default {
  name: 'DashboardManager',
  components: {
    TopNavbar,
    PlotlyChart,
    Modal,
    UserInterfacePreviewModal,
  },
  data() {
    return {
      charts: [],
      filteredCharts: [], // 用來存放篩選後的圖表
      showChartModal: false,
      showPreviewModal: false,
      isEditing: false,
      selectedChartId: null,
    };
  },
  mounted() {
    this.filteredCharts = this.charts; // 預設顯示所有圖表
    axios.get('/api/backend/get-chart-configurations/')
    .then(response => {
      this.charts = response.data.map(chart => ({
        ...chart,
        dataSource: chart.data_source,
        xAxisField: chart.x_axis_field,
        yAxisField: chart.y_axis_field,
        chartType: chart.chart_type,
        // 如果有其他字段需要转换，继续添加
      }));
      this.filteredCharts = this.charts; // 更新 filteredCharts
    })
    .catch(error => {
      console.error('Error fetching chart configurations:', error);
    });
  },
  methods: {
    openChartModal(editing, chartId = null) {
      this.isEditing = editing;
      this.selectedChartId = chartId;
      this.showChartModal = true;
    },
    closeChartModal() {
      this.showChartModal = false;
    },
    openPreviewModal() {
      this.showPreviewModal = true;
    },
    closePreviewModal() {
      this.showPreviewModal = false;
    },
    showDashboard(type) {
      if (type === 'all') {
        this.filteredCharts = this.charts;
      } else if (type === 'sales') {
        this.filteredCharts = this.charts.filter(chart => chart.name.includes('Sales'));
      } else if (type === 'revenue') {
        this.filteredCharts = this.charts.filter(chart => chart.name.includes('Revenue'));
      } else if (type === 'inventory') {
        this.filteredCharts = this.charts.filter(chart => chart.name.includes('Inventory'));
      }
    },
  },
};
</script>

<!-- 引入分離的 CSS -->
<style scoped src="@/assets/css/backend/Dashboard.css"></style>
