<template>
  <div class="history-page">
    <div class="container">
      <div class="search-container">
        <input type="text" id="searchInput" placeholder="搜尋紀錄..." v-model="searchQuery">
        <button @click="filterTimeline">搜尋</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HistoryPage',
  data() {
    return {
      searchQuery: '',
      items: [
        { id: 1, date: '2024/1/22 16:22:39', action: '編輯個人資訊', user: 'User1' },
        { id: 2, date: '2024/1/22 16:00:21', action: '查看首頁', user: 'User2' },
        { id: 3, date: '2024/1/28 16:00:21', action: '修改密碼', user: 'User2' },
        { id: 4, date: '2023/12/28 16:00:21', action: '忘記密碼', user: 'User2' },
        // 添加更多的歷史紀錄項目
      ]
    }
  },
  computed: {
    filteredItems() {
      return this.items.filter(item => {
        const query = this.searchQuery.trim().toUpperCase();
        return item.action_description.toUpperCase().includes(query) || item.action_time.includes(query);
      });
    }
  },
  methods: {
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
    logout() {
      alert("已登出");
      this.$router.push('/login');
    }
  }
}
</script>

<style src="@/assets/css/frontend/HistoryPage.css"></style>
