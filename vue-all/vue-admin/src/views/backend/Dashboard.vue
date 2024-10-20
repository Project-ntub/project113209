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

      <!-- 新增圖表和預覽角色介面按鈕 -->
      <div class="button-group">
        <button v-if="canAddChart" @click="openChartModal(false)">新增圖表</button>
        <!-- <button @click="openPreviewModal">預覽角色介面</button> -->
      </div>

      <div class="charts">
        <!-- 渲染篩選後的圖表 -->
        <div v-for="chart in filteredCharts" :key="chart.id" class="chart-wrapper">
          <ChartContainer 
            :chartConfig="chart" 
            @reload-charts="fetchCharts"
            :isFrontend="false"
            :canExport="chart.can_export"
            :canDelete="chart.can_delete"
            :canEdit="chart.can_edit"
          />
        </div>
      </div>
    </div>

    <!-- 新增圖表窗口 -->
    <Modal 
      v-if="showChartModal" 
      :isEditing="isEditing" 
      :chartId="selectedChartId" 
      :fetchChartConfig="fetchChartConfigMethod"
      @close="closeChartModal"
      @reload-charts="fetchCharts"  
    />
  </div>
</template>


<script>
import TopNavbar from '@/components/frontend/TopNavbar.vue';
// import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import ChartContainer from '@/Charts/ChartContainer.vue';
import Modal from '@/components/backend/ChartModal.vue';
import axios from 'axios';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'DashboardManager',
  components: {
    TopNavbar,
    // PlotlyChart,
    ChartContainer,
    Modal,
  },
  data() {
    return {
      charts: [],
      filteredCharts: [],
      showChartModal: false,
      isEditing: false,
      selectedChartId: null,
      filterType: 'all',
    };
  },
  computed: {
    ...mapGetters(['getPermissions']),
    canAddChart() {
      return Array.isArray(this.getPermissions) && this.getPermissions.some(perm => perm.permission_name === '儀表板管理' && perm.can_add);
    },
  },
  mounted() {
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
    openChartModal(editing, chartId = null) {
      this.isEditing = editing;
      this.selectedChartId = chartId;
      this.showChartModal = true;
    },
    closeChartModal() {
      this.showChartModal = false;
    },
    async showDashboard(type) {
      this.filterType = type;
      await this.fetchCharts();
      this.applyFilter(); // 在 fetchCharts 之後應用過濾
    },
    async fetchChartConfigMethod(chartId) {
      if (!chartId) {
        console.error('chartId is undefined');
        alert('無效的圖表 ID，無法加載圖表配置');
        return null;
      }
      try {
        const response = await axios.get(`/api/backend/charts/${chartId}/`);
        const data = response.data;

        // 呼叫 dynamic-chart-data 以獲取 x_data 和 y_data
        const dataResponse = await axios.post('/api/backend/dynamic-chart-data/', {
          table_name: data.data_source,
          x_field: data.x_axis_field,
          y_field: data.y_axis_field,
          filter_conditions: JSON.parse(data.filter_conditions || '{}'),
          join_fields: data.join_fields || []
        });

        const updatedConfig = {
          ...data,
          x_data: dataResponse.data.x_data,
          y_data: dataResponse.data.y_data,
          last_updated: dataResponse.data.last_updated,
          can_export: this.hasPermission(data.name, 'can_export'),
          can_delete: this.hasPermission(data.name, 'can_delete'),
        };

        return updatedConfig;
      } catch (error) {
        console.error('加載圖表配置時發生錯誤:', error);
        alert('加載圖表配置時發生錯誤，請稍後再試');
        return null;
      }
    },
    getChartNameByType(type) {
      const typeMap = {
        'sales': '銷售',      // 修改為 "銷售"
        'revenue': '營業',    // 修改為 "營業"
        'inventory': '庫存',  // 修改為 "庫存"
      };
      return typeMap[type] || null;
    },
    applyFilter() {
      console.log('Applying filter:', this.filterType);
      if (this.filterType === 'all') {
        this.filteredCharts = this.charts.filter(chart => {
          const hasPermission = this.hasPermission(chart.name, 'can_view');
          console.log(`Chart: ${chart.name}, Has Permission: ${hasPermission}`);
          return hasPermission;
        });
      } else {
        const expectedName = this.getChartNameByType(this.filterType);
        if (!expectedName) {
          console.error(`未知的 filterType: ${this.filterType}`);
          this.filteredCharts = [];
          return;
        }
        this.filteredCharts = this.charts.filter(chart => {
          const isTypeMatch = chart.name.includes(expectedName); // 使用包含來匹配名稱
          const hasPermission = this.hasPermission(chart.name, 'can_view');
          console.log(`Chart: ${chart.name}, Type Match: ${isTypeMatch}, Has Permission: ${hasPermission}`);
          return isTypeMatch && hasPermission;
        });
      }
      console.log('Filtered charts after applyFilter:', this.filteredCharts);
    },
    hasPermission(permissionName, action) {
      const permission = this.getPermissions.find(perm => perm.permission_name === permissionName);
      return permission ? permission[action] : false;
    },
    slugify(text) {
      return text.toString().toLowerCase()
        .replace(/\s+/g, '-') // 如果需要，可以保留或調整這部分
        .replace(/[^\w-]+/g, '')
        .replace(/--+/g, '-')
        .replace(/^-+/, '')
        .replace(/-+$/, '');
    }
  },
  watch: {
    filterType() { // 修改為監聽 filterType
      this.applyFilter();
    }
  }
};
</script>

<style scoped src="@/assets/css/backend/Dashboard.css"></style>
