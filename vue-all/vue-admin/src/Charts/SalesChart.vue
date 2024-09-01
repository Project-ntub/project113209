<template>
  <ChartContainer>
    <div class="chart-wrapper">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </ChartContainer>
</template>

<script>
import { Chart as ChartJS, LineController, LineElement, PointElement, LinearScale, Title, Tooltip, Legend, CategoryScale } from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';  // 引入通用容器组件

ChartJS.register(LineController, LineElement, PointElement, LinearScale, Title, Tooltip, Legend, CategoryScale);

export default {
  name: 'SalesChart',
  components: {
    ChartContainer
  },
  data() {
    return {
      chartData: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [
          {
            label: 'Sales',
            backgroundColor: '#f87979',
            data: [40, 20, 12, 39, 10, 40, 39, 80, 40, 39, 80, 40]
          }
        ]
      }
    };
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chartInstance = new ChartJS(ctx, {
        type: 'line', // 根據需要調整類型
        data: this.chartData,
        options: { 
          responsive: true, 
          maintainAspectRatio: false 
        },
      });
    }
  },
  mounted() {
    this.renderChart();
  },
}
</script>

<style scoped>
.chart-wrapper {
  width: 100%; /* 容器宽度占满父级 */
  max-height: 400px; /* 设置最大高度以启用滚动条 */
  overflow: auto; /* 启用滚动条 */
}

canvas {
  width: 100% !important; /* 默认占据容器的全部宽度 */
  height: 100% !important; /* 高度设为100%以适应容器 */
}

/* 超小屏幕 (如手机) */
@media (max-width: 480px) {
  .chart-wrapper {
    max-height: 250px !important; /* 在小屏幕上减少最大高度 */
  }
}

@media (max-width: 480px) {
  canvas {
    height: auto !important; /* 确保 canvas 高度自动适应容器 */
  }
}

/* 小型设备 (如小平板) */
@media (min-width: 481px) and (max-width: 768px) {
  .chart-wrapper {
    max-height: 300px !important; /* 小平板设备的最大高度适中 */
  }
}

/* 中型设备 (如大平板) */
@media (min-width: 769px) and (max-width: 1024px) {
  .chart-wrapper {
    max-height: 350px !important; /* 大平板设备的最大高度适中 */
  }
}

/* 大型设备 (如桌面) */
@media (min-width: 1025px) {
  .chart-wrapper {
    max-height: 400px !important; /* 在桌面上恢复默认最大高度 */
  }
}
</style>
