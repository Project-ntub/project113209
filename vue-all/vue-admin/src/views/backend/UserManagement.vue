<template>
  <TopNavbar title="用戶管理" />
  <div class="container">
    <div class="header">
      <!-- 判斷是否有新增用戶的權限，並顯示"待審核"按鈕 -->
      <button v-if="permissions.find(perm => perm.permission_name === '用戶管理' && perm.can_add)" @click="navigateToPendingList">
        待審核
      </button>

    </div>
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
              <!-- 編輯按鈕顯示與權限檢查 -->
              <button v-if="permissions.find(perm => perm.permission_name === '用戶管理' && perm.can_edit)" @click="navigateToEditUser(user.id)" class="edit-btn">
                編輯
              </button>
              <!-- 刪除按鈕顯示與權限檢查 -->
              <button v-if="permissions.find(perm => perm.permission_name === '用戶管理' && perm.can_delete)" @click="deleteUser(user.id)" class="delete-btn">
                刪除
              </button>
              <!-- 分配角色按鈕 -->
              <button class="assigning-roles-btn" @click="navigateToAssignRole(user.id)">
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
import '@/assets/css/backend/UserManagement.css'; // 引用外部的 CSS 文件
import TopNavbar from '@/components/frontend/TopNavbar.vue';

export default {
  name: 'UserManagement',
  components: {
    TopNavbar,
  },
  data() {
    return {
      permissions: [], // 用於存放當前用戶的權限
      sortBy: 'name', // 預設按姓名排序
      departmentFilter: 'all', // 預設顯示所有部門
      query: '', // 搜尋框的值
      users: [], // 儲存從後端取得的用戶數據
      departments: ['銷售部', '人力資源部', '資訊部', '業務部', '財務部'] // 靜態部門清單
    };
  },
  computed: {
    // 根據篩選條件計算過濾後的用戶清單
    filteredUsers() {
      let filtered = this.users;

      // 部門篩選
      if (this.departmentFilter !== 'all') {
        filtered = filtered.filter(user => user.department_id === this.departmentFilter);
      }

      // 關鍵字搜尋
      if (this.query) {
        const queryLowerCase = this.query.toLowerCase();
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(queryLowerCase) ||
          user.email.toLowerCase().includes(queryLowerCase) ||
          user.phone.toLowerCase().includes(queryLowerCase)
        );
      }

      // 排序
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
          return new Date(a.last_login) - new Date(b.last_login);
        }
        return 0;
      });
    },
  },
  methods: {
    // 獲取當前用戶的權限
    fetchUserPermissions() {
      axios.get('/api/backend/permissions/')
        .then(response => {
            this.permissions = response.data;  // 使用回應的數據作為權限列表
        })
        .catch(error => {
            console.error('Error fetching permissions:', error);
        });
    },
    // 日期格式化
    formatDate(date) {
      return new Date(date).toLocaleString();
    },
    // 過濾應用（可添加具體過濾邏輯）
    applyFilters() {
      console.log('Filters applied');
    },
    // 導航至待審核用戶列表
    navigateToPendingList() {
      this.$router.push('/backend/pending_list');
    },
    // 導航至編輯用戶頁面
    navigateToEditUser(userId) {
      this.$router.push(`/backend/edit_user/${userId}`);
    },
    // 導航至角色分配頁面
    navigateToAssignRole(userId) {
      this.$router.push(`/backend/assign_role/${userId}`);
    },
    // 獲取所有用戶
    fetchUsers() {
      axios.get('/api/backend/users/')
        .then(response => {
          this.users = response.data.filter(user => user.is_active);
        })
        .catch(error => {
          console.error('Error fetching users:', error);
        });
    },
    // 刪除用戶
    deleteUser(userId) {
      if (confirm('確定要刪除此用戶嗎？')) {
        axios.delete(`/api/backend/delete_user/${userId}/`)
          .then(() => {
            this.fetchUsers(); // 刪除後重新獲取用戶列表
          })
          .catch(error => {
            console.error('Error deleting user:', error);
          });
      }
    }
  },
  // 當元件載入時初始化
  mounted() {
    this.fetchUsers(); // 獲取用戶資料
    this.fetchUserPermissions(); // 獲取用戶權限資料
  }
};
</script>

<style scoped src="@/assets/css/backend/UserManagement.css"></style>
