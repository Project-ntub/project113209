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
import EventCalendar from '@/views/frontend/EventCalendar.vue'; // 修改的元件名稱

// Backend Views
import Login from '@/views/backend/Login.vue';
import Register from '@/views/frontend/RegisterPage.vue';
import ForgetPassword from '@/views/frontend/ForgetPasswordPage.vue';
import Management from '@/views/backend/Management.vue';
import Dashboard from '@/views/backend/Dashboard.vue';
import UserManagement from '@/views/backend/UserManagement.vue';
import RoleManagement from '@/views/backend/RoleManagement.vue';
import PendingList from '@/views/backend/PendingList.vue';
import EditUser from '@/views/backend/EditUser.vue';
import AssignRole from '@/views/backend/AssignRole.vue';
import ModuleManagement from '@/views/backend/ModuleManagement.vue';
import RoleForm from '@/components/backend/RoleForm.vue';
import RoleFormPage from '@/views/backend/RoleFormPage.vue';
import ModuleForm from '@/components/backend/ModuleForm.vue';
import RolePermissions from '@/components/backend/RolePermissions.vue';
import HistoricalRecord from '@/views/backend/HistoricalRecord.vue';
import PersonalPreference from '@/views/backend/PersonalPreference.vue';
import BackendProfile from '@/views/backend/Profile.vue';

const routes = [
  // Frontend Routes
  { path: '/', redirect: '/frontend/login' },
  { path: '/frontend/login', name: 'FrontendLogin', component: LoginPage, meta: { hideNavbar: true, hideSidebar: true, requiresAuth: false } },
  { path: '/frontend/register', name: 'FrontendRegister', component: RegisterPage, meta: { hideNavbar: true, hideSidebar: true, requiresAuth: false } },
  { path: '/frontend/forgot_password', name: 'FrontendForgetPassword', component: ForgetPasswordPage, meta: { hideNavbar: true, hideSidebar: true, requiresAuth: false } },
  { path: '/frontend/home', name: '首頁', component: HomePage, meta: { requiresAuth: true } },
  { path: '/frontend/manager_home', name: 'ManagerHome', component: ManagerHome, meta: { requiresAuth: true } },
  { path: '/frontend/branch_manager_home', name: 'BranchManagerHome', component: BranchManagerHome, meta: { requiresAuth: true } },
  { path: '/frontend/profile', name: '個人資訊', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/frontend/accountsettings', name: '帳號設定', component: AccountSettings, meta: { requiresAuth: true } },
  { path: '/frontend/changepassword', name: '修改密碼', component: ChangePassword, meta: { requiresAuth: true } },
  { path: '/frontend/preferences', name: '偏好設定', component: PreferenceSetting, meta: { requiresAuth: true } },
  { path: '/frontend/historydetails/:id', name: '歷史紀錄詳情', component: HistoryDetails, meta: { requiresAuth: true } },
  { path: '/frontend/history', name: '歷史紀錄', component: HistoryPage, meta: { requiresAuth: true } },

  // 日曆路由
  { path: '/frontend/calendar', name: '日曆', component: EventCalendar, meta: { requiresAuth: true } },

  // Backend Routes
  { path: '/backend/login', name: 'BackendLogin', component: Login, meta: { hideSidebar: true, requiresAuth: false } },
  { path: '/backend/register', name: 'BackendRegister', component: Register, meta: { requiresAuth: false } },
  { path: '/backend/forgetpassword', name: 'BackendForgetPassword', component: ForgetPassword, meta: { requiresAuth: false } },
  { path: '/backend/management', name: 'BackendManagement', component: Management, meta: { requiresAuth: true } },
  { path: '/backend/dashboard', name: '儀表板管理', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/backend/user-management', name: '用戶管理', component: UserManagement, meta: { requiresAuth: true } },
  { path: '/backend/role-management', name: '角色管理', component: RoleManagement, meta: { requiresAuth: true } },
  { path: '/backend/role-management/create', name: '新增角色', component: RoleFormPage, props: true, meta: { requiresAuth: true } },
  { path: '/backend/role-management/edit/:id', name: '編輯角色', component: RoleFormPage, props: true, meta: { requiresAuth: true } },
  { path: '/backend/pending_list', name: '待審核名單', component: PendingList, meta: { requiresAuth: true } },
  { path: '/backend/edit_user/:userId', name: 'BackendEditUser', component: EditUser, meta: { requiresAuth: true } },
  { path: '/backend/assign_role/:userId', name: 'BackendAssignRole', component: AssignRole, meta: { requiresAuth: true } },
  { path: '/backend/module-management', name: '模組管理', component: ModuleManagement, meta: { requiresAuth: true } },
  { path: '/backend/create_role', name: 'BackendCreateRole', component: RoleForm, meta: { requiresAuth: true } },
  { path: '/backend/edit_role/:roleId', name: 'BackendEditRole', component: RoleForm, meta: { requiresAuth: true } },
  { path: '/backend/create-module', name: 'BackendCreateModule', component: ModuleForm, meta: { requiresAuth: true } },
  { path: '/backend/edit_module/:moduleId', name: 'BackendEditModule', component: ModuleForm, meta: { requiresAuth: true } },
  { path: '/backend/role_permissions/:roleId', name: 'BackendRolePermissions', component: RolePermissions, meta: { requiresAuth: true } },
  { path: '/backend/history', name: '歷史紀錄', component: HistoricalRecord, meta: { requiresAuth: true } },
  { path: '/backend/preferences', name: '個人偏好', component: PersonalPreference, meta: { requiresAuth: true } },
  { path: '/backend/profile', name: '個人資料', component: BackendProfile, meta: { requiresAuth: true } }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守衛
router.beforeEach((to, from, next) => {
  const frontendToken = localStorage.getItem('frontend_token');
  const backendToken = localStorage.getItem('backend_token');

  // 前台路由邏輯
  if (to.path.startsWith('/frontend')) {
    if (!frontendToken && to.meta.requiresAuth) {
      return next({ name: 'FrontendLogin' });
    }
  }

  // 後台路由邏輯
  if (to.path.startsWith('/backend')) {
    if (!backendToken && to.meta.requiresAuth) {
      return next({ name: 'BackendLogin' });
    }
  }

  next(); // 允許導航
});

export default router;
