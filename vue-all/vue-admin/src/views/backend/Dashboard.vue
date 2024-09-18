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
        <button @click="showDashboard('sales')">銷售額儀表板</button>
        <button @click="showDashboard('revenue')">營業額儀表板</button>
        <button @click="showDashboard('inventory')">庫存量儀表板</button>
      </div>

      <div class="dashboard">
        <div v-for="chart in charts" :key="chart.chartId" class="chart-wrapper">
          <!-- 將每個圖表包裝在 ChartContainer 中 -->
          <ChartContainer>
            <PlotlyChart :chartConfig="chart" />
          </ChartContainer>
        </div>
      </div>
    </div>
    <!-- Add Chart Modal -->
    <!-- <Modal 
      v-if="showChartModal" 
      :isEditing="isEditing" 
      :chartId="selectedChartId" 
      @close="closeChartModal" 
      @chart-saved="fetchCharts" 
    />
    角色介面預覽模態窗口
    <UserInterfacePreviewModal v-if="showPreviewModal" @close="closePreviewModal" /> -->
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
// import Modal from '@/components/backend/ChartModal.vue';
// import draggable from 'vuedraggable';  // 暫時註解掉拖曳組件
// import VueResizable from 'vue-resizable';  // 暫時註解掉縮放組件

export default {
  name: 'DashboardManager',
  components: {
    TopNavbar,
    PlotlyChart,
    ChartContainer,
    // Modal,
    // draggable,  // 暫時註解掉拖曳功能
    // VueResizable  // 暫時註解掉縮放功能
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
          name: 'ProductSalesPieChart', label: '產品銷售佔比', chartId: 1, 
          chartType: 'pie', width: 600, height: 400 
        }  // 新增圖表：店鋪收益對比
      ],
      showChartModal: false,
      // 暫時註解掉縮放功能的選項
      // resizeOptions: {
      //   minWidth: 300,
      //   minHeight: 200
      // }
    };
  },
  methods: {
    openChartModal(isNew) {
      // 處理打開圖表模態框
      console.log("打開圖表模態框: ", isNew);
    },
    openPreviewModal() {
      // 處理預覽模態框
      console.log("預覽模態框已打開");
    },
    // openChartModal(editing = false, chartId = null) {
    //   this.isEditing = editing;
    //   this.selectedChartId = chartId;
    //   if (editing && chartId) {
    //     this.fetchChartData(chartId);
    //   }
    //   this.showChartModal = true;
    // },
    // closeChartModal() {
    //   this.showChartModal = false;
    //   this.fetchCharts(); // 確保更新圖表列表
    // },
    // openPreviewModal() {
    //   this.showPreviewModal = true;
    //   console.log("預覽模態框已打開");
    // },
    // closePreviewModal() {
    //   this.showPreviewModal = false;
    // }
    // 暫時註解掉縮放和拖曳方法
    // onResize(element) {
    //   console.log('Resizing:', element);
    // },
    // onDragEnd() {
    //   console.log('Charts reordered:', this.charts);
    // }
  }
};
</script>

<style scoped src="@/assets/css/backend/Dashboard.css"></style>
