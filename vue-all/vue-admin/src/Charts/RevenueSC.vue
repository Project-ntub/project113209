<template>
  <ChartContainer class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </ChartContainer>
</template>

<script>
import { 
  Chart as ChartJS, 
  ScatterController, 
  PointElement, 
  LinearScale, 
  Title, 
  Tooltip, 
  Legend, 
  CategoryScale 
} from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';

// 注册 ScatterController 和其他需要的组件
ChartJS.register(
  ScatterController, 
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend
);

export default {
  name: 'RevenueSC',
  components: {
    ChartContainer
  },
  data() {
    return {
      chartData: {
        datasets: [
          {
            label: 'Scatter Dataset',
            backgroundColor: '#ff6384',
            borderColor: '#ff6384',
            data: [{ x: 10, y: 20 }, { x: 15, y: 10 }, { x: 20, y: 25 }, { x: 30, y: 35 }]
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
        type: 'scatter', // 使用 'scatter' 类型
        data: this.chartData,
        options: { responsive: true, maintainAspectRatio: false }
      });
    }
  }
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
