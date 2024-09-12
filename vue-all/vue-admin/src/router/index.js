import { createRouter, createWebHistory } from 'vue-router';

// Frontend Views
import LoginPage from '@/views/frontend/LoginPage.vue';
import RegisterPage from '@/views/frontend/RegisterPage.vue';
import ForgetPasswordPage from '@/views/frontend/ForgetPasswordPage.vue';
import HomePage from '@/views/frontend/HomePage.vue';
import ProfilePage from '@/views/frontend/ProfilePage.vue';
import AccountSettings from '@/views/frontend/AccountSettings.vue';
import ChangePassword from '@/views/frontend/ChangePassword.vue';
import PreferenceSetting from '@/views/frontend/PreferenceSetting.vue';
import HistoryPage from '@/views/frontend/HistoryPage.vue';
import HistoryDetails from '@/views/frontend/HistoryDetails.vue';
import ManagerHome from '@/views/frontend/ManagerHome.vue';
import BranchManagerHome from '@/views/frontend/BranchManagerHome.vue';

// Backend Views
import Login from '@/views/backend/Login.vue';
import Register from '@/views/backend/Register.vue';
import ForgetPassword from '@/views/backend/ForgetPassword.vue';
import Management from '@/views/backend/Management.vue';
import Dashboard from '@/views/backend/Dashboard.vue';
import UserManagement from '@/views/backend/UserManagement.vue';
import RoleManagement from '@/views/backend/RoleManagement.vue';
import PendingList from '@/views/backend/PendingList.vue';
import EditUser from '@/views/backend/EditUser.vue';
import AssignRole from '@/views/backend/AssignRole.vue';
import ModuleManagement from '@/views/backend/ModuleManagement.vue';
import RoleForm from '@/components/backend/RoleForm.vue';
import ModuleForm from '@/components/backend/ModuleForm.vue';
import RolePermissions from '@/components/backend/RolePermissions.vue';
import HistoricalRecord from '@/views/backend/HistoricalRecord.vue';
import PersonalPreference from '@/views/backend/PersonalPreference.vue';
import Profile from '@/views/backend/Profile.vue';

const routes = [
  // Frontend Routes
  { path: '/', redirect: '/frontend/login' },
  { path: '/frontend/login', name: 'FrontendLogin', component: LoginPage, meta: { hideNavbar: true, hideSidebar: true } },
  { path: '/frontend/register', name: 'FrontendRegister', component: RegisterPage, meta: { hideNavbar: true, hideSidebar: true } },
  { path: '/frontend/forgot_password', name: 'FrontendForgetPassword', component: ForgetPasswordPage, meta: { hideNavbar: true, hideSidebar: true } },
  { path: '/frontend/home', name: '首頁', component: HomePage },
  { path: '/frontend/manager_home', name: 'ManagerHome', component: ManagerHome },
  { path: '/frontend/branch_manager_home', name: 'BranchManagerHome', component: BranchManagerHome },
  { path: '/frontend/profile', name: '個人資訊', component: ProfilePage },
  { path: '/frontend/accountsettings', name: '帳號設定', component: AccountSettings },
  { path: '/frontend/changepassword', name: '修改密碼', component: ChangePassword },
  { path: '/frontend/preferences', name: '偏好設定', component: PreferenceSetting },
  { path: '/frontend/historydetails/:id', name: '歷史紀錄詳情', component: HistoryDetails },
  { path: '/frontend/history', name: '歷史紀錄', component: HistoryPage },

  // Backend Routes
  { path: '/backend/login', name: 'BackendLogin', component: Login, meta: {hideSidebar: true} },
  { path: '/backend/register', name: 'BackendRegister', component: Register },
  { path: '/backend/forgetpassword', name: 'BackendForgetPassword', component: ForgetPassword },
  { path: '/backend/management', name: 'BackendManagement', component: Management },
  { path: '/backend/dashboard', name: '儀表板管理', component: Dashboard },
  { path: '/backend/user-management', name: '用戶管理', component: UserManagement },
  { path: '/backend/role-management', name: '角色管理', component: RoleManagement },
  { path: '/backend/pending_list', name: '待審核名單', component: PendingList },
  { path: '/backend/edit_user/:userId', name: 'BackendEditUser', component: EditUser },
  { path: '/backend/assign_role/:userId', name: 'BackendAssignRole', component: AssignRole },
  { path: '/backend/module-management', name: '模組管理', component: ModuleManagement },
  { path: '/backend/create_role', name: 'BackendCreateRole', component: RoleForm },
  { path: '/backend/edit_role/:roleId', name: 'BackendEditRole', component: RoleForm },
  { path: '/backend/create-module', name: 'BackendCreateModule', component: ModuleForm },
  { path: '/backend/edit_module/:moduleId', name: 'BackendEditModule', component: ModuleForm },
  { path: '/backend/role_permissions/:roleId', name: 'BackendRolePermissions', component: RolePermissions },
  { path: '/backend/history', name: '歷史紀錄', component: HistoricalRecord },    
  { path: '/backend/preferences', name: '個人偏好', component: PersonalPreference },
  { path: '/backend/profile', name: '個人資料', component: Profile }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const frontendToken = localStorage.getItem('frontend_token');  // 前台 token
  const backendToken = localStorage.getItem('backend_token');    // 後台 token

  // 前台路由邏輯
  if (to.path.startsWith('/frontend')) {
    if (!frontendToken && to.name !== 'FrontendLogin') {
      // 如果沒有前台 token，且路徑不是登入頁，則跳轉到前台登入頁
      return next({ name: 'FrontendLogin' });
    }
  }

  // 後台路由邏輯
  if (to.path.startsWith('/backend')) {
    if (!backendToken && to.name !== 'BackendLogin') {
      // 如果沒有後台 token，且路徑不是登入頁，則跳轉到後台登入頁
      return next({ name: 'BackendLogin' });
    }
  }

  next();
});



export default router;
