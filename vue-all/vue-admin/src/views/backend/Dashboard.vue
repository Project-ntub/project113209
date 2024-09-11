<template>
  <div class="dashboard-page">
    <TopNavbar title="儀表板管理" />
    <div class="dashboard-container">
      <div class="top-left-controls">
        <button @click="openChartModal(false)">新增圖表</button>
        <button @click="openPreviewModal">預覽角色介面</button>
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
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
// import draggable from 'vuedraggable';  // 暫時註解掉拖曳組件
// import VueResizable from 'vue-resizable';  // 暫時註解掉縮放組件

export default {
  name: 'DashboardManager',
  components: {
    TopNavbar,
    PlotlyChart,
    ChartContainer,
    // draggable,  // 暫時註解掉拖曳功能
    // VueResizable  // 暫時註解掉縮放功能
  },
  data() {
    return {
      charts: [
        { name: 'RevenueChart', label: '營業額', chartId: 1, chartType: 'bar', width: 600, height: 400 },
        { name: 'InventoryChart', label: '庫存量', chartId: 2, chartType: 'bar', width: 600, height: 400 },
        { name: 'SalesChart', label: '銷售額', chartId: 3, chartType: 'bar', width: 600, height: 400 }
      ]
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