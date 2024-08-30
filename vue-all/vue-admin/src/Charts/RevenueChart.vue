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
            data: [30, 10, 5, 25, 15, 30, 25, 60, 30, 25, 60, 30]
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
        type: 'line',
        data: this.chartData,
        options: { responsive: true, maintainAspectRatio: false }
      });
    }
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%; /* 确保容器宽度占满父级 */
  max-height: 300px; /* 设置最大高度 */
  overflow: auto; /* 启用滚动条 */
}

canvas {
  width: 100% !important; /* 设置宽度为100%以适应容器 */
  height: 100% !important; /* 高度自动适应容器 */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-container {
    max-height: 250px; /* 在小屏幕上调整最大高度 */
  }
}

@media (max-width: 480px) {
  .chart-container {
    max-height: 200px; /* 在超小屏幕上调整最大高度 */
  }
}
</style>
