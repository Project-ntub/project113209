<template>
  <ChartContainer class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </ChartContainer>
</template>

<script>
import { Chart as ChartJS, RadarController, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend } from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';

ChartJS.register(RadarController, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

export default {
  name: 'RevenueChart',
  components: {
    ChartContainer
  },
  data() {
    return {
      chartData: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [
          {
            label: 'Revenue',
            backgroundColor: '#f87979',
            data: [50, 25, 18, 45, 20, 50, 45, 100, 50, 45, 100, 50]
          }
        ]
      }
    };
  },
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      new ChartJS(ctx, {
        type: 'line', // 根據需要調整類型
        data: this.chartData,
        options: { 
          responsive: true, 
          maintainAspectRatio: false 
        }
      });
    }
  }
};
</script>

<style scoped>
.chart-container {
  width: 100%; /* 確保容器寬度佔滿父級 */
  max-height: 300px; /* 設置最大高度 */
  overflow: auto; /* 啟用滾動條 */
}

canvas {
  width: 100% !important; /* 設定寬度為100%以適應容器 */
  height: 100% !important; /* 高度自動適應容器 */
}

/* 響應式設計 */
@media (max-width: 768px) {
  .chart-container {
    max-height: 250px; /* 在小屏幕上調整最大高度 */
  }
}

@media (max-width: 480px) {
  .chart-container {
    max-height: 200px; /* 在超小屏幕上調整最大高度 */
  }
}
</style>
