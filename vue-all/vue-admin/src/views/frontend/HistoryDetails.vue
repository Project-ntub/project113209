<template>
  <div class="history-details">
    <div class="container">
      <div class="details-container" v-if="detail && !detail.error">
        <h2>{{ detail.timestamp }}</h2>
        <div class="details-content">
          <p>操作：{{ detail.action }}</p>
          <p>時間：{{ detail.timestamp }}</p>
          <p>使用者：{{ detail.user }}</p>
          <p v-if="detail.device && detail.device.brand">設備品牌：{{ detail.device.brand }}</p>
          <p v-if="detail.device && detail.device.type">設備類型：{{ detail.device.type }}</p>
          <p>操作結果：<span :class="{'success': detail.success, 'fail': !detail.success}">{{ detail.success ? '成功' : '失敗' }}</span></p>
        </div>
      </div>
      <div v-else>
        <p>未找到該紀錄的詳細信息。</p>
      </div>
      <div class="back-btn">
        <button @click="goBack">返回上一頁</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      detail: null,
    };
  },
  mounted() {
    const id = parseInt(this.$route.params.id);
    this.fetchDetail(id);
  },
  methods: {
    fetchDetail(id) {
      axios.get(`/api/frontend/history/${id}/`)
        .then(response => {
          this.detail = response.data;
        })
        .catch(() => {
          this.detail = { error: '未找到該紀錄的詳細信息。' };
        });
    },
    goBack() {
      this.$router.go(-1);
    }
  }
};
</script>

<style scoped>
.history-details {
  font-family: Arial, sans-serif;
  background-color: #f7f7f7;
  margin: 0;
  padding: 0;
}
.container {
  width: 600px;
  margin: 0 auto;
  padding-top: 50px;
}
.details-container {
  background-color: #fff;
  padding: 20px;
  border: 1px solid #d4d4d4;
  border-radius: 5px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
}
.details-container h2 {
  color: #3f51b5;
}
.details-content {
  margin-top: 10px;
}
.details-content p {
  margin: 0;
}
.details-content .success {
  color: green;
}
.details-content .fail {
  color: red;
}
.back-btn {
  margin-top: 20px;
  text-align: center;
}
.back-btn button {
  background-color: #007bff;
  color: white;
  padding: 10px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.back-btn button:hover {
  background-color: #0056b3;
}
</style>
