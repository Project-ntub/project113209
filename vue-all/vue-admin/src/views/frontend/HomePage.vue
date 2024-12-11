<!-- src/views/frontend/HomePage.vue -->
<template>
  <div :class="['home-page', { 'sidebar-open': isSidebarOpen }]">
    <!-- 頂部導航欄，顯示標題 -->
    <TopNavbar title="儀表板管理" />

    <!-- 並排顯示下拉選單和新增圖表按鈕 -->
    <div class="top-controls">
      <!-- 下拉選單，用於篩選顯示的圖表類型 -->
      <select @change="showDashboard($event.target.value)">
        <option value="all">所有圖表</option>
        <option value="sales">銷售額</option>
        <option value="revenue">營業額</option>
        <option value="inventory">庫存量</option>
      </select>
      <!-- <button @click="openChartModal(false)">新增圖表</button> -->
    </div>

    <!-- 卡片區域 -->
    <div class="cards-container">
      <div class="info-card" v-for="card in summaryCards" :key="card.id">
        <div class="card-icon">
          <font-awesome-icon icon="database" v-if="card.title.includes('總營業額')" />
          <font-awesome-icon icon="chart-line" v-else-if="card.title.includes('增長率')" />
          <font-awesome-icon icon="shopping-basket" v-else-if="card.title.includes('商品')" />
          <font-awesome-icon icon="building" v-else-if="card.title.includes('分店')" />
        </div>
        <span class="card-category">{{ card.title }}</span>
        <h3 class="card-title">{{ card.value }}</h3>
        <p class="card-subtitle">
          <span v-if="card.title.includes('商品')">最暢銷商品</span>
          <span v-else-if="card.title.includes('分店')">最佳分店</span>
          <span v-else>更新時間：現在</span>
        </p>
      </div>
    </div>


    <div class="charts">
      <!-- 渲染篩選後的圖表 -->
      <div v-for="chart in filteredCharts" :key="chart.id" class="chart-wrapper">
        <!-- 判斷是否為前台 -->
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
    />
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
import Modal from '@/components/backend/ChartModal.vue';
import axios from 'axios';
import { mapGetters, mapActions } from 'vuex';
import { fetchChartData } from '@/utils/chartDataProcessor';

export default {
  name: 'HomePage',
  components: {
    TopNavbar,
    ChartContainer,
    Modal,
  },
  data() {
    return {
      charts: [], // 儲存所有圖表配置
      filteredCharts: [], // 儲存經過篩選的圖表
      showChartModal: false, // 控制新增圖表模態視窗的顯示與隱藏
      isEditing: false, // 判斷是否為編輯模式
      selectedChartId: null, // 選定的圖表ID，若為新增則為 null
      summaryCards: [], // 添加卡片數據數組
      filterType: 'all', // 當前的篩選類型
      isSidebarOpen: localStorage.getItem('sidebarOpen') === 'true', // 側邊欄的開啟狀態
    };
  },
  computed: {
    ...mapGetters(['getPermissions']),
    // 計算用戶是否有新增圖表的權限
    canAddChart() {
      return Array.isArray(this.getPermissions) && this.getPermissions.some(perm => perm.permission_name === '儀表板管理' && perm.can_add);
    },
  },
  mounted() {
    // 組件掛載後獲取圖表配置，並應用初始篩選
    this.fetchCharts().then(() => {
      this.applyFilter(); // 初始載入時應用過濾
    });
    this.fetchSummaryData(); // 加載卡片數據
  },
  methods: {
    ...mapActions(['fetchPermissions']),
    async fetchCharts() {
      try {
        await this.fetchPermissions(); // 獲取用戶權限

        const response = await axios.get('/api/backend/charts/');
        const chartConfigs = response.data.map(chart => ({
          ...chart,
          chartType: chart.chartType?.toLowerCase(),
          dataSource: chart.dataSource || '',
          xAxisField: chart.xAxisField || '',
          yAxisFields: chart.yAxisFields?.filter(field => field) || [], // 過濾掉 null 或未定義的值
          yAxisField: chart.yAxisField || '',
        }));

        const chartsWithData = await Promise.all(chartConfigs.map(async (chart) => {
          try {
            const chartData = await fetchChartData(chart);
            return { ...chart, ...chartData };
          } catch (error) {
            console.error(`獲取圖表 ID ${chart.id} 的數據時出錯:`, error);
            return { ...chart, x_data: [], y_data: [], error: '無法獲取數據' };
          }
        }));

        this.charts = chartsWithData;
        this.applyFilter();
      } catch (error) {
        console.error('獲取圖表配置時出錯:', error);
      }
    },
    async fetchSummaryData() {
      try {
        const response = await axios.get('/api/backend/dashboard/card-data/');
        const data = response.data;

        this.summaryCards = [
          {
            id: 1,
            title: "總營業額",
            value: data.total_revenue.toLocaleString('zh-TW'),
          },
          {
            id: 2,
            title: "營業額增長率",
            value: `${data.growth_rate.toFixed(2)}%`,
          },
          {
            id: 3,
            title: "最暢銷商品",
            value: `${data.top_product.name} (${data.top_product.sales})`,
          },
          {
            id: 4,
            title: "最佳分店",
            value: `${data.top_branch.name} (${data.top_branch.revenue})`,
          },
        ];
      } catch (error) {
        console.error('獲取摘要數據時出錯:', error);
        this.summaryCards = [];
      }
    },
    openChartModal(editing, chartId = null) {
      // 打開新增或編輯圖表的模態視窗
      this.isEditing = editing;
      this.selectedChartId = chartId;
      this.showChartModal = true;
    },
    closeChartModal() {
      // 關閉新增或編輯圖表的模態視窗
      this.showChartModal = false;
    },
    async showDashboard(type) {
      // 根據選擇的類型顯示相應的圖表
      this.filterType = type;
      await this.fetchCharts(); // 獲取圖表配置
      this.applyFilter(); // 應用篩選條件
    },
    applyFilter() {
      // 根據當前的篩選類型過濾圖表
      console.log('正在應用篩選條件:', this.filterType);
      if (this.filterType === 'all') {
        // 顯示所有圖表，前提是用戶有查看權限
        this.filteredCharts = this.charts.filter(chart => this.canViewChart(chart.name));
      } else {
        // 根據篩選類型映射到圖表名稱的一部分
        const typeMap = {
          sales: '銷售',
          revenue: '營業',
          inventory: '庫存'
        };
        const expectedName = typeMap[this.filterType];
        // 篩選圖表名稱包含對應類型名稱且用戶有查看權限的圖表
        this.filteredCharts = this.charts.filter(chart => 
          chart.name.includes(expectedName) && this.canViewChart(chart.name)
        );
      }
    },
    canViewChart(chartName) {
      // 檢查用戶是否有權限查看特定圖表
      return this.getPermissions.some(perm => perm.permission_name === chartName && perm.can_view);
    },
    async onReloadCharts() {
      // 重新載入圖表配置
      await this.fetchCharts();
    }
  },
  watch: {
    filterType() {
      // 當篩選類型改變時，重新應用篩選條件
      this.applyFilter();
    }
  }
};
</script>

<style scoped src="@/assets/css/frontend/HomePage.css"></style>
 