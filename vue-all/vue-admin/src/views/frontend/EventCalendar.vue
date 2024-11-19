<script setup>
import { ref } from 'vue';
import { ScheduleXCalendar } from '@schedule-x/vue';
import {
  createCalendar,
  createViewDay,
  createViewWeek,
  createViewMonthGrid,
  createViewMonthAgenda,
} from '@schedule-x/calendar';
import axios from 'axios';  // 用於與後端 API 通訊
import '@schedule-x/theme-default/dist/index.css';  // 預設樣式

// 初始化日曆
const calendarApp = createCalendar({
  selectedDate: '2023-12-19', // 初始選中日期
  views: [
    createViewDay(),
    createViewWeek(),
    createViewMonthGrid(),
    createViewMonthAgenda(),
  ],
  events: [
    { id: 1, title: '測試事件', start: '2023-12-19T10:00:00', end: '2023-12-19T11:00:00' }, // 假事件數據
  ],
});

// 從後端動態加載事件
const fetchEvents = async () => {
  try {
    const response = await axios.get('/calendar/events/');
    const events = response.data.map((event) => ({
      id: event.id,
      title: event.title,
      start: event.start,
      end: event.end,
    }));
    calendarApp.setEvents(events); // 更新日曆的事件
  } catch (error) {
    console.error('加載事件失敗:', error);
  }
};

// 對話框相關狀態
const isDialogOpen = ref(false);
const dialogMode = ref('add'); // 'add' 用於新增事件
const form = ref({ id: null, title: '', start: '', end: '' });

// 打開對話框以新增事件
const openAddDialog = () => {
  dialogMode.value = 'add';
  form.value = { id: null, title: '', start: '', end: '' }; // 初始化表單數據
  isDialogOpen.value = true;
};

// 關閉對話框
const closeDialog = () => {
  isDialogOpen.value = false;
};

// 提交對話框
const handleDialogSubmit = async () => {
  const event = { ...form.value };
  if (dialogMode.value === 'add') {
    try {
      const response = await axios.post('/calendar/events/add/', event);  // 發送請求新增事件
      calendarApp.addEvent(response.data);  // 立即將新增事件添加到日曆
      closeDialog(); // 提交後關閉對話框
    } catch (error) {
      console.error('新增事件失敗:', error);
    }
  }
};

// 初始化時加載事件
fetchEvents();
</script>

<template>
  <div class="calendar-container">
    <div class="calendar-header">
      <button @click="openAddDialog" class="add-event-btn">新增事件</button>
    </div>
    <ScheduleXCalendar :calendar-app="calendarApp" />
    <div v-if="isDialogOpen" class="dialog-overlay">
      <div class="dialog">
        <h3>{{ dialogMode === 'edit' ? '編輯事件' : '新增事件' }}</h3>
        <form @submit.prevent="handleDialogSubmit">
          <div>
            <label for="title">標題</label>
            <input id="title" v-model="form.title" type="text" required />
          </div>
          <div>
            <label for="start">開始時間</label>
            <input id="start" v-model="form.start" type="datetime-local" required />
          </div>
          <div>
            <label for="end">結束時間</label>
            <input id="end" v-model="form.end" type="datetime-local" required />
          </div>
          <div>
            <button type="submit">{{ dialogMode === 'edit' ? '保存' : '新增' }}</button>
            <button type="button" @click="closeDialog">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-container {
  position: relative;
}

.calendar-header {
  position: absolute;
  top: 20px;
  right: 400px; /* 調整按鈕位置，避免太靠右 */
  z-index: 10;
}

.add-event-btn {
  padding: 10px 20px;
  background-color: #4caf50;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.add-event-btn:hover {
  background-color: #45a049;
}

.sx-vue-calendar-wrapper {
  width: 1200px;
  max-width: 100vw;
  height: 800px;
  max-height: 90vh;
}

.sx-vue-calendar {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  width: 300px;
}

.delete-btn {
  background-color: #f44336;
  color: #fff;
  border: none;
  border-radius: 5px;
  padding: 5px 10px;
  cursor: pointer;
}

.delete-btn:hover {
  background-color: #e53935;
}
</style>
