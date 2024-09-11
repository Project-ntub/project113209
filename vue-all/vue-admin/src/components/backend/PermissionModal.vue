<template>
  <div v-if="isVisible" class="modal-overlay">
    <div class="modal-content">
      <!-- Modal 標題 -->
      <div class="modal-header">
        <h3>權限設定</h3>
        <button class="close-button" @click="closeModal">X</button>
      </div>

      <!-- Modal 內容 -->
      <div class="modal-body">
        <!-- 顯示分店 -->
        <div class="branch-selection">
          <label>選擇分店</label>
          <!-- 添加「所有分店」選項 -->
          <div class="checkbox-item">
            <input type="checkbox" value="all" v-model="allBranches" @change="selectAllBranches" />
            <span>所有分店</span>
          </div>
          <!-- 顯示分店列表 -->
          <div v-for="branch in branches" :key="branch.branch_id" class="checkbox-item">
            <input type="checkbox" :value="branch.branch_id" v-model="selectedBranches" :disabled="allBranches" />
            <span>{{ branch.branch_name }}</span>
          </div>
        </div>
      </div>

      <!-- Modal 底部按鈕 -->
      <div class="modal-footer">
        <button class="btn cancel-btn" @click="closeModal">取消</button>
        <button class="btn save-btn" :disabled="!selectedBranches.length && !allBranches" @click="savePermissions">保存</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['isVisible'],
  data() {
    return {
      selectedBranches: [], // 已選擇的分店（多選）
      allBranches: false, // 是否選擇了「所有分店」
      branches: [] // 分店資料
    };
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    savePermissions() {
      if (!this.selectedBranches.length && !this.allBranches) {
        alert('請選擇至少一個分店');
        return;
      }
      // 處理保存邏輯
      console.log('選擇的分店:', this.selectedBranches);
      console.log('所有分店:', this.allBranches);
      this.closeModal();
    },
    async fetchBranches() {
      try {
        const response = await axios.get('/backend/branches/');
        this.branches = response.data;
      } catch (error) {
        console.error('無法獲取分店資料:', error);
      }
    },
    selectAllBranches() {
      if (this.allBranches) {
        // 如果選擇了「所有分店」，清空選中的單個分店
        this.selectedBranches = [];
      }
    }
  },
  mounted() {
    this.fetchBranches(); // 在組件掛載後獲取分店資料
  }
};
</script>

<!-- 確保使用正確的路徑引入 CSS -->
<style src="@/assets/css/backend/PermissionsModal.css"></style>
