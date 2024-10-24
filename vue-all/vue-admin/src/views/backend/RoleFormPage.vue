<!-- RoleFormPage.vue -->
<template>
    <div class="role-form-page">
      <TopNavbar title="角色管理" />
      <div class="container">
        <RoleForm ref="roleForm" :roleId="roleId" @role-saved="handleRoleSaved" />
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
    props: {
        id: {
            type: String,
            default: null,
        },
    },
    data() {
      return {
        roleId: this.$route.params.id || null,
      };
    },
    methods: {
        handleRoleSaved(roleId) {
            if (this.roleId) {
                // 編輯模式，保存後導航回角色管理頁面
                this.$router.push('/backend/role-management');
            } else {
                // 新增模式，保存後更新 roleId，使表單變為編輯模式
                this.roleId = roleId;
                // 更新路由以包含新的 roleId
                this.$router.push(`/backend/role-management/edit/${roleId}`);
            }
        },
    },
    mounted() {
        // 當元件掛載時，捲動到頁面頂部
        window.scrollTo(0, 0);
    },
    watch: {
        '$route.params.id': {
            handler(newVal) {
                this.roleId = newVal || null;
            },
            immediate: true,
        },
    },
  };
  </script>
  
  <style scoped>
  /* 根據需要添加樣式 */
  .container {
    max-width: 90%;
    margin: 0 auto;
    padding-top: 80px; /* 根據導覽列的高度調整 */
  }
  </style>
  