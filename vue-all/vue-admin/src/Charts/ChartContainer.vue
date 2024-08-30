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
  padding: 8px; /* 增加按鈕的內距 */
  font-size: 18px; /* 增加字型大小 */
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
  width: 150px; /* 設定選單寬度 */
}

.menu button {
  display: block;
  width: 100%;
  padding: 8px; /* 調整內距 */
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
}

.menu button:hover {
  background-color: #f0f0f0;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .menu-icon {
    padding: 6px; /* 縮小按鈕內距 */
    font-size: 16px; /* 縮小字型大小 */
  }

  .menu {
    width: 120px; /* 調整選單寬度 */
  }

  .menu button {
    padding: 6px; /* 調整按鈕內距 */
  }
}

@media (max-width: 480px) {
  .chart-header {
    top: 5px;
    right: 5px;
    gap: 5px;
  }

  .menu-icon {
    padding: 4px; /* 縮小按鈕內距 */
    font-size: 14px; /* 縮小字型大小 */
  }

  .menu {
    width: 100px; /* 調整選單寬度 */
  }

  .menu button {
    padding: 4px; /* 調整按鈕內距 */
  }
}
</style>
