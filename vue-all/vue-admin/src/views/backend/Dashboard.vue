<template>
  <div class="dashboard-container">
    <div class="header">
      <h2>儀表板管理</h2>
      <div class="chart-actions">
        <button @click="openAddChartModal">新增圖表</button>
        <button @click="openEditChartModal">編輯圖表</button>
      </div>
    </div>

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

    <div class="chart-selection">
      <button @click="setCurrentChart('SalesChart')">銷售額</button>
      <button @click="setCurrentChart('RevenueChart')">營業額</button>
      <button @click="setCurrentChart('InventoryChart')">庫存量</button>
    </div>

    <div class="chart-container">
      <component :is="currentChart" :role-id="selectedRole" />
    </div>

    <!-- 新增图表模态框 -->
    <Modal v-if="showAddChartModal" @close="closeAddChartModal">
      <template #header>
        <h3>新增圖表</h3>
      </template>
      <template #body>
        <form @submit.prevent="submitAddChartForm">
          <div>
            <label for="chartName">圖表名稱:</label>
            <input type="text" id="chartName" v-model="newChart.name" required>
          </div>
          <button type="submit">提交</button>
        </form>
      </template>
    </Modal>

    <!-- 编辑图表模态框 -->
    <Modal v-if="showEditChartModal" @close="closeEditChartModal">
      <template #header>
        <h3>編輯圖表</h3>
      </template>
      <template #body>
        <form @submit.prevent="submitEditChartForm">
          <div>
            <label for="chartName">圖表名稱:</label>
            <input type="text" id="chartName" v-model="editChart.name" required>
          </div>
          <button type="submit">提交</button>
        </form>
      </template>
    </Modal>
  </div>
</template>

<script>
import SalesChart from '@/Charts/SalesChart.vue';
import RevenueChart from '@/Charts/RevenueChart.vue';
import InventoryChart from '@/Charts/InventoryChart.vue';
import Modal from '@/components/backend/ChartModal.vue'; // 引入 Modal 组件
import axios from '@/axios';

export default {
  name: 'DashboardManager',
  components: {
    SalesChart,
    RevenueChart,
    InventoryChart,
    Modal,
  },
  data() {
    return {
      currentChart: 'SalesChart',
      modules: [],           // 用于存储模组
      roles: [],             // 用于存储角色
      selectedModule: null,  // 当前选中的模组
      selectedRole: null,    // 当前选中的角色
      showAddChartModal: false,
      showEditChartModal: false,
      newChart: {
        name: '',
      },
      editChart: {
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
    setCurrentChart(chart) {
      this.currentChart = chart;
    },
    onModuleChange() {
      this.fetchRoles();  // 当模组变化时，重新获取角色
      console.log('選擇的模組:', this.selectedModule);
    },
    onRoleChange() {
      console.log('選擇的角色:', this.selectedRole);
    },
    openAddChartModal() {
      this.showAddChartModal = true;
    },
    closeAddChartModal() {
      this.showAddChartModal = false;
    },
    submitAddChartForm() {
      console.log('提交新增图表表单:', this.newChart);
      this.closeAddChartModal();
    },
    openEditChartModal() {
      this.showEditChartModal = true;
    },
    closeEditChartModal() {
      this.showEditChartModal = false;
    },
    submitEditChartForm() {
      console.log('提交编辑图表表单:', this.editChart);
      this.closeEditChartModal();
    },
  },
  async mounted() {
    await this.fetchModules(); // 组件挂载后获取模组数据
    await this.fetchRoles();   // 然后获取角色数据
  },
};
</script>

<style scoped src="@/assets/css/backend/Dashboard.css"></style>