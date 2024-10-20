// store/index.js
import { createStore } from 'vuex';
import axios from 'axios';

const store = createStore({
  state: {
    frontend_token: localStorage.getItem('frontend_token') || null,
    backend_token: localStorage.getItem('backend_token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    permissions: [],
    fontSize: 'medium',
    preference: {},
  },
  getters: {
    getFrontendToken(state) {
      return state.frontend_token;
    },
    getBackendToken(state) {
      return state.backend_token;
    },
    getUser(state) {
      return state.user;
    },
    getPermissions: state => state.permissions,
    getFontSize(state) {
      return state.fontSize;
    },
    preference(state) {
      return state.preference;
    },
  },
  mutations: {
    setFrontendToken(state, token) {
      state.frontend_token = token;
      localStorage.setItem('frontend_token', token);
    },
    setBackendToken(state, token) {
      state.backend_token = token;
      localStorage.setItem('backend_token', token);
    },
    setUser(state, user) {
      state.user = user;
      localStorage.setItem('user', JSON.stringify(user));
    },
    SET_PERMISSIONS(state, permissions) {
      state.permissions = permissions;
    },
    setFontSize(state, size) {
      state.fontSize = size;
    },
    SET_PREFERENCE(state, preference) {
      state.preference = preference;
      state.fontSize = preference.fontsize;
    },
    clearAuth(state) {
      state.frontend_token = null;
      state.backend_token = null;
      state.user = null;
      state.permissions = [];
      state.preference = {};
      localStorage.removeItem('frontend_token');
      localStorage.removeItem('backend_token');
      localStorage.removeItem('user');
      localStorage.removeItem('refresh_token');
      sessionStorage.removeItem('refresh_token');
    },
  },
  actions: {
    setFrontendToken({ commit }, token) {
      commit('setFrontendToken', token);
    },
    setBackendToken({ commit }, token) {
      commit('setBackendToken', token);
    },
    setUser({ commit }, user) {
      commit('setUser', user);
    },
    clearAuth({ commit }) {
      commit('clearAuth');
    },
    async fetchPermissions({ commit }) {
      try {
        const response = await axios.get('/api/backend/permissions/');
        commit('SET_PERMISSIONS', response.data);
      } catch (error) {
        console.error('無法獲取權限:', error);
        commit('SET_PERMISSIONS', []);
      }
    },
    async fetchPreference({ commit }) {
      try {
        const response = await axios.get('/api/backend/user_preferences/');
        if (response.data.length > 0) {
          commit('SET_PREFERENCE', response.data[0]);
        }
      } catch (error) {
        console.error('無法獲取用戶偏好設定:', error);
      }
    },
    updateFontSize({ commit }, size) {
      commit('setFontSize', size);
    },
    initializeStore({ dispatch }) {
      // 初始化後台 Token
      if (localStorage.getItem('backend_token') || sessionStorage.getItem('backend_token')) {
        dispatch('fetchPermissions');
        dispatch('fetchPreference');
      }
      // 初始化前台 Token
      if (localStorage.getItem('frontend_token') || sessionStorage.getItem('frontend_token')) {
        dispatch('fetchPermissions');
        dispatch('fetchPreference');
      }
    },
  },
});

export default store;
