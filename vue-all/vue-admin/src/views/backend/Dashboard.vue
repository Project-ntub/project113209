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
        <div v-for="chart in filteredCharts" :key="chart.chartId" class="chart-wrapper">
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
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
import Modal from '@/components/backend/ChartModal.vue';
import UserInterfacePreviewModal from '@/components/backend/UserInterfacePreviewModal.vue';

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
          chartType: 'bar', width: 400, height: 300, 
          xAxisLabel: '店铺名稱', yAxisLabel: '營業額' 
        },
        { 
          name: 'InventoryChart', label: '庫存量', chartId: 2, 
          chartType: 'bar', width: 400, height: 300, 
          xAxisLabel: '商品名稱', yAxisLabel: '數量' 
        },
        { 
          name: 'SalesChart', label: '銷售額', chartId: 3, 
          chartType: 'line', width: 400, height: 300,
          xAxisLabel: '日期', yAxisLabel: '銷售額'         
        },
        { 
          name: 'ProductSalesPieChart', label: '產品銷售佔比', chartId: 4, 
          chartType: 'pie', width: 400, height: 300 
        }
      ],
      filteredCharts: [], // 用來存放篩選後的圖表
      showChartModal: false,
      showPreviewModal: false,
      isEditing: false,
      selectedChartId: null,
    };
  },
  mounted() {
    this.filteredCharts = this.charts; // 預設顯示所有圖表
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
    }
  }
};
</script>

<!-- 引入分離的 CSS -->
<style scoped src="@/assets/css/backend/Dashboard.css"></style>
