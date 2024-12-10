<template>
	<div>
	  <div id="app" class="calendar-container">
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
	  <div v-if="showModal" class="modal">
		<div class="modal-content">
		  <span class="close" @click="closeModal">&times;</span>
		  <h3>{{ modalDate }}</h3>
		  <div v-if="modalEvents.length > 0">
			<ul>
			  <li v-for="event in modalEvents" :key="event.id">
				<strong>{{ event.title }}</strong> - {{ event.time.start }} 至 {{ event.time.end }}
			  </li>
			</ul>
		  </div>
		  <div v-else>
			<p>沒有活動</p>
		  </div>
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
      showModal: false,
      modalDate: "",
      modalEvents: [],
      events: [
        {
          id: "event-1",
          title: "Meeting with Dora",
          time: { start: "2024-12-10 09:00", end: "2024-12-10 10:00" },
          color: "blue",
        },
      ],
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
    handleDateClick(date) {
      this.modalDate = date.toISOString().split("T")[0];
      this.modalEvents = this.events.filter((event) =>
        event.time.start.startsWith(this.modalDate)
      );
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
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
	z-index: 2;
	height: 450px;
	width: 330%;
	margin: 0 auto; /* 水平置中 */
	/* margin-top: -120px; */
	top:-60px;
	margin-left: -230px;
}
.modal {
	z-index: 10;
	position: fixed;
	width: 100%;
	height: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: rgba(0, 0, 0, 0.4);
}
.modal-content {
	background: #fff;
	padding: 20px;
	border-radius: 10px;
	width: 400px;
}
</style>
