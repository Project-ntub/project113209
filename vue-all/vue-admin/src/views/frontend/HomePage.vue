<template>
  <div class="home-page">
    <!-- 顶部导航栏组件 -->
    <TopNavbar @export="exportChart" />
    
    <!-- 分店下拉式選單 -->
    <div class="branch-selection">
      <label for="branch-select">選擇分店:</label>
      <select id="branch-select" v-model="selectedBranch" @change="onBranchChange">
        <option v-for="branch in branches" :key="branch.branch_id" :value="branch.branch_id">
          {{ branch.branch_name }}
        </option>
      </select>
    </div>
    
    <div class="chart-controls">
      <!-- 控制不同图表显示的按钮 -->
      <button @click="setCurrentChart('RevenueChart')">營業額</button>
      <button @click="setCurrentChart('SalesChart')">銷售額</button>
      <button @click="setCurrentChart('InventoryChart')">庫存量</button>
    </div>
    
    <div class="chart-container">
      <!-- 动态组件，根据 currentChart 的值渲染相应的组件 -->
      <component :is="currentChart" :branch-id="selectedBranch" />
    </div>
  </div>
</template>

<script>
// 引入所需组件
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import SalesChart from '@/Charts/SalesChart.vue';
import RevenueChart from '@/Charts/RevenueChart.vue';
import InventoryChart from '@/Charts/InventoryChart.vue';
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
      currentChart: 'SalesChart', // 默认显示的图表组件
      branches: [], // 动态存储所有可访问的分店
      selectedBranch: null, // 当前选中的分店
    };
  },
  methods: {
    async fetchBranches() {
      try {
          const response = await axios.get('/api/frontend/branches/');
          this.branches = response.data;
          this.selectedBranch = this.branches.length > 0 ? this.branches[0].branch_id : null;
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
  },
  async mounted() {
    await this.fetchBranches();
  },
};
</script>

<style src="@/assets/css/frontend/HomePage.css"></style>
