<template>
  <div class="modal-container">
    <div class="modal-content">
      <h3>權限設定</h3>

      <!-- 分店勾選框 -->
      <div class="checkbox-group">
        <label v-for="branch in branches" :key="branch.branch_id">
          <input type="checkbox" :value="branch.branch_id" v-model="selectedBranches" />
          {{ branch.branch_name }}
        </label>
        <!-- 額外的選項：所有分店 -->
        <label>
          <input type="checkbox" value="all" v-model="selectedBranches" />
          所有分店
        </label>
      </div>

      <!-- 確認和取消按鈕 -->
      <div class="button-group">
        <button class="cancel-btn" @click="closeModal">取消</button>
        <button class="save-btn" :disabled="!isFormValid" @click="savePermissions">保存</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      branches: [], // 存儲 API 獲取的分店數據
      selectedBranches: [] // 存儲選擇的分店
    };
  },
  computed: {
    isFormValid() {
      // 表單驗證，當至少選擇了一個分店時表單才有效
      return this.selectedBranches.length > 0;
    }
  },
  methods: {
    closeModal() {
      // 關閉模態框
      this.$emit('close');
    },
    savePermissions() {
      // 傳遞選擇的分店權限並關閉模態框
      this.$emit('save', this.selectedBranches);
      this.closeModal();
    },
    async fetchBranches() {
      // 從 API 獲取分店資料
      try {
        const response = await axios.get('/api/branches/'); // 假設你在後端有 `/api/branches/` 這個 API
        this.branches = response.data;
      } catch (error) {
        console.error('Error fetching branches:', error);
      }
    }
  },
  mounted() {
    // 組件加載時調用 API 獲取分店資料
    this.fetchBranches();
  }
};
</script>

<style scoped>
.modal-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 300px;
  text-align: center;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.button-group {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  width: 48%;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  width: 48%;
}

.save-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
