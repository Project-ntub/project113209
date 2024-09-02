<template>
  <nav class="navbar">
    <div class="navbar-title">{{ currentRouteName }}</div>
    <div v-if="isHomePage" class="export-container">
      <button class="export-button" @click="toggleExportMenu">匯出</button>
      <div v-if="showExportMenu" class="export-menu">
        <button @click="exportFile('pdf')">匯出PDF</button>
        <button @click="exportFile('excel')">匯出Excel</button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  data() {
    return {
      showExportMenu: false
    };
  },
  computed: {
    currentRouteName() {
      return this.$route.name;
    },
    isHomePage() {
      return this.$route.name === '首頁'; // 确认首页的路由名称
    }
  },
  methods: {
    toggleExportMenu() {
      this.showExportMenu = !this.showExportMenu;
    },
    exportFile(type) {
      this.$emit('export', type);
      this.showExportMenu = false;
    }
  }
};
</script>
<style scoped src="@/assets/css/frontend/TopNavbar.css"></style>