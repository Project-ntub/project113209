<template>
  <div class="dashboard-container">
    <div class="header">
      <h2>儀表板管理</h2>
      <div class="chart-actions">
        <button @click="openChartModal(false)">新增圖表</button>
      </div>
    </div>

    <div class="selection-container">
      <div class="module-selection">
        <label for="module-select">選擇模組:</label>
        <select id="module-select" v-model="selectedModule" @change="onModuleChange">
          <option v-for="module in modules" :key="module.id" :value="module.id">{{ module.name }}</option>
        </select>
      </div>

      <div class="role-selection">
        <label for="role-select">選擇角色:</label>
        <select id="role-select" v-model="selectedRole" @change="onRoleChange">
          <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
        </select>
      </div>
    </div>

    <!-- 使用 vuedraggable 並添加 item 插槽 -->
    <draggable v-model="charts" itemKey="name" @end="onDragEnd">
      <template #item="{ element }">
        <div class="chart-selection">
          <button @click="setCurrentCharts(element.name)" class="chart-button">{{ element.label }}</button>
        </div>
      </template>
    </draggable>

    <div class="chart-container">
      <!-- 循環 currentCharts 顯示每個選中的圖表 -->
      <component v-for="chart in currentCharts" :is="chart" :key="chart" :role-id="selectedRole" />
    </div>

    <!-- Add Chart Modal -->
    <Modal v-if="showChartModal" :isEditing="isEditing" @close="closeChartModal">
    </Modal>
  </div>
</template>

<script>
import draggable from 'vuedraggable';
import SalesChart from '@/Charts/SalesChart.vue';
import RevenueChart from '@/Charts/RevenueChart.vue';
import RevenueSC from '@/Charts/RevenueSC.vue';
import InventoryChart from '@/Charts/InventoryChart.vue';
import InventorySC from '@/Charts/InventorySC.vue';
import Modal from '@/components/backend/ChartModal.vue'; // 引入 Modal 组件
import axios from '@/axios';

export default {
  name: 'DashboardManager',
  components: {
    draggable,
    SalesChart,
    RevenueChart,
    RevenueSC,
    InventoryChart,
    InventorySC,
    Modal,
  },
  data() {
    return {
      currentCharts: [], // 變更為陣列
      modules: [],
      roles: [],
      selectedModule: null,
      selectedRole: null,
      showChartModal: false,
      isEditing: false,
      currentChartData: null, 
      charts: [
        { name: ['RevenueChart', 'RevenueSC'], label: '營業額' }, // 更新為數組
        { name: ['InventoryChart', 'InventorySC'], label: '庫存量' },
        { name: ['SalesChart'], label: '銷售額' }
      ],
      newChart: {
        type: 'bar',
        name: '',
      },
      editChart: {
        type: 'bar',
        name: '',
      },
    };
  },
  methods: {
    async fetchModules() {
      try {
        const response = await axios.get('/api/backend/modules/');
        this.modules = response.data;
        this.selectedModule = this.modules.length > 0 ? this.modules[0].id : null;
      } catch (error) {
        console.error('Error fetching modules:', error);
      }
    },
    async fetchRoles() {
      try {
        const response = await axios.get(`/api/backend/get_roles_by_module/${this.selectedModule}/`);
        this.roles = response.data;
        this.selectedRole = this.roles.length > 0 ? this.roles[0].id : null;
      } catch (error) {
        console.error('Error fetching roles:', error);
      }
    },
    setCurrentCharts(chartNames) {
      this.currentCharts = chartNames; // 將選擇的圖表設置為數組
    },
    onModuleChange() {
      this.fetchRoles();
    },
    onRoleChange() {
      console.log('選擇的角色:', this.selectedRole);
    },
    openChartModal(editing) {
      this.isEditing = editing;
      this.showChartModal = true;
    },
    closeChartModal() {
      this.showChartModal = false;
    },
    async submitAddChartForm() {
      try {
        const response = await axios.post('/api/backend/charts/', this.newChart);
        console.log('新增圖表成功:', response.data);
        this.closeAddChartModal();
      } catch (error) {
        console.error('新增圖表失敗:', error);
      }
    },
    openEditModal() {
      // 設置當前圖表數據
      this.currentChartData = {
        // 在這裡獲取當前圖表的數據
        style: 'bar', // 示例數據，實際數據應根據圖表類型調整
        name: '當前圖表名稱',
        showLabels: true,
        color: '#007BFF',
        xAxisLabel: 'X 軸',
        yAxisLabel: 'Y 軸',
      };
      this.isEditing = true;
    },
    closeEditModal() {
      this.isEditing = false;
    },
    async submitEditChartForm() {
      try {
        const response = await axios.put(`/api/backend/charts/${this.editChart.id}/`, this.editChart);
        console.log('編輯圖表成功:', response.data);
        this.closeEditChartModal();
      } catch (error) {
        console.error('編輯圖表失敗:', error);
      }
    },
    onDragEnd() {
      console.log('Charts reordered:', this.charts);
    }
  },
  async mounted() {
    await this.fetchModules();
    await this.fetchRoles();
  },
};
</script>

<style scoped src="@/assets/css/backend/Dashboard.css"></style>