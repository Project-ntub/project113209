<!-- src/views/backend/UserManagement.vue -->
<template>
  <TopNavbar title="用戶管理" />
  <div class="container">
    <div class="filter-section">
      <!-- 排序下拉選單 -->
      <label for="sort-select">排序:</label>
      <select id="sort-select" v-model="sortBy" @change="applyFilters">
        <option value="name">姓名</option>
        <option value="email">電子郵件</option>
        <option value="department">部門</option>
        <option value="position">職位</option>
        <option value="creation-time">建立時間</option>
        <option value="last-login">最近登入時間</option>
      </select>
      <!-- 部門過濾下拉選單 -->
      <label for="department-select">部門:</label>
      <select id="department-select" v-model="departmentFilter" @change="applyFilters">
        <option value="all">全部</option>
        <option v-for="department in departments" :key="department" :value="department">{{ department }}</option>
      </select>
      <!-- 搜尋框 -->
      <input type="text" id="search-box" placeholder="搜尋..." v-model="query" @keydown.enter="applyFilters">
      <button @click="applyFilters" class="search-btn">搜尋</button>

      <!-- 待審核按鈕，與搜尋欄一體化 -->
      <button class="pending-approval-btn" v-if="hasAddPermission" @click="navigateToPendingList">
        待審核
      </button>
    </div>

    <!-- 用戶表格 -->
    <div class="table-container">
      <table class="user-table">
        <thead>
          <tr>
            <th>姓名</th>
            <th>電子郵件</th>
            <th>電話號碼</th>
            <th>部門</th>
            <th>職位</th>
            <th>建立時間</th>
            <th>最近登入時間</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.phone }}</td>
            <td>{{ user.department_id }}</td>
            <td>{{ user.position_id }}</td>
            <td>{{ formatDate(user.date_joined) }}</td>
            <td>{{ formatDate(user.last_login) }}</td>
            <td>
              <!-- 編輯按鈕 -->
              <button v-if="hasEditPermission" @click="navigateToEditUser(user.id)" class="edit-btn">
                編輯
              </button>
              <!-- 刪除按鈕 -->
              <button v-if="hasDeletePermission" @click="deleteUser(user.id)" class="delete-btn">
                刪除
              </button>
              <!-- 分配角色按鈕 -->
              <button v-if="hasEditPermission" class="assigning-roles-btn" @click="navigateToAssignRole(user.id)">
                分配角色
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';
import TopNavbar from '@/components/frontend/TopNavbar.vue';
import { mapGetters } from 'vuex';

export default {
  name: 'UserManagement',
  components: {
    TopNavbar,
  },
  data() {
    return {
      sortBy: 'name',
      departmentFilter: 'all',
      query: '',
      users: [],
      departments: ['銷售部', '人力資源部', '資訊部', '業務部', '財務部'],
    };
  },
  computed: {
    ...mapGetters(['getPermissions']),
    filteredUsers() {
      let filtered = this.users;

      if (this.departmentFilter !== 'all') {
        filtered = filtered.filter(user => user.department_id === this.departmentFilter);
      }

      if (this.query) {
        const queryLowerCase = this.query.toLowerCase();
        filtered = filtered.filter(user =>
          user.username.toLowerCase().includes(queryLowerCase) ||
          user.email.toLowerCase().includes(queryLowerCase) ||
          user.phone.toLowerCase().includes(queryLowerCase)
        );
      }

      return filtered.sort((a, b) => {
        if (this.sortBy === 'name') {
          return a.username.localeCompare(b.username);
        } else if (this.sortBy === 'email') {
          return a.email.localeCompare(b.email);
        } else if (this.sortBy === 'department') {
          return a.department_id.localeCompare(b.department_id);
        } else if (this.sortBy === 'position') {
          return a.position_id.localeCompare(b.position_id);
        } else if (this.sortBy === 'creation-time') {
          return new Date(a.date_joined) - new Date(b.date_joined);
        } else if (this.sortBy === 'last-login') {
          const dateA = a.last_login ? new Date(a.last_login) : new Date(0);
          const dateB = b.last_login ? new Date(b.last_login) : new Date(0);
          return dateB - dateA;
        }
        return 0;
      });
    },
    hasAddPermission() {
      const hasPermission = this.getPermissions.some(
        perm => perm.permission_name === '用戶管理' && perm.can_add
      );
      console.log(`hasAddPermission: ${hasPermission}`);
      return hasPermission;
    },
    hasEditPermission() {
      const hasPermission = this.getPermissions.some(
        perm => perm.permission_name === '用戶管理' && perm.can_edit
      );
      console.log(`hasEditPermission: ${hasPermission}`);
      return hasPermission;
    },
    hasDeletePermission() {
      const hasPermission = this.getPermissions.some(
        perm => perm.permission_name === '用戶管理' && perm.can_delete
      );
      console.log(`hasDeletePermission: ${hasPermission}`);
      return hasPermission;
    }
  },
  methods: {
    fetchUsers() {
      axios.get('/api/backend/users/')
        .then(response => {
          this.users = response.data.filter(user => user.is_active);
        })
        .catch(error => {
          console.error('Error fetching users:', error);
        });
    },
    deleteUser(userId) {
      if (confirm('確定要刪除此用戶嗎？')) {
        axios.delete(`/api/backend/delete_user/${userId}/`)
          .then(() => {
            this.fetchUsers();
          })
          .catch(error => {
            console.error('Error deleting user:', error);
          });
      }
    },
    navigateToPendingList() {
      this.$router.push('/backend/pending_list');
    },
    navigateToEditUser(userId) {
      this.$router.push(`/backend/edit_user/${userId}`);
    },
    navigateToAssignRole(userId) {
      this.$router.push(`/backend/assign_role/${userId}`);
    },
    formatDate(date) {
      if (!date) {
        return '從未登入';
      }
      return new Date(date).toLocaleString();
    },
    applyFilters() {
      console.log('Filters applied');
    }
  },
  mounted() {
    this.fetchUsers();
    console.log('User Permissions:', this.getPermissions); // 添加日誌
  },
};
</script>


<style scoped src="@/assets/css/backend/UserManagement.css"></style>
