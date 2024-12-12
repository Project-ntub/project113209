<template>
    <div>
        <div id="app" class="calendar-container">
            <div class="calendar-header">
                <button class="add-button-header" @click="toggleAddEventForm">＋</button>
            </div>

            <!-- 日曆組件 -->
            <Qalendar
                v-if="isReady"
                :key="calendarKey"
                :selected-date="today"
                :events="events"
                :config="config"
                @event-clicked="handleEventClick"
            >
                <template #monthEvent="eventProps">
                    <span
                        :style="{
                            backgroundColor: eventProps.eventData.privacy === 'private' ? '#6c757d' : '#007bff',
                            borderRadius: '50%',
                            display: 'inline-block',
                            width: '8px',
                            height: '8px',
                            margin: '2px',
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

        <!-- 事件詳細資訊彈窗 -->
        <div v-if="selectedEvent" class="modal">
            <div class="modal-content">
                <span class="close" @click="selectedEvent = null">&times;</span>
                <div class="event-flyout__info-wrapper">
                    <!-- 刪除與修改按鈕 -->
                    <!-- <div class="action-icons">
                        <span class="icon edit-icon" @click="editEvent(selectedEvent)">✏️</span>
                        <span class="icon delete-icon" @click="deleteEvent(selectedEvent.id)">🗑️</span>
                    </div> -->
                    <div class="event-flyout__row is-title">
                        <div
                            class="event-flyout__color-icon"
                            :style="{ backgroundColor: selectedEvent.privacy === 'private' ? '#6c757d' : '#007bff' }"
                        ></div>
                        <div>{{ selectedEvent.title }}</div>
                    </div>
                    <div class="event-flyout__row is-time">
                        {{ formatDateTime(selectedEvent.time.start) }} - {{ formatDateTime(selectedEvent.time.end) }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { Qalendar } from "qalendar";
import axios from "axios";
require("qalendar/dist/style.css");

axios.defaults.baseURL = "http://127.0.0.1:8000"; // 配置後端基礎 URL
axios.defaults.withCredentials = true; // 攜帶 Cookie 用於認證

export default {
    components: {
        Qalendar,
    },
    data() {
        return {
            isReady: false,
            today: new Date(),
            showAddEventForm: false,
            calendarKey: 0, // 用於強制日曆重新渲染
            events: [],
            newEvent: {
                title: "",
                start: "",
                end: "",
                privacy: "public",
            },
            selectedEvent: null,
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
        async fetchEvents() {
            try {
                const response = await axios.get("/frontend/calendar/events/");
                const events = response.data.map((event) => ({
                    id: event.id,
                    title: event.title || "未命名事件",
                    time: {
                        start: new Date(event.start).toISOString().slice(0, 16).replace("T", " "),
                        end: new Date(event.end).toISOString().slice(0, 16).replace("T", " "),
                    },
                    description: event.description || "",
                    privacy: event.privacy || "public",
                    color: event.privacy === "private" ? "#6c757d" : "#007bff", // 私人灰色，公開藍色
                }));
                console.log("確認事件顏色：", events);
                this.events = events;
            } catch (error) {
                console.error("加載事件失敗:", error);
            }
        },
        toggleAddEventForm() {
            this.showAddEventForm = !this.showAddEventForm;
            if (!this.showAddEventForm) {
                this.newEvent = {
                    title: "",
                    start: "",
                    end: "",
                    privacy: "public",
                };
            }
        },
        async addEvent() {
            if (this.newEvent.title && this.newEvent.start && this.newEvent.end) {
                const event = {
                    title: this.newEvent.title,
                    start: new Date(this.newEvent.start).toISOString(),
                    end: new Date(this.newEvent.end).toISOString(),
                    description: this.newEvent.description || "",
                    privacy: this.newEvent.privacy,
                };
                try {
                    const response = await axios.post(
                        "/frontend/calendar/events/add/",
                        event
                    );
                    const newEvent = response.data;

                    // 確保返回的數據格式正確
                    if (newEvent.start && newEvent.end) {
                        this.events.push({
                            id: newEvent.id,
                            title: newEvent.title || "未命名事件",
                            time: {
                                start: new Date(newEvent.start).toISOString().slice(0, 16).replace("T", " "),
                                end: new Date(newEvent.end).toISOString().slice(0, 16).replace("T", " "),
                            },
                            description: newEvent.description || "",
                            privacy: newEvent.privacy || "public",
                            color: newEvent.privacy === "private" ? "#6c757d" : "#007bff",
                        });
                        this.calendarKey += 1;
                        this.toggleAddEventForm();
                    } else {
                        console.error("後端返回的數據不完整:", newEvent);
                        alert("新增事件失敗：數據不完整！");
                    }
                } catch (error) {
                    console.error("新增事件失敗:", error);
                    alert("新增事件失敗！");
                }
            } else {
                alert("請填寫完整的事件資料！");
            }
        },
        async deleteEvent(eventId) {
            try {
                await axios.delete(`/frontend/calendar/events/delete/${eventId}/`);
                this.events = this.events.filter((event) => event.id !== eventId);
                this.calendarKey += 1; // 強制刷新日曆
                this.selectedEvent = null;
            } catch (error) {
                console.error("刪除事件失敗:", error);
                alert("刪除事件失敗！");
            }
        },
        editEvent(event) {
            this.newEvent = { ...event };
            this.showAddEventForm = true;
        },
        handleEventClick(event) {
            this.selectedEvent = event;
        },
        formatDateTime(date) {
            return new Date(date).toLocaleString("zh-TW", {
                dateStyle: "short",
                timeStyle: "short",
            });
        },
    },
    mounted() {
        this.fetchEvents().then(() => {
            console.log("傳遞給 Qalendar 的事件數據：", this.events);
            this.isReady = true;
        });
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
    top: -60px;
    margin-left: -40px;
}

.modal {
    z-index: 2;
    position: fixed;
    margin-top: 30px;
    left: 0;
    width: 100%;
    height: 100%; /* 使遮罩覆蓋全視窗 */
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: rgba(0, 0, 0, 0.6); /* 半透明背景遮罩 */
}

.modal-content {
    background: #fff;
    padding: 5px; /* 增加內部間距 */
    border-radius: 10px;
    width: 400px; /* 固定寬度 */
    max-width: 90%; /* 避免小螢幕溢出 */
    max-height: 80vh;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    overflow-y: auto !important;
    position: relative; /* 確保子元素定位基於此 */
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

.delete-button {
    margin-top: 10px;
    padding: 10px 20px;
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.delete-button:hover {
    background-color: #a71d2a;
}

label {
    display: block;
    margin-top: 5px;
    margin-bottom: 2px;
    font-size: 16px;
    color: #333;
}

input,
select {
    width: 100%;
    padding: 2.5px;
    margin-top: 1px;
    margin-bottom: 2px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
}

input:focus,
select:focus {
    outline: none;
    border-color: #007bff;
}

h3 {
    margin: 0 0 10px 0;
    font-size: 16px;
    text-align: center;
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

/* .action-icons {
    position: absolute;
    top: 10px;
    left: 10px;
    display: flex;
    gap: 10px;
    z-index: 9999; 
} */

/* .icon {
    cursor: pointer;
    font-size: 16px;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f5f5;
    border-radius: 50%;
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
} */

.icon:hover {
    background-color: #e0e0e0;
}

.edit-icon {
    color: #007bff;
}

.delete-icon {
    color: #dc3545;
}

.event-flyout__color-icon {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    display: inline-block;
    background-color: var(--event-color, #007bff) !important;
}
</style>