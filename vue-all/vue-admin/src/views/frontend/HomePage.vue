<template>
  <div :class="['home-page', { 'sidebar-open': isSidebarOpen }]">
    <TopNavbar @trigger-export="exportChart" ref="topNavbar" />
    <div v-if="userPosition === '經理'" class="branch-selection">
      <label for="branch-select">選擇分店:</label>
      <select id="branch-select" v-model="selectedBranch" @change="onBranchChange">
        <option v-for="branch in branches" :key="branch.branch_id" :value="branch.branch_id">
          {{ branch.branch_name }}
        </option>
      </select>
    </div>
    <div v-else-if="userPosition === '店長'" class="branch-info">
      <p>當前分店: {{ branches[0]?.branch_name }}</p>
    </div>
    <div v-if="permissions.length > 0" class="chart-controls">
      <button v-if="permissions.find(perm => perm.permission_name === '營業額' && perm.can_view)" @click="setCurrentChart('RevenueChart')">營業額</button>
      <button v-if="permissions.find(perm => perm.permission_name === '銷售額' && perm.can_view)" @click="setCurrentChart('SalesCharts')">銷售額</button>
      <button v-if="permissions.find(perm => perm.permission_name === '庫存量' && perm.can_view)" @click="setCurrentChart('InventoryChart')">庫存量</button>
      <button @click="setCurrentChart('all')">顯示所有圖表</button>
    </div>
    <div class="chart-grid">
      <ChartContainer v-if="currentChart === 'all' || currentChart === 'RevenueChart'" :chartConfig="getChartConfig('RevenueChart')" :is-Frontend="true">
        <PlotlyChart :chartConfig="getChartConfig('RevenueChart')" />
      </ChartContainer>
      <ChartContainer v-if="currentChart === 'all' || currentChart === 'SalesCharts'" :chartConfig="getChartConfig('SalesChart')" :is-Frontend="true">
        <PlotlyChart :chartConfig="getChartConfig('SalesChart')" />
      </ChartContainer>
      <ChartContainer v-if="currentChart === 'all' || currentChart === 'ProductSalesPieChart'" :chartConfig="getChartConfig('ProductSalesPieChart')" :is-Frontend="true">
        <PlotlyChart :chartConfig="getChartConfig('ProductSalesPieChart')" />
      </ChartContainer>
      <ChartContainer v-if="currentChart === 'all' || currentChart === 'InventoryChart'" :chartConfig="getChartConfig('InventoryChart')" :is-Frontend="true">
        <PlotlyChart :chartConfig="getChartConfig('InventoryChart')" />
      </ChartContainer>
    </div>
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
import axios from 'axios';

export default {
  name: 'HomePage',
  components: {
    TopNavbar,
    PlotlyChart,
    ChartContainer,
  },
  data() {
    return {
      isSidebarOpen: localStorage.getItem('sidebarOpen') === 'true',
      currentChart: 'all',
      branches: [],
      selectedBranch: null,
      userPosition: null,
      permissions: [],
    };
  },
  methods: {
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
      } catch (error) {
        console.error('Error fetching branches:', error);
      }
    },
    fetchPermissions() {
      axios.get('/api/backend/permissions/')
        .then(response => {
          this.permissions = response.data.filter(perm => perm.can_view === 1);
        })
        .catch(error => {
          console.error('無法獲取權限:', error);
        });
    },
    setCurrentChart(chart) {
      const allowedCharts = this.permissions.map(perm => perm.permission_name);

      if (chart === 'all') {
        this.currentChart = 'all';
      } else if (allowedCharts.includes(chart)) {
        this.currentChart = chart;
      } else {
        alert('您沒有檢視此圖表的權限');
      }
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
        ProductSalesPieChart: {
          name: 'ProductSalesPieChart',
          label: '產品銷售佔比',
          chartType: 'pie',
          width: 300,
          height: 250,
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