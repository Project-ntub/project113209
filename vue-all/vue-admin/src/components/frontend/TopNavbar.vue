<template>
  <nav class="navbar">
    <div class="navbar-title">{{ currentRouteName }}</div>
    <div v-if="isHomePage" class="export-container">
      <button class="export-button" @click="toggleExportMenu">匯出</button>
      <div v-if="showExportMenu" class="export-menu">
        <button @click="triggerExport('pdf')">匯出PDF</button>
        <button @click="triggerExport('excel')">匯出Excel</button>
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
    triggerExport(type) {
      this.$emit('trigger-export', type); // 改用另一個事件名避免混淆
      this.showExportMenu = false;
    }
  }
};
</script>
<<<<<<< HEAD
<style scoped src="@/assets/css/frontend/TopNavbar.css"></style>
=======

<style scoped src="@/assets/css/frontend/TopNavbar.css"></style>
>>>>>>> 52076dd484a07528b0836eaaddb1357e7dfb0f05
