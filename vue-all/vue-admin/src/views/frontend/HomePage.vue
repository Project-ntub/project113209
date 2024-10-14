<!-- src/views/frontend/HomePage.vue -->
<template>
  <div :class="['home-page', { 'sidebar-open': isSidebarOpen }]">
    <TopNavbar @trigger-export="exportChart" ref="topNavbar" />
    
    <!-- 分店選擇
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
    </div> -->
    
    <!-- 圖表控制按鈕 -->
    <div v-if="availableChartTypes.length > 0" class="chart-controls">
      <button 
        v-for="type in availableChartTypes" 
        :key="type.type" 
        @click="setCurrentChart(type.type)">
        {{ type.label }}
      </button>
      <button @click="setCurrentChart('all')">顯示所有圖表</button>
    </div>
        
    <!-- 渲染圖表 -->
    <div v-for="chart in filteredCharts" :key="chart.id" class="chart-wrapper">
      <ChartContainer 
        :chartConfig="chart"
        @reload-charts="fetchCharts"
        :isFrontend="true"
        :canEdit="chart.can_edit"
        :canExport="chart.can_export"
        :canDelete="chart.can_delete"
      >
      </ChartContainer>
    </div>
  </div>
</template>

<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
// import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
import axios from 'axios';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'HomePage',
  components: {
    TopNavbar,
    // PlotlyChart,
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
      filteredCharts: [], // 確保只有一次定義
      chartVisibility: {}, // 用於存儲每個圖表的可見性
      chartTypeMap: { // 定義圖表類型映射
        sales: { substring: '銷售', label: '銷售額' },
        revenue: { substring: '營業', label: '營業額' },
        inventory: { substring: '庫存', label: '庫存量' }
      }
    };
  },
  computed: {
    ...mapGetters(['getPermissions']),
    availableChartTypes() {
      return Object.keys(this.chartTypeMap).map(key => ({
        type: key,
        label: this.chartTypeMap[key].label,
        substring: this.chartTypeMap[key].substring
      })).filter(({ substring }) => {
        return this.charts.some(chart => 
          chart.name.includes(substring) && this.canViewChart(chart.name)
        );
      });
    }
  },
  mounted() {
    this.fetchUserPosition();
    this.fetchCharts().then(() => {
      this.applyFilter(); // 初始載入時應用過濾
    });
  },
  methods: {
    ...mapActions(['fetchPermissions']),
    
    async fetchCharts() {
      try {
        await this.fetchPermissions();

        const response = await axios.get('/api/backend/charts/');
        const chartConfigs = response.data.map(chart => ({
          ...chart,
          chartType: chart.chartType ? chart.chartType.toLowerCase() : 'bar',
          dataSource: chart.dataSource || '',
          xAxisField: chart.xAxisField || '',
          yAxisField: chart.yAxisField || '',
        }));

        console.log('Fetched chart configurations:', chartConfigs);

        const chartsWithData = await Promise.all(chartConfigs.map(async (chart) => {
          try {
            const filterConditions = typeof chart.filter_conditions === 'string' 
              ? JSON.parse(chart.filter_conditions || '{}') 
              : chart.filter_conditions || {};

            const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
              table_name: chart.dataSource,
              x_field: chart.xAxisField,
              y_field: chart.yAxisField,
              filter_conditions: filterConditions,
              join_fields: chart.joinFields || []
            });

            console.log(`Chart ID ${chart.id} data:`, dataResponse.data);

            return {
              ...chart,
              x_data: dataResponse.data.x_data,
              y_data: dataResponse.data.y_data,
              last_updated: dataResponse.data.last_updated,
              can_export: chart.can_export,
              can_delete: chart.can_delete,
              can_edit: chart.can_edit,
            };
          } catch (error) {
            console.error(`Error fetching data for chart ID ${chart.id}:`, error);
            return {
              ...chart,
              x_data: [],
              y_data: [],
              last_updated: null,
              error: '無法獲取數據',
              can_export: false,
              can_delete: false,
              can_edit: false,
            };
          }
        }));

        console.log('Charts with data:', chartsWithData);

        this.charts = chartsWithData;
        // 不再直接設置 filteredCharts

        console.log('Charts count:', this.charts.length);
        console.log('Charts:', this.charts);
      } catch (error) {
        console.error('Error fetching chart configurations:', error);
      }
    },
    
    async fetchUserPosition() {
      try {
        const response = await axios.get('/api/frontend/profile/');
        this.userPosition = response.data.position_id;
        this.selectedBranch = response.data.branch_id;
        await this.fetchBranches();
        await this.fetchPermissions(); // 確保權限被獲取並過濾
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
    
    setCurrentChart(chartType) {
      console.log(`Setting current chart to: ${chartType}`);
      this.currentChart = chartType;
      this.applyFilter();
    },
    
    applyFilter() {
      console.log('Applying filter:', this.currentChart);
      if (this.currentChart === 'all') {
        this.filteredCharts = this.charts.filter(chart => {
          const hasPermission = this.canViewChart(chart.name);
          console.log(`Chart: ${chart.name}, Has Permission: ${hasPermission}`);
          return hasPermission;
        });
      } else {
        const type = this.currentChart;
        const chartType = this.chartTypeMap[type];
        if (!chartType) {
          console.error(`未知的 currentChart: ${type}`);
          this.filteredCharts = [];
          return;
        }
        const { substring } = chartType;
        this.filteredCharts = this.charts.filter(chart => {
          const isTypeMatch = chart.name.includes(substring); // 使用包含來匹配名稱
          const hasPermission = this.canViewChart(chart.name);
          console.log(`Chart: ${chart.name}, Type Match: ${isTypeMatch}, Has Permission: ${hasPermission}`);
          return isTypeMatch && hasPermission;
        });
      }
      console.log('Filtered charts after applyFilter:', this.filteredCharts);
    },
    
    async exportChart(format) {
      try {
        // 從當前選中的圖表中獲取 chartConfig
        const selectedChart = this.filteredCharts.find(chart => chart.can_export);
        if (!selectedChart) {
          alert('沒有可匯出的圖表');
          return;
        }

        const response = await axios.post('/api/backend/export-data/', {
          chartConfig: selectedChart,
          format: format
        }, { responseType: 'blob' });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${selectedChart.name || 'exported-file'}.${format}`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (error) {
        console.error('匯出數據時出錯:', error);
        alert('匯出失敗，請檢查數據並重試。');
      }
    },
    
    hasPermission(permissionName, action) {
      const permission = this.getPermissions.find(perm => perm.permission_name === permissionName);
      return permission ? permission[action] : false;
    },
    
    onBranchChange() {
      // 根據選擇的分店過濾圖表數據或重新獲取圖表
      this.fetchCharts().then(() => {
        this.applyFilter(); // 重新獲取圖表後應用過濾
      });
    },
    
    canViewChart(chartName) {
      return this.getPermissions.some(perm => perm.permission_name === chartName && perm.can_view);
    },
    
    slugify(text) {
      return text.toString().toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w-]+/g, '')       // 移除不必要的字符
        .replace(/--+/g, '-')          // 移除重複的連字符
        .replace(/^-+/, '')
        .replace(/-+$/, '');
    }
  },
  watch: {
    chartVisibility: {
      handler() {
        this.applyFilter();
      },
      deep: true
    },
    currentChart() {
      this.applyFilter();
    }
  }
};
</script>

<style scoped src="@/assets/css/frontend/HomePage.css"></style>
