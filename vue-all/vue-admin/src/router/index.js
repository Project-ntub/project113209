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
import ResetPasswordPage from '@/views/frontend/ResetPasswordPage.vue';

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
  { path: '/frontend/profile', name: '個人資訊', component: ProfilePage },
  { path: '/frontend/accountsettings', name: '帳號設定', component: AccountSettings },
  { path: '/frontend/changepassword', name: '修改密碼', component: ChangePassword },
  { path: '/frontend/preferences', name: '偏好設定', component: PreferenceSetting },
  { path: '/frontend/historydetails', name: '歷史紀錄詳情', component: HistoryDetails },
  { path: '/frontend/detail/:id', name: '歷史紀錄詳情', component: HistoryDetails },
  { path: '/frontend/history', name: '歷史紀錄', component: HistoryPage },
  { path: '/frontend/reset_password', name: 'ResetPassword', component: ResetPasswordPage,meta: { hideNavbar: true, hideSidebar: true } },
  // Backend Routes
  { path: '/backend/login', name: 'BackendLogin', component: Login, meta: {hideSidebar: true} },
  { path: '/backend/register', name: 'BackendRegister', component: Register },
  { path: '/backend/forgetpassword', name: 'BackendForgetPassword', component: ForgetPassword },
  { path: '/backend/management', name: 'BackendManagement', component: Management },
  { path: '/backend/dashboard', name: 'BackendDashboard', component: Dashboard },
  { path: '/backend/user-management', name: 'BackendUserManagement', component: UserManagement },
  { path: '/backend/role-management', name: 'BackendRoleManagement', component: RoleManagement },
  { path: '/backend/pending_list', name: 'BackendPendingList', component: PendingList },
  { path: '/backend/edit_user/:userId', name: 'BackendEditUser', component: EditUser },
  { path: '/backend/assign_role/:userId', name: 'BackendAssignRole', component: AssignRole },
  { path: '/backend/module-management', name: 'BackendModuleManagement', component: ModuleManagement },
  { path: '/backend/create_role', name: 'BackendCreateRole', component: RoleForm },
  { path: '/backend/edit_role/:roleId', name: 'BackendEditRole', component: RoleForm },
  { path: '/backend/create-module', name: 'BackendCreateModule', component: ModuleForm },
  { path: '/backend/edit_module/:moduleId', name: 'BackendEditModule', component: ModuleForm },
  { path: '/backend/role_permissions/:roleId', name: 'BackendRolePermissions', component: RolePermissions },
  { path: '/backend/history', name: 'BackendHistory', component: HistoricalRecord },    
  { path: '/backend/preferences', name: 'BackendPreference', component: PersonalPreference },
  { path: '/backend/profile', name: 'BackendProfile', component: Profile }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
