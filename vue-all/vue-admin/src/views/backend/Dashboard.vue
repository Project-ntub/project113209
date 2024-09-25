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
      charts: [
        { 
          name: 'RevenueChart', label: '營業額', chartId: 1, 
          chartType: 'bar', width: 600, height: 400, 
          xAxisLabel: '店铺名稱', yAxisLabel: '營業額' 
        },
        { 
          name: 'InventoryChart', label: '庫存量', chartId: 2, 
          chartType: 'bar', width: 600, height: 400, 
          xAxisLabel: '商品名稱', yAxisLabel: '數量' 
        },
        { 
          name: 'SalesChart', label: '銷售額', chartId: 3, 
          chartType: 'line', width: 600, height: 400,
          xAxisLabel: '日期', yAxisLabel: '銷售額'         
        },
        { 
          name: 'ProductSalesPieChart', label: '產品銷售佔比', chartId: 4, 
          chartType: 'pie', width: 600, height: 400 
        }
      ],
      filteredCharts: [], // 用來存放篩選後的圖表
      showChartModal: false,
      showPreviewModal: false
    };
  },
  mounted() {
    // 預設顯示所有圖表
    console.log(this.chartConfig);
    this.filteredCharts = this.charts;
  },
  methods: {
    openChartModal(editing, chartId = null) {
      this.isEditing = editing;
      this.selectedChartId = chartId;
      this.showChartModal = true;
    },
    closeChartModal() {
      this.showChartModal = false;
      // 如果不需要刷新圖表，可以移除此行
      // this.fetchCharts();
    },
    fetchCharts() {
      // 確保 fetchCharts 是定義的並正確工作
      console.log('Fetching charts from backend');
      // 可以根據需求從後端重新獲取圖表數據
      // axios.get('/api/charts').then(response => {
      //   this.charts = response.data;
      //   this.filteredCharts = this.charts;
      // });
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
