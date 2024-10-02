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

      <!-- 新增圖表和預覽角色介面按鈕放在這裡 -->
      <div class="button-group">
        <button @click="openChartModal(false)">新增圖表</button>
        <button @click="openPreviewModal">預覽角色介面</button>
      </div>

      <div class="dashboard">
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
      showPreviewModal: false,
      isEditing: false,
      selectedChartId: null,
      permissions: [] // 確保權限初始為空
    };
  },
  async mounted() {
    await this.fetchPermissions(); // 確保權限加載完畢後執行篩選
    this.filteredCharts = this.charts.filter(chart => 
      this.permissions.some(perm => perm.permission_name === chart.name && perm.can_view === 1)
    );
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
    async fetchPermissions() {
      try {
        const response = await axios.get('/api/backend/permissions/');
        this.permissions = response.data.filter(perm => perm.can_view === 1); // 加載權限並過濾可查看的圖表
      } catch (error) {
        console.error('無法獲取權限:', error);
      }
    },
    showDashboard(type) {
      // 提取當前用戶具有檢視權限的圖表名稱
      const visibleCharts = this.permissions.map(perm => perm.permission_name);

      if (type === 'all') {
        // 當選擇「所有圖表」時，只顯示具有檢視權限的圖表
        this.filteredCharts = this.charts.filter(chart => visibleCharts.includes(chart.name));
      } else {
        // 根據選中的類型進行篩選，同時確保用戶有檢視權限
        this.filteredCharts = this.charts.filter(chart => 
          chart.name.includes(type) && visibleCharts.includes(chart.name)
        );
      }
    },
  },
};
</script>

<!-- 引入分離的 CSS -->
<style scoped src="@/assets/css/backend/Dashboard.css"></style>
