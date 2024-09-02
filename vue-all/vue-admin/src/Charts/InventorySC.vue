<template>
  <ChartContainer class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </ChartContainer>
</template>

<script>
import { 
  Chart as ChartJS, 
  RadarController, 
  PointElement, 
  RadialLinearScale, 
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';

// 注册所有需要的组件，包括 RadialLinearScale
ChartJS.register(
  RadarController,
  PointElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
);

export default {
  name: 'InventorySC',
  components: {
    ChartContainer
  },
  data() {
    return {
      chartData: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [
          {
            label: 'Inventory',
            backgroundColor: 'rgba(34,202,236,0.2)',
            borderColor: 'rgba(34,202,236,1)',
            pointBackgroundColor: 'rgba(34,202,236,1)',
            data: [50, 25, 18, 45, 20, 50, 45, 100, 50, 45, 100, 50]
          }
        ]
      }
    };
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      new ChartJS(ctx, {
        type: 'radar', // 确保使用的是 'radar' 类型
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
};
</script>

<style scoped>
.chart-container {
  width: 100%; /* 容器宽度为100% */
  max-height: 400px; /* 设置最大高度 */
  overflow: auto; /* 启用滚动条 */
}

canvas {
  width: 100% !important; /* 画布宽度占满容器 */
  height: 100% !important; /* 画布高度占满容器 */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-container {
    max-height: 300px; /* 在小屏幕上调整最大高度 */
  }
}

@media (max-width: 480px) {
  .chart-container {
    max-height: 200px; /* 在超小屏幕上调整最大高度 */
  }
}
</style>
