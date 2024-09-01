<template>
  <div class="dashboard-container">
    <div class="header">
      <h2>儀表板管理</h2>
      <div class="chart-actions">
        <button @click="openChartModal(false)">新增圖表</button>
        <button @click="openPreviewModal">預覽角色介面</button>
      </div>
    </div>

    <!-- 使用 vuedraggable 並添加 item 插槽 -->
    <draggable v-model="charts" itemKey="name" @end="onDragEnd" :move="onMove">
      <template #item="{ element }">
        <div class="chart-selection">
          <button @click="setCurrentCharts(element.name)" class="chart-button">{{ element.label }}</button>
        </div>
      </template>
    </draggable>

    <div class="chart-container">
      <!-- 循環 currentCharts 顯示每個選中的圖表 -->
      <component v-for="chart in currentCharts" :is="chart" :key="chart" />
    </div>

    <!-- Add Chart Modal -->
    <Modal v-if="showChartModal" :isEditing="isEditing" @close="closeChartModal" />

    <!-- 角色介面預覽模態窗口 -->
    <UserInterfacePreviewModal v-if="showPreviewModal" @close="closePreviewModal" />
  </div>
</template>

<script>
import draggable from 'vuedraggable';
import SalesChart from '@/Charts/SalesChart.vue';
import RevenueChart from '@/Charts/RevenueChart.vue';
import InventoryChart from '@/Charts/InventoryChart.vue';
import Modal from '@/components/backend/ChartModal.vue';
import UserInterfacePreviewModal from '@/components/backend/UserInterfacePreviewModal.vue'; // 預覽角色介面視窗

export default {
  name: 'DashboardManager',
  components: {
    draggable,
    SalesChart,
    RevenueChart,
    InventoryChart,
    Modal,
    UserInterfacePreviewModal,
  },
  data() {
    return {
      currentCharts: [], 
      showChartModal: false,
      isEditing: false,
      showPreviewModal: false, // 控制角色介面預覽模態窗口
      charts: [
        { name: ['RevenueChart'], label: '營業額' },
        { name: ['InventoryChart'], label: '庫存量' },
        { name: ['SalesChart'], label: '銷售額' }
      ],
    };
  },
  methods: {
    setCurrentCharts(chartNames) {
      this.currentCharts = chartNames; 
    },
    openChartModal(editing) {
      this.isEditing = editing;
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
    onDragEnd() {
      console.log('Charts reordered:', this.charts);
    },
    onMove() {
      return true;
    }
  },
};
</script>

<style scoped src="@/assets/css/backend/Dashboard.css"></style>
