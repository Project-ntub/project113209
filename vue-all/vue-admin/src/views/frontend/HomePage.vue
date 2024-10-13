<template>
  <div class="home-page" :class="{ 'sidebar-open': isSidebarOpen }">
    <TopNavbar @trigger-export="exportChart" ref="topNavbar" />
    
    <!-- 分店選擇 -->
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

    <!-- 圖表控制按鈕區域 -->
    <div v-if="permissions.length > 0" class="chart-controls">
      <button v-if="permissions.find(perm => perm.permission_name === '營業額' && perm.can_view)" @click="setCurrentChart('RevenueChart')">營業額</button>
      <button v-if="permissions.find(perm => perm.permission_name === '銷售額' && perm.can_view)" @click="setCurrentChart('SalesCharts')">銷售額</button>
      <button v-if="permissions.find(perm => perm.permission_name === '庫存量' && perm.can_view)" @click="setCurrentChart('InventoryChart')">庫存量</button>
      <button @click="setCurrentChart('all')">顯示所有圖表</button>
    </div>

    <!-- 圖表顯示區域 -->
    <div class="charts">
      <div v-for="chart in filteredCharts" :key="chart.id" class="chart-wrapper">
        <ChartContainer :chartConfig="chart">
          <PlotlyChart :chartConfig="chart" />
        </ChartContainer>
      </div>
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
      filteredCharts: [],
      isSidebarOpen: localStorage.getItem('sidebarOpen') === 'true',
      currentChart: 'all',
      branches: [],
      selectedBranch: null,
      userPosition: null,
      permissions: [],
    };
  },
  mounted() {
    this.fetchCharts();
    this.fetchUserPosition();
  },
  methods: {
    fetchCharts() {
      axios.get('/api/backend/get-chart-configurations/')
        .then(response => {
          this.charts = response.data.map(chart => ({
            ...chart,
            dataSource: chart.data_source,
            xAxisField: chart.x_axis_field,
            yAxisField: chart.y_axis_field,
            chartType: chart.chart_type,
          }));
          this.filteredCharts = this.charts;
        })
        .catch(error => {
          console.error('Error fetching chart configurations:', error);
        });
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
      } catch (error) {
        console.error('Error fetching branches:', error);
      }
    },
    fetchPermissions() {
      axios.get('/api/backend/permissions/')
        .then(response => {
          this.permissions = response.data.filter(perm => perm.can_view == 1);
          console.log('Permissions:', this.permissions);
        })
        .catch(error => {
          console.error('無法獲取權限:', error);
        });
    },
    setCurrentChart(chart) {
      const allowedCharts = this.permissions.map(perm => perm.permission_name);

      if (chart === 'all') {
        this.filteredCharts = this.charts;
      } else if (allowedCharts.includes(chart)) {
        this.filteredCharts = this.charts.filter(c => c.chartType === chart);
      } else {
        alert('您沒有檢視此圖表的權限');
      }
    },
  },
};
</script>

<style scoped src="@/assets/css/frontend/HomePage.css"></style>
