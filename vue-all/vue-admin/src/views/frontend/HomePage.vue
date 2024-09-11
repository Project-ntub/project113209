<template>
  <div :class="['home-page', { 'sidebar-open': isSidebarOpen }]">
    <!-- 顶部导航栏组件 -->
    <TopNavbar @trigger-export="exportChart" ref="topNavbar" />
    
    <!-- 分店下拉式選單，如果用户是經理则显示 -->
    <div v-if="userPosition === '經理'" class="branch-selection">
      <label for="branch-select">選擇分店:</label>
      <select id="branch-select" v-model="selectedBranch" @change="onBranchChange">
        <option v-for="branch in branches" :key="branch.branch_id" :value="branch.branch_id">
          {{ branch.branch_name }}
        </option>
      </select>
    </div>

    <!-- 如果用户是店長，只显示该店数据 -->
    <div v-else-if="userPosition === '店長'" class="branch-info">
      <p>當前分店: {{ branches[0]?.branch_name }}</p>
    </div>

    <!-- 按鈕控制區域 -->
    <div class="chart-controls">
      <button @click="setCurrentChart('RevenueChart')">營業額</button>
      <button @click="setCurrentChart('SalesChart')">銷售額</button>
      <button @click="setCurrentChart('InventoryChart')">庫存量</button>
    </div>

    <!-- 圖表區域 -->
    <div class="chart-container">
      <component :is="currentChart" :branch-id="selectedBranch" ref="currentChartComponent" />
    </div>
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import SalesChart from '@/Charts/SalesChart.vue';
import RevenueChart from '@/Charts/RevenueChart.vue';
import InventoryChart from '@/Charts/InventoryChart.vue';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import axios from 'axios';

export default {
  name: 'HomePage',
  components: {
    TopNavbar,
    SalesChart,
    RevenueChart,
    InventoryChart,
  },
  data() {
    return {
      isSidebarOpen: false,
      currentChart: 'SalesChart',
      branches: [],
      selectedBranch: null,
      userPosition: null,
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
  },
  async mounted() {
    await this.fetchUserPosition();
  },
};
</script>

<style scoped src="@/assets/css/frontend/HomePage.css"></style>
