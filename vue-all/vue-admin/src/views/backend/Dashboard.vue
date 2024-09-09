<template>
  <TopNavbar title="儀表板管理" />
  <div class="dashboard-container">
    <div class="top-left-controls">
      <button @click="openChartModal(false)">新增圖表</button>
      <button @click="openPreviewModal">預覽角色介面</button>
    </div>

    <!-- 新增一個區域來顯示所有圖表 -->
    <div class="dashboard">
      <div v-for="chart in charts" :key="chart.id">
        <PlotlyChart :chartConfig="chart" />
      </div>
    </div>

    <div class="chart-button-row">
      <button @click="setCurrentCharts(['RevenueChart'])" class="chart-button">營業額</button>
      <button @click="setCurrentCharts(['SalesChart'])" class="chart-button">銷售額</button>
      <button @click="setCurrentCharts(['InventoryChart'])" class="chart-button">庫存量</button>
    </div>

    <!-- 使用 vuedraggable 並添加 item 插槽 -->
    <draggable v-model="charts" itemKey="name" @end="onDragEnd" :move="onMove">
      <template #item="{ element }">
        <vue-resizable :key="element.name" class="chart-item">
          <component :is="element.name" />
        </vue-resizable>
      </template>
    </draggable>

    <div class="chart-container">
      <!-- 循環 currentCharts 顯示每個選中的圖表 -->
      <component v-for="chart in currentCharts" :is="chart" :key="chart" />
    </div>

    <!-- Add Chart Modal -->
    <Modal 
      v-if="showChartModal" 
      :isEditing="isEditing" 
      :chartId="selectedChartId" 
      @close="closeChartModal" 
      @chart-saved="fetchCharts" 
    />

    <!-- 角色介面預覽模態窗口 -->
    <UserInterfacePreviewModal v-if="showPreviewModal" @close="closePreviewModal" />
  </div>
</template>

<script>
import axios from 'axios';
import { markRaw } from 'vue';
import TopNavbar from '@/components/frontend/TopNavbar.vue'; // 引入前台的TopNavbar组件
import draggable from 'vuedraggable';
import VueResizable from 'vue-resizable';
import SalesChart from '@/Charts/SalesChart.vue';
import RevenueChart from '@/Charts/RevenueChart.vue';
import InventoryChart from '@/Charts/InventoryChart.vue';
import Modal from '@/components/backend/ChartModal.vue';
import UserInterfacePreviewModal from '@/components/backend/UserInterfacePreviewModal.vue'; // 預覽角色介面視窗
import PlotlyChart from '@/components/backend/PlotlyChart.vue';

export default {
  name: 'DashboardManager',
  components: {
    TopNavbar,
    draggable: markRaw(draggable),
    VueResizable: markRaw(VueResizable),
    SalesChart: markRaw(SalesChart),
    RevenueChart: markRaw(RevenueChart),
    InventoryChart: markRaw(InventoryChart),
    Modal,
    UserInterfacePreviewModal,
    PlotlyChart
  },
  data() {
    return {
      currentCharts: [], 
      showChartModal: false,
      isEditing: false,
      selectedChartId: null,
      showPreviewModal: false, // 控制角色介面預覽模態窗口
      charts: [
        { name: 'RevenueChart', label: '營業額', width: 300, height: 200 },
        { name: 'InventoryChart', label: '庫存量', width: 300, height: 200 },
        { name: 'SalesChart', label: '銷售額', width: 300, height: 200 }
      ],
      salesData: []
    };
  },
  created() {
    this.fetchSalesData();
    this.fetchCharts();
    setInterval(() => {
      this.fetchCharts();
    }, 60000); // 每60秒刷新一次
  },
  methods: {
    fetchCharts() {
      axios.get('/api/backend/charts/')
        .then(response => {
          this.charts = response.data.map(chart => ({
            id: chart.id,
            name: chart.name,
            dataSource: chart.dataSource,
            xAxisField: chart.xAxisField,
            yAxisField: chart.yAxisField,
            filterConditions: chart.filterConditions,
            style: chart.chart_type,
            data: {
              x: chart.x_data,
              y: chart.y_data
            }
          }));
        })
        .catch(error => {
          console.error('Fetching charts data failed:', error);
        });
    },
    fetchSalesData() {
      axios.get('/api/backend/sales-data/') // 假設您的API端點是這個URL
        .then(response => {
          this.salesData = response.data; // 將數據存儲在 Vue 的 data 中
          this.updateChart(); // 更新圖表
        })
        .catch(error => {
          console.error('Error fetching sales data:', error);
        });
    },
    updateChart() {
      this.charts.forEach(chart => {
        if (chart.name === 'SalesChart') {
          chart.data = this.salesData;  // 確保數據格式一致
        }
      });
    },
    setCurrentCharts(chartNames) {
      this.currentCharts = chartNames; 
    },
    openChartModal(editing, chartId = null) {
      this.isEditing = editing;
      this.selectedChartId = chartId;
      if (editing && chartId) {
        this.fetchChartData(chartId);
      }
      this.showChartModal = true;
    },
    fetchChartData(chartId) {
      axios.get(`/api/backend/charts/${chartId}/`)
        .then(() => {
          // 處理回應
        })
        .catch(error => {
          console.error('取得圖表資料時出錯:', error);
        });
    },
    closeChartModal() {
      this.showChartModal = false;
      this.fetchCharts(); // 確保更新圖表列表
    },
    openPreviewModal() {
      this.showPreviewModal = true;
    },
    closePreviewModal() {
      this.showPreviewModal = false;
    },
    onDragEnd() {
      console.log('Charts reordered:', this.charts);
    },
    onMove() {
      return true;
    }
  }
};
</script>

<style scoped src="@/assets/css/backend/Dashboard.css"></style>
