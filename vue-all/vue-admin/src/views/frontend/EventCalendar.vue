<template>
	<div>
	  <div id="app" class="calendar-container">
		<div class="calendar-header">
 			 <button class="add-button-header" @click="toggleAddEventForm">＋</button>
		</div>

  
		<!-- 日曆組件 -->
		<Qalendar
		  v-if="isReady"
		  :selected-date="today"
		  :events="events"
		  :config="config"
		  @date-clicked="handleDateClick"
		>
		  <template #monthEvent="eventProps">
			<span
			  :style="{
				backgroundColor: eventProps.eventData.color,
				borderRadius: '50%',
				display: 'inline-block',
				width: '8px',
				height: '8px',
			  }"
			></span>
		  </template>
		</Qalendar>
	  </div>
  
	  <!-- 新增事件表單 -->
	  <div v-if="showAddEventForm" class="modal">
		<div class="modal-content">
		  <span class="close" @click="toggleAddEventForm">&times;</span>
		  <h3>新增事件</h3>
		  <label for="title">事件標題：</label>
		  <input type="text" id="title" v-model="newEvent.title" placeholder="輸入事件標題" />
  
		  <label for="start">開始時間：</label>
		  <input type="datetime-local" id="start" v-model="newEvent.start" />
  
		  <label for="end">結束時間：</label>
		  <input type="datetime-local" id="end" v-model="newEvent.end" />
  
		  <label for="privacy">公開或私人：</label>
		  <select id="privacy" v-model="newEvent.privacy">
			<option value="public">公開</option>
			<option value="private">私人</option>
		  </select>
  
		  <button class="save-button" @click="addEvent">保存</button>
		</div>
	  </div>
	</div>
  </template>
  
  <script>
  import { Qalendar } from "qalendar";
  require("qalendar/dist/style.css");
  
  export default {
	components: {
	  Qalendar,
	},
	data() {
	  return {
		isReady: false,
		today: new Date(),
		showAddEventForm: false,
		events: [
		  {
			id: "event-1",
			title: "Meeting with Dora",
			time: { start: "2024-12-10 09:00", end: "2024-12-10 10:00" },
			color: "blue",
		  },
		],
		newEvent: {
		  title: "",
		  start: "",
		  end: "",
		  privacy: "public",
		},
		config: {
		  locale: "zh-TW",
		  defaultMode: "month",
		  style: {
			fontFamily: "Arial, sans-serif",
		  },
		},
	  };
	},
	methods: {
	  // 切換新增事件表單
	  toggleAddEventForm() {
		this.showAddEventForm = !this.showAddEventForm;
		if (!this.showAddEventForm) {
		  // 清空表單
		  this.newEvent = {
			title: "",
			start: "",
			end: "",
			privacy: "public",
		  };
		}
	  },
  
	  // 新增事件
	  addEvent() {
		if (this.newEvent.title && this.newEvent.start && this.newEvent.end) {
		  const newEvent = {
			id: `event-${this.events.length + 1}`,
			title: this.newEvent.title,
			time: {
			  start: this.newEvent.start,
			  end: this.newEvent.end,
			},
			color: this.newEvent.privacy === "public" ? "blue" : "gray", // 公開或私人顏色
		  };
  
		  // 新增事件到事件列表
		  this.events.push(newEvent);
  
		  // 關閉表單並清空內容
		  this.toggleAddEventForm();
		} else {
		  alert("請填寫完整的事件資料！");
		}
	  },
	},
	mounted() {
	  this.isReady = true;
	},
  };
  </script>
  
  <style>
.calendar-container {
	position: relative;
	z-index: 1;
	height: 420px;
	width: 120%;
	margin: 0 auto; /* 水平置中 */
	max-width: 1200px; /* 限制最大寬度，避免過大 */
	min-width: 800px; /* 限制最小寬度 */
	top:-60px;
	margin-left: -40px;
}

.modal {
  z-index: 2; 
  position: fixed; /* 固定在視窗中央 */
  margin-top: 30px;
  left: 0;
  width: 100%;
  height: 100%; /* 使遮罩覆蓋全視窗 */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.6); /* 半透明背景遮罩 */
  overflow: hidden; /* 確保背景不滾動 */
  
}

.modal-content {
  background: #fff;
  padding: 20px; /* 增加內部間距 */
  border-radius: 10px;
  width: 400px; /* 固定寬度 */
  max-width: 90%; /* 避免小螢幕溢出 */
  max-height: 60vh;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow-y: auto; /* 垂直方向啟用滾動條 */
  position: relative;
  
}

.close {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  cursor: pointer;
  position: absolute;
  top: 10px;
  right: 15px;
}

.save-button {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.save-button:hover {
  background-color: #0056b3;
}

label {
  display: block;
  margin-top: 10px;
}

input,
select {
  width: 100%;
  padding: 3px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 0px; /* 增加輸入框之間的垂直間距 */
}

input:focus,
select:focus {
  outline: none;
  border-color: #007bff;
}

h3 {
  margin: 0;
  font-size: 18px;
  text-align: center; /* 標題置中 */
}
.calendar-header {
  display: flex; /* 使用 Flexbox 排版 */
  justify-content: flex-end; /* 按鈕靠右排列 */
  align-items: center; /* 垂直置中 */
  padding-right: -80px; /* 向右移動按鈕，調整間距 */
  margin-top: 20px; /* 按鈕向下移動 */
}
.add-button-header {
  position: absolute; /* 絕對定位 */
  top: 1%; 
  right: -60px; /* 按鈕向右偏移 */
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 30%; /* 圓形按鈕 */
  width: 40px;
  height: 40px;
  font-size: 20px;
  cursor: pointer;
  display: flex; /* 使用 Flexbox */
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.add-button-header:hover {
  background-color: #0056b3;
}
  </style>
  