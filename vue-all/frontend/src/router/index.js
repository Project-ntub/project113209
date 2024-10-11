import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '@/views/LoginPage.vue';
import RegisterPage from '@/views/RegisterPage.vue';
import ForgetPasswordPage from '@/views/ForgetPasswordPage.vue';
import HomePage from '@/views/HomePage.vue';
import ProfilePage from '@/views/ProfilePage.vue';
import AccountSettings from '@/views/AccountSettings.vue';
import ChangePassword from '@/views/ChangePassword.vue';
import PreferenceSetting from '@/views/PreferenceSetting.vue';
import HistoryPage from '@/views/HistoryPage.vue';
import HistoryDetails from '@/views/HistoryDetails.vue';
import ResetPasswordPage from '@/views/ResetPasswordPage.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: LoginPage, meta: { hideNavbar: true, hideSidebar: true } },
  { path: '/register', name: 'Register', component: RegisterPage, meta: { hideNavbar: true, hideSidebar: true } },
  { path: '/forgot_password', name: 'ForgetPassword', component: ForgetPasswordPage, meta: { hideNavbar: true, hideSidebar: true } },
  { path: '/home', name: 'Home', component: HomePage },
  { path: '/profile', name: 'Profile', component: ProfilePage },
  { path: '/accountsettings', name: 'AccountSettings', component: AccountSettings },
  { path: '/changepassword', name: 'ChangePassword', component: ChangePassword },
  { path: '/preferences', name: 'PreferenceSetting', component: PreferenceSetting },
  { path: '/history', name: 'History', component: HistoryPage },
  { path: '/detail/:id', name: 'HistoryDetails', component: HistoryDetails },
  { path: '/resetpassword', name: 'ResetPassword', component: ResetPasswordPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});


export default router;
