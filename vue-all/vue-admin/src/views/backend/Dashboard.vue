<template>
  <div class="dashboard-page">
    <TopNavbar title="儀表板管理" />
    <div class="dashboard-container">
      <div class="top-left-controls">
        <button @click="openChartModal(false)">新增圖表</button>
        <button @click="openPreviewModal">預覽角色介面</button>
      </div>

      <div class="top-left-controls">
        <button @click="showDashboard('all')">所有圖表</button>
        <button @click="showDashboard('sales')">銷售額</button>
        <button @click="showDashboard('revenue')">營業額</button>
        <button @click="showDashboard('inventory')">庫存量</button>
      </div>

      <div class="dashboard">
        <div v-for="chart in filteredCharts" :key="chart.chartId" class="chart-wrapper">
          <!-- 將每個圖表包裝在 ChartContainer 中 -->
          <ChartContainer :chartConfig="chart">
            <PlotlyChart :chartConfig="chart" />
          </ChartContainer>
        </div>
      </div>
    </div>

    <!-- 新增圖表窗口  -->
    <Modal 
      v-if="showChartModal" 
      :isEditing="isEditing" 
      :chartId="selectedChartId" 
      @close="closeChartModal" 
    />

    <!-- 角色介面預覽模態窗口 -->
    <UserInterfacePreviewModal v-if="showPreviewModal" @close="closePreviewModal" />
  </div>
</template>

<script>
import axios from 'axios';
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
import Modal from '@/components/backend/ChartModal.vue';
import UserInterfacePreviewModal from '@/components/backend/UserInterfacePreviewModal.vue'; // 預覽角色介面視窗

export default {
  name: 'DashboardManager',
  components: {
    TopNavbar,
    PlotlyChart,
    ChartContainer,
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
    // 預設加載圖表資料
    this.fetchCharts();
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
    fetchCharts() {
      // 根據不同 API 端點抓取數據
      axios.get('/backend/dashboard/revenue/')
        .then(response => {
          const revenueData = response.data;
          this.charts.push({
            name: 'RevenueChart',
            label: '營業額',
            chartId: 1,
            chartType: 'bar',
            width: 600,
            height: 400,
            xAxisLabel: '店鋪名稱',
            yAxisLabel: '營業額',
            data: revenueData
          });
        })
        .catch(error => {
          console.error('Error fetching revenue data:', error);
        });

      axios.get('/backend/dashboard/sales/')
        .then(response => {
          const salesData = response.data;
          this.charts.push({
            name: 'SalesChart',
            label: '銷售額',
            chartId: 2,
            chartType: 'line',
            width: 600,
            height: 400,
            xAxisLabel: '日期',
            yAxisLabel: '銷售額',
            data: salesData
          });
        })
        .catch(error => {
          console.error('Error fetching sales data:', error);
        });

      axios.get('/backend/dashboard/stock/')
        .then(response => {
          const stockData = response.data;
          this.charts.push({
            name: 'InventoryChart',
            label: '庫存量',
            chartId: 3,
            chartType: 'bar',
            width: 600,
            height: 400,
            xAxisLabel: '商品名稱',
            yAxisLabel: '數量',
            data: stockData
          });
        })
        .catch(error => {
          console.error('Error fetching stock data:', error);
        });

      // 預設顯示所有圖表
      this.filteredCharts = this.charts;
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
    }
  }
};
</script>

<style scoped src="@/assets/css/backend/Dashboard.css"></style>
