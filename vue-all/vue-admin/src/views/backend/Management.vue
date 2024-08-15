<!-- AppManagement.vue -->
<template>
  <div>
    <div class="hamburger-menu" @click="toggleSidebar">
      <div class="hamburger-icon">☰</div>
    </div>
    <Sidebar :isSidebarActive="isSidebarActive" />
    <div class="main-content" :class="{ shifted: isSidebarActive }" id="main-content">
      <router-view v-slot="{ Component }">
        <component :is="Component" v-if="Component" />
      </router-view>
      <div v-if="!hasRouteComponent">
        <h1 id="welcome-title">歡迎來到管理介面</h1>
        <p id="welcome-description">請選擇一個選項來管理。</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from '@/components/backend/SideBar.vue';

export default {
  name: 'AppManagement',
  components: {
    Sidebar
  },
  setup() {
    const isSidebarActive = ref(false);
    const route = useRoute();
    const hasRouteComponent = ref(false);

    watch(route, (newRoute) => {
      hasRouteComponent.value = newRoute.matched.length > 1;
    }, { immediate: true });

    const toggleSidebar = () => {
      isSidebarActive.value = !isSidebarActive.value;
    };

    return {
      isSidebarActive,
      toggleSidebar,
      hasRouteComponent,
    };
  }
};
</script>

<style scoped src="@/assets/css/backend/Management.css"></style>
