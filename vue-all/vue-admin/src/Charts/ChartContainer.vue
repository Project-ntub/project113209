<template>
  <div>
    <!-- 圖表容器 -->
    <div class="chart-container">
      <div class="chart-header">
        <!-- 菜單按鈕 -->
        <div class="menu-button">
          <button class="menu-icon" @click="toggleMenu">
            ⋮
          </button>
          <!-- 下拉選單 -->
          <div v-if="showMenu" class="menu">
            <button @click="editChart">編輯圖表</button>
            <button @click="exportChart">匯出</button>
          </div>
        </div>
      </div>
      <!-- 使用插槽來插入圖表 -->
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showMenu: false,
    };
  },
  methods: {
    toggleMenu() {
      this.showMenu = !this.showMenu;
    },
    editChart() {
      this.$emit('edit-chart');
      this.showMenu = false;
    },
    exportChart() {
      alert("匯出圖表");
      this.showMenu = false;
    },
  },
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
}

.menu-button {
  position: relative;
}

.menu-icon {
  background: rgba(255, 255, 255, 0.8);
  border: none;
  padding: 10px; /* 增加按鈕的內距來放大按鈕 */
  font-size: 20px; /* 增加字型大小來放大按鈕 */
  cursor: pointer;
  border-radius: 50%;
}

.menu-icon:hover {
  background: rgba(255, 255, 255, 1);
}

.menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.menu button {
  display: block;
  width: 100%;
  padding: 10px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
}

.menu button:hover {
  background-color: #f0f0f0;
}
</style>
