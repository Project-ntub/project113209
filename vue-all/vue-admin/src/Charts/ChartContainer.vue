<template>
    <div>
      <!-- 圖表容器 -->
      <div class="chart-container">
        <div class="chart-header">
          <!-- 詳細資訊按鈕 -->
          <button class="info-button" @click="showDetails">
            ℹ️
          </button>
          <!-- 放大按鈕 -->
          <button class="zoom-button" @click="zoomChart">
            ⤢
          </button>
          <!-- 菜單按鈕 -->
          <div class="menu-button">
            <button @click="toggleMenu">
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
  
      <!-- 放大圖表的彈跳視窗 -->
      <div v-if="isZoomed" class="modal-overlay">
        <div class="modal-content">
          <button class="close-button" @click="closeZoom">X</button>
          <!-- 將插槽的內容放大顯示在這裡 -->
          <slot name="zoomed"></slot>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        showMenu: false,
        isZoomed: false,  // 用於控制彈跳視窗的顯示
      };
    },
    methods: {
      toggleMenu() {
        this.showMenu = !this.showMenu;
      },
      showDetails() {
        // 顯示詳細資訊的邏輯
        alert("顯示詳細資訊");
      },
      zoomChart() {
        // 顯示放大視窗
        this.isZoomed = true;
      },
      closeZoom() {
        this.isZoomed = false;
      },
      editChart() {
        // 編輯圖表的邏輯，發送當前圖表的詳細資訊給父組件
        this.$emit('edit-chart'); // 觸發事件以打開編輯模式
        this.showMenu = false;
      },
      exportChart() {
        // 匯出圖表的邏輯
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
  
  .chart-header button {
    background: rgba(255, 255, 255, 0.8);
    border: none;
    padding: 5px;
    cursor: pointer;
    border-radius: 50%;
  }
  
  .chart-header button:hover {
    background: rgba(255, 255, 255, 1);
  }
  
  .menu-button {
    position: relative;
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
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    position: relative;
  }
  
  .close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    cursor: pointer;
  }
  </style>
  