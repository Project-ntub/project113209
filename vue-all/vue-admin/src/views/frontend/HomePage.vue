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

    <div class="chart-controls">
      <!-- 控制不同图表显示的按钮 -->
      <button @click="setCurrentChart('RevenueChart')">營業額</button>
      <button @click="setCurrentChart('SalesChart')">銷售額</button>
      <button @click="setCurrentChart('InventoryChart')">庫存量</button>
    </div>
    
    <div class="chart-container">
      <!-- 动态组件，根据 currentChart 的值渲染相应的组件 -->
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
import * as XLSX from 'xlsx'; // 使用 * as 導入以避免 utils 未定義問題
import axios from 'axios';

export default {
  name: 'HomePage',
  components: {
    TopNavbar,
    SalesChart,
    RevenueChart,
    InventoryChart
  },
  data() {
    return {
      isSidebarOpen: false, // 用于控制侧边栏是否展开
      currentChart: 'SalesChart', // 默认显示的图表组件
      branches: [], // 动态存储所有可访问的分店
      selectedBranch: null, // 当前选中的分店
      userPosition: null  // 存储用户角色
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
        await this.fetchBranches();  // 根據用戶角色再進行請求
      } catch (error) {
        console.error('Error fetching user position:', error);
      }
    },
    async fetchBranches() {
      try {
        const response = await axios.get('/api/frontend/branches/');
        this.branches = response.data;
        // 如果用户是店长，将selectedBranch设为其所属分店
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
      const chartComponent = this.$refs.currentChartComponent; // 使用ref引用當前顯示的圖表
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
        value: chartData.datasets[0].data[index]
      }));

      doc.autoTable({
        head: [['Month', 'Value']],
        body: formattedData.map((data) => [data.label, data.value])
      });

      doc.save('chart-data.pdf');
    },
    exportExcel(chartData) {
      const formattedData = chartData.labels.map((label, index) => ({
        label,
        value: chartData.datasets[0].data[index]
      }));

      const ws = XLSX.utils.json_to_sheet(formattedData);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Chart Data');
      XLSX.writeFile(wb, 'chart-data.xlsx');
    }
  },
  async mounted() {
    await this.fetchUserPosition();
  }
};
</script>

<style scoped src="@/assets/css/frontend/HomePage.css"></style>
