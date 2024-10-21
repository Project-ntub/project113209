<!-- RoleFormPage.vue -->
<template>
    <div class="role-form-page">
      <TopNavbar title="角色管理" />
      <div class="container">
        <RoleForm :roleId="roleId" @role-saved="handleRoleSaved" />
      </div>
    </div>
  </template>
  
  <script>
  import TopNavbar from '@/components/frontend/TopNavbar.vue';
  import RoleForm from '@/components/backend/RoleForm.vue';
  
  export default {
    name: 'RoleFormPage',
    components: {
      TopNavbar,
      RoleForm,
    },
    data() {
      return {
        roleId: this.$route.params.id || null,
      };
    },
    methods: {
        
      handleRoleSaved() {
        // 保存後導航回角色管理頁面
        this.$router.push('/backend/role-management');
      },
    },
    mounted() {
        // 当组件挂载时，滚动到页面顶部
        window.scrollTo(0, 0);
    },
  };
  </script>
  
  <style scoped>
  /* 根據需要添加樣式 */
  .container {
    max-width: 90%;
    margin: 0 auto;
    padding-top: 80px; /* 根据导航栏的高度调整 */
  }
  </style>
  