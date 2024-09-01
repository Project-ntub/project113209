<template>
  <ChartContainer>
    <canvas ref="chartCanvas"></canvas>
  </ChartContainer>
</template>

<script>
import { 
  Chart as ChartJS, 
  ScatterController, // 匯入 ScatterController
  PointElement, 
  LinearScale, 
  Title, 
  Tooltip, 
  Legend, 
  CategoryScale 
} from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';

// 註冊 ScatterController 和其他需要的組件
ChartJS.register(
  ScatterController, // 確保註冊這個
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
            data: [{ x: 10, y: 20 }, { x: 15, y: 10 }, { x: 20, y: 25 }, { x: 30, y: 35 }],
          }
        ]
      }
    };
  },
    methods: {
      renderChart() {
        const ctx = this.$refs.chartCanvas.getContext('2d');
        this.chartInstance = new ChartJS(ctx, {
          type: 'scatter', // 根據需要調整類型
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
canvas {
  width: 100% !important;
  height: 100% !important; /* 使用百分比以確保圖表隨容器縮放 */
}
</style>
