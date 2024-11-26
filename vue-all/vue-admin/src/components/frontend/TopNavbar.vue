<template>
  <nav class="navbar">
    <!-- Navbar 左側：顯示當前頁面名稱 -->
    <div class="navbar-title">
      <i class="fas fa-home"></i> <!-- 圖標 -->
      {{ currentRouteName }}
    </div>

    <!-- Navbar 右側：匯出按鈕與下拉選單 -->
    <div v-if="isHomePage" class="export-container">
      <!-- <button class="export-button" @click="toggleExportMenu">匯出</button> -->
      <!-- <div v-if="showExportMenu" class="export-menu">
        <button @click="triggerExport('pdf')">匯出 PDF</button>
        <button @click="triggerExport('excel')">匯出 Excel</button>
      </div> -->
    </div>
  </nav>
</template>

<script>
export default {
  data() {
    return {
      showExportMenu: false, // 控制匯出選單是否顯示
    };
  },
  computed: {
    // 取得當前路由名稱
    currentRouteName() {
      return this.$route.name || '未知頁面'; // 默認顯示 "未知頁面"
    },
    // 判斷是否為首頁
    isHomePage() {
      return this.$route.name === '首頁'; // 根據路由名稱判斷
    },
  },
  methods: {
    // 切換匯出選單顯示狀態
    toggleExportMenu() {
      this.showExportMenu = !this.showExportMenu;
    },
    // 觸發匯出功能
    triggerExport(type) {
      this.$emit('trigger-export', type); // 向父組件發送事件
      this.showExportMenu = false; // 隱藏匯出選單
    },
  },
};
</script>


<style scoped src="@/assets/css/frontend/TopNavbar.css"></style>
