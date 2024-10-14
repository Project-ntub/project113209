// src/store/index.js
import { createStore } from 'vuex';
import axios from 'axios';

const store = createStore({
  state: {
    token: null,
    user: null,
    permissions: [], // 新增 permissions 狀態
  },
  getters: {
    getToken(state) {
      return state.token;
    },
    getUser(state) {
      return state.user;
    },
    getPermissions(state) { // 新增 getPermissions getter
      return state.permissions;
    },
  },
  mutations: {
    setToken(state, token) {
      state.token = token;
    },
    setUser(state, user) {
      state.user = user;
    },
    SET_PERMISSIONS(state, permissions) { // 新增 SET_PERMISSIONS mutation
      state.permissions = permissions;
    },
  },
  actions: {
    setToken({ commit }, token) {
      commit('setToken', token);
    },
    setUser({ commit }, user) {
      commit('setUser', user);
    },
    async fetchPermissions({ commit }) { // 新增 fetchPermissions action
      try {
        const response = await axios.get('/api/backend/permissions/');
        commit('SET_PERMISSIONS', response.data);
      } catch (error) {
        console.error('無法獲取權限:', error);
        commit('SET_PERMISSIONS', []); // 在錯誤時設置為空陣列
      }
    },
  },
});

export default store;
