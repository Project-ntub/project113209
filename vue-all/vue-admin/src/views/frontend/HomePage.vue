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
    <div v-for="chart in charts" :key="chart.id" class="chart-grid">
      <ChartContainer :chartConfig="chart">
        <PlotlyChart :chartConfig="chart" />
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
      charts: [],
      isSidebarOpen: localStorage.getItem('sidebarOpen') === 'true',
      currentChart: 'all',
      branches: [],
      selectedBranch: null,
      userPosition: null,
      permissions: [],
    };
  },
  async mounted() {
    axios.get('/api/backend/get-chart-configurations/')
    .then(response => {
      this.charts = response.data.map(chart => ({
        ...chart,
        dataSource: chart.data_source,
        xAxisField: chart.x_axis_field,
        yAxisField: chart.y_axis_field,
        chartType: chart.chart_type,
        // 如果有其他字段需要转换，继续添加
      }));
      this.filteredCharts = this.charts; // 更新 filteredCharts
    })
    .catch(error => {
      console.error('Error fetching chart configurations:', error);
    });
    
    // 获取用户职位等信息
    await this.fetchUserPosition();
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
  },
};
</script>

<style scoped src="@/assets/css/frontend/HomePage.css"></style>
