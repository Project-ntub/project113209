<template>
  <vue-resizable @resize="onResize">
    <div>
      <div class="chart-container">
        <div class="chart-header">
          <div class="menu-button">
            <button class="menu-icon" @click="toggleMenu">⋮</button>
            <div v-if="showMenu" class="menu">
              <button @click="editChart">編輯圖表</button>
              <button @click="openPermissionModal">編輯權限</button>
              <button @click="exportChart">匯出</button>
            </div>
          </div>
        </div>
        <slot></slot>
      </div>

      <PermissionModal :isVisible="isPermissionModalVisible" @close="isPermissionModalVisible = false" />
      <ChartModal v-if="isChartModalVisible" :isEditing="true" @close="isChartModalVisible = false" />
    </div>
  </vue-resizable>
</template>

<script>
import PermissionModal from '@/components/backend/PermissionModal.vue';
import ChartModal from '@/components/backend/ChartModal.vue';

export default {
  components: {
    PermissionModal,
    ChartModal
  },
  data() {
    return {
      showMenu: false,
      isPermissionModalVisible: false,
      isChartModalVisible: false
    };
  },
  methods: {
    toggleMenu() {
      this.showMenu = !this.showMenu;
    },
    editChart() {
      this.isChartModalVisible = true;
      this.showMenu = false;
    },
    openPermissionModal() {
      this.isPermissionModalVisible = true;
      this.showMenu = false;
    },
    exportChart() {
      alert('匯出圖表');
      this.showMenu = false;
    },
    onResize() {
      // 如果有 chart 实例，可以调用相关函数调整大小
    }
  }
};
</script>

<style scoped>
.chart-container {
  position: relative;
  padding: 10px;
  border-radius: 10px;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-header {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 10; /* 确保菜单按钮显示在最上层 */
}

.menu-button {
  position: relative;
  z-index: 11; /* 确保按钮的点击优先 */
}

.menu-icon {
  background: rgba(255, 255, 255, 0.8);
  border: none;
  padding: 8px;
  font-size: 18px;
  cursor: pointer;
  border-radius: 50%;
  z-index: 11; /* 确保图标在前景 */
}

.menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: #3498db;
  border: 1px solid #2980b9;
  border-radius: 5px;
  width: 150px;
  z-index: 12; /* 确保菜单在最上层 */
}

.menu button {
  display: block;
  width: 100%;
  padding: 8px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  color: white;
}

.menu button:hover {
  background-color: #2980b9;
}
</style>
