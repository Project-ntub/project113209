<template>
  <vue-resizable @resize="onResize">
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
              <button @click="openPermissionModal">編輯權限</button>
              <button @click="exportChart">匯出</button>
            </div>
          </div>
        </div>
        <!-- 使用插槽來插入圖表 -->
        <slot></slot>
      </div>

      <!-- 權限設定彈跳視窗 -->
      <PermissionModal :isVisible="isPermissionModalVisible" @close="isPermissionModalVisible = false" />

      <!-- 圖表編輯模態窗口 -->
      <ChartModal v-if="isChartModalVisible" :isEditing="true" @close="isChartModalVisible = false" />
    </div>  
  </vue-resizable>
</template>

<script>
import VueResizable from 'vue-resizable';
import PermissionModal from '@/components/backend/PermissionModal.vue';
import ChartModal from '@/components/backend/ChartModal.vue'; // 確保你已經有這個彈跳視窗組件

export default {
  components: {
    VueResizable,
    PermissionModal,
    ChartModal,
  },
  data() {
    return {
      showMenu: false,
      isPermissionModalVisible: false, // 控制彈跳視窗的顯示
      isChartModalVisible: false, // 控制圖表編輯模態窗口的顯示
      chartInstance: null, // 初始化圖表實例
    };
  },
  methods: {
    toggleMenu() {
      this.showMenu = !this.showMenu;
    },
    editChart() {
      this.isChartModalVisible = true; // 顯示編輯圖表的模態窗口
      this.showMenu = false;
    },
    openPermissionModal() {
      this.isPermissionModalVisible = true; // 顯示彈跳視窗
      this.showMenu = false;
    },
    exportChart() {
      alert("匯出圖表");
      this.showMenu = false;
    },
    onResize() {
      if (this.chartInstance) {
        this.chartInstance.resize(); // 當容器大小改變時，重新調整圖表大小
      }
    },
  },
  mounted() {
    this.$nextTick(() => {
      if (this.renderChart) {
        this.renderChart();
      } else {
        console.warn('renderChart method is not defined in this component.');
      }
    });
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
  background-color: #3498db; /* 改為藍色背景 */
  border: 1px solid #2980b9; /* 調整邊框顏色 */
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
  color: white; /* 將文字顏色改為白色，與藍色背景形成對比 */
}

.menu button:hover {
  background-color: #2980b9; /* 鼠標懸停時背景改為深藍色 */
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
