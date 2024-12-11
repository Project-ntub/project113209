<template>
  <TopNavbar title="用戶管理" />
  <div class="main-container">
    <div class="filter-section">
      <!-- 排序下拉選單 -->
      <div class="filter-item">
        <span class="filter-label">排序:</span>
        <select 
          id="sort-select" 
          v-model="sortBy" 
          @change="applyFilters"
          class="filter-select"
        >
          <option value="name">姓名</option>
          <option value="email">電子郵件</option>
          <option value="department">部門</option>
          <option value="position">職位</option>
          <option value="creation-time">建立時間</option>
          <option value="last-login">最近登入時間</option>
        </select>
      </div>
      <!-- 部門過濾下拉選單 -->
      <div class="filter-item">
        <span class="filter-label">部門:</span>
        <select 
          id="department-select" 
          v-model="departmentFilter" 
          @change="applyFilters"
          class="filter-select"
        >
          <option value="all">全部</option>
          <option 
            v-for="department in departments" 
            :key="department" 
            :value="department"
          >
            {{ department }}
          </option>
        </select>
      </div>
      <!-- 搜尋框 -->
      <input type="text" id="search-box" placeholder="搜尋..." v-model="query" @keydown.enter="applyFilters" />
      <button @click="applyFilters" class="search-btn">搜尋</button>
      <!-- 待審核按鈕 -->
      <button v-if="hasAddPermission" @click="navigateToPendingList" class="pending-approval-btn">
        待審核
      </button>
    </div>

    <!-- 用戶表格 -->
    <div class="table-container">
      <table class="user-table">
        <thead>
          <tr>
            <th>用戶名</th>
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
              <div class="button-group">
                <button v-if="hasEditPermission" @click="navigateToEditUser(user.id)" class="edit-btn">
                  編輯
                </button>
                <button v-if="hasDeletePermission" @click="deleteUser(user.id)" class="delete-btn">
                  刪除
                </button>
                <button v-if="hasEditPermission" class="assigning-roles-btn" @click="navigateToAssignRole(user.id)">
                  分配角色
                </button>
              </div>
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
        if (this.sortBy === 'name') return a.username.localeCompare(b.username);
        if (this.sortBy === 'email') return a.email.localeCompare(b.email);
        if (this.sortBy === 'department') return a.department_id.localeCompare(b.department_id);
        if (this.sortBy === 'position') return a.position_id.localeCompare(b.position_id);
        if (this.sortBy === 'creation-time') return new Date(a.date_joined) - new Date(b.date_joined);
        if (this.sortBy === 'last-login') return (new Date(b.last_login) || 0) - (new Date(a.last_login) || 0);
        return 0;
      });
    },
    hasAddPermission() {
      return this.getPermissions.some(perm => perm.permission_name === '用戶管理' && perm.can_add);
    },
    hasEditPermission() {
      return this.getPermissions.some(perm => perm.permission_name === '用戶管理' && perm.can_edit);
    },
    hasDeletePermission() {
      return this.getPermissions.some(perm => perm.permission_name === '用戶管理' && perm.can_delete);
    },
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
      return date ? new Date(date).toLocaleString() : '從未登入';
    },
    applyFilters() {
      console.log('Filters applied');
    }
  },
  mounted() {
    this.fetchUsers();
  },
};
</script>

<style scoped>
.main-container {
  width: 100%;
  min-height: calc(105vh - 60px);
  /* height: 100%; */
  /* max-width: 1200px;  */
  /* margin: 1.5rem auto; */
  margin-left: 40px;
  padding: 1.5rem; 
  background-color: #ffffff;
  box-shadow: none;
  border-radius: 0;
  /* overflow: hidden; */
}

.filter-section {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px;
  /* margin-left: 20px;  */
  /* margin-top: -30px; */
}

/* 排序和部門標籤的容器 */
.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 標籤文字樣式 */
.filter-label {
  white-space: nowrap;  /* 防止文字換行 */
  min-width: 40px;     /* 設定最小寬度 */
}

.filter-select {
  min-width: 120px;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}


.search-btn, .pending-approval-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  color: white;
  font-size: 1rem;
  min-width: 80px;  /* 設定最小寬度 */
  /* width: 30%;
  align-items: center */
}

.search-btn {
  background-color: #4a90e2;
}

.pending-approval-btn {
  background-color: #ffa500;
}

.table-container {
  overflow-x: auto;
  max-height: calc(100vh - 200px);
  margin: 1.5rem 20px;
  /* margin-left: 50px; */
  /* margin-top: 1.5rem; */
  align-items: center
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th {
  background-color: #4A90E2;
  color: #ffffff;
  font-weight: bold;
}

.user-table th, .user-table td {
  border: 1px solid #ddd;
  padding: 1rem;
  text-align: left;
}

.user-table tr:nth-child(even) {
  background-color: #f0f0f0;
}

.user-table tr:nth-child(odd) {
  background-color: #ffffff;
}

.user-table tr:hover {
  background-color: #e0e0e0;
}

.button-group {
  display: flex;
  gap: 5px;
}

.edit-btn, .delete-btn, .assigning-roles-btn {
  padding: 0.3rem 0.5rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  color: white;
}

.edit-btn {
  background-color: #ffa500;
}

.delete-btn {
  background-color: #ff4500;
}

.assigning-roles-btn {
  background-color: #1e90ff;
}
</style>
