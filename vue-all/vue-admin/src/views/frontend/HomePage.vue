<template>
  <div :class="['home-page', { 'sidebar-open': isSidebarOpen }]">
    <!-- 頂部導航欄 -->
    <TopNavbar @trigger-export="exportChart" ref="topNavbar" />

    <!-- 分店下拉選單（經理） -->
    <div v-if="userPosition === '經理'" class="branch-selection">
      <label for="branch-select">選擇分店:</label>
      <select id="branch-select" v-model="selectedBranch" @change="onBranchChange">
        <option v-for="branch in branches" :key="branch.branch_id" :value="branch.branch_id">
          {{ branch.branch_name }}
        </option>
      </select>
    </div>

    <!-- 店長專用顯示當前分店 -->
    <div v-else-if="userPosition === '店長'" class="branch-info">
      <p>當前分店: {{ branches[0]?.branch_name }}</p>
    </div>

    <!-- 按鈕控制區域，根據權限顯示按鈕 -->
    <div class="chart-controls">
      <button v-if ="permissions.find(perm => perm.permission_name === '營業額' && perm.can_view)" @click="setCurrentChart('RevenueChart')">營業額</button>
      <button v-if ="permissions.find(perm => perm.permission_name === '銷售額' && perm.can_view)" @click="setCurrentChart('SalesChart')">銷售額</button>
      <button v-if ="permissions.find(perm => perm.permission_name === '庫存量' && perm.can_view)" @click="setCurrentChart('InventoryChart')">庫存量</button>
      <button @click="setCurrentChart('all')">顯示所有圖表</button>
    </div>

    <!-- 圖表區域 -->
    <div class="chart-container">
      <!-- 顯示所有圖表 -->
      <template v-if="currentChart === 'all'">
        <div class="chart-grid">
          <PlotlyChart v-if ="permissions.find(perm => perm.permission_name === '營業額' && perm.can_view)" :chartConfig="getChartConfig('RevenueChart')" />
          <PlotlyChart v-if ="permissions.find(perm => perm.permission_name === '銷售額' && perm.can_view)" :chartConfig="getChartConfig('SalesChart')" />
          <PlotlyChart v-if ="permissions.find(perm => perm.permission_name === '庫存量' && perm.can_view)" :chartConfig="getChartConfig('InventoryChart')" />
        </div>
      </template>
      <!-- 顯示選定的單個圖表 -->
      <template v-else>
        <PlotlyChart :chartConfig="getChartConfig(currentChart)" />
      </template>
    </div>
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import axios from 'axios';

export default {
  name: 'HomePage',
  components: {
    TopNavbar,
    PlotlyChart,
  },
  data() {
    return {
      isSidebarOpen: false,
      currentChart: 'all',
      branches: [],
      selectedBranch: null,
      userPosition: null,
      permissions: [], // 用戶權限列表
    };
  },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    async fetchUserPosition() {
      try {
        const response = await axios.get('/api/frontend/profile/');
        this.userPosition = response.data.position_id;
        this.selectedBranch = response.data.branch_id;
        await this.fetchBranches();
        await this.fetchPermissions();
      } catch (error) {
        console.error('Error fetching user position:', error);
      }
    },
    async fetchBranches() {
      try {
        const response = await axios.get('/api/frontend/branches/');
        this.branches = response.data;
        if (this.userPosition === '店長') {
          this.selectedBranch = this.branches.find(branch => branch.branch_id === this.selectedBranch)?.branch_id;
        } else {
          this.selectedBranch = this.branches.length > 0 ? this.branches[0].branch_id : null;
        }
      } catch (error) {
        console.error('Error fetching branches:', error);
      }
    },
    async fetchPermissions() {
      try {
        const response = await axios.get('/api/backend/permissions/');
        this.permissions = response.data; // 獲取用戶的權限
      } catch (error) {
        console.error('Error fetching permissions:', error);
      }
    },
    hasPermission(chartName) {
      // 根據權限判斷用戶是否可以查看指定圖表
      return this.permissions.some(permission => permission.permission_name === chartName && permission.can_view);
    },
    setCurrentChart(chart) {
      this.currentChart = chart;
    },
    onBranchChange() {
      console.log('Selected branch:', this.selectedBranch);
    },
    exportChart(type) {
      const chartComponent = this.$refs.currentChartComponent;
      if (chartComponent && chartComponent.chartData) {
        const chartData = chartComponent.chartData;
        if (type === 'pdf') {
          this.exportPDF(chartData);
        } else if (type === 'excel') {
          this.exportExcel(chartData);
        }
      } else {
        console.error('沒有找到有效的圖表組件');
      }
    },
    exportPDF(chartData) {
      const doc = new jsPDF();
      doc.text('Chart Data', 14, 16);
      const formattedData = chartData.labels.map((label, index) => ({
        label,
        value: chartData.datasets[0].data[index],
      }));
      doc.autoTable({
        head: [['Month', 'Value']],
        body: formattedData.map(data => [data.label, data.value]),
      });
      doc.save('chart-data.pdf');
    },
    exportExcel(chartData) {
      const formattedData = chartData.labels.map((label, index) => ({
        label,
        value: chartData.datasets[0].data[index],
      }));
      const ws = XLSX.utils.json_to_sheet(formattedData);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Chart Data');
      XLSX.writeFile(wb, 'chart-data.xlsx');
    },
    getChartConfig(chartName) {
      const chartConfigs = {
        RevenueChart: {
          name: 'RevenueChart',
          label: '營業額',
          chartType: 'bar',
          width: 300,
          height: 250,
          xAxisLabel: '店铺名稱',
          yAxisLabel: '營業額',
        },
        InventoryChart: {
          name: 'InventoryChart',
          label: '庫存量',
          chartType: 'bar',
          width: 300,
          height: 250,
          xAxisLabel: '商品名稱',
          yAxisLabel: '數量',
        },
        SalesChart: {
          name: 'SalesChart',
          label: '銷售額',
          chartType: 'line',
          width: 300,
          height: 250,
          xAxisLabel: '日期',
          yAxisLabel: '銷售額',
        },
      };
      return chartConfigs[chartName] || chartConfigs['SalesChart'];
    },
  },
  async mounted() {
    await this.fetchUserPosition();
  },
};
</script>

<style scoped src="@/assets/css/frontend/HomePage.css"></style>
